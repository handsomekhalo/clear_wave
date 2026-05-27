"""
ClearWave — forms_engine/api/serializers.py

One serializer per operation. No reuse across views.
Mirrors case_management serializer patterns exactly.
"""
from forms_engine_management.models import CaseFormAssignment, FormResponse, FormSection, FormSubmission, FormTemplate, Question, QuestionOption, SectionQuestion
from rest_framework import serializers
from django.utils import timezone



# ---------------------------------------------------------------------------
# FORM TEMPLATE
# ---------------------------------------------------------------------------

class CreateFormTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTemplate
        fields = ["name", "description", "case_type", "is_active"]

    def validate_case_type(self, value):
        if value and value.firm != self.context["request"].user.firm:
            raise serializers.ValidationError("Invalid case type.")
        return value

    def validate_name(self, value):
        firm = self.context["request"].user.firm
        if FormTemplate.objects.filter(firm=firm, name=value).exists():
            raise serializers.ValidationError(
                "A template with this name already exists for your firm."
            )
        return value

    def create(self, validated_data):
        return FormTemplate.objects.create(
            firm=self.context["request"].user.firm,
            created_by=self.context["request"].user,
            **validated_data
        )


class GetFormTemplateSerializer(serializers.ModelSerializer):
    case_type = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    section_count = serializers.SerializerMethodField()

    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "name",
            "description",
            "case_type",
            "is_active",
            "created_by",
            "section_count",
            "date_created",
            "date_updated",
        ]

    def get_case_type(self, obj):
        if obj.case_type:
            return {"id": obj.case_type.id, "name": obj.case_type.name}
        return None

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "name": f"{obj.created_by.first_name} {obj.created_by.last_name}",
            }
        return None

    def get_section_count(self, obj):
        return obj.sections.filter(is_active=True).count()


class UpdateFormTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTemplate
        fields = ["name", "description", "case_type", "is_active"]

    def validate_case_type(self, value):
        if value and value.firm != self.context["request"].user.firm:
            raise serializers.ValidationError("Invalid case type.")
        return value

    def validate_name(self, value):
        firm = self.context["request"].user.firm
        qs = FormTemplate.objects.filter(firm=firm, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A template with this name already exists for your firm."
            )
        return value


# ---------------------------------------------------------------------------
# FORM SECTION
# ---------------------------------------------------------------------------

class CreateFormSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSection
        fields = ["name", "description", "order", "is_active"]

    def validate_name(self, value):
        template = self.context["template"]
        if FormSection.objects.filter(template=template, name=value).exists():
            raise serializers.ValidationError(
                "A section with this name already exists in this template."
            )
        return value

    def create(self, validated_data):
        return FormSection.objects.create(
            template=self.context["template"],
            **validated_data
        )


class GetFormSectionSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = FormSection
        fields = [
            "id",
            "name",
            "description",
            "order",
            "is_active",
            "question_count",
            "date_created",
        ]

    def get_question_count(self, obj):
        return obj.section_questions.count()


class UpdateFormSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSection
        fields = ["name", "description", "order", "is_active"]

    def validate_name(self, value):
        template = self.instance.template
        qs = FormSection.objects.filter(template=template, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A section with this name already exists in this template."
            )
        return value


# ---------------------------------------------------------------------------
# QUESTION (FIRM QUESTION BANK)
# ---------------------------------------------------------------------------

class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "text",
            "input_type",
            "is_required",
            "allow_other_option",
            "helper_text",
        ]

    def create(self, validated_data):
        return Question.objects.create(
            firm=self.context["request"].user.firm,
            created_by=self.context["request"].user,
            **validated_data
        )


class GetQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "input_type",
            "is_required",
            "is_active",
            "allow_other_option",
            "helper_text",
            "options",
            "created_by",
            "date_created",
            "date_updated",
        ]

    def get_options(self, obj):
        return [
            {"id": o.id, "text": o.text, "order": o.order, "is_default": o.is_default}
            for o in obj.options.all()
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "name": f"{obj.created_by.first_name} {obj.created_by.last_name}",
            }
        return None



class GetListForQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "input_type",
            "is_required",
            "is_active",
            "allow_other_option",
            "helper_text",
            "options",
            "created_by",
            "date_created",
            "date_updated",
        ]

    def get_options(self, obj):
        return [
            {"id": o.id, "text": o.text, "order": o.order, "is_default": o.is_default}
            for o in obj.options.all()
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "name": f"{obj.created_by.first_name} {obj.created_by.last_name}",
            }
        return None

class UpdateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "text",
            "input_type",
            "is_required",
            "is_active",
            "allow_other_option",
            "helper_text",
        ]


# ---------------------------------------------------------------------------
# QUESTION OPTION
# ---------------------------------------------------------------------------

class CreateQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["text", "order", "is_default"]

    def create(self, validated_data):
        return QuestionOption.objects.create(
            question=self.context["question"],
            **validated_data
        )


class GetQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "text", "order", "is_default"]


class UpdateQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["text", "order", "is_default"]


# ---------------------------------------------------------------------------
# SECTION QUESTION (assigning a question to a section)
# ---------------------------------------------------------------------------

class AssignQuestionToSectionSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all()
    )

    class Meta:
        model = SectionQuestion
        fields = ["question", "order", "is_required_override"]

    def validate_question(self, value):
        # Question must belong to the same firm
        firm = self.context["request"].user.firm
        if value.firm != firm:
            raise serializers.ValidationError("Question does not belong to your firm.")
        return value

    def validate(self, data):
        section = self.context["section"]
        if SectionQuestion.objects.filter(
            section=section, question=data["question"]
        ).exists():
            raise serializers.ValidationError(
                "This question is already assigned to this section."
            )
        return data

    def create(self, validated_data):
        return SectionQuestion.objects.create(
            section=self.context["section"],
            **validated_data
        )


class GetSectionQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    is_required = serializers.ReadOnlyField()

    class Meta:
        model = SectionQuestion
        fields = ["id", "question", "order", "is_required_override", "is_required"]

    def get_question(self, obj):
        q = obj.question
        return {
            "id": q.id,
            "text": q.text,
            "input_type": q.input_type,
            "helper_text": q.helper_text,
            "allow_other_option": q.allow_other_option,
            "options": [
                {"id": o.id, "text": o.text, "order": o.order, "is_default": o.is_default}
                for o in q.options.all()
            ],
        }


class UpdateSectionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionQuestion
        fields = ["order", "is_required_override"]


# ---------------------------------------------------------------------------
# CASE FORM ASSIGNMENT
# ---------------------------------------------------------------------------

class CreateCaseFormAssignmentSerializer(serializers.ModelSerializer):
    template = serializers.PrimaryKeyRelatedField(
        queryset=FormTemplate.objects.all()
    )

    class Meta:
        model = CaseFormAssignment
        fields = ["template", "due_date"]

    def validate_template(self, value):
        firm = self.context["request"].user.firm
        if value.firm != firm:
            raise serializers.ValidationError("Template does not belong to your firm.")
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign an inactive template.")
        return value

    def validate(self, data):
        case = self.context["case"]
        if CaseFormAssignment.objects.filter(
            case=case, template=data["template"]
        ).exists():
            raise serializers.ValidationError(
                "This template is already assigned to this case."
            )
        return data

    def create(self, validated_data):
        return CaseFormAssignment.objects.create(
            case=self.context["case"],
            assigned_by=self.context["request"].user,
            **validated_data
        )


class GetCaseFormAssignmentSerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()
    assigned_by = serializers.SerializerMethodField()
    reviewed_by = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = CaseFormAssignment
        fields = [
            "id",
            "template",
            "status",
            "status_display",
            "due_date",
            "is_overdue",
            "assigned_by",
            "assigned_at",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
        ]

    def get_template(self, obj):
        return {"id": obj.template.id, "name": obj.template.name}

    def get_assigned_by(self, obj):
        if obj.assigned_by:
            return {
                "id": obj.assigned_by.id,
                "name": f"{obj.assigned_by.first_name} {obj.assigned_by.last_name}",
            }
        return None

    def get_reviewed_by(self, obj):
        if obj.reviewed_by:
            return {
                "id": obj.reviewed_by.id,
                "name": f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}",
            }
        return None


class ReviewCaseFormAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseFormAssignment
        fields = ["status", "review_notes"]

    def validate_status(self, value):
        allowed = ["approved", "rejected", "under_review"]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed)}"
            )
        return value


# ---------------------------------------------------------------------------
# FORM SUBMISSION (client fills in the form)
# ---------------------------------------------------------------------------

class StartFormSubmissionSerializer(serializers.ModelSerializer):
    """
    Called when client opens the form for the first time (draft save).
    Creates the FormSubmission shell with is_complete=False.
    """
    class Meta:
        model = FormSubmission
        fields = []  # No client input needed — everything from context

    def create(self, validated_data):
        return FormSubmission.objects.create(
            assignment=self.context["assignment"],
            submitted_by=self.context["request"].user,
            is_complete=False,
        )


class GetFormSubmissionSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        fields = [
            "id",
            "assignment",
            "submitted_by",
            "is_complete",
            "submitted_at",
            "last_saved_at",
            "response_count",
        ]

    def get_submitted_by(self, obj):
        return {
            "id": obj.submitted_by.id,
            "email": obj.submitted_by.email,
            "name": f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}",
        }

    def get_assignment(self, obj):
        return {
            "id": obj.assignment.id,
            "template_name": obj.assignment.template.name,
            "template_id": obj.assignment.template.id,  # add this
            "case_reference": obj.assignment.case.reference_number,
            "case_id": obj.assignment.case.id,  # add this

        }

    def get_response_count(self, obj):
        return obj.responses.count()


# ---------------------------------------------------------------------------
# FORM RESPONSE (one answer per question)
# ---------------------------------------------------------------------------

class SaveFormResponseSerializer(serializers.ModelSerializer):
    """
    Saves or updates a single question's answer.
    Called repeatedly as client fills each question.
    """
    class Meta:
        model = FormResponse
        fields = [
            "question",
            "section",
            "response_text",
            "response_number",
            "response_date",
            "response_boolean",
            "selected_option",
            "document",
            "other_text",
        ]

    def validate_question(self, value):
        # Question must belong to the same firm
        firm = self.context["request"].user.firm
        if value.firm != firm:
            raise serializers.ValidationError("Invalid question.")
        return value

    def validate_selected_option(self, value):
        if value:
            # Option must belong to the question being answered
            question = self.initial_data.get("question")
            if question and str(value.question_id) != str(question):
                raise serializers.ValidationError(
                    "Selected option does not belong to this question."
                )
        return value

    def create(self, validated_data):
        submission = self.context["submission"]
        # Use update_or_create so partial saves don't duplicate rows
        response, _ = FormResponse.objects.update_or_create(
            submission=submission,
            question=validated_data["question"],
            defaults=validated_data,
        )
        return response


class GetFormResponseSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    selected_option = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()

    class Meta:
        model = FormResponse
        fields = [
            "id",
            "question",
            "section",
            "response_text",
            "response_number",
            "response_date",
            "response_boolean",
            "selected_option",
            "document",
            "other_text",
            "created_at",
            "updated_at",
        ]

    def get_question(self, obj):
        return {
            "id": obj.question.id,
            "text": obj.question.text,
            "input_type": obj.question.input_type,
        }

    def get_selected_option(self, obj):
        if obj.selected_option:
            return {"id": obj.selected_option.id, "text": obj.selected_option.text}
        return None

    def get_document(self, obj):
        if obj.document:
            return {"id": obj.document.id, "name": obj.document.file_name}
        return None


class SubmitFormSerializer(serializers.ModelSerializer):
    """
    Final submit. Sets is_complete=True and stamps submitted_at.
    Separate from SaveFormResponseSerializer — submitting is its own action.
    """
    class Meta:
        model = FormSubmission
        fields = []  # No input — just the action of submitting

    def update(self, instance, validated_data):
        instance.is_complete = True
        instance.submitted_at = timezone.now()
        instance.save()
        return instance