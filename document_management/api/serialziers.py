# documents/serializers.py

from rest_framework import serializers
# from pytz import timezone
from django.utils import timezone
from document_management.models import Document, DocumentAccess


class ReadDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    case_id = serializers.IntegerField(source="case.id", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "case_id",
            "file_name",
            "file_size",
            "file_type",
            "mime_type",
            "category",
            "description",
            "version",
            "is_shared",
            "shared_link",
            "shared_until",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = fields



class UploadDocumentSerializer(serializers.Serializer):
    file = serializers.FileField()
    category = serializers.ChoiceField(choices=Document.CATEGORY_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context["request"]
        case = self.context["case"]
        file = validated_data["file"]

        from .storage import S3StorageHandler

        storage = S3StorageHandler()

        # Generate unique S3 key
        import uuid
        s3_key = f"cases/{case.id}/{uuid.uuid4()}_{file.name}"

        storage.upload_file(file, s3_key)

        document = Document.objects.create(
            case=case,
            firm=case.firm,
            uploaded_by=request.user,
            file_name=file.name,
            file_path=s3_key,
            file_size=file.size,
            mime_type=file.content_type,
            category=validated_data.get("category", "other"),
            description=validated_data.get("description", ""),
        )

        return document
    


class DocumentAccessSerializer(serializers.ModelSerializer):
    accessed_by = serializers.StringRelatedField()

    class Meta:
        model = DocumentAccess
        fields = "__all__"


class DocumentShareSerializer(serializers.Serializer):
    shared_until = serializers.DateTimeField(required=False)

    def validate_shared_until(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("shared_until must be in the future.")
        return value


class DocumentRevokeSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)



class DocumentAccessLogSerializer(serializers.ModelSerializer):
    accessed_by = serializers.StringRelatedField()

    class Meta:
        model = DocumentAccess
        fields = [
            "id",
            "document",
            "accessed_by",
            "action",
            "ip_address",
            "user_agent",
            "shared_link_used",
            "notes",
            "accessed_at",
        ]