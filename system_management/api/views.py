# system_management/views.py

from rest_framework.authtoken.models import Token

# from datetime import timezone
import datetime
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny



from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate


from system_management.models import Firm, User, AuditLog
from .serializers import (
    CreateFirmSerializer,
    FirmListSerializer,
    FirmUpdateDetailsSerializer,
    GetFirmDetailSerializer,
    LoginSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangeRoleSerializer,
    AuditLogSerializer,
    MyFirmSerializer,
)
from system_management.permissions import IsSuperAdmin, IsFirmOwner

# from rest_framework.decorators import (
#     api_view,
#     authentication_classes,
#     permission_classes
# )


# ============================================================================
# SUPER ADMIN - FIRM MANAGEMENT
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """User login endpoint."""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Please provide both email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    user = authenticate(email=email, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Account is inactive. Please contact your firm owner.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    
    # Update last login
    user.last_login = datetime.now()
    user.save(update_fields=['last_login'])
    
    # Log login
    if user.firm:
        AuditLog.objects.create(
            firm=user.firm,
            user=user,
            action='user_login',
            model_type='user',
            model_id=user.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    
    # Prepare response
    response_data = {
        'token': token.key,
        'user': UserSerializer(user).data,
        'firm': None,
    }
    
    # Add firm info if user has one
    if user.firm:
        response_data['firm'] = {
            'id': user.firm.id,
            'name': user.firm.name,
            'subscription_status': user.firm.subscription_status,
            'subscription_plan': user.firm.subscription_plan,
            'can_create_case': user.firm.can_create_case(),
            'can_add_user': user.firm.can_add_user(),
        }
    
    return Response(response_data, status=status.HTTP_200_OK)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_firm_list_api(request):
    """
    GET: List all firms
    Super admin only
    """
    if request.user.role != 'super_admin':
        return Response(
            {'error': 'Only super admins can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )

    firms = Firm.objects.all()
    serializer = FirmListSerializer(firms, many=True)
    return Response(serializer.data)


# ────────────────────────────────────────────────
# 2. Create a new firm (POST only)
# ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_firm_create_api(request):
    """
    POST: Create a new firm
    Super admin only
    """
    if request.user.role != 'super_admin':
        return Response(
            {'error': 'Only super admins can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CreateFirmSerializer(data=request.data)
    if serializer.is_valid():
        firm = serializer.save()

        # Log action
        AuditLog.objects.create(
            firm=firm,
            user=request.user,
            action='firm_created',
            model_type='firm',
            model_id=firm.id,
            changes={'name': firm.name},
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response(
            CreateFirmSerializer(firm).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# ────────────────────────────────────────────────
# 1. Retrieve a single firm (GET only)
# ────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_firm_retrieve_api(request, pk):
    """
    GET: Retrieve details of a specific firm
    Super admin only
    """
    if request.user.role != 'super_admin':
        return Response(
            {'error': 'Only super admins can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )

    firm = get_object_or_404(Firm, pk=pk)
    serializer = GetFirmDetailSerializer(firm)
    return Response(serializer.data)


# ────────────────────────────────────────────────
# 2. Update a firm (PATCH only)
# ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_firm_update_api(request, pk):
    """
    PATCH: Partially update a firm
    Super admin only
    """
    if request.user.role != 'super_admin':
        return Response(
            {'error': 'Only super admins can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )

    firm = get_object_or_404(Firm, pk=pk)

    # Capture old values for audit (only the fields we care about)
    old_data = {
        'subscription_status': firm.subscription_status,
        'subscription_plan': firm.subscription_plan,
        'max_users': firm.max_users,
    }

    serializer = FirmUpdateDetailsSerializer(firm, data=request.data, partial=True)
    if serializer.is_valid():
        updated_firm = serializer.save()

        # Log changes
        AuditLog.objects.create(
            firm=updated_firm,
            user=request.user,
            action='firm_updated',
            model_type='firm',
            model_id=updated_firm.id,
            changes={
                'old': old_data,
                'new': {
                    'subscription_status': updated_firm.subscription_status,
                    'subscription_plan': updated_firm.subscription_plan,
                    'max_users': updated_firm.max_users,
                }
            },
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response(FirmUpdateDetailsSerializer(updated_firm).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────
# 3. Delete a firm (DELETE only)
# ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_firm_destroy(request, pk):
    """
    DELETE: Permanently delete a firm
    Super admin only - dangerous operation
    """
    if request.user.role != 'super_admin':
        return Response(
            {'error': 'Only super admins can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )

    firm = get_object_or_404(Firm, pk=pk)

    # Log before deletion
    AuditLog.objects.create(
        firm=firm,
        user=request.user,
        action='firm_deleted',
        model_type='firm',
        model_id=firm.id,
        changes={
            'name': firm.name,
            'user_count': firm.users.count(),
        },
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    firm.delete()

    return Response(
        {'message': 'Firm deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )


# ============================================================================
# FIRM OWNER - USER MANAGEMENT
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def firm_user_list_create(request):
    """
    GET:  List users in my firm
    POST: Add user to my firm (firm owner or super admin)
    """
    # Check permissions
    if request.user.role not in ['super_admin', 'firm_owner']:
        return Response(
            {'error': 'Only firm owners can manage users.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        # List users in requester's firm
        if request.user.role == 'super_admin':
            # Super admin can see all users across all firms
            users = User.objects.all()
        else:
            users = User.objects.filter(firm=request.user.firm)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Check if firm can add more users
        if request.user.role == 'firm_owner':
            if not request.user.firm.can_add_user():
                return Response(
                    {
                        'error': 'User limit reached for your plan.',
                        'max_users': request.user.firm.max_users,
                        'current_users': request.user.firm.users.count(),
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = UserCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Auto-assign firm if not super admin
            if request.user.role == 'firm_owner':
                serializer.validated_data['firm'] = request.user.firm
            
            user = serializer.save()
            
            # Log action
            AuditLog.objects.create(
                firm=user.firm,
                user=request.user,
                action='user_created',
                model_type='user',
                model_id=user.id,
                changes={
                    'email': user.email,
                    'role': user.role,
                },
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def firm_user_detail(request, pk):
    """
    GET:    Get user details
    PATCH:  Update user
    DELETE: Remove user from firm
    """
    user = get_object_or_404(User, pk=pk)
    
    # Permission check: Must be same firm or super admin
    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only manage users in your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Firm owner can't edit themselves
        if user == request.user and request.method != 'GET':
            return Response(
                {'error': 'You cannot modify your own account.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            
            # Log action
            AuditLog.objects.create(
                firm=user.firm,
                user=request.user,
                action='user_updated',
                model_type='user',
                model_id=user.id,
                changes=request.data,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response(UserSerializer(updated_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Can't delete yourself
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log deletion
        AuditLog.objects.create(
            firm=user.firm,
            user=request.user,
            action='user_deleted',
            model_type='user',
            model_id=user.id,
            changes={'email': user.email, 'role': user.role},
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        user.delete()
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_user_role(request, pk):
    """
    Change a user's role.
    Only firm owner or super admin can do this.
    """
    user = get_object_or_404(User, pk=pk)
    
    # Permission check
    if request.user.role not in ['super_admin', 'firm_owner']:
        return Response(
            {'error': 'Only firm owners can change user roles.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Must be same firm or super admin
    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only manage users in your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = ChangeRoleSerializer(
        data=request.data,
        context={'request': request, 'user': user}
    )
    
    if serializer.is_valid():
        old_role = user.role
        new_role = serializer.validated_data['role']
        
        user.role = new_role
        user.save()
        
        # Log action
        AuditLog.objects.create(
            firm=user.firm,
            user=request.user,
            action='user_role_changed',
            model_type='user',
            model_id=user.id,
            changes={'old_role': old_role, 'new_role': new_role},
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# FIRM OWNER - MY FIRM
# ============================================================================

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def my_firm_detail(request):
    """
    GET:   View my firm details
    PATCH: Update my firm settings (limited fields)
    """
    if not request.user.firm:
        return Response(
            {'error': 'You are not associated with any firm.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    firm = request.user.firm
    
    if request.method == 'GET':
        serializer = MyFirmSerializer(firm)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Firm owner can only update name
        if request.user.role != 'firm_owner':
            return Response(
                {'error': 'Only firm owners can update firm settings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only allow updating name
        allowed_fields = ['name']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = MyFirmSerializer(firm, data=data, partial=True)
        if serializer.is_valid():
            updated_firm = serializer.save()
            
            # Log action
            AuditLog.objects.create(
                firm=firm,
                user=request.user,
                action='firm_settings_updated',
                model_type='firm',
                model_id=firm.id,
                changes=data,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response(MyFirmSerializer(updated_firm).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# AUDIT LOGS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_list(request):
    """
    Get audit logs for my firm.
    Firm owner sees their firm's logs.
    Super admin can see all logs (with firm filter).
    """
    if request.user.role == 'super_admin':
        # Super admin can filter by firm_id
        firm_id = request.query_params.get('firm_id')
        if firm_id:
            logs = AuditLog.objects.filter(firm_id=firm_id)
        else:
            logs = AuditLog.objects.all()
    elif request.user.role in ['firm_owner', 'lawyer']:
        # Firm owner and lawyers see their firm's logs
        logs = AuditLog.objects.filter(firm=request.user.firm)
    else:
        return Response(
            {'error': 'You do not have permission to view audit logs.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Pagination (manual for now, can use DRF pagination later)
    page_size = int(request.query_params.get('page_size', 50))
    logs = logs[:page_size]
    
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_detail(request, pk):
    """
    Get specific audit log entry.
    """
    log = get_object_or_404(AuditLog, pk=pk)
    
    # Permission check
    if request.user.role != 'super_admin':
        if log.firm != request.user.firm:
            return Response(
                {'error': 'You can only view logs from your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = AuditLogSerializer(log)
    return Response(serializer.data)