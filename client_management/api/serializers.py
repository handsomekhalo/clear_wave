from forms_engine_management.models import CaseFormAssignment
from rest_framework import serializers
from case_management.models import Case
from client_management.models import ClientMessage
from document_management.models import Document
from system_management.models import User
from system_management.storage_util import upload_document_to_backblaze


class ClientCaseSerializer(serializers.ModelSerializer):
    """
    Limited case view for clients.
    Only shows fields clients should see.
    """
    client_name = serializers.SerializerMethodField()
    lawyer_name = serializers.SerializerMethodField()
    matter_type_name = serializers.CharField(source='matter_type.name', read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id',
            'reference_number',
            'title',
            'description',
            'status',
            'priority',
            'deadline',
            'matter_type_name',
            'client_name',
            'lawyer_name',
            'created_at',
            'updated_at',
        ]
        # read_only_fields = '__all__'
        read_only_fields = fields
    
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}".strip() or obj.client.email
    
    def get_lawyer_name(self, obj):
        if obj.assigned_lawyer:
            return f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}".strip() or obj.assigned_lawyer.email
        return None


class ClientMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for client-lawyer messages.
    """
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    
    class Meta:
        model = ClientMessage
        fields = [
            'id',
            'case',
            'sender',
            'sender_name',
            'sender_role',
            'recipient',
            'recipient_name',
            'content',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'sender_name', 'recipient_name', 'sender_role']
    
    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email
    
    def get_recipient_name(self, obj):
        return f"{obj.recipient.first_name} {obj.recipient.last_name}".strip() or obj.recipient.email
    
    def validate_case(self, value):
        """Ensure user has access to this case."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        # Client can only message about their own case
        if request.user.role == 'client':
            if value.client != request.user:
                raise serializers.ValidationError("You can only message about your own case.")
        
        # Lawyer can only message about their assigned cases
        elif request.user.role == 'lawyer':
            if value.assigned_lawyer != request.user and value.firm != request.user.firm:
                raise serializers.ValidationError("You can only message about your assigned cases.")
        
        return value


class MagicLinkRequestSerializer(serializers.Serializer):
    """
    Request magic link for email.
    """
    email = serializers.EmailField(required=True)


class MagicLinkLoginSerializer(serializers.Serializer):
    """
    Login using magic link token.
    """
    token = serializers.CharField(required=True)


from rest_framework import serializers
class ClientDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "file_name",
            "description",
            "category",
            "file_type",
            "file_size",
            "uploaded_at",
            "date_updated",
            "version",
            "file_url",
        ]

    def get_file_url(self, obj):
        try:
            return obj.get_presigned_url()
        except Exception:
            return None
# class ClientDocumentSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Document
#         fields = [
#             "id",
#             "file_name",
#             "description",
#             "category",
#             "file_type",
#             "file_size",
#             "uploaded_at",
#             "date_updated",
#             "version",
#             "file_url",
#         ]

#     def get_file_url(self, obj):
#         try:
#             return obj.get_presigned_url()
#         except Exception:
#             return None


# In client_management/api/serializers.py

class ClientFormAssignmentSerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()
    case_reference = serializers.CharField(
        source='case.reference_number', read_only=True
    )
    case_title = serializers.CharField(
        source='case.title', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = CaseFormAssignment
        fields = [
            'id',
            'template',
            'status',
            'status_display',
            'due_date',
            'is_overdue',
            'case_reference',
            'case_title',
            'review_notes',
            'assigned_at',
        ]

    def get_template(self, obj):
        return {
            'id': obj.template.id,
            'name': obj.template.name,
        }

class ClientUploadDocumentSerializer(serializers.Serializer):
    file = serializers.FileField()
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context["request"]
        case = self.context["case"]
        file = validated_data["file"]

        try:
            file_url, checksum, file_size, key = upload_document_to_backblaze(
                file=file,
                case_id=case.id,
                filename=file.name,
            )
        except Exception as e:
            print("CLIENT UPLOAD ERROR:", str(e))
            raise

        if not file_url:
            raise serializers.ValidationError("File upload failed.")

        document = Document.objects.create(
            case=case,
            firm=case.firm,
            uploaded_by=request.user,
            file_name=file.name,
            file_path=key,
            file_size=file_size or file.size,
            file_type=file.name.split(".")[-1].lower(),
            mime_type=file.content_type or "application/octet-stream",
            checksum=checksum or "",
            category="other",  # default for client uploads
            description=validated_data.get("description", ""),
        )

        return document