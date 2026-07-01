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


from django.core.mail import send_mail

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
    git branchnk_url = f"{settings.FRONTEND_URL}/client_portal/auth?token={magic_link}"
    print('Generated magic link URL:', magic_link_url)  # Debug log

    # ── Send the actual email ──────────────────────────────────────
    firm_name = user.firm.name if user.firm else "ClearWave"

    subject = f"Your secure access link — {firm_name}"
    message = (
        f"Hi {user.first_name or ''},\n\n"
        f"Here is your secure link to access your case portal with {firm_name}:\n\n"
        f"{magic_link_url}\n\n"
        f"This link will expire in 1 hour and can only be used once.\n\n"
        f"If you did not request this, you can safely ignore this email.\n\n"
        f"— {firm_name}"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"Magic link email sent to {user.email}")
    except Exception as e:
        # Don't fail the request just because email failed — log it.
        # The token still exists and the link is still valid; this
        # just means the client didn't receive an email and someone
        # (you) needs to know SMTP failed.
        print(f"⚠️ Failed to send magic link email to {user.email}: {e}")

    return Response({
        'message': 'Magic link sent to your email.',
        # 'token': magic_link,            # REMOVE — was testing only
        # 'magic_link_url': magic_link_url # REMOVE — was testing only
    })
# ============================================================================
# MAGIC LINK AUTHENTICATION
# ============================================================================

# @api_view(['POST'])
# @throttle_classes([MagicLinkThrottle])
# @permission_classes([AllowAny])
# def request_magic_link_api(request):
#     """
#     Request magic link for client login.
#     Sends email with token.
#     """
#     serializer = MagicLinkRequestSerializer(data=request.data)
    
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=400)
    
#     email = serializer.validated_data['email']
    
#     # Find client user
#     try:
#         user = User.objects.get(email=email, role='client')
#     except User.DoesNotExist:
#         # Don't reveal if email exists (security)
#         return Response({
#             'message': 'If this email exists, a magic link has been sent.'
#         })
    
#     # Generate magic link
#     magic_link = MagicLink.generate_for_user(user)
#     magic_link_url = f"{settings.FRONTEND_URL}/client_portal/auth?token={magic_link}"
#     print('Generated magic link URL:', magic_link_url)  # Debug log


    
#     # TODO: Send email with magic link
#     # For now, return token in response (TESTING ONLY - remove in production)
#     return Response(
#         print('Magic magic_link_url:', magic_link_url) or {
#         'message': 'Magic link sent to your email.',
#         'token': magic_link,  # REMOVE THIS IN PRODUCTION
#         'magic_link_url':magic_link_url
        
#     })




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

    print(f"Client {request.user.email} accessed case {case_id} details.")
    
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





# Add to client_management/api/views.py
# Requires: from .models import MagicLink  (already imported if request_magic_link_api is in same file)
# Requires: from system_management.models import User (or wherever your User model lives)

from django.core.mail import send_mail
# from django.conf import settings
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404

from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_magic_link_status_api(request, client_id):
    """
    Returns the most recent MagicLink status for a client,
    so the lawyer UI can show: never sent / pending / expired / used.
    """
    client = get_object_or_404(User, id=client_id, role='client')

    latest_link = MagicLink.objects.filter(user=client).order_by('-created_at').first()

    if not latest_link:
        return Response({
            'status': 'never_sent',
            'last_login': client.last_login,
        })

    if latest_link.is_used:
        link_status = 'used'
    elif timezone.now() > latest_link.expires_at:
        link_status = 'expired'
    else:
        link_status = 'pending'

    return Response({
        'status': link_status,
        'created_at': latest_link.created_at,
        'expires_at': latest_link.expires_at,
        'last_login': client.last_login,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_client_magic_link_api(request, client_id):
    """
    Lawyer/firm-owner triggered: generate + email a fresh magic link
    to the given client. Reuses the same logic as the client-facing
    request_magic_link_api, but authenticated and explicit about who.
    """
    client = get_object_or_404(User, id=client_id, role='client')

    magic_link = MagicLink.generate_for_user(client)
    magic_link_url = f"{settings.FRONTEND_URL}/client_portal/auth?token={magic_link}"

    firm_name = client.firm.name if client.firm else "ClearWave"

    subject = f"Your secure access link — {firm_name}"
    message = (
        f"Hi {client.first_name or ''},\n\n"
        f"Here is your secure link to access your case portal with {firm_name}:\n\n"
        f"{magic_link_url}\n\n"
        f"This link will expire in 1 hour and can only be used once.\n\n"
        f"If you did not request this, you can safely ignore this email.\n\n"
        f"— {firm_name}"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"⚠️ Failed to send magic link email to {client.email}: {e}")
        return Response(
            {'error': f'Link generated but email failed to send: {str(e)}'},
            status=502
        )

    return Response({'message': f'Portal access link sent to {client.email}.'})