from django.db import models

# Create your models here.
# case_management/models.py
from django.utils import timezone
from system_management.models import Firm, User




class CaseType(models.Model):
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, related_name='case_types')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('firm', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name

class Case(models.Model):
    """
    Represents a legal case/matter.
    Core entity in the system - everything else revolves around Case.
    """
    NEW = 'new'
    ACTIVE = 'active'
    ON_HOLD = 'on_hold'
    CLOSED = 'closed'
    ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (NEW, 'New'),
        (ACTIVE, 'Active'),
        (ON_HOLD, 'On Hold'),
        (CLOSED, 'Closed'),
        (ARCHIVED, 'Archived'),
    ]
    
    LITIGATION = 'litigation'
    CONVEYANCING = 'conveyancing'
    CORPORATE = 'corporate'
    FAMILY = 'family'
    CRIMINAL = 'criminal'
    IMMIGRATION = 'immigration'
    OTHER = 'other'
    
    MATTER_TYPE_CHOICES = [
        (LITIGATION, 'Litigation'),
        (CONVEYANCING, 'Conveyancing'),
        (CORPORATE, 'Corporate'),
        (FAMILY, 'Family Law'),
        (CRIMINAL, 'Criminal'),
        (IMMIGRATION, 'Immigration'),
        (OTHER, 'Other'),
    ]
    
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]
    
    # Tenant isolation
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name='cases'
    )
    
    # Basic info
    title = models.CharField(max_length=255)

    # case identifiers...

    reference_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False,
        db_index=True,
        help_text="Internal system-generated reference (e.g. 2026-ALPHA-0001)"
    )

    external_case_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official court/registry/client-provided case number (if applicable)"
    )

    # ... rest of your fields (status, client, assigned_lawyer, etc.)
    description = models.TextField(blank=True)
    

    # Parties
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_cases',
        limit_choices_to={'role': 'client'}
        
        
    )
    assigned_lawyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_cases',
        limit_choices_to={'role__in': ['lawyer', 'firm_owner']}
    )
    assigned_assistant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistant_cases',
        limit_choices_to={'role': 'assistant'}
    )
    # Classification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NEW
    )
    # matter_type = models.CharField(
    #     max_length=20,
    #     choices=MATTER_TYPE_CHOICES,
    #     default=OTHER
    # )
    matter_type = models.ForeignKey(
            CaseType,
            on_delete=models.SET_NULL,
            null=True,
            related_name='cases'
        )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=MEDIUM
    )
    
    # Important dates
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['firm', 'status']),
            models.Index(fields=['assigned_lawyer', 'status']),
            models.Index(fields=['deadline']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def close(self):
        """Mark case as closed."""
        self.status = self.CLOSED
        self.closed_at = timezone.now()
        self.save()
    
    def reopen(self):
        """Reopen a closed case."""
        self.status = self.ACTIVE
        self.closed_at = None
        self.save()
    
    def is_overdue(self):
        """Check if case deadline has passed."""
        if not self.deadline:
            return False
        return self.deadline < timezone.now().date()
    
    @property
    def days_until_deadline(self):
        """Calculate days until deadline."""
        if not self.deadline:
            return None
        delta = self.deadline - timezone.now().date()
        return delta.days




class Note(models.Model):
    """
    Internal notes on a case.
    NOT visible to clients - only lawyers/assistants.
    """
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"Note on {self.case.title} by {self.created_by.email}"