import hmac
import hashlib
import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_PUBLIC_KEY}",
    "Content-Type": "application/json",
}


class PaystackService:

    @staticmethod
    def initialize_subscription(email, plan_code, firm_id, callback_url):
        """
        Step 1 — Initialize a subscription transaction.
        Returns the authorization_url to redirect the user to.
        """
        payload = {
            "email": email,
            "plan": plan_code,
            "callback_url": callback_url,
            "metadata": {
                "firm_id": firm_id,
            }
        }
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload,
            headers=HEADERS
        )
        data = response.json()
        if data.get("status"):
            return data["data"]["authorization_url"], data["data"]["reference"]
        raise Exception(f"Paystack initialization failed: {data.get('message')}")

    @staticmethod
    def verify_transaction(reference):
        """
        Step 2 — Verify transaction after callback.
        Returns full transaction data including subscription_code and customer_code.
        """
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=HEADERS
        )
        data = response.json()
        if data.get("status"):
            return data["data"]
        raise Exception(f"Paystack verification failed: {data.get('message')}")

    @staticmethod
    def cancel_subscription(subscription_code, email_token):
        """
        Cancel a subscription via Paystack.
        email_token comes from the subscription object.
        """
        payload = {
            "code": subscription_code,
            "token": email_token,
        }
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/subscription/disable",
            json=payload,
            headers=HEADERS
        )
        return response.json()

    @staticmethod
    def get_subscription(subscription_code):
        """
        Fetch current subscription details from Paystack.
        """
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/subscription/{subscription_code}",
            headers=HEADERS
        )
        return response.json()

    @staticmethod
    def verify_webhook_signature(payload_bytes, signature):
        """
        Verify that the webhook actually came from Paystack.
        """
        secret = settings.PAYSTACK_SECRET_KEY.encode("utf-8")
        computed = hmac.new(secret, payload_bytes, hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed, signature)
    
