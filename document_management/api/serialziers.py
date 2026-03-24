# documents/serializers.py

import mimetypes
import uuid
from rest_framework import serializers
# from pytz import timezone
from django.utils import timezone
from document_management.models import Document, DocumentAccess
from system_management.storage_util import upload_document_to_backblaze


class ReadDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    case_id = serializers.IntegerField(source="case.id", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "case_id", "file_name", "file_size", "file_type",
            "mime_type", "category", "description", "version",
            "is_shared", "shared_link", "shared_until",
            "uploaded_by", "uploaded_at",
        ]
        read_only_fields = fields


class GetAllDocumentsForCaseSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    case_id = serializers.IntegerField(source="case.id", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "case_id", "file_name", "file_size", "file_type",
            "mime_type", "category", "description", "version",
            "is_shared", "shared_link", "shared_until",
            "uploaded_by", "uploaded_at",
        ]
        read_only_fields = fields



class UploadDocumentSerializer(serializers.Serializer):
    file = serializers.FileField()
    category = serializers.ChoiceField(choices=Document.CATEGORY_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context["request"]
        case = self.context["case"]
        file = validated_data["file"]

        title = validated_data.get("title") or file.name

        file_url, checksum, file_size, key = upload_document_to_backblaze(
            file=file,
            case_id=case.id,
            filename=file.name,
        )

        if not file_url:
            raise serializers.ValidationError("File upload failed.")

        ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else 'other'
        file_type = ext if ext in dict(Document.FILE_TYPE_CHOICES) else 'other'

        document = Document.objects.create(
            case=case,
            firm=case.firm,
            uploaded_by=request.user,
            file_name=title,
            file_path=key,  # ✅ FIXED (THIS IS THE KEY USED FOR PRESIGNED URL)
            file_size=file_size or file.size,
            file_type=file_type,
            # mime_type=file.content_type,
            mime_type = file.content_type or mimetypes.guess_type(file.name)[0] or "application/octet-stream",
            checksum=checksum or "",
            category=validated_data.get("category", "other"),
            description=validated_data.get("description", ""),
        )

        return document
# class UploadDocumentSerializer(serializers.Serializer):
#     file = serializers.FileField()
#     category = serializers.ChoiceField(choices=Document.CATEGORY_CHOICES)
#     description = serializers.CharField(required=False, allow_blank=True)
#     title = serializers.CharField(required=False, allow_blank=True)

#     def create(self, validated_data):
#         request = self.context["request"]
#         case = self.context["case"]
#         file = validated_data["file"]

#         # Use title if provided, else fallback to file name
#         title = validated_data.get("title") or file.name

#         s3_key = f"cases/{case.id}/{uuid.uuid4()}_{file.name}"

#         # file_url, checksum, file_size = upload_document_to_backblaze(
#         #     file=file,
#         #     case_id=case.id,
#         #     filename=file.name,
#         # )
#         file_url, checksum, file_size = upload_document_to_backblaze(
#                     file=file,
#                     case_id=case.id,
#                     filename=file.name,
#                 )

#         if not file_url:
#             raise serializers.ValidationError("File upload failed. Please try again.")

#         ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else 'other'
#         file_type = ext if ext in dict(Document.FILE_TYPE_CHOICES) else 'other'

#         document = Document.objects.create(
#             case=case,
#             firm=case.firm,
#             uploaded_by=request.user,
#             file_name=title,  # ✅ USE TITLE HERE
#             file_path=s3_key,
#             file_size=file_size or file.size,
#             file_type=file_type,
#             mime_type=file.content_type,
#             checksum=checksum or "",
#             category=validated_data.get("category", "other"),
#             description=validated_data.get("description", ""),
#         )

#         return document
# class UploadDocumentSerializer(serializers.Serializer):
#     file = serializers.FileField()
#     category = serializers.ChoiceField(choices=Document.CATEGORY_CHOICES)
#     description = serializers.CharField(required=False, allow_blank=True)
#     title = serializers.CharField(required=False, allow_blank=True)


#     def create(self, validated_data):
#         request = self.context["request"]
#         case = self.context["case"]
#         file = validated_data["file"]

#         s3_key = f"cases/{case.id}/{uuid.uuid4()}_{file.name}"

#         file_url, checksum, file_size = upload_document_to_backblaze(
#             file=file,
#             case_id=case.id,
#             filename=file.name,
#         )

#         if not file_url:
#             raise serializers.ValidationError("File upload failed. Please try again.")

#         # Detect file type from extension
#         ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else 'other'
#         file_type = ext if ext in dict(Document.FILE_TYPE_CHOICES) else 'other'

#         document = Document.objects.create(
#             case=case,
#             firm=case.firm,
#             uploaded_by=request.user,
#             file_name=file.name,
#             file_path=s3_key,
#             file_size=file_size or file.size,
#             file_type=file_type,
#             mime_type=file.content_type,
#             checksum=checksum or "",
#             category=validated_data.get("category", "other"),
#             description=validated_data.get("description", ""),
#         )

#         return document

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