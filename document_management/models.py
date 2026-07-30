import uuid
from django.db import models
from django.utils import timezone

from case_management.models import Case
from system_management.models import Firm, User




class Document(models.Model):
    """
    Stores documents linked to a case, including S3 storage details,
    sharing controls, soft delete, and versioning support.
    """

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('xlsx', 'XLSX'),
        ('jpg', 'JPG'),
        ('png', 'PNG'),
        ('other', 'Other'),
    ]

    CATEGORY_CHOICES = [
        ('correspondence', 'Correspondence'),
        ('contract', 'Contract'),
        ('court_filing', 'Court Filing'),
        ('evidence', 'Evidence'),
        ('client_document', 'Client Document'),
        ('other', 'Other'),
    ]

    # Tenant isolation
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # Core
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )

    # File info
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # S3 key (must be generated uniquely)
    file_size = models.IntegerField()  # bytes
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='other')
    mime_type = models.CharField(max_length=100, blank=True)
    checksum = models.CharField(max_length=64, blank=True)  # SHA256

    # Classification
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    version = models.IntegerField(default=1)

    # Sharing
    is_shared = models.BooleanField(default=False)
    shared_link = models.UUIDField(unique=True, null=True, blank=True)
    shared_until = models.DateTimeField(null=True, blank=True)
    shared_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shared_documents'
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deleted_documents'
    )

    # Timestamps
    uploaded_at = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['firm']),
            models.Index(fields=['case']),
            models.Index(fields=['shared_link']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.file_name} — {self.case} (v{self.version})"

    def save(self, *args, **kwargs):
        # Ensure firm is always derived from case
        if not self.firm_id:
            self.firm = self.case.firm
        super().save(*args, **kwargs)

    def generate_share_link(self, shared_by=None, expires_at=None):
        self.shared_link = uuid.uuid4()
        self.is_shared = True
        self.shared_by = shared_by
        self.shared_until = expires_at
        self.save()

    def revoke_share_link(self):
        self.shared_link = None
        self.is_shared = False
        self.shared_until = None
        self.shared_by = None
        self.save()

    def get_presigned_url(self, expires_in=3600):
        from .storage import S3StorageHandler
        return S3StorageHandler().generate_presigned_url(self.file_path, expires_in)

    def soft_delete(self, deleted_by=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save()


class DocumentVersion(models.Model):
    """
    Tracks previous versions of a document so history is never lost
    when a file is updated.
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.IntegerField()
    file_path = models.CharField(max_length=500)  # S3 key for this version
    file_size = models.IntegerField()

    uploaded_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='document_versions'
    )

    change_note = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('document', 'version_number')
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['document', 'version_number']),
        ]

    def __str__(self):
        return f"{self.document.file_name} — v{self.version_number}"


class DocumentAccess(models.Model):
    """
    Audit log for every action taken on a document.
    """

    ACTION_CHOICES = [
        ('view', 'View'),
        ('download', 'Download'),
        ('share', 'Share'),
        ('revoke', 'Revoke'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )

    accessed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='document_accesses'
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    shared_link_used = models.BooleanField(default=False)
    success = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    accessed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['accessed_at']),
        ]

    def __str__(self):
        actor = self.accessed_by or "Anonymous"
        return f"{actor} — {self.action} — {self.document.file_name}"