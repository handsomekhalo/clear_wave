# system_management/tests/test_case_management.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from system_management.models import User, Firm
from case_management.models import Case  # ← import your Case model

User = get_user_model()


class BaseCaseTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Reuse firms/users from your base if possible, or recreate minimal
        self.firm = Firm.objects.create(
            name="Case Test Firm",
            subscription_status="free_tier",
            subscription_plan="solo",
            max_users=10,
            max_active_cases=10,
            storage_limit_gb=5
        )

        self.superadmin = User.objects.create_user(
            email="super@case.com",
            password="super123",
            role="super_admin"
        )

        self.owner = User.objects.create_user(
            email="owner@case.com",
            password="owner123",
            role="firm_owner",
            firm=self.firm
        )
        self.firm.owner = self.owner
        self.firm.save()

        self.lawyer = User.objects.create_user(
            email="lawyer@case.com",
            password="law123",
            role="lawyer",
            firm=self.firm
        )