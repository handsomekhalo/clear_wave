from django.db import models

# Create your models here.
# system_management/models.py

from django.contrib.auth.models import AbstractUser

from django.db import models
from django.utils import timezone
from datetime import timedelta


class Firm(models.Model):
    """
    Represents a law firm (tenant in multi-tenant architecture).
    Each firm is completely isolated from other firms.
    """
    ACTIVE = 'active'
    FREE_TIER = 'free_tier'
    SUSPENDED = 'suspended'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active Subscription'),
        (FREE_TIER, 'Free Tier'),
        (SUSPENDED, 'Suspended'),
    ]
    
    SOLO = 'solo'
    SMALL_FIRM = 'small_firm'
    GROWING_FIRM = 'growing_firm'
    
    PLAN_CHOICES = [
        (SOLO, 'Solo Plan'),
        (SMALL_FIRM, 'Small Firm Plan'),
        (GROWING_FIRM, 'Growing Firm Plan'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='owned_firm'
    )
    
    # Subscription
    subscription_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=FREE_TIER
    )
    subscription_plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default=SOLO
    )
    subscription_end_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    
    # Limits (based on plan)
    max_users = models.IntegerField(default=1)
    max_active_cases = models.IntegerField(default=5)
    storage_limit_gb = models.IntegerField(default=5)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Firm'
        verbose_name_plural = 'Firms'
    
    def __str__(self):
        return self.name
    
    def can_create_case(self):
        """Check if firm can create new cases based on plan limits."""
        if self.subscription_status == self.ACTIVE:
            return True
        
        # Free tier: check case limit
        from case_management.models import Case
        active_cases = Case.objects.filter(
            firm=self,
            status__in=['new', 'active', 'on_hold']
        ).count()
        
        return active_cases < self.max_active_cases
    
    def can_add_user(self):
        """Check if firm can add new users based on plan limits."""
        if self.subscription_status == self.ACTIVE:
            return self.users.count() < self.max_users
        
        # Free tier: max 1 user
        return self.users.count() < 1
    
    def check_subscription_status(self):
        """
        Check and update subscription status.
        Run this daily via Celery task.
        """
        if self.subscription_status == self.ACTIVE:
            if self.subscription_end_date and self.subscription_end_date < timezone.now().date():
                # Subscription expired, downgrade to free tier
                self.subscription_status = self.FREE_TIER
                self.save()
                
                # TODO: Send email notification
                from notifications.tasks import send_downgrade_email
                send_downgrade_email.delay(self.id)


class User(AbstractUser):
    """
    Custom user model with role-based access and firm association.
    """
    SUPER_ADMIN = 'super_admin'
    FIRM_OWNER = 'firm_owner'
    LAWYER = 'lawyer'
    ASSISTANT = 'assistant'
    CLIENT = 'client'
    
    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (FIRM_OWNER, 'Firm Owner'),
        (LAWYER, 'Lawyer'),
        (ASSISTANT, 'Assistant'),
        (CLIENT, 'Client'),
    ]
    
    # Use email as username
    username = None
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD
    
    # Firm association
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )
    
    # Role
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENT
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def is_firm_owner(self):
        """Check if user is a firm owner."""
        return self.role == self.FIRM_OWNER
    
    def is_lawyer(self):
        """Check if user is a lawyer."""
        return self.role == self.LAWYER
    
    def is_client(self):
        """Check if user is a client."""
        return self.role == self.CLIENT
    
    def can_manage_users(self):
        """Check if user can add/remove users in their firm."""
        return self.role in [self.SUPER_ADMIN, self.FIRM_OWNER]
    
    def can_view_case(self, case):
        """Check if user can view a specific case."""
        # Super admin can view all
        if self.role == self.SUPER_ADMIN:
            return True
        
        # Must be same firm
        if self.firm != case.firm:
            return False
        
        # Firm owner can view all cases in firm
        if self.role == self.FIRM_OWNER:
            return True
        
        # Lawyer/assistant can view all cases
        if self.role in [self.LAWYER, self.ASSISTANT]:
            return True
        
        # Client can only view their own cases
        if self.role == self.CLIENT:
            return case.client == self
        
        return False


class AuditLog(models.Model):
    """
    System-wide audit log for compliance.
    Tracks all significant actions across the platform.
    """
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Action details
    action = models.CharField(max_length=100)
    model_type = models.CharField(
        max_length=50,
        choices=[
            ('case', 'Case'),
            ('document', 'Document'),
            ('user', 'User'),
            ('firm', 'Firm'),
        ]
    )
    model_id = models.IntegerField()
    
    # Change tracking
    changes = models.JSONField(default=dict, blank=True)
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['firm', 'timestamp']),
            models.Index(fields=['model_type', 'model_id']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"