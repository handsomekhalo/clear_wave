from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_deadline_reminders():
    from case_management.models import Case

    today = timezone.now().date()
    reminder_days = [7, 3, 1]
    sent_count = 0

    for days in reminder_days:
        target_date = today + timedelta(days=days)

        cases = Case.objects.filter(
            deadline=target_date,
            status__in=['new', 'active', 'on_hold'],
        ).select_related('assigned_lawyer', 'client', 'firm')

        for case in cases:
            # Email assigned lawyer
            if case.assigned_lawyer and case.assigned_lawyer.email:
                try:
                    send_mail(
                        subject=f"[ClearWave] Deadline Reminder — {case.title}",
                        message=f"""Hi {case.assigned_lawyer.first_name or 'there'},

This is a reminder that the following case has a deadline in {days} day{'s' if days > 1 else ''}:

Case: {case.title}
Reference: {case.reference_number}
Deadline: {case.deadline.strftime('%d %B %Y')}
Status: {case.get_status_display()}
Firm: {case.firm.name}

Please log in to ClearWave to review the case.

— ClearWave
""",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[case.assigned_lawyer.email],
                        fail_silently=False,
                    )
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send reminder for case {case.reference_number}: {e}")

    return f"Sent {sent_count} deadline reminder(s)"


@shared_task
def test_celery():
    """Use this to confirm Celery is working."""
    return "Celery is working correctly."