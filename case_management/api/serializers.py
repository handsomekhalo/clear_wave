# case_management/serializers.py

from rest_framework import serializers
# from pytz import timezone
from django.utils import timezone


from case_management.models import Case, CaseType, Note




# system_management/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "password"
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.role = User.CLIENT
        user.firm = self.context["request"].user.firm
        user.set_password(password)
        user.save()
        return user
    
# class CreateCaseSerializer(serializers.ModelSerializer):
class CreateCaseSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='client'),
        required=True
    )

    class Meta:
        model = Case
        fields = [
            "title",
            "description",
            "client",          # ← PK of client
            "matter_type",
        ]

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

            # Generate reference BEFORE creating case
        firm = self.context["request"].user.firm
        year = timezone.now().year
        firm_prefix = firm.name[:5].upper().replace(" ", "")
        seq = Case.objects.filter(firm=firm).count() + 1
        reference_number = f"{year}-{firm_prefix}-{seq:04d}"

            # Now create with reference_number included
        case = Case.objects.create(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            client=validated_data['client'],
            matter_type=validated_data['matter_type'],
            firm=firm,
            created_by=self.context["request"].user,
            status=Case.NEW,
            reference_number=reference_number  # <-- Include it here
        )

        # case = Case.objects.create(
        #     title=validated_data['title'],
        #     description=validated_data.get('description', ''),
        #     client=validated_data['client'],
        #     matter_type=validated_data['matter_type'],
        #     firm=self.context["request"].user.firm,
        #     created_by=self.context["request"].user,
        #     status=Case.NEW
        # )

        # # Generate reference number
        # year = timezone.now().year
        # firm_prefix = case.firm.name[:5].upper().replace(" ", "")
        # seq = Case.objects.filter(firm=case.firm).count()
        # case.reference_number = f"{year}-{firm_prefix}-{seq:04d}"
        # case.save(update_fields=['reference_number'])

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
        
    def get_assigned_lawyer(self, obj):
        if not obj.assigned_lawyer:
            return None
        return {
            "id": obj.assigned_lawyer.id,
            "email": obj.assigned_lawyer.email,
            "first_name": obj.assigned_lawyer.first_name,
            "last_name": obj.assigned_lawyer.last_name,
        }


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
            "external_case_number",  # ← add this so lawyers can fill it later

        ]

    def validate_matter_type(self, value):
        request = self.context["request"]
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
    days_until_deadline = serializers.ReadOnlyField()
    reference_number = serializers.CharField(read_only=True)
    external_case_number = serializers.CharField(read_only=True)


    class Meta:
        model = Case
        fields = [
            'id',
            'reference_number',
            'external_case_number',
            'title',
            'client_name',
            'assigned_lawyer_name',
            'status',
            'priority',
            'days_until_deadline',
            'created_at',
            'updated_at',
            'closed_at',
        ]

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}" if obj.client else None

    def get_assigned_lawyer_name(self, obj):
        return f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}" if obj.assigned_lawyer else None


class CreateMatterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ["name"]

    def create(self, validated_data):
        firm = self.context["request"].user.firm
        return CaseType.objects.create(firm=firm, **validated_data)