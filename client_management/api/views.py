from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


from case_management.models import Case
from client_management.api.serializers import ClientCaseSerializer, ClientMessageSerializer, MagicLinkLoginSerializer, MagicLinkRequestSerializer
from client_management.models import ClientMessage, MagicLink
from system_management.models import User


# ============================================================================
# MAGIC LINK AUTHENTICATION
# ============================================================================

@api_view(['POST'])
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
    
    # TODO: Send email with magic link
    # For now, return token in response (TESTING ONLY - remove in production)
    return Response({
        'message': 'Magic link sent to your email.',
        'token': magic_link.token  # REMOVE THIS IN PRODUCTION
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def magic_link_login_api(request):
    """
    Login using magic link token.
    Returns auth token for subsequent requests.
    """
    serializer = MagicLinkLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    token_str = serializer.validated_data['token']
    
    # Find magic link
    try:
        magic_link = MagicLink.objects.get(token=token_str)
    except MagicLink.DoesNotExist:
        return Response({'error': 'Invalid magic link.'}, status=400)
    
    # Check if valid
    if not magic_link.is_valid():
        return Response({'error': 'Magic link expired or already used.'}, status=400)
    
    # Mark as used
    magic_link.mark_as_used()
    
    # Get or create auth token
    token, _ = Token.objects.get_or_create(user=magic_link.user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': magic_link.user.id,
            'email': magic_link.user.email,
            'first_name': magic_link.user.first_name,
            'last_name': magic_link.user.last_name,
        }
    })


# ============================================================================
# CLIENT CASE VIEW
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_client_cases_api(request):
    """
    Get all cases for logged-in client.
    Clients can only see their own cases.
    """
    if request.user.role != 'client':
        return Response({'error': 'Only clients can access this endpoint.'}, status=403)
    
    cases = Case.objects.filter(client=request.user)
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


# ============================================================================
# CLIENT MESSAGING
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def case_messages_api(request, case_id):
    """
    GET: List all messages for a case
    POST: Send new message
    """
    case = get_object_or_404(Case, id=case_id)
    
    # Permission check
    if request.user.role == 'client':
        if case.client != request.user:
            return Response({'error': 'Not your case.'}, status=403)
    elif request.user.role in ['lawyer', 'firm_owner']:
        if case.firm != request.user.firm:
            return Response({'error': 'Not your firm.'}, status=403)
    else:
        return Response({'error': 'No access.'}, status=403)
    
    if request.method == 'GET':
        messages = ClientMessage.objects.filter(case=case)
        serializer = ClientMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
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