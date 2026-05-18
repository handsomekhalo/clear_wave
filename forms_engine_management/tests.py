# from django.test import TestCase

# from system_management.models import Firm

# # Create your tests here.
# """
# ClearWave — forms_engine/tests/test_forms_engine_api.py

# Tests for every API endpoint in forms_engine.
# Pattern mirrors test_case_management.py exactly.

# Run with:
#     python manage.py test forms_engine.tests.test_forms_engine_api -v 2

# Structure:
#     1. SetupMixin         — shared firm, users, base data
#     2. FormTemplateTests  — CRUD on templates
#     3. FormSectionTests   — CRUD on sections
#     4. QuestionBankTests  — CRUD on firm question bank
#     5. QuestionOptionTests — CRUD on options
#     6. SectionQuestionTests — assign/remove questions from sections
#     7. CaseFormAssignmentTests — assign templates to cases, review
#     8. FormSubmissionTests — client starts, saves answers, submits
#     9. PermissionTests    — wrong firm, wrong role, wrong user
# """



# # ---------------------------------------------------------------------------
# # SHARED SETUP
# # ---------------------------------------------------------------------------

# class SetupMixin(TestCase):
#     """
#     Base class. Every test class inherits this.
#     Creates two completely isolated firms so we can test cross-firm leakage.
#     """

#     def setUp(self):
#         self.client_http = Client()

#         # ── FIRM A ──────────────────────────────────────────────────────────
#         self.firm_a = Firm.objects.create(
#             name="Alpha Legal",
#             subscription_tier="small",
#         )

#         self.owner_a = User.objects.create_user(
#             email="owner@alpha.com",
#             password="TestPass123!",
#             first_name="Alice",
#             last_name="Owner",
#             role="firm_owner",
#             firm=self.firm_a,
#             is_active=True,
#         )

#         self.lawyer_a = User.objects.create_user(
#             email="lawyer@alpha.com",
#             password="TestPass123!",
#             first_name="Bob",
#             last_name="Lawyer",
#             role="lawyer",
#             firm=self.firm_a,
#             is_active=True,
#         )

#         self.assistant_a = User.objects.create_user(
#             email="assistant@alpha.com",
#             password="TestPass123!",
#             first_name="Carol",
#             last_name="Assistant",
#             role="assistant",
#             firm=self.firm_a,
#             is_active=True,
#         )

#         self.client_a = User.objects.create_user(
#             email="client@alpha.com",
#             password="TestPass123!",
#             first_name="Dave",
#             last_name="Client",
#             role="client",
#             firm=self.firm_a,
#             is_active=True,
#         )

#         # ── FIRM B (separate firm — nothing should bleed across) ─────────────
#         self.firm_b = Firm.objects.create(
#             name="Beta Law",
#             subscription_tier="solo",
#         )

#         self.owner_b = User.objects.create_user(
#             email="owner@beta.com",
#             password="TestPass123!",
#             first_name="Eve",
#             last_name="Owner",
#             role="firm_owner",
#             firm=self.firm_b,
#             is_active=True,
#         )

#         self.client_b = User.objects.create_user(
#             email="client@beta.com",
#             password="TestPass123!",
#             first_name="Frank",
#             last_name="Client",
#             role="client",
#             firm=self.firm_b,
#             is_active=True,
#         )

#         # ── CASE TYPE & CASE (Firm A) ────────────────────────────────────────
#         self.case_type_a = CaseType.objects.create(
#             name="Conveyancing",
#             firm=self.firm_a,
#         )

#         self.case_a = Case.objects.create(
#             title="Smith Property Transfer",
#             firm=self.firm_a,
#             client=self.client_a,
#             matter_type=self.case_type_a,
#             created_by=self.owner_a,
#             status=Case.NEW,
#             reference_number="2026-ALPHA-0001",
#         )

#         # ── QUESTION BANK SEED DATA (Firm A) ────────────────────────────────
#         self.question_text_a = Question.objects.create(
#             firm=self.firm_a,
#             text="What is your full legal name?",
#             input_type="text",
#             is_required=True,
#             created_by=self.owner_a,
#         )

#         self.question_select_a = Question.objects.create(
#             firm=self.firm_a,
#             text="What is your marital status?",
#             input_type="select",
#             is_required=True,
#             allow_other_option=True,
#             created_by=self.owner_a,
#         )

#         self.option_single = QuestionOption.objects.create(
#             question=self.question_select_a,
#             text="Single",
#             order=1,
#         )
#         self.option_married = QuestionOption.objects.create(
#             question=self.question_select_a,
#             text="Married",
#             order=2,
#         )

#         self.question_date_a = Question.objects.create(
#             firm=self.firm_a,
#             text="What is your date of birth?",
#             input_type="date",
#             is_required=True,
#             created_by=self.owner_a,
#         )

#         self.question_file_a = Question.objects.create(
#             firm=self.firm_a,
#             text="Please upload your ID document.",
#             input_type="file",
#             is_required=True,
#             created_by=self.owner_a,
#         )

#         # ── TEMPLATE & SECTIONS (Firm A) ─────────────────────────────────────
#         self.template_a = FormTemplate.objects.create(
#             firm=self.firm_a,
#             name="Conveyancing Intake",
#             description="Standard intake form for property transfers.",
#             case_type=self.case_type_a,
#             created_by=self.owner_a,
#             is_active=True,
#         )

#         self.section_personal = FormSection.objects.create(
#             template=self.template_a,
#             name="Personal Details",
#             order=1,
#             is_active=True,
#         )

#         self.section_property = FormSection.objects.create(
#             template=self.template_a,
#             name="Property Information",
#             order=2,
#             is_active=True,
#         )

#         # ── FIRM B TEMPLATE (for cross-firm tests) ───────────────────────────
#         self.template_b = FormTemplate.objects.create(
#             firm=self.firm_b,
#             name="Beta Intake",
#             created_by=self.owner_b,
#             is_active=True,
#         )

#     # ── AUTH HELPERS ─────────────────────────────────────────────────────────

#     def login(self, user):
#         self.client_http.force_authenticate(user=user)

#     def logout(self):
#         self.client_http.force_authenticate(user=None)


# # ---------------------------------------------------------------------------
# # 1. FORM TEMPLATE TESTS
# # ---------------------------------------------------------------------------

# class FormTemplateTests(SetupMixin):

#     def test_owner_can_create_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Divorce Intake",
#             "description": "For divorce matters.",
#             "is_active": True,
#         })
#         self.assertEqual(response.status_code, 201)
#         self.assertIn("id", response.data)
#         self.assertTrue(
#             FormTemplate.objects.filter(firm=self.firm_a, name="Divorce Intake").exists()
#         )

#     def test_lawyer_can_create_template(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Wills Intake",
#             "is_active": True,
#         })
#         self.assertEqual(response.status_code, 201)

#     def test_assistant_cannot_create_template(self):
#         self.login(self.assistant_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Should Fail",
#         })
#         self.assertEqual(response.status_code, 403)

#     def test_client_cannot_create_template(self):
#         self.login(self.client_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Should Fail",
#         })
#         self.assertEqual(response.status_code, 403)

#     def test_duplicate_template_name_rejected(self):
#         self.login(self.owner_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Conveyancing Intake",  # already exists in setUp
#         })
#         self.assertEqual(response.status_code, 400)

#     def test_same_name_allowed_for_different_firm(self):
#         """Firm B can have a template with the same name as Firm A."""
#         self.login(self.owner_b)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Conveyancing Intake",
#         })
#         self.assertEqual(response.status_code, 201)

#     def test_list_templates_only_returns_own_firm(self):
#         self.login(self.owner_a)
#         response = self.client_http.get("/api/forms/templates/")
#         self.assertEqual(response.status_code, 200)
#         names = [t["name"] for t in response.data]
#         self.assertIn("Conveyancing Intake", names)
#         self.assertNotIn("Beta Intake", names)

#     def test_get_template_detail(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.get(f"/api/forms/templates/{self.template_a.id}/")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["name"], "Conveyancing Intake")
#         self.assertEqual(response.data["section_count"], 2)

#     def test_cannot_get_other_firms_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.get(f"/api/forms/templates/{self.template_b.id}/")
#         self.assertEqual(response.status_code, 404)

#     def test_update_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/templates/{self.template_a.id}/update/",
#             {"description": "Updated description."}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.template_a.refresh_from_db()
#         self.assertEqual(self.template_a.description, "Updated description.")

#     def test_cannot_update_other_firms_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/templates/{self.template_b.id}/update/",
#             {"description": "Hacked."}
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_unauthenticated_blocked(self):
#         self.logout()
#         response = self.client_http.get("/api/forms/templates/")
#         self.assertEqual(response.status_code, 401)


# # ---------------------------------------------------------------------------
# # 2. FORM SECTION TESTS
# # ---------------------------------------------------------------------------

# class FormSectionTests(SetupMixin):

#     def test_create_section(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_a.id}/sections/create/",
#             {"name": "Financial Details", "order": 3}
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(
#             FormSection.objects.filter(
#                 template=self.template_a, name="Financial Details"
#             ).exists()
#         )

#     def test_duplicate_section_name_in_same_template_rejected(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_a.id}/sections/create/",
#             {"name": "Personal Details"}  # already exists
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_list_sections(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/templates/{self.template_a.id}/sections/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#     def test_update_section_order(self):
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/update/",
#             {"order": 99}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.section_personal.refresh_from_db()
#         self.assertEqual(self.section_personal.order, 99)

#     def test_cannot_create_section_on_other_firms_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_b.id}/sections/create/",
#             {"name": "Sneaky Section", "order": 1}
#         )
#         self.assertEqual(response.status_code, 404)


# # ---------------------------------------------------------------------------
# # 3. QUESTION BANK TESTS
# # ---------------------------------------------------------------------------

# class QuestionBankTests(SetupMixin):

#     def test_create_text_question(self):
#         self.login(self.owner_a)
#         response = self.client_http.post("/api/forms/questions/create/", {
#             "text": "What is your residential address?",
#             "input_type": "textarea",
#             "is_required": True,
#         })
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(
#             Question.objects.filter(
#                 firm=self.firm_a,
#                 text="What is your residential address?"
#             ).exists()
#         )

#     def test_create_question_is_firm_scoped(self):
#         """Question created by Firm A must not appear in Firm B's list."""
#         self.login(self.owner_a)
#         self.client_http.post("/api/forms/questions/create/", {
#             "text": "Alpha only question",
#             "input_type": "text",
#         })

#         self.login(self.owner_b)
#         response = self.client_http.get("/api/forms/questions/")
#         texts = [q["text"] for q in response.data]
#         self.assertNotIn("Alpha only question", texts)

#     def test_list_questions_returns_own_firm_only(self):
#         self.login(self.owner_a)
#         response = self.client_http.get("/api/forms/questions/")
#         self.assertEqual(response.status_code, 200)
#         for q in response.data:
#             # We can't check firm directly in response but count must match
#             pass
#         # Firm A has 4 questions from setUp
#         self.assertEqual(len(response.data), 4)

#     def test_get_question_detail_includes_options(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/questions/{self.question_select_a.id}/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data["options"]), 2)

#     def test_cannot_get_other_firms_question(self):
#         """Firm B owner tries to GET a Firm A question by ID."""
#         self.login(self.owner_b)
#         response = self.client_http.get(
#             f"/api/forms/questions/{self.question_text_a.id}/"
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_update_question(self):
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/questions/{self.question_text_a.id}/update/",
#             {"helper_text": "As it appears on your ID document."}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.question_text_a.refresh_from_db()
#         self.assertEqual(
#             self.question_text_a.helper_text,
#             "As it appears on your ID document."
#         )

#     def test_invalid_input_type_rejected(self):
#         self.login(self.owner_a)
#         response = self.client_http.post("/api/forms/questions/create/", {
#             "text": "Some question",
#             "input_type": "voice_note",  # not a valid choice
#         })
#         self.assertEqual(response.status_code, 400)

#     def test_client_cannot_create_question(self):
#         self.login(self.client_a)
#         response = self.client_http.post("/api/forms/questions/create/", {
#             "text": "Should not work",
#             "input_type": "text",
#         })
#         self.assertEqual(response.status_code, 403)


# # ---------------------------------------------------------------------------
# # 4. QUESTION OPTION TESTS
# # ---------------------------------------------------------------------------

# class QuestionOptionTests(SetupMixin):

#     def test_add_option_to_select_question(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/questions/{self.question_select_a.id}/options/add/",
#             {"text": "Divorced", "order": 3}
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(
#             QuestionOption.objects.filter(
#                 question=self.question_select_a, text="Divorced"
#             ).exists()
#         )

#     def test_cannot_add_option_to_text_question(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/questions/{self.question_text_a.id}/options/add/",
#             {"text": "Invalid option"}
#         )
#         self.assertEqual(response.status_code, 400)
#         self.assertIn("error", response.data)

#     def test_list_options(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/questions/{self.question_select_a.id}/options/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#     def test_update_option(self):
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/questions/{self.question_select_a.id}/options/{self.option_single.id}/update/",
#             {"text": "Never Married"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.option_single.refresh_from_db()
#         self.assertEqual(self.option_single.text, "Never Married")

#     def test_delete_option(self):
#         self.login(self.owner_a)
#         option_id = self.option_married.id
#         response = self.client_http.delete(
#             f"/api/forms/questions/{self.question_select_a.id}/options/{option_id}/delete/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(QuestionOption.objects.filter(pk=option_id).exists())

#     def test_cannot_access_other_firms_question_options(self):
#         self.login(self.owner_b)
#         response = self.client_http.get(
#             f"/api/forms/questions/{self.question_select_a.id}/options/"
#         )
#         self.assertEqual(response.status_code, 404)


# # ---------------------------------------------------------------------------
# # 5. SECTION QUESTION ASSIGNMENT TESTS
# # ---------------------------------------------------------------------------

# class SectionQuestionTests(SetupMixin):

#     def test_assign_question_to_section(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/assign/",
#             {
#                 "question": self.question_text_a.id,
#                 "order": 1,
#             }
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(
#             SectionQuestion.objects.filter(
#                 section=self.section_personal,
#                 question=self.question_text_a
#             ).exists()
#         )

#     def test_duplicate_assignment_rejected(self):
#         # First assignment
#         SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,
#             order=1,
#         )
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/assign/",
#             {"question": self.question_text_a.id, "order": 2}
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_cannot_assign_other_firms_question(self):
#         """Firm A tries to assign a Firm B question to Firm A's section."""
#         question_b = Question.objects.create(
#             firm=self.firm_b,
#             text="Firm B question",
#             input_type="text",
#             created_by=self.owner_b,
#         )
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/assign/",
#             {"question": question_b.id, "order": 1}
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_list_section_questions(self):
#         SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,
#             order=1,
#         )
#         SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_select_a,
#             order=2,
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)
#         # Options should be nested on select question
#         select_q = next(
#             (q for q in response.data if q["question"]["input_type"] == "select"),
#             None
#         )
#         self.assertIsNotNone(select_q)
#         self.assertEqual(len(select_q["question"]["options"]), 2)

#     def test_is_required_override(self):
#         """is_required_override=False should override question's default True."""
#         sq = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,  # is_required=True
#             order=1,
#             is_required_override=False,
#         )
#         self.assertFalse(sq.is_required)

#     def test_is_required_falls_back_to_question_default(self):
#         sq = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,  # is_required=True
#             order=1,
#             is_required_override=None,
#         )
#         self.assertTrue(sq.is_required)

#     def test_update_section_question_order(self):
#         sq = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,
#             order=1,
#         )
#         self.login(self.owner_a)
#         response = self.client_http.patch(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/{sq.id}/update/",
#             {"order": 5}
#         )
#         self.assertEqual(response.status_code, 200)
#         sq.refresh_from_db()
#         self.assertEqual(sq.order, 5)

#     def test_remove_question_from_section(self):
#         sq = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,
#             order=1,
#         )
#         sq_id = sq.id
#         self.login(self.owner_a)
#         response = self.client_http.delete(
#             f"/api/forms/templates/{self.template_a.id}/sections/{self.section_personal.id}/questions/{sq_id}/remove/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(SectionQuestion.objects.filter(pk=sq_id).exists())


# # ---------------------------------------------------------------------------
# # 6. CASE FORM ASSIGNMENT TESTS
# # ---------------------------------------------------------------------------

# class CaseFormAssignmentTests(SetupMixin):

#     def test_lawyer_assigns_template_to_case(self):
#         self.login(self.lawyer_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assign/",
#             {"template": self.template_a.id}
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(
#             CaseFormAssignment.objects.filter(
#                 case=self.case_a,
#                 template=self.template_a
#             ).exists()
#         )

#     def test_duplicate_assignment_rejected(self):
#         CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#         )
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assign/",
#             {"template": self.template_a.id}
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_cannot_assign_other_firms_template(self):
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assign/",
#             {"template": self.template_b.id}
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_cannot_assign_to_other_firms_case(self):
#         case_b = Case.objects.create(
#             title="Beta Case",
#             firm=self.firm_b,
#             client=self.client_b,
#             matter_type=CaseType.objects.create(name="General", firm=self.firm_b),
#             created_by=self.owner_b,
#             status=Case.NEW,
#             reference_number="2026-BETA-0001",
#         )
#         self.login(self.owner_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{case_b.id}/assign/",
#             {"template": self.template_a.id}
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_list_case_form_assignments(self):
#         CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/cases/{self.case_a.id}/assignments/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["status"], "pending")

#     def test_is_overdue_when_due_date_passed(self):
#         assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             due_date=timezone.now().date() - timezone.timedelta(days=1),
#             status="pending",
#         )
#         self.assertTrue(assignment.is_overdue)

#     def test_is_overdue_false_when_due_date_future(self):
#         assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             due_date=timezone.now().date() + timezone.timedelta(days=7),
#             status="pending",
#         )
#         self.assertFalse(assignment.is_overdue)

#     def test_lawyer_can_review_submitted_form(self):
#         assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             status="submitted",
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assignments/{assignment.id}/review/",
#             {"status": "approved", "review_notes": "All good."}
#         )
#         self.assertEqual(response.status_code, 200)
#         assignment.refresh_from_db()
#         self.assertEqual(assignment.status, "approved")
#         self.assertEqual(assignment.reviewed_by, self.lawyer_a)

#     def test_cannot_review_non_submitted_form(self):
#         assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             status="pending",  # not submitted yet
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assignments/{assignment.id}/review/",
#             {"status": "approved"}
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_invalid_review_status_rejected(self):
#         assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             status="submitted",
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assignments/{assignment.id}/review/",
#             {"status": "pending"}  # not an allowed review status
#         )
#         self.assertEqual(response.status_code, 400)


# # ---------------------------------------------------------------------------
# # 7. FORM SUBMISSION TESTS (CLIENT PORTAL)
# # ---------------------------------------------------------------------------

# class FormSubmissionTests(SetupMixin):

#     def setUp(self):
#         super().setUp()
#         # Assignment that client_a needs to fill in
#         self.assignment = CaseFormAssignment.objects.create(
#             case=self.case_a,
#             template=self.template_a,
#             assigned_by=self.owner_a,
#             status="pending",
#         )
#         # Questions assigned to sections
#         self.sq_text = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_text_a,
#             order=1,
#         )
#         self.sq_select = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_select_a,
#             order=2,
#         )
#         self.sq_date = SectionQuestion.objects.create(
#             section=self.section_personal,
#             question=self.question_date_a,
#             order=3,
#         )

#     def test_client_starts_form(self):
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/assignments/{self.assignment.id}/start/"
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertIn("submission_id", response.data)
#         # Assignment should move to in_progress
#         self.assignment.refresh_from_db()
#         self.assertEqual(self.assignment.status, "in_progress")

#     def test_starting_form_twice_returns_existing_draft(self):
#         self.login(self.client_a)
#         r1 = self.client_http.post(
#             f"/api/forms/assignments/{self.assignment.id}/start/"
#         )
#         r2 = self.client_http.post(
#             f"/api/forms/assignments/{self.assignment.id}/start/"
#         )
#         self.assertEqual(r1.status_code, 201)
#         self.assertEqual(r2.status_code, 200)
#         # Both should reference the same submission
#         self.assertEqual(
#             FormSubmission.objects.filter(assignment=self.assignment).count(),
#             1
#         )

#     def test_wrong_client_cannot_start_form(self):
#         """client_b should not be able to start a form assigned to client_a's case."""
#         self.login(self.client_b)
#         response = self.client_http.post(
#             f"/api/forms/assignments/{self.assignment.id}/start/"
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_client_saves_text_response(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=False,
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_text_a.id,
#                 "section": self.section_personal.id,
#                 "response_text": "David James Client",
#             }
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(
#             FormResponse.objects.filter(
#                 submission=submission,
#                 question=self.question_text_a,
#                 response_text="David James Client",
#             ).exists()
#         )

#     def test_client_saves_select_response(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=False,
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_select_a.id,
#                 "section": self.section_personal.id,
#                 "selected_option": self.option_single.id,
#             }
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_client_saves_date_response(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=False,
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_date_a.id,
#                 "section": self.section_personal.id,
#                 "response_date": "1990-06-15",
#             }
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_saving_same_question_twice_updates_not_duplicates(self):
#         """Idempotency — same question saved twice = 1 row, updated value."""
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=False,
#         )
#         self.login(self.client_a)
#         self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_text_a.id,
#                 "section": self.section_personal.id,
#                 "response_text": "First answer",
#             }
#         )
#         self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_text_a.id,
#                 "section": self.section_personal.id,
#                 "response_text": "Corrected answer",
#             }
#         )
#         responses = FormResponse.objects.filter(
#             submission=submission,
#             question=self.question_text_a
#         )
#         self.assertEqual(responses.count(), 1)
#         self.assertEqual(responses.first().response_text, "Corrected answer")

#     def test_cannot_save_response_after_submit(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=True,
#             submitted_at=timezone.now(),
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/respond/",
#             {
#                 "question": self.question_text_a.id,
#                 "response_text": "Too late",
#             }
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_client_submits_form(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=False,
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/submit/"
#         )
#         self.assertEqual(response.status_code, 200)
#         submission.refresh_from_db()
#         self.assertTrue(submission.is_complete)
#         self.assertIsNotNone(submission.submitted_at)
#         self.assignment.refresh_from_db()
#         self.assertEqual(self.assignment.status, "submitted")

#     def test_cannot_submit_twice(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=True,
#             submitted_at=timezone.now(),
#         )
#         self.login(self.client_a)
#         response = self.client_http.post(
#             f"/api/forms/submissions/{submission.id}/submit/"
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_lawyer_can_view_submission_and_responses(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=True,
#             submitted_at=timezone.now(),
#         )
#         FormResponse.objects.create(
#             submission=submission,
#             question=self.question_text_a,
#             section=self.section_personal,
#             response_text="David James Client",
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/assignments/{self.assignment.id}/submission/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["response_count"], 1)

#     def test_list_responses_as_lawyer(self):
#         submission = FormSubmission.objects.create(
#             assignment=self.assignment,
#             submitted_by=self.client_a,
#             is_complete=True,
#             submitted_at=timezone.now(),
#         )
#         FormResponse.objects.create(
#             submission=submission,
#             question=self.question_text_a,
#             section=self.section_personal,
#             response_text="David James Client",
#         )
#         FormResponse.objects.create(
#             submission=submission,
#             question=self.question_date_a,
#             section=self.section_personal,
#             response_date="1990-06-15",
#         )
#         self.login(self.lawyer_a)
#         response = self.client_http.get(
#             f"/api/forms/submissions/{submission.id}/responses/"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)


# # ---------------------------------------------------------------------------
# # 8. PERMISSION EDGE CASE TESTS
# # ---------------------------------------------------------------------------

# class PermissionTests(SetupMixin):

#     def test_unauthenticated_cannot_access_any_endpoint(self):
#         self.logout()
#         endpoints = [
#             "/api/forms/templates/",
#             "/api/forms/questions/",
#             f"/api/forms/cases/{self.case_a.id}/assignments/",
#         ]
#         for url in endpoints:
#             response = self.client_http.get(url)
#             self.assertEqual(
#                 response.status_code, 401,
#                 f"Expected 401 on {url}, got {response.status_code}"
#             )

#     def test_client_cannot_list_templates(self):
#         self.login(self.client_a)
#         response = self.client_http.get("/api/forms/templates/")
#         self.assertEqual(response.status_code, 403)

#     def test_client_cannot_list_questions(self):
#         self.login(self.client_a)
#         response = self.client_http.get("/api/forms/questions/")
#         self.assertEqual(response.status_code, 403)

#     def test_assistant_can_list_templates(self):
#         """Assistants have read access."""
#         self.login(self.assistant_a)
#         response = self.client_http.get("/api/forms/templates/")
#         self.assertEqual(response.status_code, 200)

#     def test_assistant_cannot_create_template(self):
#         self.login(self.assistant_a)
#         response = self.client_http.post("/api/forms/templates/create/", {
#             "name": "Should Fail",
#         })
#         self.assertEqual(response.status_code, 403)

#     def test_firm_b_owner_cannot_read_firm_a_template(self):
#         self.login(self.owner_b)
#         response = self.client_http.get(
#             f"/api/forms/templates/{self.template_a.id}/"
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_firm_b_cannot_assign_form_to_firm_a_case(self):
#         self.login(self.owner_b)
#         response = self.client_http.post(
#             f"/api/forms/cases/{self.case_a.id}/assign/",
#             {"template": self.template_b.id}
#         )
#         self.assertEqual(response.status_code, 404)