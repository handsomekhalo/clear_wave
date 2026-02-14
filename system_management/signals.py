# case_management/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Case
from system_management.models import AuditLog


@receiver(post_save, sender=Case)
def log_case_created(sender, instance, created, **kwargs):
    """Log case creation to audit log."""
    if created:
        AuditLog.objects.create(
            firm=instance.firm,
            user=instance.assigned_lawyer,
            action='case_created',
            model_type='case',
            model_id=instance.id,
            changes={
                'title': instance.title,
                'client': instance.client.email,
                'assigned_lawyer': instance.assigned_lawyer.email,
                'matter_type': instance.matter_type,
            }
        )


@receiver(pre_save, sender=Case)
def log_status_change(sender, instance, **kwargs):
    """Log case status changes."""
    if instance.pk:  # Only for updates, not creation
        try:
            old_instance = Case.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                AuditLog.objects.create(
                    firm=instance.firm,
                    user=None,  # Will be set by middleware if available
                    action='case_status_changed',
                    model_type='case',
                    model_id=instance.id,
                    changes={
                        'old_status': old_instance.status,
                        'new_status': instance.status,
                    }
                )
        except Case.DoesNotExist:
            pass