"""
ClearWave — forms_engine/api/views.py

Function-based views. One function does absolutely one thing.
Each function uses only its own serializer.
Mirrors case_management/api/views.py patterns exactly.
"""

from django.utils import timezone
from django.shortcuts import get_object_or_404

from forms_engine_management.api.serializers import AssignQuestionToSectionSerializer, CreateCaseFormAssignmentSerializer, CreateFormSectionSerializer, CreateFormTemplateSerializer, CreateQuestionOptionSerializer, CreateQuestionSerializer, GetCaseFormAssignmentSerializer, GetFormResponseSerializer, GetFormSectionSerializer, GetFormSubmissionSerializer, GetFormTemplateSerializer, GetListForQuestionSerializer, GetQuestionOptionSerializer, GetQuestionSerializer, GetSectionQuestionSerializer, ReviewCaseFormAssignmentSerializer, SaveFormResponseSerializer, StartFormSubmissionSerializer, SubmitFormSerializer, UpdateFormSectionSerializer, UpdateFormTemplateSerializer, UpdateQuestionOptionSerializer, UpdateQuestionSerializer, UpdateSectionQuestionSerializer
from forms_engine_management.models import CaseFormAssignment, FormSection, FormSubmission, FormTemplate, Question, QuestionOption, SectionQuestion
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response

from system_management.models import AuditLog
from case_management.models import Case



# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _is_staff(user):
    """Firm owner, lawyer, or assistant — not a client."""
    return user.role in ("firm_owner", "lawyer", "assistant")

def _is_lawyer_or_owner(user):
    return user.role in ("firm_owner", "lawyer")


# ---------------------------------------------------------------------------
# FORM TEMPLATE
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_form_template_api(request):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    serializer = CreateFormTemplateSerializer(
        data=request.data,
        context={"request": request}
    )
    if serializer.is_valid():
        template = serializer.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="form_template_created",
            model_type="formtemplate",
            model_id=template.id,
            changes={"name": template.name},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": "Form template created.", "id": template.id}, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_form_templates_api(request):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    templates = FormTemplate.objects.filter(
        firm=request.user.firm
    ).select_related("case_type", "created_by")

    serializer = GetFormTemplateSerializer(templates, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_form_template_api(request, template_id):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    serializer = GetFormTemplateSerializer(template)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_form_template_api(request, template_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    serializer = UpdateFormTemplateSerializer(
        template,
        data=request.data,
        partial=True,
        context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="form_template_updated",
            model_type="formtemplate",
            model_id=template.id,
            changes=request.data,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": "Form template updated."})

    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# FORM SECTION
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_form_section_api(request, template_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    serializer = CreateFormSectionSerializer(
        data=request.data,
        context={"request": request, "template": template}
    )
    if serializer.is_valid():
        section = serializer.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="form_section_created",
            model_type="formsection",
            model_id=section.id,
            changes={"template_id": template.id, "name": section.name},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": "Section created.", "id": section.id}, status=201)

    return Response(serializer.errors, status=400)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_form_sections_api(request, template_id):
    # Staff see any template in their firm
    if _is_staff(request.user):
        template = get_object_or_404(
            FormTemplate,
            pk=template_id,
            firm=request.user.firm
        )
    # Clients can only see templates assigned to their cases
    elif request.user.role == "client":
        template = get_object_or_404(
            FormTemplate,
            pk=template_id,
            case_assignments__case__client=request.user
        )
    else:
        return Response({"error": "Permission denied."}, status=403)

    sections = template.sections.filter(is_active=True)
    serializer = GetFormSectionSerializer(sections, many=True)
    return Response(serializer.data)
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def list_form_sections_api(request, template_id):
#     if not _is_staff(request.user):
#         return Response({"error": "Permission denied."}, status=403)

#     template = get_object_or_404(
#         FormTemplate,
#         pk=template_id,
#         firm=request.user.firm
#     )

#     sections = template.sections.filter(is_active=True)
#     serializer = GetFormSectionSerializer(sections, many=True)
#     return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_form_section_api(request, template_id, section_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    section = get_object_or_404(FormSection, pk=section_id, template=template)

    serializer = UpdateFormSectionSerializer(
        section,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Section updated."})

    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# QUESTION BANK
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_question_api(request):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    serializer = CreateQuestionSerializer(
        data=request.data,
        context={"request": request}
    )
    if serializer.is_valid():
        question = serializer.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="question_created",
            model_type="question",
            model_id=question.id,
            changes={"text": question.text, "input_type": question.input_type},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": "Question created.", "id": question.id}, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_questions_api(request):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    questions = Question.objects.filter(
        firm=request.user.firm,
        is_active=True
    ).select_related("created_by").prefetch_related("options")

    serializer = GetListForQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_question_api(request, question_id):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    serializer = GetQuestionSerializer(question)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_question_api(request, question_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    serializer = UpdateQuestionSerializer(
        question,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question updated."})

    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# QUESTION OPTIONS
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_question_option_api(request, question_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    if question.input_type not in ("select", "checkbox"):
        return Response(
            {"error": "Options can only be added to select or checkbox questions."},
            status=400
        )

    serializer = CreateQuestionOptionSerializer(
        data=request.data,
        context={"question": question}
    )
    if serializer.is_valid():
        option = serializer.save()
        return Response({"message": "Option added.", "id": option.id}, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_question_options_api(request, question_id):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    options = question.options.all()
    serializer = GetQuestionOptionSerializer(options, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_question_option_api(request, question_id, option_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    option = get_object_or_404(QuestionOption, pk=option_id, question=question)

    serializer = UpdateQuestionOptionSerializer(
        option,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Option updated."})

    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_question_option_api(request, question_id, option_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    question = get_object_or_404(
        Question,
        pk=question_id,
        firm=request.user.firm
    )

    option = get_object_or_404(QuestionOption, pk=option_id, question=question)
    option.delete()
    return Response({"message": "Option deleted."})


# ---------------------------------------------------------------------------
# SECTION QUESTION ASSIGNMENT
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_question_to_section_api(request, template_id, section_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    section = get_object_or_404(FormSection, pk=section_id, template=template)

    serializer = AssignQuestionToSectionSerializer(
        data=request.data,
        context={"request": request, "section": section}
    )
    if serializer.is_valid():
        assignment = serializer.save()
        return Response(
            {"message": "Question assigned to section.", "id": assignment.id},
            status=201
        )

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_section_questions_api(request, template_id, section_id):
    if _is_staff(request.user):
        template = get_object_or_404(
            FormTemplate,
            pk=template_id,
            firm=request.user.firm
        )
    elif request.user.role == "client":
        template = get_object_or_404(
            FormTemplate,
            pk=template_id,
            case_assignments__case__client=request.user
        )
    else:
        return Response({"error": "Permission denied."}, status=403)

    section = get_object_or_404(FormSection, pk=section_id, template=template)
    sq = section.section_questions.select_related(
        "question"
    ).prefetch_related("question__options")

    serializer = GetSectionQuestionSerializer(sq, many=True)
    return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_section_question_api(request, template_id, section_id, section_question_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    section = get_object_or_404(FormSection, pk=section_id, template=template)
    sq = get_object_or_404(SectionQuestion, pk=section_question_id, section=section)

    serializer = UpdateSectionQuestionSerializer(sq, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Section question updated."})

    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_question_from_section_api(request, template_id, section_id, section_question_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    template = get_object_or_404(
        FormTemplate,
        pk=template_id,
        firm=request.user.firm
    )

    section = get_object_or_404(FormSection, pk=section_id, template=template)
    sq = get_object_or_404(SectionQuestion, pk=section_question_id, section=section)
    sq.delete()

    return Response({"message": "Question removed from section."})


# ---------------------------------------------------------------------------
# CASE FORM ASSIGNMENT (lawyer assigns a template to a case)
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_form_to_case_api(request, case_id):
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    serializer = CreateCaseFormAssignmentSerializer(
        data=request.data,
        context={"request": request, "case": case}
    )
    if serializer.is_valid():
        assignment = serializer.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="form_assigned_to_case",
            model_type="caseformassignment",
            model_id=assignment.id,
            changes={
                "case_id": case.id,
                "template_id": assignment.template.id,
                "template_name": assignment.template.name,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response(
            {"message": "Form assigned to case.", "id": assignment.id},
            status=201
        )

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_case_form_assignments_api(request, case_id):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    assignments = case.form_assignments.select_related(
        "template", "assigned_by", "reviewed_by"
    )

    serializer = GetCaseFormAssignmentSerializer(assignments, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_case_form_assignment_api(request, case_id, assignment_id):
    if not _is_staff(request.user):
        return Response({"error": "Permission denied."}, status=403)

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    assignment = get_object_or_404(CaseFormAssignment, pk=assignment_id, case=case)

    serializer = GetCaseFormAssignmentSerializer(assignment)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_case_form_assignment_api(request, case_id, assignment_id):
    """Lawyer approves or rejects a submitted form."""
    if not _is_lawyer_or_owner(request.user):
        return Response({"error": "Permission denied."}, status=403)

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    assignment = get_object_or_404(CaseFormAssignment, pk=assignment_id, case=case)

    # AFTER
    if assignment.status not in ("submitted", "approved", "rejected", "under_review"):
        return Response(
            {"error": "Form must be submitted before it can be reviewed."},
            status=400
        )

    # if assignment.status != "submitted":
    #     return Response(
    #         {"error": "Only submitted forms can be reviewed."},
    #         status=400
    #     )

    serializer = ReviewCaseFormAssignmentSerializer(
        assignment,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        assignment = serializer.save(
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="form_reviewed",
            model_type="caseformassignment",
            model_id=assignment.id,
            changes={
                "status": assignment.status,
                "review_notes": assignment.review_notes,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": f"Form marked as {assignment.status}."})

    return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# FORM SUBMISSION — CLIENT PORTAL
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_form_submission_api(request, assignment_id):
    """
    Client opens a form for the first time.
    Creates the FormSubmission shell (is_complete=False / draft).
    If a draft already exists, returns it instead of creating a duplicate.
    """
    assignment = get_object_or_404(
        CaseFormAssignment,
        pk=assignment_id,
        case__client=request.user
    )

    if assignment.status not in ("pending", "in_progress", "rejected"):
        return Response(
            {"error": "This form is not available for editing."},
            status=400
        )

    # Return existing draft if one exists
    existing = FormSubmission.objects.filter(assignment=assignment).first()
    if existing:
        serializer = GetFormSubmissionSerializer(existing)
        return Response(serializer.data)

    serializer = StartFormSubmissionSerializer(
        data={},
        context={"request": request, "assignment": assignment}
    )
    if serializer.is_valid():
        submission = serializer.save()

        # Move assignment to in_progress
        assignment.status = "in_progress"
        assignment.save()

        return Response(
            {"message": "Form started.", "submission_id": submission.id},
            status=201
        )

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_form_submission_api(request, assignment_id):
    """
    Get the full form submission with all responses.
    Used by both client (viewing their answers) and lawyer (reviewing).
    """
    # Lawyer/owner path
    if _is_staff(request.user):
        assignment = get_object_or_404(
            CaseFormAssignment,
            pk=assignment_id,
            case__firm=request.user.firm
        )
    else:
        # Client path
        assignment = get_object_or_404(
            CaseFormAssignment,
            pk=assignment_id,
            case__client=request.user
        )

    submission = get_object_or_404(FormSubmission, assignment=assignment)
    serializer = GetFormSubmissionSerializer(submission)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# FORM RESPONSE — CLIENT SAVES ANSWERS
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_form_response_api(request, submission_id):
    """
    Client saves a single question answer. Idempotent — calling it again
    updates the existing answer (update_or_create in the serializer).
    """
    submission = get_object_or_404(
        FormSubmission,
        pk=submission_id,
        submitted_by=request.user
    )

    if submission.is_complete:
        return Response(
            {"error": "Cannot edit a submitted form."},
            status=400
        )

    serializer = SaveFormResponseSerializer(
        data=request.data,
        context={"request": request, "submission": submission}
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Response saved."})

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_form_responses_api(request, submission_id):
    """Get all answers for a submission."""
    if _is_staff(request.user):
        submission = get_object_or_404(
            FormSubmission,
            pk=submission_id,
            assignment__case__firm=request.user.firm
        )
    else:
        submission = get_object_or_404(
            FormSubmission,
            pk=submission_id,
            submitted_by=request.user
        )

    responses = submission.responses.select_related(
        "question", "section", "selected_option", "document"
    )

    serializer = GetFormResponseSerializer(responses, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_form_api(request, submission_id):
    """
    Client finalises and submits the form.
    Sets is_complete=True, stamps submitted_at, moves assignment to 'submitted'.
    Separate from save_form_response — submitting is its own deliberate action.
    """
    submission = get_object_or_404(
        FormSubmission,
        pk=submission_id,
        submitted_by=request.user
    )

    if submission.is_complete:
        return Response({"error": "Form already submitted."}, status=400)

    serializer = SubmitFormSerializer(
        submission,
        data={},
        partial=True
    )
    if serializer.is_valid():
        serializer.save()

        # Move assignment status to submitted
        assignment = submission.assignment
        assignment.status = "submitted"
        assignment.save()

        AuditLog.objects.create(
            firm=assignment.case.firm,
            user=request.user,
            action="form_submitted",
            model_type="formsubmission",
            model_id=submission.id,
            changes={
                "case_id": assignment.case.id,
                "template_name": assignment.template.name,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"message": "Form submitted successfully."})

    return Response(serializer.errors, status=400)

