# system_management/serializers.py

from case_management.models import Case
from rest_framework import serializers
from system_management.general_func_classes import BaseFormSerializer
from system_management.models import Firm, User, AuditLog

from django.contrib.auth.password_validation import validate_password

from system_management.views import generate_password


# system_management/serializers.py (add this)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for user management within a firm.
    """
    firm_name = serializers.CharField(source='firm.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
            'firm_name',
            'is_active',
            'last_login',
            'created_at',
        ]
        read_only_fields = ['id', 'last_login', 'created_at', 'firm_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_role(self, value):
        """
        Ensure role is appropriate.
        Firm owners can't create super admins.
        """
        request = self.context.get('request')
        if request and request.user:
            # Only super admin can create super admin
            if value == 'super_admin' and request.user.role != 'super_admin':
                raise serializers.ValidationError(
                    "Only super admins can create super admin users."
                )
        return value
    
    def validate_firm(self, value):
        """
        Ensure firm owner can only add users to their own firm.
        """
        request = self.context.get('request')
        if request and request.user:
            # Super admin can add users to any firm
            if request.user.role == 'super_admin':
                return value
            
            # Firm owner can only add to their own firm
            if request.user.role == 'firm_owner':
                if value != request.user.firm:
                    raise serializers.ValidationError(
                        "You can only add users to your own firm."
                    )
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)



class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()
    firm = serializers.DictField(required=False, allow_null=True)

    def to_representation(self, instance):
        """
        instance must be:
        {
            "token": str,
            "user": User instance
        }
        """
        user = instance.get("user")

        data = {
            "token": instance.get("token"),
            "user": UserSerializer(user).data,
            "firm": None
        }

        if user and user.firm:
            data["firm"] = {
                "id": user.firm.id,
                "name": user.firm.name,
                "subscription_status": user.firm.subscription_status,
                "subscription_plan": user.firm.subscription_plan,
                "can_create_case": user.firm.can_create_case(),
                "can_add_user": user.firm.can_add_user(),
            }

        return data


class CreateFirmSerializer(serializers.ModelSerializer):
    """
    Serializer for Firm model.
    Used by super admin to create/manage firms.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    user_count = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Firm
        fields = [
        'id',
        'name',
        'owner',
        'owner_email',
        'subscription_status',
        'subscription_plan',
        'subscription_end_date',
        'last_payment_date',
        'max_users',
        'max_active_cases',
        'storage_limit_gb',
        'onboarding_step',
        'is_onboarded',
        'user_count',
        'case_count',
        'created_at',
        'updated_at',
    ]

    read_only_fields = [
        'id',
        'created_at',
        'updated_at',
        'owner_email',
        'user_count',
        'case_count'
    ]
      
    def get_user_count(self, obj):
        """Get number of users in firm."""
        return obj.users.count()
    
    def get_case_count(self, obj):
        """Get number of active cases in firm."""
        return Case.objects.filter(
            firm=obj,
            status__in=['new', 'active', 'on_hold']
        ).count()


class RegisterFirmByOwnerSerializer(serializers.ModelSerializer):
    """
    Serializer for Firm model.
    Used by super admin to create/manage firms.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    user_count = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Firm
        fields = [
            'id',
            'name',
            'owner',
            'owner_email',
            'subscription_status',
            'subscription_plan',
            'subscription_end_date',
            'last_payment_date',
            'max_users',
            'max_active_cases',
            'storage_limit_gb',
            'user_count',
            'case_count',
            'created_at',
            'updated_at',
            
        ]
        extra_kwargs = {
            "subscription_status": {"required": False},
            "subscription_end_date": {"required": False},
            "last_payment_date": {"required": False},
            "max_users": {"required": False},
            "max_active_cases": {"required": False},
            "storage_limit_gb": {"required": False},
        }
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_email', 'user_count', 'case_count']
    
    def get_user_count(self, obj):
        """Get number of users in firm."""
        return obj.users.count()
    
    def get_case_count(self, obj):
        """Get number of active cases in firm."""
        from case_management.models import Case
        return Case.objects.filter(
            firm=obj,
            status__in=['new', 'active', 'on_hold']
        ).count()


class FirmListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing firms.
    Used in list views where we don't need all details.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Firm
        fields = [
            'id',
            'name',
            'owner_email',
            'subscription_status',
            'subscription_plan',
            'user_count',
            'created_at',
        ]
    
    def get_user_count(self, obj):
        return obj.users.count()




class GetFirmDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer for super admin when retrieving a firm.
    Includes computed fields and owner info.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    user_count  = serializers.SerializerMethodField()
    case_count  = serializers.SerializerMethodField()

    class Meta:
        model = Firm
        fields = [
            'id',
            'name',
            'owner',
            'owner_email',
            'subscription_status',
            'subscription_plan',
            'subscription_end_date',
            'last_payment_date',
            'max_users',
            'max_active_cases',
            'storage_limit_gb',
            'user_count',
            'case_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'owner_email', 'user_count', 'case_count',
        ]

    def get_user_count(self, obj):
        return obj.users.count()

    def get_case_count(self, obj):
        return Case.objects.filter(
            firm=obj,
            status__in=['new', 'active', 'on_hold']
        ).count()




class FirmUpdateDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer used exclusively for partial updates by super admin.
    Only includes fields that are allowed to be changed.
    Excludes computed / read-only stats.
    """
    class Meta:
        model = Firm
        fields = [
            'name',
            'subscription_status',
            'subscription_plan',
            'subscription_end_date',
            'last_payment_date',
            'max_users',
            'max_active_cases',
            'storage_limit_gb',
            # Add 'owner' here later if you want to allow reassigning owner
        ]
        # No read_only_fields here — all listed fields are potentially writable

# serializers.py

class FirmUserListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing users in a firm (or all for super admin).
    Used in firm_user_list_api.
    Shows essential info without sensitive data.
    """
    firm_name = serializers.CharField(source='firm.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
            'firm_name',
            'is_active',
            'created_at',
            'last_login',
        ]
        # read_only_fields = '__all__'  # everything read-only (tuple: ('__all__',))
        read_only_fields = ('__all__',)  # tuple fixes the TypeError



class GetFirmUserListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing users (firm owner or super admin).
    Shows essential info, no sensitive write fields.
    """
    firm_name = serializers.CharField(source='firm.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
            'firm_name',
            'is_active',
            'last_login',
            'created_at',
        ]
        read_only_fields = fields  # everything read-only here



class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users in a firm.
    Handles firm auto-assignment + role restrictions.
    """
    password = serializers.CharField(write_only=True, required=False)  # Optional now
    send_credentials_email = serializers.BooleanField(default=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'send_credentials_email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }
    
    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Request context missing.")

        if value == 'super_admin' and request.user.role != 'super_admin':
            raise serializers.ValidationError(
                "Only super admins can create super admin users."
            )

        if value == 'firm_owner' and request.user.role != 'super_admin':
            raise serializers.ValidationError(
                "Only super admins can create firm owners."
            )

        return value

    def validate_firm(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Request context missing.")

        if request.user.role == 'firm_owner':
            if value is not None and value != request.user.firm:
                raise serializers.ValidationError(
                    "You can only add users to your own firm."
                )
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data):
        send_email = validated_data.pop('send_credentials_email', True)
        
        # Auto-assign firm for firm owners
        request = self.context['request']
        if request.user.role == 'firm_owner':
            validated_data['firm'] = request.user.firm
        
        # Generate password if not provided
        if 'password' in validated_data and validated_data['password']:
            password = validated_data.pop('password')
        else:
            password = generate_password(length=12)
        
        # Create user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        user._plaintext_password = password 
        
        # Send email with credentials
        # if send_email and user.role in ['firm_owner', 'lawyer', 'assistant']:
            # from django.core.mail import EmailMessage
            # from django.template.loader import get_template
            # from django.conf import settings
            
            # context = {
            #     'user': user,
            #     'email': user.email,
            #     'password': password,
            #     'login_url': f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else 'https://clearwave.app/login',
            #     'firm_name': user.firm.name if user.firm else 'ClearWave',
            # }
            
            # try:
            #     email_html = get_template('emails/welcome_credentials.html').render(context)
                
            #     email_msg = EmailMessage(
            #         subject='Welcome to ClearWave - Your Account Credentials',
            #         body=email_html,
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         to=[user.email],
            #     )
            #     email_msg.content_subtype = 'html'
            #     email_msg.send(fail_silently=True)
            # except Exception as e:
            #     # Log error but don't fail user creation
            #     print(f"Failed to send welcome email: {e}")
        
        return user
    



class GetFirmUserDetailSerializer(serializers.ModelSerializer):
    """
    Full read-only serializer for viewing a single user detail.
    Used in GET /firm/users/<pk>/
    """
    firm_name = serializers.CharField(source='firm.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
            'firm_name',
            'is_active',
            'last_login',
            'created_at',
        ]
        read_only_fields = fields  # everything read-only
    
class UpdateFirmUserSerializer(serializers.ModelSerializer):
    """
    Serializer for partial updates of a user.
    Firm owners / super admins can update most fields (except sensitive ones).
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'role',          # super admin only in most cases
            'is_active',
            # 'email' usually not changeable — add if needed with extra validation
            # 'firm' — usually not changeable after creation
        ]
        extra_kwargs = {
            'role': {'required': False},
            'is_active': {'required': False},
        }

    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            return value

        # Only super admin can change to super_admin or firm_owner
        if value in ['super_admin', 'firm_owner'] and request.user.role != 'super_admin':
            raise serializers.ValidationError(
                "Only super admins can assign super_admin or firm_owner roles."
            )
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    Cannot change firm or role (use separate endpoint for that).
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'is_active',
            'role'
        ]


class ChangeRoleSerializer(serializers.Serializer):
    """
    Serializer for changing a user's role.
    Separate from update to make it explicit.
    """
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    def validate_role(self, value):
        """Only firm owner or super admin can change roles."""
        request = self.context.get('request')
        user = self.context.get('user')  # User being updated
        
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        # Can't change super admin role unless you're super admin
        if value == 'super_admin' and request.user.role != 'super_admin':
            raise serializers.ValidationError(
                "Only super admins can assign super admin role."
            )
        
        # Can't change your own role
        if user == request.user:
            raise serializers.ValidationError(
                "You cannot change your own role."
            )
        
        return value


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',           # read-only
            'first_name',
            'last_name',
            'phone',
            # 'role'            → NEVER writable here
            # 'firm'            → NEVER
            # 'is_active'       → NEVER
            'created_at',
            'last_login',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'last_login']


class UpdateMyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer EXCLUSIVELY for users to update their OWN profile.
    Only exposes safe, personal fields that any authenticated user should change.
    Sensitive/system fields are excluded entirely.
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            # Add more personal fields later if needed (e.g. 'profile_picture_url')
        ]

    def validate_phone(self, value):
        """
        Optional: basic phone validation (customize as needed).
        """
        if value and not value.strip():
            raise serializers.ValidationError("Phone number cannot be empty if provided.")
        return value.strip() if value else value

# 

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit logs.
    Read-only, used for compliance reporting.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    firm_name = serializers.CharField(source='firm.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'firm',
            'firm_name',
            'user',
            'user_email',
            'action',
            'model_type',
            'model_id',
            'changes',
            'ip_address',
            'user_agent',
            'timestamp',
        ]
        read_only_fields = ('__all__',)  # tuple fixes the TypeError
        # Alternative: read_only_fields = fields  # if you prefer explicit

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)  # <-- Change to True
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return data
    
class ViewMyFirmSerializer(serializers.ModelSerializer):
    """
    Serializer for firm owner to view/update their own firm.
    Limited fields compared to super admin view.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    user_count = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()
    can_add_user = serializers.SerializerMethodField()
    can_create_case = serializers.SerializerMethodField()
    
    class Meta:
        model = Firm
        fields = [
            'id',
            'name',
            'owner_email',
            'subscription_status',
            'subscription_plan',
            'subscription_end_date',
            'max_users',
            'max_active_cases',
            'storage_limit_gb',
            'user_count',
            'case_count',
            'can_add_user',
            'can_create_case',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'owner_email',
            'subscription_status',
            'subscription_plan',
            'subscription_end_date',
            'max_users',
            'max_active_cases',
            'storage_limit_gb',
            'user_count',
            'case_count',
            'can_add_user',
            'can_create_case',
            'created_at',
        ]
    
    def get_user_count(self, obj):
        return obj.users.count()
    
    def get_case_count(self, obj):
        from case_management.models import Case
        return Case.objects.filter(
            firm=obj,
            status__in=['new', 'active', 'on_hold']
        ).count()
    
    def get_can_add_user(self, obj):
        return obj.can_add_user()
    
    def get_can_create_case(self, obj):
        return obj.can_create_case()


class UpdateMyFirmSerializer(serializers.ModelSerializer):
    """
    Serializer EXCLUSIVELY for firm owners to update their own firm settings.
    Only includes fields that are actually allowed to be changed.
    All other fields are excluded or read-only by design.
    """
    class Meta:
        model = Firm
        fields = [
            'name',                     # The only field currently allowed to change
            # Add more writable fields here in the future if you decide to expand
            # e.g. 'phone', 'address_line_1', 'logo_url', etc.
        ]

    def validate_name(self, value):
        """
        Basic validation for firm name (optional but good practice).
        """
        if not value.strip():
            raise serializers.ValidationError("Firm name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Firm name must be at least 3 characters long.")
        return value.strip()


# system_management/serializers.py
class FirmOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = ['name']  # Step 1: just firm name
        
class MatterTypesOnboardingSerializer(serializers.Serializer):
    matter_types = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1
    )

class SendEmailSerializer(BaseFormSerializer):
    """Serializer for sending email"""
    context_data = serializers.DictField(
        allow_empty=True,
        required=False,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The context data field is required.'
        }
    )
    html_tpl_path = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The html_tpl_path field is required.',
            'max_length': 'The html_tpl_path field must be less than 100 characters.'
        }
    )
    subject = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The subject field is required.',
            'max_length': 'The subject field must be less than 100 characters.'
        }
    )

class GetAllRolesSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
# ────────────────────────────────────────────────
# FUTURE / OPTIONAL: Dedicated serializer for single audit log detail view
# Currently commented out → we reuse AuditLogSerializer for both list & detail
# Uncomment and customize when needed (e.g. during case/document integration)
# ────────────────────────────────────────────────

class AuditLogDetailSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for retrieving a SINGLE audit log entry.
    Use this when detail view needs:
    - extra nested objects (e.g. full related Case or Document)
    - pretty-printed or diff-formatted 'changes'
    - more verbose metadata
    - different field ordering or additional computed fields
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    firm_name  = serializers.CharField(source='firm.name', read_only=True)

    # Example future additions (uncomment when relevant):
    # related_case = serializers.SerializerMethodField()
    # change_diff = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'firm',
            'firm_name',
            'user',
            'user_email',
            'action',
            'model_type',
            'model_id',
            'changes',
            'ip_address',
            'user_agent',
            'timestamp',
            # 'related_case',    # example future field
            # 'change_diff',     # example future field
        ]
        read_only_fields = ('__all__',)

    # Example future method fields (uncomment when you add case/document relation)
    # def get_related_case(self, obj):
    #     if obj.model_type == 'case' and 'case_id' in obj.changes:
    #         try:
    #             from case_management.models import Case
    #             case = Case.objects.get(id=obj.changes['case_id'])
    #             return {'id': case.id, 'title': case.title}
    #         except Case.DoesNotExist:
    #             return None
    #     return None

    # def get_change_diff(self, obj):
    #     # Future: return human-readable diff instead of raw dict
    #     return obj.changes  # placeholder