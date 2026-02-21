from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.
# system_management/models.py



from django.db import models
from django.utils import timezone
from datetime import timedelta



# models.py
# from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.SUPER_ADMIN)  # or whatever your super admin role constant is

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    SUPER_ADMIN = 'super_admin'
    FIRM_OWNER  = 'firm_owner'
    LAWYER      = 'lawyer'
    ASSISTANT   = 'assistant'
    CLIENT      = 'client'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (FIRM_OWNER,  'Firm Owner'),
        (LAWYER,      'Lawyer'),
        (ASSISTANT,   'Assistant'),
        (CLIENT,      'Client'),
    ]

    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # No username field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []   # nothing extra — just email + password

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENT
    )

    firm = models.ForeignKey(
        'Firm',  # adjust if Firm is in another app → 'yourapp.Firm'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    phone = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)   # crucial for admin access

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # for soft delete





    objects = UserManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['firm', 'role']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    # Your helper methods...
    def is_firm_owner(self): return self.role == self.FIRM_OWNER
    def is_lawyer(self):     return self.role == self.LAWYER
    def is_client(self):     return self.role == self.CLIENT
    def can_manage_users(self):
        return self.role in [self.SUPER_ADMIN, self.FIRM_OWNER]
    # ... etc.

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
    
    #for soolft delet
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # optional for timestamps
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Firm'
        verbose_name_plural = 'Firms'
    
    def __str__(self):
        return self.name
    
    def can_create_case(self):
        """Check if firm can create new cases based on plan limits."""
        #to be enforeced later
        #if self.subscription_status == self.ACTIVE:
            # return True
        if self.subscription_status == self.ACTIVE:
            return True
        
        # Free tier: check case limit
        from case_management.models import Case
        active_cases = Case.objects.filter(
            firm=self,
            status__in=['new', 'active', 'on_hold']
        ).count()
        
        return active_cases < self.max_active_cases
    
    # def can_add_user(self):
    #     """Check if firm can add new users based on plan limits."""
    #     if self.subscription_status == self.ACTIVE:
    #         return self.users.count() < self.max_users
        
    #     # Free tier: max 1 user
    #     return self.users.count() < 1
    
    def can_add_user(self):
        """Check if firm can add new users based on plan limits."""
        # Count only active users (exclude deactivated)
        current_active = self.users.filter(is_active=True).count()
        
        # Use max_users for all statuses (free tier can have higher if you upgrade plan)
        return current_active < self.max_users
    
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