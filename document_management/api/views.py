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
from document_management.api.serialziers import DocumentAccessLogSerializer, DocumentRevokeSerializer, DocumentShareSerializer, GetAllDocumentsForCaseSerializer, ReadDocumentSerializer, UploadDocumentSerializer
from document_management.models import Document, DocumentAccess
from system_management.permissions import CanAccessCaseDocuments
from system_management.storage_util import get_presigned_url




@api_view(["POST"])
@permission_classes([IsAuthenticated, CanAccessCaseDocuments])
def upload_document_api(request, case_id):
    case = get_object_or_404(Case, id=case_id, firm=request.user.firm)

     # Permission: owner always, lawyer if assigned, assistant if assigned
    # This triggers has_object_permission
    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, case):
        return Response({"error": "Access denied."}, status=403)
    
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_documents_api(request, case_id):
    case = get_object_or_404(Case, id=case_id, firm=request.user.firm)

    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, case):
        return Response({"error": "Access denied."}, status=403)

    documents = Document.objects.filter(case=case, is_deleted=False)
    category = request.query_params.get("category")
    file_type = request.query_params.get("file_type")
    if category:
        documents = documents.filter(category=category)
    if file_type:
        documents = documents.filter(file_type=file_type)
    

    return Response(GetAllDocumentsForCaseSerializer(documents, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_document_api(request, document_id):
    """
    Returns a presigned URL to view/download a specific document.
    Only accessible by users within the same firm.
    """
    document = get_object_or_404(
        Document,
        id=document_id,
        firm=request.user.firm,
        is_deleted=False
    )

    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, document.case):
        return Response({"error": "Access denied."}, status=403)

    presigned_url = get_presigned_url(document.file_path, expires_in=3600)
    

    if not presigned_url:
        return Response({"error": "Could not generate document URL."}, status=500)

    DocumentAccess.objects.create(
        document=document,
        accessed_by=request.user,
        action="view",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return Response({
        "url": presigned_url,
        "file_name": document.file_name,
        "file_type": document.file_type,
        "mime_type": document.mime_type,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def share_document_api(request, document_id):
    document = get_object_or_404(Document, id=document_id, firm=request.user.firm, is_deleted=False)

    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, document.case):
        return Response({"error": "Access denied."}, status=403)

    # Only lawyers and above can share
    if request.user.role not in ['super_admin', 'firm_owner', 'lawyer']:
        return Response({"error": "Only lawyers can share documents."}, status=403)

    serializer = DocumentShareSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    expires_at = serializer.validated_data.get("shared_until")
    document.generate_share_link(shared_by=request.user, expires_at=expires_at)

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
    document = get_object_or_404(Document, id=document_id, firm=request.user.firm, is_deleted=False)

    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, document.case):
        return Response({"error": "Access denied."}, status=403)

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
@permission_classes([AllowAny])
def access_document_api(request, shared_link):
    """Public endpoint — access document via share link."""

    document = get_object_or_404(Document, shared_link=shared_link, is_shared=True, is_deleted=False)
    if document.shared_until and document.shared_until < timezone.now():
        return Response({"error": "This link has expired."}, status=403)

    user = request.user if request.user.is_authenticated else None

    presigned_url = get_presigned_url(document.file_path, expires_in=3600)

    if not presigned_url:
        return Response({"error": "Could not generate document URL."}, status=500)

    DocumentAccess.objects.create(
        document=document,
        accessed_by=user,
        action="view",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        shared_link_used=True
    )

    return Response({"url": presigned_url, "file_name": document.file_name})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_access_logs_api(request, document_id):
    document = get_object_or_404(Document, id=document_id, firm=request.user.firm)
    
    permission = CanAccessCaseDocuments()
    if not permission.has_object_permission(request, None, document.case):
        return Response({"error": "Access denied."}, status=403)

    # Clients cannot view audit logs
    if request.user.role == 'client':
        return Response({"error": "Access denied."}, status=403)

    logs = document.access_logs.all()
    logs = document.access_logs.order_by("-accessed_at")
    serializer = DocumentAccessLogSerializer(logs, many=True)
    return Response(serializer.data)