# # system_management/tests/test_models.py

# class FirmModelTest(TestCase):
#     def test_can_create_case_active_subscription(self):
#         firm = Firm.objects.create(
#             name="Test Firm",
#             subscription_status='active'
#         )
#         self.assertTrue(firm.can_create_case())
    
#     def test_can_create_case_free_tier_under_limit(self):
#         firm = Firm.objects.create(
#             name="Test Firm",
#             subscription_status='free_tier',
#             max_active_cases=5
#         )
#         # Create 3 cases
#         for i in range(3):
#             Case.objects.create(firm=firm, title=f"Case {i}", ...)
        
#         self.assertTrue(firm.can_create_case())  # 3 < 5
    
#     def test_can_create_case_free_tier_at_limit(self):
#         firm = Firm.objects.create(
#             name="Test Firm",
#             subscription_status='free_tier',
#             max_active_cases=5
#         )
#         # Create 5 cases (at limit)
#         for i in range(5):
#             Case.objects.create(firm=firm, title=f"Case {i}", ...)
        
#         self.assertFalse(firm.can_create_case())  # 5 == 5