from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from system_management.models import User
from case_management.models import Case
import secrets
import hashlib

class MagicLink(models.Model):
    """
    Passwordless authentication for clients.
    Token sent via email, valid for 1 hour.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'client'}
    )
    # token_hash = models.CharField(max_length=64, unique=True)
    token_hash = models.CharField(max_length=64, unique=True)

    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"MagicLink for {self.user.email}"
    
    def is_valid(self):
        """Check if link is still valid (not expired, not used)."""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """Mark link as used (one-time use)."""
        self.is_used = True
        self.save(update_fields=['is_used'])
    @classmethod
    def generate_for_user(cls, user):
        # Delete all previous links for this user
        cls.objects.filter(user=user).delete()
        
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = timezone.now() + timedelta(hours=1)
        
        cls.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at
        )
        return raw_token
    # @classmethod
    # def generate_for_user(cls, user):
    #     """Generate new magic link for user."""
    #     raw_token = secrets.token_urlsafe(32)
    #     token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    #     expires_at = timezone.now() + timedelta(hours=1)
        
    #     cls.objects.create(
    #     user=user,
    #     token_hash=token_hash,
    #     expires_at=expires_at
    # )

    #     return raw_token  # return raw token to email
    


class ClientMessage(models.Model):
    """
    Messages between client and lawyer.
    Bidirectional: client → lawyer, lawyer → client.
    """
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.email} → {self.recipient.email} ({self.case.title})"