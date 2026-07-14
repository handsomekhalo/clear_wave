import json
import hmac
import hashlib
from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from system_management.models import Firm
from system_management.paystack import PaystackService


# Reverse lookup: plan_code → plan name
def get_plan_name_from_code(plan_code):
    return next(
        (name for name, code in settings.PAYSTACK_PLANS.items() if code == plan_code),
        None
    )


# ─────────────────────────────────────────────
# VIEW 1 — INITIALIZE SUBSCRIPTION
# ─────────────────────────────────────────────

class InitializeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Only firm owners can subscribe
        if not user.is_firm_owner():
            return Response(
                {"error": "Only firm owners can manage subscriptions."},
                status=status.HTTP_403_FORBIDDEN
            )

        plan_name = request.data.get("plan")
        if not plan_name:
            return Response(
                {"error": "Plan is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        plan_code = settings.PAYSTACK_PLANS.get(plan_name)
        if not plan_code:
            return Response(
                {"error": "Invalid plan selected."},
                status=status.HTTP_400_BAD_REQUEST
            )

        firm = user.firm
        if not firm:
            return Response(
                {"error": "No firm associated with this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        callback_url = f"{settings.FRONTEND_URL}/subscription/callback"

        try:
            authorization_url, reference = PaystackService.initialize_subscription(
                email=user.email,
                plan_code=plan_code,
                firm_id=firm.id,
                callback_url=callback_url,
            )
            return Response({
                "authorization_url": authorization_url,
                "reference": reference,
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )


# ─────────────────────────────────────────────
# VIEW 2 — CALLBACK (Paystack redirects here)
# ─────────────────────────────────────────────

class SubscriptionCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get("reference") or request.query_params.get("trxref")

        if not reference:
            return redirect(f"{settings.FRONTEND_URL}/subscription?error=missing_reference")

        try:
            transaction = PaystackService.verify_transaction(reference)
        except Exception:
            return redirect(f"{settings.FRONTEND_URL}/subscription?error=verification_failed")

        # Only activate on successful charge
        if transaction.get("status") != "success":
            return redirect(f"{settings.FRONTEND_URL}/subscription?error=payment_failed")

        firm_id = transaction.get("metadata", {}).get("firm_id")
        if not firm_id:
            return redirect(f"{settings.FRONTEND_URL}/subscription?error=missing_firm")

        try:
            firm = Firm.objects.get(id=firm_id)
        except Firm.DoesNotExist:
            return redirect(f"{settings.FRONTEND_URL}/subscription?error=firm_not_found")

        # Map plan code back to our plan name
        plan_code = transaction.get("plan", {}).get("plan_code", "")
        plan_name = get_plan_name_from_code(plan_code) or "solo"

        # Update firm subscription
        firm.subscription_status = Firm.ACTIVE
        firm.subscription_plan = plan_name
        firm.last_payment_date = date.today()
        firm.subscription_end_date = date.today() + relativedelta(months=1)
        firm.paystack_customer_code = transaction.get("customer", {}).get("customer_code", "")

        # subscription_code may arrive here or via webhook — store if present
        subscription_code = transaction.get("subscription_code", "")
        if subscription_code:
            firm.paystack_subscription_code = subscription_code

        # Update user limits based on plan
        plan_limits = {
            "solo": {"max_users": 1, "max_active_cases": 999, "storage_limit_gb": 10},
            "small_firm": {"max_users": 3, "max_active_cases": 999, "storage_limit_gb": 25},
            "growing_firm": {"max_users": 10, "max_active_cases": 999, "storage_limit_gb": 50},
        }
        limits = plan_limits.get(plan_name, plan_limits["solo"])
        firm.max_users = limits["max_users"]
        firm.max_active_cases = limits["max_active_cases"]
        firm.storage_limit_gb = limits["storage_limit_gb"]

        firm.save()

        return redirect(f"{settings.FRONTEND_URL}/subscription?success=true&plan={plan_name}")


# ─────────────────────────────────────────────
# VIEW 3 — WEBHOOK (Paystack server → your server)
# ─────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        signature = request.headers.get("x-paystack-signature", "")

        # Verify it actually came from Paystack
        computed = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            request.body,
            hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(computed, signature):
            return Response({"error": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON."}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get("event")
        data = payload.get("data", {})

        if event == "subscription.create":
            self._handle_subscription_create(data)

        elif event == "charge.success":
            self._handle_charge_success(data)

        elif event == "invoice.payment_failed":
            self._handle_payment_failed(data)

        elif event == "subscription.disable":
            self._handle_subscription_disabled(data)

        # Always return 200 — Paystack will retry if you don't
        return Response({"status": "ok"})

    def _get_firm_by_customer_code(self, customer_code):
        return Firm.objects.filter(paystack_customer_code=customer_code).first()

    def _handle_subscription_create(self, data):
        """Fires after first payment — store the subscription_code."""
        customer_code = data.get("customer", {}).get("customer_code")
        subscription_code = data.get("subscription_code")

        firm = self._get_firm_by_customer_code(customer_code)
        if firm and subscription_code:
            firm.paystack_subscription_code = subscription_code
            firm.save(update_fields=["paystack_subscription_code"])

    def _handle_charge_success(self, data):
        """Fires on every successful recurring charge — extend subscription."""
        customer_code = data.get("customer", {}).get("customer_code")

        firm = self._get_firm_by_customer_code(customer_code)
        if not firm:
            return

        plan_code = data.get("plan", {}).get("plan_code", "")
        plan_name = get_plan_name_from_code(plan_code) or firm.subscription_plan

        firm.subscription_status = Firm.ACTIVE
        firm.subscription_plan = plan_name
        firm.last_payment_date = date.today()
        firm.subscription_end_date = date.today() + relativedelta(months=1)
        firm.save(update_fields=[
            "subscription_status",
            "subscription_plan",
            "last_payment_date",
            "subscription_end_date",
        ])

    def _handle_payment_failed(self, data):
        """Recurring charge failed — suspend the firm."""
        customer_code = data.get("customer", {}).get("customer_code")

        firm = self._get_firm_by_customer_code(customer_code)
        if firm:
            firm.subscription_status = Firm.SUSPENDED
            firm.save(update_fields=["subscription_status"])

    def _handle_subscription_disabled(self, data):
        """Subscription cancelled — downgrade to free tier."""
        customer_code = data.get("customer", {}).get("customer_code")

        firm = self._get_firm_by_customer_code(customer_code)
        if firm:
            firm.subscription_status = Firm.FREE_TIER
            firm.paystack_subscription_code = ""
            firm.save(update_fields=["subscription_status", "paystack_subscription_code"])