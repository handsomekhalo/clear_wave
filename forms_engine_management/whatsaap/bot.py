 
import logging
from django.utils import timezone
from forms_engine_management.models import FormResponse, FormSection, FormSubmission, WhatsAppMessage, WhatsAppSession
from twilio.rest import Client as TwilioClient
from django.conf import settings


logger = logging.getLogger(__name__)
 
 
def send_whatsapp_message(to, body):
    """
    Send a WhatsApp message via Twilio.
    Reads TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM from settings.
    """
    try:
        client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{to}",
            body=body,
        )
    except Exception as e:
        logger.exception(f"Failed to send WhatsApp message to {to}: {e}")
 
 
def get_ordered_section_questions(template_id):
    """
    Returns all SectionQuestions for a template in section order then question order.
    Returns list of (section, sq) tuples.
    """

    sections = FormSection.objects.filter(
        template_id=template_id,
        is_active=True
    ).order_by("order").prefetch_related("section_questions__question__options")
 
    result = []
    for section in sections:
        for sq in section.section_questions.order_by("order"):
            result.append((section, sq))
    return result
 
 
def format_question(section, sq, index, total):
    """
    Format a question for WhatsApp — plain text, no markdown.
    """
    q = sq.question
    lines = []
 
    # Section header if first question in section
    lines.append(f"*{section.name}*")
    lines.append(f"Question {index + 1} of {total}")
    lines.append("")
    lines.append(q.text)
 
    if q.helper_text:
        lines.append(f"_{q.helper_text}_")
 
    # Options for select/checkbox
    if q.input_type in ("select", "checkbox") and q.options.exists():
        lines.append("")
        for i, opt in enumerate(q.options.all().order_by("order"), 1):
            lines.append(f"{i}. {opt.text}")
        if q.allow_other_option:
            lines.append(f"{q.options.count() + 1}. Other")
 
    if q.input_type == "yes_no":
        lines.append("")
        lines.append("Reply: *Yes* or *No*")
 
    if not sq.is_required:
        lines.append("")
        lines.append("_(Optional — reply 'skip' to skip this question)_")
 
    return "\n".join(lines)
 
 
def parse_answer(sq, body):
    """
    Parse client's text reply into a FormResponse payload dict.
    Returns None if answer is invalid and a retry message is needed.
    Returns "skip" if client typed skip on an optional question.
    """
    q = sq.question
    body_lower = body.strip().lower()
 
    if body_lower == "skip" and not sq.is_required:
        return "skip"
 
    if q.input_type in ("text", "textarea", "email"):
        return {"response_text": body.strip()}
 
    if q.input_type == "number":
        try:
            return {"response_number": float(body.strip())}
        except ValueError:
            return None
 
    if q.input_type == "date":
        # Accept DD/MM/YYYY or YYYY-MM-DD
        import re
        dmy = re.match(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", body.strip())
        ymd = re.match(r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", body.strip())
        if dmy:
            d, m, y = dmy.groups()
            return {"response_date": f"{y}-{int(m):02d}-{int(d):02d}"}
        if ymd:
            y, m, d = ymd.groups()
            return {"response_date": f"{y}-{int(m):02d}-{int(d):02d}"}
        return None
 
    if q.input_type == "yes_no":
        if body_lower in ("yes", "y", "1"):
            return {"response_boolean": True}
        if body_lower in ("no", "n", "0"):
            return {"response_boolean": False}
        return None
 
    if q.input_type == "select":
        options = list(q.options.all().order_by("order"))
        # Try numeric reply
        try:
            idx = int(body.strip()) - 1
            if 0 <= idx < len(options):
                return {"selected_option": options[idx].id}
            if q.allow_other_option and idx == len(options):
                return {"other_text": "Other"}
        except ValueError:
            # Try text match
            for opt in options:
                if opt.text.lower() == body_lower:
                    return {"selected_option": opt.id}
        return None
 
    # File uploads — client sends media
    # Handled separately via media_url in webhook
    if q.input_type == "file":
        return {"response_text": "[File received via WhatsApp]"}
 
    return {"response_text": body.strip()}
 
 
def process_inbound_message(session, body, media_url=None):
    """
    Core bot logic.
    1. Find current question from session state
    2. Parse and save the answer
    3. Advance to next question or finish
    """
    assignment = session.assignment
    template_id = assignment.template_id
 
    # Get or create submission
    submission, _ = FormSubmission.objects.get_or_create(
        assignment=assignment,
        defaults={"submitted_by": session.client, "is_complete": False}
    )
    if not session.submission:
        session.submission = submission
        session.save(update_fields=["submission"])
 
    # Load all questions in order
    all_questions = get_ordered_section_questions(template_id)
    total = len(all_questions)
 
    if total == 0:
        send_whatsapp_message(
            session.phone_number,
            "This form has no questions yet. Please contact your lawyer."
        )
        return
 
    # Current question index (flat across all sections)
    flat_index = (
        session.current_section_index * 1000 +  # rough offset, recalculate below
        session.current_question_index
    )
 
    # Recalculate flat index properly
    flat_index = 0
    section_ids = []
    for i, (sec, sq) in enumerate(all_questions):
        if sec.id not in section_ids:
            section_ids.append(sec.id)
        sec_idx = section_ids.index(sec.id)
        if sec_idx == session.current_section_index:
            if flat_index == 0:
                flat_index = i
            if i - flat_index == session.current_question_index:
                current_idx = i
                current_section, current_sq = sec, sq
                break
    else:
        # Session state is past end — form is already done
        _finish_session(session, submission)
        return
 
    # Handle YES to start
    if body.strip().upper() == "YES" and not FormResponse.objects.filter(submission=submission).exists():
        # Send first question
        section, sq = all_questions[0]
        msg = format_question(section, sq, 0, total)
        send_whatsapp_message(session.phone_number, msg)
        return
 
    # Parse answer
    payload = parse_answer(current_sq, body)
 
    if payload is None:
        # Invalid answer — retry
        section, sq = current_section, current_sq
        retry_msg = (
            "Sorry, I didn't understand that answer. Please try again.\n\n" +
            format_question(section, sq, current_idx, total)
        )
        send_whatsapp_message(session.phone_number, retry_msg)
        return
 
    if payload != "skip":
        # Save response
        FormResponse.objects.update_or_create(
            submission=submission,
            question=current_sq.question,
            defaults={
                "section": current_section,
                **payload,
            }
        )
 
    # Advance to next question
    next_idx = current_idx + 1
 
    if next_idx >= total:
        # All questions answered
        _finish_session(session, submission)
        return
 
    # Update session state
    next_section, next_sq = all_questions[next_idx]
    next_section_ids = []
    for sec, sq in all_questions[:next_idx + 1]:
        if sec.id not in next_section_ids:
            next_section_ids.append(sec.id)
    session.current_section_index = next_section_ids.index(next_section.id)
    session.current_question_index = next_idx - sum(
        1 for sec, _ in all_questions[:next_idx] if sec.id != next_section.id
    )
    session.last_activity = timezone.now()
    session.save(update_fields=[
        "current_section_index", "current_question_index", "last_activity"
    ])
 
    # Send next question
    msg = format_question(next_section, next_sq, next_idx, total)
    send_whatsapp_message(session.phone_number, msg)
 
    # Log outbound
    WhatsAppMessage.objects.create(
        session=session,
        direction="outbound",
        message_type="text",
        body=msg,
        question=next_sq.question,
    )
 
 
def _finish_session(session, submission):
    """
    All questions answered — submit the form and close the session.
    """
    submission.is_complete = True
    submission.submitted_at = timezone.now()
    submission.save()
 
    assignment = session.assignment
    assignment.status = "submitted"
    assignment.save()
 
    session.status = "completed"
    session.completed_at = timezone.now()
    session.save(update_fields=["status", "completed_at"])
 
    send_whatsapp_message(
        session.phone_number,
        "✅ All done! Your information has been sent to "
        f"{assignment.case.firm.name}. They'll be in touch shortly."
    )
 
 
def start_whatsapp_session(assignment, client, phone_number, provider="twilio"):
    """
    Called by the lawyer-side view when they choose to send a form via WhatsApp
    instead of (or in addition to) the client portal.
 
    Creates the session and sends the opening message.
    Add this call to assign_form_to_case_api or a separate endpoint.
    """
    session, created = WhatsAppSession.objects.get_or_create(
        assignment=assignment,
        phone_number=phone_number,
        defaults={
            "client": client,
            "provider": provider,
            "status": "active",
            "current_section_index": 0,
            "current_question_index": 0,
        }
    )
 
    if not created and session.status == "completed":
        # Reopen for re-submission (e.g. after rejection)
        session.status = "active"
        session.current_section_index = 0
        session.current_question_index = 0
        session.save()
 
    # Opening message
    opening = (
        f"Hi {client.first_name}, {assignment.case.firm.name} needs some "
        f"information for your case ({assignment.case.reference_number}).\n\n"
        f"I'll ask you a few quick questions — just reply to each one.\n\n"
        f"Reply *YES* to start."
    )
    send_whatsapp_message(phone_number, opening)
 
    WhatsAppMessage.objects.create(
        session=session,
        direction="outbound",
        message_type="text",
        body=opening,
    )
 
    return session
