# # system_management/tests/test_case_management.py

# from rest_framework.test import APITestCase, APIClient
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth import get_user_model

# from system_management.models import User, Firm
# from case_management.models import Case  # ← import your Case model

# User = get_user_model()


# class BaseCaseTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()

#         # Reuse firms/users from your base if possible, or recreate minimal
#         self.firm = Firm.objects.create(
#             name="Case Test Firm",
#             subscription_status="free_tier",
#             subscription_plan="solo",
#             max_users=10,
#             max_active_cases=10,
#             storage_limit_gb=5
#         )

#         self.superadmin = User.objects.create_user(
#             email="super@case.com",
#             password="super123",
#             role="super_admin"
#         )

#         self.owner = User.objects.create_user(
#             email="owner@case.com",
#             password="owner123",
#             role="firm_owner",
#             firm=self.firm
#         )
#         self.firm.owner = self.owner
#         self.firm.save()

#         self.lawyer = User.objects.create_user(
#             email="lawyer@case.com",
#             password="law123",
#             role="lawyer",
#             firm=self.firm
#         )


# system_management/tests/test_case_management.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from system_management.models import User, Firm
from case_management.models import Case, CaseType, Note

User = get_user_model()


class BaseCaseTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Firm
        self.firm = Firm.objects.create(
            name="Case Test Firm",
            subscription_status="free_tier",
            subscription_plan="solo",
            max_users=10,
            max_active_cases=10,
            storage_limit_gb=5
        )

        # Users
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

        self.assistant = User.objects.create_user(
            email="assistant@case.com",
            password="assist123",
            role="assistant",
            firm=self.firm
        )

        self.client_user = User.objects.create_user(
            email="client@case.com",
            password="client123",
            role="client",
            firm=self.firm
        )

        # Matter Type (needed for case creation)
        self.matter_type = CaseType.objects.create(
            firm=self.firm,
            name="Divorce"
        )

        # A sample case (for detail/update/assign tests)
        self.case = Case.objects.create(
            firm=self.firm,
            title="Test Divorce Case",
            description="Test matter",
            client=self.client_user,
            matter_type=self.matter_type,
            created_by=self.lawyer,
            assigned_lawyer=self.lawyer,
            status=Case.NEW
        )
        self.case2 = Case.objects.create(
    firm=self.firm,
    title="Second Case",
    description="Another test",
    client=self.client_user,
    matter_type=self.matter_type,
    created_by=self.owner,
    status=Case.NEW,
    reference_number=f"2026-TEST-0002"  # <-- Add this
)


class CreateClientTests(BaseCaseTest):
    def test_firm_owner_can_create_client(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('create_client_api')  # adjust name if different

        data = {
            "email": "newclient@test.com",
            "first_name": "New",
            "last_name": "Client",
            "phone": "+27123456789",
            "password": "Client123!"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], "newclient@test.com")

    def test_assistant_can_create_client(self):
        self.client.force_authenticate(user=self.assistant)
        url = reverse('create_client_api')
        data = {"email": "assistclient@test.com", "first_name": "Assist", "last_name": "Client", "phone": "+27", "password": "Pass123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_cannot_create_client(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('create_client_api')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateCaseTests(BaseCaseTest):
    def test_lawyer_can_create_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('create_case_api')

        data = {
            "title": "New Divorce Matter",
            "description": "Test case",
            "client": self.client_user.id,
            "matter_type": self.matter_type.id,
            # "reference_number":self.generate_reference_number.id
        }   

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('case_id', response.data)
        # self.assertIn('reference_number', response.data)  # from generation

    def test_no_client_fails(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('create_case_api')
        data = {"title": "No Client", "description": "Test", "matter_type": self.matter_type.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client', response.data)  # required field error

    def test_wrong_firm_client_fails(self):
        other_client = User.objects.create_user(email="other@client.com", password="pass", role="client")  # no firm
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('create_case_api')
        data = {"title": "Wrong Client", "description": "Test", "client": other_client.id, "matter_type": self.matter_type.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Client must belong to your firm", str(response.data))


class ViewCasesByFirmTests(BaseCaseTest):
    def test_firm_owner_sees_all_cases(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('view_cases_by_firm_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # from setUp

    def test_lawyer_sees_assigned_or_created_cases(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('view_cases_by_firm_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # only the one assigned/created by lawyer

    def test_client_sees_only_own_cases(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('view_cases_by_firm_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # both cases have same client

    def test_superadmin_forbidden(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('view_cases_by_firm_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllMatterTypesTests(BaseCaseTest):
    def test_user_sees_firm_matter_types(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('get_all_matter_types_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # from setUp
        self.assertEqual(response.data[0]['name'], "Divorce")

    def test_superadmin_no_firm_fails(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('get_all_matter_types_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # from your view check


class CaseDetailTests(BaseCaseTest):
    def test_owner_can_view_any_case(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('case_detail_api', kwargs={'case_id': self.case.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Divorce Case")

    def test_lawyer_can_view_assigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('case_detail_api', kwargs={'case_id': self.case.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lawyer_cannot_view_unassigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('case_detail_api', kwargs={'case_id': self.case2.id})  # not assigned to lawyer
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdateCaseTests(BaseCaseTest):
    def test_owner_can_update_case(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('update_case_api', kwargs={'case_id': self.case.id})
        data = {"title": "Updated Title", "priority": "urgent"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case.refresh_from_db()
        self.assertEqual(self.case.title, "Updated Title")
        self.assertEqual(self.case.priority, "urgent")

    def test_lawyer_can_update_assigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('update_case_api', kwargs={'case_id': self.case.id})
        data = {"description": "Updated desc"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lawyer_cannot_update_unassigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('update_case_api', kwargs={'case_id': self.case2.id})
        response = self.client.patch(url, {"title": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AssignToCaseTests(BaseCaseTest):
    def test_owner_can_assign_lawyer(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('assign_to_case_api', kwargs={'case_id': self.case.id})
        data = {"user_id": self.lawyer.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case.refresh_from_db()
        self.assertEqual(self.case.assigned_lawyer, self.lawyer)

    def test_lawyer_can_assign_assistant(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('assign_to_case_api', kwargs={'case_id': self.case.id})
        data = {"user_id": self.assistant.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case.refresh_from_db()
        self.assertEqual(self.case.assigned_assistant, self.assistant)

    def test_assistant_cannot_assign(self):
        self.client.force_authenticate(user=self.assistant)
        url = reverse('assign_to_case_api', kwargs={'case_id': self.case.id})
        response = self.client.post(url, {"user_id": self.lawyer.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Run with: python manage.py test system_management.tests.test_case_management
# Run with: python manage.py test system_management.tests.test_case_management
# Run with: python manage.py test system_management.tests.test_case_management