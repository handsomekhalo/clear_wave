from rest_framework import serializers
from case_management.models import Case
from client_management.models import ClientMessage
from document_management.models import Document
from system_management.models import User


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