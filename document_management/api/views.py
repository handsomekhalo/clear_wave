from pytz import timezone
from rest_framework.authtoken.models import Token

# from datetime import timezone
import datetime
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from django.utils import timezone


from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate

from case_management.models import Case
from document_management.api.serialziers import DocumentAccessLogSerializer, DocumentRevokeSerializer, DocumentShareSerializer, ReadDocumentSerializer, UploadDocumentSerializer
from document_management.models import Document, DocumentAccess


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_document_api(request, case_id):
    case = get_object_or_404(Case, id=case_id, firm=request.user.firm)
    serializer = UploadDocumentSerializer(data=request.data, context={"request": request, "case": case})
    serializer.is_valid(raise_exception=True)
    document = serializer.save()

    DocumentAccess.objects.create(
        document=document,
        accessed_by=request.user,
        action="upload",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return Response(ReadDocumentSerializer(document).data, status=201)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def share_document_api(request, document_id):
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)

    serializer = DocumentShareSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    document.generate_share_link()
    if serializer.validated_data.get("shared_until"):
        document.shared_until = serializer.validated_data["shared_until"]
        document.shared_by = request.user
        document.save()

    # Log access
    DocumentAccess.objects.create(
        document=document,
        accessed_by=request.user,
        action="share",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        notes=f"Shared until {document.shared_until}" if document.shared_until else ""
    )

    return Response({
        "message": "Document shared successfully.",
        "shared_link": document.shared_link,
        "shared_until": document.shared_until
    })




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def revoke_document_api(request, document_id):
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)

    serializer = DocumentRevokeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    reason = serializer.validated_data.get("reason", "")

    document.revoke_share_link()

    DocumentAccess.objects.create(
        document=document,
        accessed_by=request.user,
        action="revoke",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        notes=reason
    )

    return Response({"message": "Document sharing revoked successfully."})



@api_view(["GET"])
def access_document_api(request, shared_link):
    document = get_object_or_404(Document, shared_link=shared_link, is_shared=True)

    # Optional: check expiry
    if document.shared_until and document.shared_until < timezone.now():
        return Response({"error": "This link has expired."}, status=403)

    # Log anonymous access if not authenticated
    user = request.user if request.user.is_authenticated else None
    DocumentAccess.objects.create(
        document=document,
        accessed_by=user,
        action="view",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        shared_link_used=True
    )

    presigned_url = document.get_presigned_url(expires_in=3600)
    return Response({"url": presigned_url, "file_name": document.file_name})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_access_logs_api(request, document_id):
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)

    logs = document.access_logs.all()
    serializer = DocumentAccessLogSerializer(logs, many=True)
    return Response(serializer.data)