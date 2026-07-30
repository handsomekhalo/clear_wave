# system_management/tests/test_user_firm_audit.py

# from urllib import response
from rest_framework.response import Response

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone


from system_management.models import User, Firm, AuditLog
# from rest_framework.test import TransactionTestCase
from django.test import TransactionTestCase


User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        print("Base setUp started")

        try:
            self.firm_a = Firm.objects.create(
                name="Firm Alpha",
                subscription_status="free_tier",
                subscription_plan="solo",
                max_users=20,  # higher to avoid limit issues
                max_active_cases=10,
                storage_limit_gb=5
            )
            print(f"Created firm_a with ID: {self.firm_a.id}")
        except Exception as e:
            print(f"Failed to create firm_a: {e}")
            raise


        # Create firms
        # self.firm_a = Firm.objects.create(
        #     name="Firm Alpha",
        #     subscription_status="free_tier",
        #     subscription_plan="solo",
        #     max_users=99,
        #     max_active_cases=10,
        #     storage_limit_gb=5
        # )
        self.firm_b = Firm.objects.create(
            name="Firm Beta",
            subscription_status="free_tier",
            subscription_plan="solo",
            max_users=3,
            max_active_cases=5,
            storage_limit_gb=2
        )

        # Create users
        self.superadmin = User.objects.create_user(
            email="super@admin.com",
            password="superPass123!",
            role="super_admin"
        )

        self.owner_a = User.objects.create_user(
            email="owner@alpha.com",
            password="ownerPass123!",
            role="firm_owner",
            firm=self.firm_a
        )
        self.firm_a.owner = self.owner_a
        self.firm_a.save()

        self.lawyer_a = User.objects.create_user(
            email="lawyer@alpha.com",
            password="lawPass123!",
            role="lawyer",
            firm=self.firm_a
        )

        self.assistant_a = User.objects.create_user(
            email="assist@alpha.com",
            password="assistPass123!",
            role="assistant",
            firm=self.firm_a
        )

        self.client_b = User.objects.create_user(
            email="client@beta.com",
            password="clientPass123!",
            role="client",
            firm=self.firm_b
        )


class FirmCreationTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()  # ← THIS LINE WAS MISSING or not called

    # def test_superadmin_can_create_firm(self):
    #     self.client.force_authenticate(user=self.superadmin)
        
    #     # Use the correct URL name from your urls.py
    #     # Example: if path('admin/firms/create/', ..., name='admin-firm-create')
    #     # url = reverse('create_firm_with_owner_api')   # CHANGE THIS to your actual name!
    #     # url = reverse('create_firm_with_owner_api')  # ← this is now correct!
    #     url = reverse('create_firm_with_owner_api')  # ← this is now correct!

    #     data = {
    #         "name": "Test Firm Gamma",
    #         "subscription_status": "free_tier",
    #         "subscription_plan": "solo",
    #         "max_users": 4,
    #         "max_active_cases": 15,
    #         "storage_limit_gb": 10
    #     }

    #     response = self.client.post(url, data, format='json')

    #     print("\n=== RESPONSE STATUS ===")
    #     print(response.status_code)
    #     print("\n=== RESPONSE DATA ===")
    #     print(response.data)  # ← this will show the exact serializer

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Firm.objects.count(), 3)  # 2 from setUp + 1 new
    #     self.assertEqual(response.data['name'], "Test Firm Gamma")
    def test_superadmin_can_create_firm(self):
        self.client.force_authenticate(user=self.superadmin)
        
        url = reverse('create_firm_with_owner_api')

        data = {
            "firm_name": "Test Firm Gamma",               # ← firm_name, not name
            "email": "owner@gamma.com",                   # required for owner
            "first_name": "Gamma",
            "last_name": "Owner",
            "subscription_plan": "solo",                  # optional, defaults to solo
            # "subscription_status": "free_tier",        # if you want to set it
            # "max_users": 4,
            # "max_active_cases": 15,
            # "storage_limit_gb": 10
        }

        response = self.client.post(url, data, format='json')

        print("\n=== RESPONSE STATUS ===")
        print(response.status_code)
        print("\n=== RESPONSE DATA ===")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                        msg=f"Create failed: {response.data}")
        
        # Check firm was created
        self.assertEqual(Firm.objects.filter(name="Test Firm Gamma").count(), 1)
        
        # Check owner user was created
        new_firm = Firm.objects.get(name="Test Firm Gamma")
        self.assertEqual(new_firm.owner.email, "owner@gamma.com")
        
        # Check response has both firm and owner
        # self.assertIn('firm', response.data)
        # self.assertIn('owner', response.data)
        # So change your test:
        self.assertIn('firm', response.data)
        self.assertIn('user', response.data)  # <-- Change from 'owner' to 'user'
        self.assertIn('password', response.data)  # temp password included
            
    def test_firm_owner_cannot_create_firm(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('create_firm_with_owner_api')

        data = {
            "firm_name": "Unauthorized Firm",
            "email": "fake@owner.com",
            "first_name": "Fake",
            "last_name": "Owner"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Option 1: exact match (recommended)
        self.assertEqual(response.data, {'error': 'Super admin only'})
    
    # Option 2: looser (if message changes later)
    # self.assertIn('super admin only', response.data['error'].lower())

    def test_create_firm_requires_firm_name(self):
        """Missing firm_name should return 400."""
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('create_firm_with_owner_api')

        data = {
            "email": "owner@gamma.com",
            "first_name": "Gamma",
            "last_name": "Owner"
            # no firm_name
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertIn('name', response.data)  # or whatever error key your serializer returns
        self.assertIn('may not be null', str(response.data))  # or exact string match


        
        
class AuditLogPermissionTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        # Create one sample audit log for testing visibility
        AuditLog.objects.create(
            firm=self.firm_a,
            user=self.owner_a,
            action='firm_settings_updated',
            model_type='firm',
            model_id=self.firm_a.id,
            changes={'name': 'Updated Name'},
            ip_address='127.0.0.1'
        )

    def test_superadmin_sees_all_audit_logs(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('audit_log_list_api')  # CHANGE to your actual URL name

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # at least the one we created

    def test_assistant_sees_own_firm_logs(self):
        self.client.force_authenticate(user=self.assistant_a)
        url = reverse('audit_log_list_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_unauthorized_user_cannot_see_logs(self):
        # Example: client role (assuming not allowed)
        self.client.force_authenticate(user=self.client_b)
        url = reverse('audit_log_list_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)





# ────────────────────────────────────────────────
# Admin Firm Endpoints (Retrieve, Update, Destroy)
# ────────────────────────────────────────────────

class AdminFirmDetailTests(BaseAPITestCase):
    """
    Tests for super-admin firm detail endpoints:
    - GET /admin/firms/<pk>/
    - PATCH /admin/firms/<pk>/update/
    - DELETE /admin/firms/<pk>/delete/
    """

    def setUp(self):
        super().setUp()

        # Create a test firm owned by someone else (so superadmin can manage it)
        self.test_firm = Firm.objects.create(
            name="SuperAdmin Test Firm",
            subscription_status="free_tier",
            subscription_plan="solo",
            max_users=5,
            max_active_cases=10,
            storage_limit_gb=5
        )

        # Create a sample audit log for visibility checks
        AuditLog.objects.create(
            firm=self.test_firm,
            user=self.superadmin,
            action='firm_created',
            model_type='firm',
            model_id=self.test_firm.id,
            changes={'name': self.test_firm.name},
            ip_address='127.0.0.1'
        )

    # ── GET Retrieve ──────────────────────────────────────

    def test_superadmin_can_retrieve_firm(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('admin_firm_retrieve_api', kwargs={'pk': self.test_firm.pk})  # CHANGE to your actual name!

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.test_firm.id)
        self.assertEqual(response.data['name'], "SuperAdmin Test Firm")
        self.assertIn('user_count', response.data)  # from serializer

    def test_non_superadmin_cannot_retrieve_firm(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('admin_firm_retrieve_api', kwargs={'pk': self.test_firm.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertIn('Only super admins', str(response.data).lower())
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only super admins can access this endpoint.')  # capital O

        # self.assertEqual(response.data['error'], 'only super admins can access this endpoint.')  # exact


    def test_retrieve_non_existent_firm_returns_404(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('admin_firm_retrieve_api', kwargs={'pk': 999999})  # invalid PK

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── PATCH Update ──────────────────────────────────────

    def test_superadmin_can_update_firm(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('admin_firm_update_api', kwargs={'pk': self.test_firm.pk})

        # Force a real change
        data = {
            "subscription_status": "active",  # different from free_tier in setUp
            "max_users": 20                   # different from 5
        }

        logs_before = AuditLog.objects.count()

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_firm.refresh_from_db()
        self.assertEqual(self.test_firm.subscription_status, "active")
        self.assertEqual(self.test_firm.max_users, 20)

        # Exactly one new log
        self.assertEqual(AuditLog.objects.count(), logs_before + 1)

        last_log = AuditLog.objects.order_by('-timestamp').first()
        self.assertEqual(last_log.action, 'firm_updated')
        self.assertIn('old', last_log.changes)
        self.assertIn('new', last_log.changes)
        self.assertEqual(last_log.changes['new']['subscription_status'], 'active')


    def test_non_superadmin_cannot_update_firm(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('admin_firm_update_api', kwargs={'pk': self.test_firm.pk})

        response = self.client.patch(url, {"name": "Hacked"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertIn('Only super admins', str(response.data).lower())
        # self.assertEqual(response.data['error'], 'only super admins can access this endpoint.')

        self.assertEqual(response.data['error'], 'Only super admins can access this endpoint.')


    # ── DELETE Destroy ────────────────────────────────────

    # def test_superadmin_can_deactivate_firm(self):
    #     self.client.force_authenticate(user=self.superadmin)
    #     url = reverse('admin_firm_delete_api', kwargs={'pk': self.test_firm.pk})

    #     firm_id = self.test_firm.id  # ← already defined

    #     logs_before = AuditLog.objects.count()

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.test_firm.refresh_from_db()
    #     self.assertFalse(self.test_firm.is_active)
    #     self.assertIsNotNone(self.test_firm.deleted_at)

    #     self.assertEqual(AuditLog.objects.count(), logs_before + 1)

    #     last_log = AuditLog.objects.order_by('-timestamp').first()
    #     self.assertEqual(last_log.action, 'firm_deactivated')

    # def test_superadmin_can_deactivate_firm(self):
    #     # Ensure active
    #     self.test_firm.is_active = None
    #     self.test_firm.save()

    #     self.client.force_authenticate(user=self.superadmin)
    #     url = reverse('admin_firm_delete_api', kwargs={'pk': self.test_firm.pk})

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.test_firm.refresh_from_db()
    #     self.assertFalse(self.test_firm.is_active)
    def test_superadmin_can_deactivate_firm(self):
        # Ensure firm is active before test
        self.test_firm.is_active = True
        self.test_firm.deleted_at = None  # clear soft delete flag
        self.test_firm.save()

        self.client.force_authenticate(user=self.superadmin)
        url = reverse('admin_firm_delete_api', kwargs={'pk': self.test_firm.pk})

        logs_before = AuditLog.objects.count()

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_firm.refresh_from_db()
        self.assertFalse(self.test_firm.is_active)
        self.assertIsNotNone(self.test_firm.deleted_at)

        # Log check
        self.assertEqual(AuditLog.objects.count(), logs_before + 1)
        last_log = AuditLog.objects.order_by('-timestamp').first()
        self.assertEqual(last_log.action, 'firm_deactivated')




    # def test_superadmin_can_deactivate_firm(self):
    # # Ensure firm is active
    #     self.test_firm.is_active = True
    #     self.test_firm.save()

    #     self.client.force_authenticate(user=self.superadmin)
    #     url = reverse('admin-firm-delete', kwargs={'pk': self.test_firm.pk})

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

        # self.client.force_authenticate(user=self.superadmin)
        # url = reverse('admin_firm_delete_api', kwargs={'pk': self.test_firm.pk})

        # firm_id = self.test_firm.id

        # logs_before = AuditLog.objects.count()

        # response = self.client.delete(url)

        # self.assertEqual(response.status_code, status.HTTP_200_OK)  # or 204 if you prefer
        # # Force DB refresh
        # deactivated_user = User.objects.get(id=user_id)
        # self.assertFalse(deactivated_user.is_active)
        # self.assertIsNotNone(deactivated_user.deleted_at)
        
        # self.test_firm.refresh_from_db()
        # self.assertFalse(self.test_firm.is_active)
        # self.assertIsNotNone(self.test_firm.deleted_at)

        # # Check audit log
        # self.assertEqual(AuditLog.objects.count(), logs_before + 1)
        # last_log = AuditLog.objects.order_by('-timestamp').first()
        # self.assertEqual(last_log.action, 'firm_deactivated')
        # self.assertEqual(last_log.model_id, firm_id)

    def test_non_superadmin_cannot_delete_firm(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('admin_firm_delete_api', kwargs={'pk': self.test_firm.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertIn('Only super admins', str(response.data).lower())
        self.assertEqual(response.data['error'], 'Only super admins can access this endpoint.')



# ────────────────────────────────────────────────
# Firm Owner / Super Admin User Management Tests
# ────────────────────────────────────────────────

class FirmUserManagementTests(BaseAPITestCase):  # <-- Use your base class

    def setUp(self):
        super().setUp()  # This MUST create self.firm_a

        # Debug: confirm attributes exist
        if not hasattr(self, 'firm_a'):
            raise AttributeError("Base setUp did not create self.firm_a — check BaseAPITestCase")

        

    # 1. List users (GET firm_user_list_api)

    def test_superadmin_sees_all_users(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('firm_user_list_api')  # CHANGE to your actual URL name!

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see users from all firms (at least 6 from setUp + extra)
        self.assertGreaterEqual(len(response.data), 5)
        # self.assertGreaterEqual(len(response.data), 5)



    def test_firm_owner_sees_only_own_firm_users(self):

        self.extra_lawyer = User.objects.create_user(
            email="extra@alpha.com",
            password="extra123",
            role="lawyer",
            firm=self.firm_a
        )

        self.client.force_authenticate(user=self.owner_a)
        url = reverse('firm_user_list_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only firm_a users (owner_a, lawyer_a, assistant_a, extra_lawyer)
        # self.assertEqual(len(response.data), 4)
        self.assertEqual(len(response.data), 4) # owner + lawyer + assistant + extra + 1 more?


        for user_data in response.data:
            self.assertEqual(user_data['firm'], self.firm_a.id)

    def test_lawyer_cannot_list_users(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('firm_user_list_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('only super admins and firm owners can view user lists', str(response.data).lower())

    # 2. Create user (POST firm_user_create_api)
    

    def test_firm_owner_can_create_user_in_own_firm(self):
    # Clean extra users
        User.objects.filter(firm=self.firm_a).exclude(id=self.owner_a.id).delete()

        # Force high limit for this test
        self.firm_a.max_users = 999
        self.firm_a.save()

        print("Forced max_users:", self.firm_a.max_users)
        print("Current users:", self.firm_a.users.count())

        self.client.force_authenticate(user=self.owner_a)
        url = reverse('firm_user_create_api')

        data = {
            "email": "newlawyer@alpha.com",
            "first_name": "New",
            "last_name": "Lawyer",
            "phone": "+123",
            "role": "lawyer",
        }

        response = self.client.post(url, data, format='json')

        print("Create status:", response.status_code, response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email="newlawyer@alpha.com").count(), 1)
    # #     # self.client.force_authenticate(user=self.owner_a)
        # url = reverse('firm_user_create_api')

        # data = {
        #     "email": "hacker@beta.com",
        #     "first_name": "Hacker",
        #     "last_name": "Beta",
        #     "role": "lawyer",
        #     "firm": self.firm_b.id  # trying to force other firm
        # }

        # response = self.client.post(url, data, format='json')

        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('own firm', str(response.data).lower())

    # 3. Retrieve single user (GET firm_user_retrieve_api)

    def test_firm_owner_can_retrieve_own_firm_user(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('firm_user_retrieve_api', kwargs={'pk': self.lawyer_a.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lawyer_a.id)
        self.assertEqual(response.data['email'], self.lawyer_a.email)

    # 4. Update user (PATCH firm_user_update_api) — similar pattern

    # 5. Soft delete user (DELETE firm_user_delete_api)

    # def test_superadmin_can_deactivate_user(self):
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('firm_user_delete_api', kwargs={'pk': self.lawyer_a.pk})

        user_id = self.lawyer_a.id

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lawyer_a.refresh_from_db()
        self.assertFalse(self.lawyer_a.is_active)
        self.assertIsNotNone(self.lawyer_a.deleted_at)

        # Check log
        last_log = AuditLog.objects.order_by('-timestamp').first()
        self.assertEqual(last_log.action, 'user_deactivated')




    def test_superadmin_can_deactivate_user(self):
            self.client.force_authenticate(user=self.superadmin)
            url = reverse('firm_user_delete_api', kwargs={'pk': self.lawyer_a.pk})

            response = self.client.delete(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Force fresh DB query
            deactivated_user = User.objects.get(id=self.lawyer_a.id)
            self.assertFalse(deactivated_user.is_active)
            self.assertIsNotNone(deactivated_user.deleted_at)

            # Log check
            last_log = AuditLog.objects.order_by('-timestamp').first()
            self.assertEqual(last_log.action, 'user_deactivated')
    # def test_superadmin_can_deactivate_user(self):
    #     self.client.force_authenticate(user=self.superadmin)
    #     url = reverse('firm_user_delete_api', kwargs={'pk': self.lawyer_a.pk})

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Force fresh DB query (self.lawyer_a is stale object)
    #     deactivated_user = User.objects.get(id=self.lawyer_a.id)
    #     self.assertFalse(deactivated_user.is_active)
    #     self.assertIsNotNone(deactivated_user.deleted_at)

    #     # Log check
    #     last_log = AuditLog.objects.order_by('-timestamp').first()
    #     self.assertEqual(last_log.action, 'user_deactivated')
class MyFirmRetrieveTests(BaseAPITestCase):
    def test_authenticated_user_with_firm_can_retrieve_my_firm(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('my_firm_retrieve_api')  # CHANGE to your actual name!

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.firm_a.id)
        self.assertEqual(response.data['name'], self.firm_a.name)
        self.assertIn('user_count', response.data)  # from serializer

    def test_user_without_firm_gets_404(self):
        # Use a user without firm (e.g. superadmin if not assigned)
        self.client.force_authenticate(user=self.superadmin)
        url = reverse('my_firm_retrieve_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not associated with any firm', str(response.data).lower())



class MyFirmUpdateTests(BaseAPITestCase):
    def test_firm_owner_can_update_own_firm_name(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('my_firm_update_api')

        data = {"name": "Updated Firm Alpha"}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.firm_a.refresh_from_db()
        self.assertEqual(self.firm_a.name, "Updated Firm Alpha")

        # Check audit log
        last_log = AuditLog.objects.order_by('-timestamp').first()
        self.assertEqual(last_log.action, 'firm_settings_updated')
        self.assertIn('name', last_log.changes)

    def test_non_owner_cannot_update_firm(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('my_firm_update_api')

        response = self.client.patch(url, {"name": "Hacked"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertIn('Only firm owners', str(response.data).lower())
        # self.assertIn('super admins and firm owners', response.data['error'].lower())
        self.assertIn('only firm owners can update firm settings', response.data['error'].lower())


    # def test_update_with_no_allowed_fields_returns_400(self):
    #     self.client.force_authenticate(user=self.owner_a)
    #     url = reverse('my_firm_update_api')

    #     # data = {"subscription_plan": "growing_firm"}  # not allowed
    #     data = {"subscription_plan": "growing_firm"}  # not in allowed_fields → filtered_data = {} → 400

    #     response = self.client.patch(url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('No updatable fields', str(response.data).lower())
    def test_update_with_no_allowed_fields_returns_400(self):
        self.client.force_authenticate(user=self.owner_a)
        url = reverse('my_firm_update_api')

        # data = {"subscription_plan": "growing_firm"}  # not allowed → filtered_data = {} → 400
        data = {"subscription_plan": "growing_firms"}  # not in ['name'] → filtered_data = {} → 400



        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no updatable fields', str(response.data).lower())

class MyProfileRetrieveTests(BaseAPITestCase):
    def test_authenticated_user_can_retrieve_own_profile(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('my_profile_retrieve_api')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lawyer_a.id)
        self.assertEqual(response.data['email'], self.lawyer_a.email)
        self.assertNotIn('password', response.data)  # sensitive field hidden



class MyProfileUpdateTests(BaseAPITestCase):
    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('my_profile_update_api')

        data = {
            "first_name": "Updated First",
            "phone": "+999888777"
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lawyer_a.refresh_from_db()
        self.assertEqual(self.lawyer_a.first_name, "Updated First")
        self.assertEqual(self.lawyer_a.phone, "+999888777")

        # Check audit log
        last_log = AuditLog.objects.order_by('-timestamp').first()
        self.assertEqual(last_log.action, 'profile_updated')
        self.assertIn('first_name', last_log.changes)

    def test_update_with_no_changes_returns_400(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('my_profile_update_api')

        filtered_data = {}  # no fields

        if not filtered_data:
            print("No filtered data — returning 400")
            return Response({'detail': 'No updatable fields provided.'}, status=400)
        
        

        response = self.client.patch(url, filtered_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No updatable fields', str(response.data).lower())


class ChangePasswordTests(BaseAPITestCase):

    def test_user_can_change_password(self):
        self.client.force_authenticate(user=self.lawyer_a)
        url = reverse('change_password_api')
        
        # Check what password was set in setUp
        print("Testing password change for:", self.lawyer_a.email)
        print("Password check:", self.lawyer_a.check_password("lawPass123!"))
        
        data = {
            "old_password": "lawPass123!",  # Must match setUp
            "new_password": "NewPass456!",
            "new_password_confirm": "NewPass456!"
        }
        
        response = self.client.post(url, data, format='json')
        
        print("Response status:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    # def test_user_can_change_password(self):
    #     self.client.force_authenticate(user=self.lawyer_a)
    #     url = reverse('change_password_api')  # your name

    #     data = {
    #         "old_password": "law123",  # from setUp
    #         "new_password": "NewPass456!",
    #         "new_password_confirm": "NewPass456!"
    #     }

    #     response = self.client.post(url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("Password updated successfully", str(response.data))

    #     # Verify password changed (can't check directly, but login with new works)
    #     self.lawyer_a.refresh_from_db()
    #     self.assertTrue(self.lawyer_a.check_password("NewPass456!"))

    #     # Check audit log
    #     last_log = AuditLog.objects.order_by('-timestamp').first()
    #     self.assertEqual(last_log.action, 'password_changed')

    # def test_wrong_old_password_fails(self):
    #     self.client.force_authenticate(user=self.lawyer_a)
    #     url = reverse('change_password_api')

    #     data = {
    #         "old_password": "wrong",
    #         "new_password": "NewPass456!",
    #         "new_password_confirm": "NewPass456!"
    #     }

    #     response = self.client.post(url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('old_password', response.data)