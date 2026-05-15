
"""
ClearWave — forms_engine/models.py

New app: forms_engine

Add to INSTALLED_APPS in settings.py:
    'forms_engine',

Run after creating the app:
    python manage.py makemigrations forms_engine
    python manage.py migrate

Architecture:
    Template Layer  — Firm builds reusable templates per matter type
    Assignment Layer — Template gets assigned to a specific Case
    Submission Layer — Client fills it in via the client portal

All questions are firm-scoped. Two firms using the same template
structure ask their own questions in their own way.
"""

from django.db import models
from django.utils import timezone

from system_management.models import Firm, User
from case_management.models import Case, CaseType


# ---------------------------------------------------------------------------
# TEMPLATE LAYER
# ---------------------------------------------------------------------------

class FormTemplate(models.Model):
    """
    A reusable form template created by a firm.
    Typically mapped to a matter/case type (e.g. Conveyancing, Divorce, Will).
    One firm can have many templates. Templates are never shared across firms.
    """
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name='form_templates'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Optional: link to a CaseType so it can be auto-suggested when creating a case
    case_type = models.ForeignKey(
        CaseType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_templates',
        help_text="If set, this template is suggested when a case of this type is created."
    )

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_form_templates'
    )
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('firm', 'name')  # Firm can't have two templates with same name

    def __str__(self):
        return f"{self.firm.name} — {self.name}"


class FormSection(models.Model):
    """
    A named section/category within a FormTemplate.
    Equivalent to MainCategory in dynamic_forms.
    e.g. "Personal Details", "Property Information", "Financial Disclosure"
    """
    template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order']
        unique_together = ('template', 'name')

    def __str__(self):
        return f"{self.template.name} › {self.name}"


# ---------------------------------------------------------------------------
# QUESTION BANK (FIRM-SCOPED)
# ---------------------------------------------------------------------------

class Question(models.Model):
    """
    A question created by a firm. Fully firm-scoped — no question bleeds
    across firms. A question lives in the firm's question bank and can be
    reused across multiple templates.
    """
    INPUT_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Long Text Area'),
        ('number', 'Number Input'),
        ('date', 'Date Picker'),
        ('email', 'Email Input'),
        ('select', 'Dropdown Selection'),
        ('checkbox', 'Checkbox'),
        ('file', 'File Upload'),
        ('yes_no', 'Yes / No'),
    ]

    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField(help_text="The question text shown to the client.")
    input_type = models.CharField(max_length=50, choices=INPUT_TYPES)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    allow_other_option = models.BooleanField(
        default=False,
        help_text="Adds an 'Other (please specify)' option for select/checkbox types."
    )
    helper_text = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional hint shown below the question field."
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions'
    )
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return f"[{self.firm.name}] {self.text[:60]}"


class QuestionOption(models.Model):
    """
    Predefined options for select/checkbox question types.
    Equivalent to Option in dynamic_forms.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.text[:30]} › {self.text}"


class SectionQuestion(models.Model):
    """
    Assignment of a Question to a FormSection within a template.
    This is the join table — a question from the firm's bank gets
    placed into a section at a specific order.
    Equivalent to FormQuestionAssignment in dynamic_forms.
    """
    section = models.ForeignKey(
        FormSection,
        on_delete=models.CASCADE,
        related_name='section_questions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='section_assignments'
    )
    order = models.PositiveIntegerField(default=0)

    # Override is_required at the template level
    # (a question might be required in one template, optional in another)
    is_required_override = models.BooleanField(
        null=True,
        blank=True,
        help_text="If set, overrides the question's default is_required. Leave blank to use question default."
    )

    class Meta:
        ordering = ['order']
        unique_together = ('section', 'question')

    def __str__(self):
        return f"{self.section} › Q{self.order}: {self.question.text[:40]}"

    @property
    def is_required(self):
        if self.is_required_override is not None:
            return self.is_required_override
        return self.question.is_required


# ---------------------------------------------------------------------------
# ASSIGNMENT LAYER
# ---------------------------------------------------------------------------

class CaseFormAssignment(models.Model):
    """
    A FormTemplate assigned to a specific Case.
    A case can have multiple templates assigned (e.g. intake form + KYC form).
    This is what triggers the client seeing a form in their portal.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),         # Assigned, client hasn't started
        ('in_progress', 'In Progress'), # Client has started filling
        ('submitted', 'Submitted'),     # Client submitted, lawyer hasn't reviewed
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),       # Sent back for corrections
    ]

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='form_assignments'
    )
    template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        related_name='case_assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_forms'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional deadline for the client to complete this form."
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_form_assignments'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Lawyer's notes when approving or rejecting a submission."
    )

    class Meta:
        unique_together = ('case', 'template')  # One template per case (assign a new one if needed)
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.case.reference_number} — {self.template.name} [{self.status}]"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status in ('pending', 'in_progress'):
            return self.due_date < timezone.now().date()
        return False


# ---------------------------------------------------------------------------
# SUBMISSION LAYER
# ---------------------------------------------------------------------------

class FormSubmission(models.Model):
    """
    A client's actual submission against a CaseFormAssignment.
    One submission per assignment. Partial saves supported (is_complete=False).
    """
    assignment = models.OneToOneField(
        CaseFormAssignment,
        on_delete=models.CASCADE,
        related_name='submission'
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='form_submissions'
    )
    is_complete = models.BooleanField(
        default=False,
        help_text="False = draft/partial save. True = client clicked Submit."
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_saved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission: {self.assignment} by {self.submitted_by.email}"


class FormResponse(models.Model):
    """
    A single question's answer within a FormSubmission.
    Typed fields mirror dynamic_forms: text, number, date, boolean, file, option.
    Only one field will be populated per response depending on the question's input_type.
    """
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    section = models.ForeignKey(
        FormSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # Typed answer fields — only one will be populated
    response_text = models.TextField(blank=True, null=True)         # text, textarea, email
    response_number = models.FloatField(null=True, blank=True)      # number
    response_date = models.DateField(null=True, blank=True)         # date
    response_boolean = models.BooleanField(null=True, blank=True)   # yes_no
    selected_option = models.ForeignKey(                            # select, checkbox
        QuestionOption,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='responses'
    )
    # File uploads go through document_management — store the Document FK here
    document = models.ForeignKey(
        'document_management.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='form_responses',
        help_text="For file-type questions, reference the document uploaded via document_management."
    )
    other_text = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Free text when client selects 'Other' on a select/checkbox question."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"{self.submission} — Q: {self.question.text[:40]}"
