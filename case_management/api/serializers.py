# case_management/serializers.py

from rest_framework import serializers
# from pytz import timezone
from django.utils import timezone


from case_management.models import Case, CaseType, Note, TimeLog




# system_management/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


import secrets

class CreateClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):

        request = self.context["request"]

        # 🔐 Auto-generate password
        password = secrets.token_urlsafe(8)

        user = User(**validated_data)

        user.role = User.CLIENT
        user.firm = request.user.firm

        user.set_password(password)

        user.save()

        # Attach password so API can return it
        user.generated_password = password

        return user


class CreateCaseSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='client'),
        required=False  # 🔥 no longer mandatory
    )

    client_email = serializers.EmailField(required=False)

    class Meta:
        model = Case
        fields = [
            "title",
            "description",
            "client",
            "client_email",   # 🔥 NEW
            "matter_type",
        ]

    def validate(self, data):
        """
        Ensure at least one of client or client_email is provided
        """
        if not data.get("client") and not data.get("client_email"):
            raise serializers.ValidationError(
                "Either client or client_email is required."
            )
        return data

    def validate_client(self, value):
        if value.firm != self.context["request"].user.firm:
            raise serializers.ValidationError("Client must belong to your firm.")
        return value

    def validate_matter_type(self, value):
        user = self.context["request"].user
        if value.firm != user.firm:
            raise serializers.ValidationError("Invalid matter type.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        firm = request.user.firm

        client = validated_data.get("client")
        client_email = validated_data.get("client_email")

        # 🔥 HANDLE CLIENT CREATION HERE (not in view)
        if not client:
            client, created = User.objects.get_or_create(
                email=client_email,
                defaults={
                    "role": "client",
                    "is_active": True,
                    "firm": firm
                }
            )

        # 🔢 Reference generation
        year = timezone.now().year
        firm_prefix = firm.name[:5].upper().replace(" ", "")
        seq = Case.objects.filter(firm=firm).count() + 1
        reference_number = f"{year}-{firm_prefix}-{seq:04d}"

        case = Case.objects.create(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            client=client,  # 🔥 ALWAYS resolved
            matter_type=validated_data['matter_type'],
            firm=firm,
            created_by=request.user,
            status=Case.NEW,
            reference_number=reference_number
        )

        return case
class MatterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ["id", "name"]


class GetCaseDetailSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    assigned_lawyer = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    days_until_deadline = serializers.ReadOnlyField()
    reference_number = serializers.CharField(read_only=True)
    external_case_number = serializers.CharField(read_only=True)
    # matter_type = serializers.CharField(source='matter_type.name', read_only=True)  # Add this
    matter_type = serializers.SerializerMethodField()


    class Meta:
        model = Case
        fields = [
            "id",
             'reference_number',
            'external_case_number',
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "deadline",
            "days_until_deadline",
            "client",
            "assigned_lawyer",
            "created_at",
            "updated_at",
            "matter_type",
            "billing_status",
        ]

    # def get_client(self, obj):
    #     return {
    #         "id": obj.client.id,
    #         "email": obj.client.email,
    #         "first_name": obj.client.first_name,
    #         "last_name": obj.client.last_name,
    #     }
    def get_client(self, obj):
        if not obj.client:
            return None  # or {} if you prefer empty dict
        
        return {
            "id": obj.client.id,
            "email": obj.client.email,
            "first_name": obj.client.first_name,
            "last_name": obj.client.last_name,
        }
    def get_matter_type(self, obj):
        if obj.matter_type:
            return {
                "id": obj.matter_type.id,
                "name": obj.matter_type.name
        }
        return None
    
    def get_assigned_lawyer(self, obj):
        if obj.assigned_lawyer:
            return {
                "id": obj.assigned_lawyer.id,
                "name": f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}",
                "role": obj.assigned_lawyer.role,
            }
        return None
    
class AssignToCaseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context["request"]
        case = self.context["case"]
        user_id = data["user_id"]

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Tenant isolation
        if target_user.firm != request.user.firm:
            raise serializers.ValidationError("User does not belong to your firm.")

        data["target_user"] = target_user
        return data


class UpdateCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "title",
            "description",
            "priority",
            "deadline",
            "matter_type",
            'status',
            "external_case_number",  # ← add this so lawyers can fill it later

        ]

        def validate_matter_type(self, value):
            request = self.context["request"]

            if value is None:
                return value  # ✅ allow null safely

            if value.firm != request.user.firm:
                raise serializers.ValidationError("Invalid matter type.")

            return value


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Case.STATUS_CHOICES)

class AddNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["content", "is_pinned"]


class GetCaseListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    assigned_lawyer_name = serializers.SerializerMethodField()
    matter_type_name = serializers.CharField(source='matter_type.name', read_only=True)  # Add this
    days_until_deadline = serializers.ReadOnlyField()
    
    class Meta:
        model = Case
        fields = [
            'id',
            'reference_number',
            'external_case_number',
            'title',
            'client_name',
            'assigned_lawyer_name',
            'matter_type_name',  # Add this
            'status',
            'priority',
            'deadline',  # Don't redefine, let ModelSerializer handle it
            'days_until_deadline',
            'created_at',
            'updated_at',
            'closed_at',
        ]
    
    def get_client_name(self, obj):
        if not obj.client:
            return None
        return f"{obj.client.first_name} {obj.client.last_name}".strip() or obj.client.email
    
    def get_assigned_lawyer_name(self, obj):
        if not obj.assigned_lawyer:
            return "Unassigned"
        return f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}".strip() or obj.assigned_lawyer.email

class CreateMatterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ["name"]

    def create(self, validated_data):
        firm = self.context["request"].user.firm
        return CaseType.objects.create(firm=firm, **validated_data)
    

class GetAllClientsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",  # Easier for dropdowns
            "email",
            "phone",
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class GetNotesSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.email",
        read_only=True
    )

    class Meta:
        model = Note
        fields = [
            "id",
            "content",
            "is_pinned",
            "created_at",
            "updated_at",
            "created_by_name"
        ]


class CreateTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = [
            'date',
            'duration',
            'activity_type',
            'description',
            'is_billable',
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        if value > 24:
            raise serializers.ValidationError("Duration cannot exceed 24 hours.")
        return value

    def create(self, validated_data):
        return TimeLog.objects.create(
            case=self.context['case'],
            firm=self.context['request'].user.firm,
            logged_by=self.context['request'].user,
            **validated_data
        )


class GetTimeLogSerializer(serializers.ModelSerializer):
    logged_by = serializers.SerializerMethodField()
    activity_display = serializers.CharField(
        source='get_activity_type_display',
        read_only=True
    )
    duration = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    class Meta:
        model = TimeLog
        fields = [
            'id',
            'date',
            'duration',
            'activity_type',
            'activity_display',
            'description',
            'is_billable',
            'logged_by',
            'created_at',
        ]

    def get_logged_by(self, obj):
        return {
            'id': obj.logged_by.id,
            'name': f"{obj.logged_by.first_name} {obj.logged_by.last_name}".strip(),
            'role': obj.logged_by.role,
        }


class UpdateTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = [
            'date',
            'duration',
            'activity_type',
            'description',
            'is_billable',
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        if value > 24:
            raise serializers.ValidationError("Duration cannot exceed 24 hours.")
        return value