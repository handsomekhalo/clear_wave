import hashlib
from forms_engine_management.models import CaseFormAssignment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from datetime import datetime
from case_management.models import Case
from client_management.api.serializers import ClientCaseSerializer, ClientDocumentSerializer, ClientMessageSerializer, ClientUploadDocumentSerializer, MagicLinkLoginSerializer, MagicLinkRequestSerializer
from client_management.models import ClientMessage, MagicLink
from document_management.api.serializers import ReadDocumentSerializer
from document_management.models import Document, DocumentAccess
from system_management.api.serializers import UserSerializer
from system_management.models import AuditLog, User
from system_management.permissions import MagicLinkThrottle,SimpleRateThrottle
from system_management.permissions import  MagicLinkThrottle

from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes
)
from django.conf import settings

# ============================================================================
# MAGIC LINK AUTHENTICATION
# ============================================================================

@api_view(['POST'])
@throttle_classes([MagicLinkThrottle])
@permission_classes([AllowAny])
def request_magic_link_api(request):
    """
    Request magic link for client login.
    Sends email with token.
    """
    serializer = MagicLinkRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    email = serializer.validated_data['email']
    
    # Find client user
    try:
        user = User.objects.get(email=email, role='client')
    except User.DoesNotExist:
        # Don't reveal if email exists (security)
        return Response({
            'message': 'If this email exists, a magic link has been sent.'
        })
    
    # Generate magic link
    magic_link = MagicLink.generate_for_user(user)
    magic_link_url = f"{settings.FRONTEND_URL}/client_portal/auth?token={magic_link}"
    print('Generated magic link URL:', magic_link_url)  # Debug log


    
    # TODO: Send email with magic link
    # For now, return token in response (TESTING ONLY - remove in production)
    return Response(
        print('Magic magic_link_url:', magic_link_url) or {
        'message': 'Magic link sent to your email.',
        'token': magic_link,  # REMOVE THIS IN PRODUCTION
        'magic_link_url':magic_link_url
        
    })




@api_view(['POST'])
@throttle_classes([MagicLinkThrottle])
@permission_classes([AllowAny])
def sign_in_with_link_api(request):
    """
    Login using magic link token.
    Mirrors standard login behavior.
    """
    serializer = MagicLinkLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    # token_str = serializer.validated_data['token']

    token_str = serializer.validated_data['token']
    token_hash = hashlib.sha256(token_str.encode()).hexdigest()

    try:
        magic_link = MagicLink.objects.get(token_hash=token_hash)
    except MagicLink.DoesNotExist:
        return Response({'error': 'Invalid magic link.'}, status=400)

    if not magic_link.is_valid():
        return Response({'error': 'Magic link expired or already used.'}, status=400)

    user = magic_link.user

    if not user.is_active:
        return Response(
            {'error': 'Account is inactive. Please contact your firm.'},
            status=403
        )

    # Mark as used
    magic_link.mark_as_used()

    # Get or create auth token
    token, _ = Token.objects.get_or_create(user=user)

    # Update last login
    user.last_login = datetime.now()
    user.save(update_fields=['last_login'])

    # Log login (if firm exists)
    if user.firm:
        AuditLog.objects.create(
            firm=user.firm,
            user=user,
            action='user_login_magic_link',
            model_type='user',
            model_id=user.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

    # Prepare response (mirror login_api)
    response_data = {
        'token': token.key,
        'user': UserSerializer(user).data,
        'firm': None,
    }

    if user.firm:
        response_data['firm'] = {
            'id': user.firm.id,
            'name': user.firm.name,
            'subscription_status': user.firm.subscription_status,
            'subscription_plan': user.firm.subscription_plan,
            'can_create_case': user.firm.can_create_case(),
            'can_add_user': user.firm.can_add_user(),
        }

    return Response(response_data, status=200)

# ============================================================================
# CLIENT CASE VIEW
# ============================================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_me(request):
    print('Debug me endpoint hit')
    return Response({
        "id": request.user.id,
        "email": request.user.email,
        "role": request.user.role,
        "firm": request.user.firm.id if request.user.firm else None,
    })


# 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_client_cases_api(request):
    if request.user.role != 'client':
        return Response({'error': 'Only clients allowed'}, status=403)

    cases = Case.objects.filter(client=request.user).order_by('-created_at')

    serializer = ClientCaseSerializer(cases, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_client_cases_api(request):
    """
    Get all cases for logged-in client.
    Clients can only see their own cases.
    """
    print('User role:', request.user.role)
    if request.user.role == 'client':
        print('Fetching cases for client:', request.user.email)
        cases = Case.objects.filter(client=request.user)

    elif request.user.role in ['lawyer', 'firm_owner']:
            cases = Case.objects.filter(firm=request.user.firm)

    else:
            return Response({'error': 'Unauthorized role.'}, status=403)
        
    # cases = Case.objects.filter(client=request.user)
    cases = Case.objects.filter(client=request.user, firm=request.user.firm)
    serializer = ClientCaseSerializer(cases, many=True)
    
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_case_detail_api(request, case_id):
    """
    Get specific case detail for client.
    """
    if request.user.role != 'client':
        return Response({'error': 'Only clients can access this endpoint.'}, status=403)
    
    case = get_object_or_404(Case, id=case_id, client=request.user)
    serializer = ClientCaseSerializer(case)
    
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_client_documents_api(request, case_id):

    if request.user.role != 'client':
        return Response({'error': 'Only clients allowed'}, status=403)

    case = get_object_or_404(Case, id=case_id)

    if case.client != request.user:
        return Response({'error': 'Not your case'}, status=403)

    documents = Document.objects.filter(
        case=case,
        is_deleted=False
    ).order_by('-uploaded_at')

    print(f"Found {documents.count()} documents for case {case_id} and client {request.user.email}")

    serializer = ClientDocumentSerializer(documents, many=True)

    return Response(serializer.data)# ============================================================================
# CLIENT MESSAGING
# ============================================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_case_messages_api(request, case_id):
    """
    List all messages for a case.
    """
    case = get_object_or_404(Case, id=case_id)

    # Permission checks
    if request.user.role == 'client':
        if case.client != request.user:
            return Response({'error': 'Not your case.'}, status=403)

    elif request.user.role == 'lawyer':
        if case.assigned_lawyer != request.user:
            return Response({'error': 'Not your assigned case.'}, status=403)

    elif request.user.role == 'firm_owner':
        if case.firm != request.user.firm:
            return Response({'error': 'Not your firm.'}, status=403)

    else:
        return Response({'error': 'No access.'}, status=403)

    messages = ClientMessage.objects.filter(case=case)
    serializer = ClientMessageSerializer(messages, many=True)

    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_case_message_api(request, case_id):
    """
    Send new message for a case.
    """
    case = get_object_or_404(Case, id=case_id)

    # Permission checks
    if request.user.role == 'client':
        if case.client != request.user:
            return Response({'error': 'Not your ca  se.'}, status=403)

    elif request.user.role == 'lawyer':
        if case.assigned_lawyer != request.user:
            return Response({'error': 'Not your assigned case.'}, status=403)

    elif request.user.role == 'firm_owner':
        if case.firm != request.user.firm:
            return Response({'error': 'Not your firm.'}, status=403)

    else:
        return Response({'error': 'No access.'}, status=403)

    # Determine recipient
    if request.user.role == 'client':
        recipient = case.assigned_lawyer or case.firm.owner
    else:
        recipient = case.client

    data = request.data.copy()
    data['case'] = case.id
    data['recipient'] = recipient.id

    serializer = ClientMessageSerializer(
        data=data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save(sender=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_message_read_api(request, message_id):
    """
    Mark message as read.
    """
    message = get_object_or_404(ClientMessage, id=message_id)
    
    # Only recipient can mark as read
    if message.recipient != request.user:
        return Response({'error': 'Not your message.'}, status=403)
    
    message.is_read = True
    message.save(update_fields=['is_read'])
    
    return Response({'message': 'Marked as read'})


# In client_management/api/views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_client_form_assignments_api(request):
    """
    Returns all form assignments across all cases
    where the logged-in client is the case client.
    One DB query. No internal HTTP chaining.
    """
    if request.user.role != 'client':
        return Response({'error': 'Clients only.'}, status=403)

    assignments = CaseFormAssignment.objects.filter(
        case__client=request.user
    ).select_related(
        'template',
        'case',
    ).order_by('-assigned_at')

    from client_management.api.serializers import ClientFormAssignmentSerializer
    serializer = ClientFormAssignmentSerializer(assignments, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def client_upload_document_api(request, case_id):
    """
    Client uploads a document from the form completion page.
    Scoped to cases where they are the client — no firm check needed.
    """
    if request.user.role != "client":
        return Response({"error": "Clients only."}, status=403)

    case = get_object_or_404(Case, id=case_id, client=request.user)

    serializer = ClientUploadDocumentSerializer(
        data=request.data,
        context={"request": request, "case": case}
    )
    serializer.is_valid(raise_exception=True)
    document = serializer.save()

    DocumentAccess.objects.create(
        document=document,
        accessed_by=request.user,
        action="upload",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return Response({
        "id": document.id,
        "name": document.file_name,
        "file_type": document.file_type,
    }, status=201)