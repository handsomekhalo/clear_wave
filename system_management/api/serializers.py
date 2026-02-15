# system_management/serializers.py

from case_management.models import Case
from rest_framework import serializers
from system_management.models import Firm, User, AuditLog

from django.contrib.auth.password_validation import validate_password



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
            'user_count',
            'case_count',
            'created_at',
            'updated_at',
        ]
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


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Includes password field.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone',
            'role',
            'firm',
        ]
    
    def validate(self, attrs):
        """Check passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_role(self, value):
        """Validate role assignment."""
        request = self.context.get('request')
        if request and request.user:
            if value == 'super_admin' and request.user.role != 'super_admin':
                raise serializers.ValidationError(
                    "Only super admins can create super admin users."
                )
        return value
    
    def validate_firm(self, value):
        """Validate firm assignment."""
        request = self.context.get('request')
        if request and request.user:
            if request.user.role == 'super_admin':
                return value
            
            if request.user.role == 'firm_owner':
                if value != request.user.firm:
                    raise serializers.ValidationError(
                        "You can only add users to your own firm."
                    )
        return value
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


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
        read_only_fields = '__all__'  # Audit logs are never editable


class MyFirmSerializer(serializers.ModelSerializer):
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