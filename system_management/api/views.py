# system_management/views.py

from rest_framework.authtoken.models import Token

# from datetime import timezone
import datetime
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination




from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate


from system_management.models import Firm, User, AuditLog
from .serializers import (
    ChangePasswordSerializer,
    CreateFirmSerializer,
    FirmListSerializer,
    FirmUpdateDetailsSerializer,
    GetFirmDetailSerializer,
    GetFirmUserListSerializer,
    LoginSerializer,
    MyProfileSerializer,
    UpdateFirmUserSerializer,
    UpdateMyFirmSerializer,
    UpdateMyProfileSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangeRoleSerializer,
    AuditLogSerializer,
    ViewMyFirmSerializer,
)
from system_management.permissions import CanViewAuditLogs, IsSuperAdmin, IsFirmOwner

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
def create_firm_with_owner_api(request):
    """Create firm and owner user in one request (super admin only)."""
    if request.user.role != 'super_admin':
        return Response({'error': 'Super admin only'}, status=403)
    
    # Create firm
    firm_data = {
        'name': request.data.get('firm_name'),
        'subscription_plan': request.data.get('subscription_plan', 'solo'),
    }
    firm_serializer = CreateFirmSerializer(data=firm_data)
    if not firm_serializer.is_valid():
        return Response(firm_serializer.errors, status=400)
    
    firm = firm_serializer.save()
    
    # Log firm creation
    AuditLog.objects.create(
        firm=firm,
        user=request.user,
        action='firm_created',
        model_type='firm',
        model_id=firm.id,
        changes={'name': firm.name},
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    # Create owner user
    user_data = {
        'email': request.data.get('email'),
        'first_name': request.data.get('first_name'),
        'last_name': request.data.get('last_name'),
        'role': 'firm_owner',
        'firm': firm.id,
    }
    user_serializer = UserCreateSerializer(data=user_data, context={'request': request})
    if not user_serializer.is_valid():
        firm.delete()  # Rollback
        return Response(user_serializer.errors, status=400)
    
    user = user_serializer.save()
    
    # Log owner creation
    AuditLog.objects.create(
        firm=firm,
        user=request.user,
        action='firm_owner_created',
        model_type='user',
        model_id=user.id,
        changes={
            'email': user.email,
            'role': user.role,
            'firm': firm.name,
        },
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    # Set firm owner
    firm.owner = user
    firm.save()
    
    # Log firm owner assignment
    AuditLog.objects.create(
        firm=firm,
        user=request.user,
        action='firm_owner_assigned',
        model_type='firm',
        model_id=firm.id,
        changes={'owner_email': user.email},
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    return Response({
        'firm': CreateFirmSerializer(firm).data,
        'owner': UserSerializer(user).data,
        'password': getattr(user, '_plaintext_password', None),  # TESTING ONLY
    }, status=201)


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



# ────────────────────────────────────────────────
# 1. List users in firm / all users (GET only)
# ────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def firm_user_list_api(request):
    """
    GET: List users
    - Super admin → all users across all firms
    - Firm owner  → only users in their own firm
    """
    if request.user.role not in ['super_admin', 'firm_owner']:
        return Response(
            {'error': 'Only super admins and firm owners can view user lists.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.user.role == 'super_admin':
        users = User.objects.all()
    else:
        users = User.objects.filter(firm=request.user.firm)

    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data)


# ────────────────────────────────────────────────
# 2. Create new user in firm (POST only)
# ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def firm_user_create_api(request):
    """
    POST: Add a new user to a firm
    - Firm owner → adds to their own firm
    - Super admin → can add to any firm
    """
    if request.user.role not in ['super_admin', 'firm_owner']:
        return Response(
            {'error': 'Only super admins and firm owners can create users.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Plan limit check (only for firm owners)
    if request.user.role == 'firm_owner':
        if not request.user.firm.can_add_user():
            return Response(
                {
                    'error': 'User limit reached for your current plan.',
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
        user = serializer.save()

        # Audit log
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

        # Return full detail after creation
        return Response(
            {
                **GetFirmUserListSerializer(user).data,
                #to be removed after testing, only for demo purposes including
                #  the inner brackets and ** to unpack the dict
                'password': getattr(user, '_plaintext_password', None)
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────
# 1. Retrieve single user detail (GET only)
# ────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def firm_user_retrieve_api(request, pk):
    """
    GET: Retrieve details of a specific user
    - Super admin: any user
    - Firm owner: only users in their firm
    """
    user = get_object_or_404(User, pk=pk)

    # Permission check
    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only view users in your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )

    # serializer = GetFirmDetailSerializer(user)
    serializer = UserSerializer(user)
    return Response(serializer.data)


# ────────────────────────────────────────────────
# 2. Update user (PATCH only)
# ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def firm_user_update_api(request, pk):
    """
    PATCH: Update user information
    - Super admin: any user
    - Firm owner: only users in their firm (cannot edit self)
    """
    user = get_object_or_404(User, pk=pk)

    # Permission check
    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only manage users in your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if user == request.user:
            return Response(
                {'error': 'You cannot modify your own account.'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = UserUpdateSerializer(
        user,
        data=request.data,
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        updated_user = serializer.save()

        # Log changes
        AuditLog.objects.create(
            firm=updated_user.firm,
            user=request.user,
            action='user_updated',
            model_type='user',
            model_id=updated_user.id,
            changes=request.data,
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response(UpdateFirmUserSerializer(updated_user).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────
# 3. Delete / remove user (DELETE only)
# ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def firm_user_delete_api(request, pk):
    """
    DELETE: Remove a user from the firm
    - Super admin: any user
    - Firm owner: only users in their firm (cannot delete self)
    """
    user = get_object_or_404(User, pk=pk)

    # Permission check
    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only manage users in your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )

    # Cannot delete yourself
    if user == request.user:
        return Response(
            {'error': 'You cannot delete your own account.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Log before deletion
    AuditLog.objects.create(
        firm=user.firm,
        user=request.user,
        action='user_deleted',
        model_type='user',
        model_id=user.id,
        changes={
            'email': user.email,
            'role': user.role,
        },
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    user.delete()

    return Response(
        {'message': 'User deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_user_role_api(request, pk):
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_firm_retrieve_api(request):
    """
    GET: Retrieve details of the current user's firm
    Available to any authenticated user who belongs to a firm
    """
    if not request.user.firm:
        return Response(
            {'error': 'You are not associated with any firm.'},
            status=status.HTTP_404_NOT_FOUND
        )

    firm = request.user.firm
    serializer = ViewMyFirmSerializer(firm)
    return Response(serializer.data)



# ────────────────────────────────────────────────
# 2. Update my firm settings (PATCH only)
# ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def my_firm_update_api(request):
    """
    PATCH: Update limited settings of the current user's firm
    Only firm owners can perform this action
    Currently only 'name' is allowed to be updated
    """
    if not request.user.firm:
        return Response(
            {'error': 'You are not associated with any firm.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.user.role != 'firm_owner':
        return Response(
            {'error': 'Only firm owners can update firm settings.'},
            status=status.HTTP_403_FORBIDDEN
        )

    firm = request.user.firm

    # Restrict to allowed fields (very important for security)
    allowed_fields = ['name']  # you can expand this list later if needed
    filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}

    if not filtered_data:
        return Response(
            {'detail': 'No updatable fields provided.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UpdateMyFirmSerializer(firm, data=filtered_data, partial=True)
    if serializer.is_valid():
        updated_firm = serializer.save()

        # Audit log
        AuditLog.objects.create(
            firm=updated_firm,
            user=request.user,
            action='firm_settings_updated',
            model_type='firm',
            model_id=updated_firm.id,
            changes=filtered_data,
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response(UpdateMyFirmSerializer(updated_firm).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ────────────────────────────────────────────────
# 1. Retrieve my own profile (GET only)
# ────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile_retrieve_api(request):
    """
    GET: Retrieve the current user's own profile details.
    Available to any authenticated user.
    """
    user = request.user
    serializer = MyProfileSerializer(user)
    return Response(serializer.data)

    

# ────────────────────────────────────────────────
# 2. Update my own profile (PATCH only)
# ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def my_profile_update_api(request):
    """
    PATCH: Update the current user's own profile.
    Only personal fields (name, phone, etc.) are allowed.
    """
    user = request.user

    serializer = UpdateMyProfileSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        updated_user = serializer.save()

        # Audit log (only log actual changes)
        if serializer.validated_data:  # only if something changed
            AuditLog.objects.create(
                firm=user.firm,
                user=request.user,
                action='profile_updated',
                model_type='user',
                model_id=user.id,
                changes=serializer.validated_data,
                ip_address=request.META.get('REMOTE_ADDR'),
            )

        # Return full read-view after update
        return Response(UpdateMyProfileSerializer(updated_user).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action='password_changed',
            model_type='user',
            model_id=request.user.id,
            changes={},
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response({"message": "Password updated successfully"})
    return Response(serializer.errors, status=400)
# ============================================================================
# AUDIT LOGS
# ============================================================================
class AuditLogPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAuditLogs])
def audit_log_list_api(request):
    """
    GET: Retrieve audit logs
    - Super admin: all logs (optional ?firm_id= filter)
    - Firm owner / Lawyer / Assistant: all logs for their own firm
    """
    logs = AuditLog.objects.none()  # safe default

    if request.user.role == 'super_admin':
        firm_id = request.query_params.get('firm_id')
        if firm_id:
            logs = AuditLog.objects.filter(firm_id=firm_id)
        else:
            logs = AuditLog.objects.all()
    else:
        # Firm owner, lawyer, assistant: only their own firm
        if request.user.firm:
            logs = AuditLog.objects.filter(firm=request.user.firm)
        else:
            return Response(
                {'error': 'You are not associated with any firm.'},
                status=status.HTTP_403_FORBIDDEN
            )

    # Order by newest first (most useful for recent activity)
    logs = logs.order_by('-timestamp')

    # Pagination
    paginator = AuditLogPagination()
    page = paginator.paginate_queryset(logs, request)
    serializer = AuditLogSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def audit_log_list_api(request):
#     """
#     Get audit logs for my firm.
#     Firm owner sees their firm's logs.
#     Super admin can see all logs (with firm filter).
#     """
#     if request.user.role == 'super_admin':
#         # Super admin can filter by firm_id
#         firm_id = request.query_params.get('firm_id')
#         if firm_id:
#             logs = AuditLog.objects.filter(firm_id=firm_id)
#         else:
#             logs = AuditLog.objects.all()
#     elif request.user.role in ['firm_owner', 'lawyer']:
#         # Firm owner and lawyers see their firm's logs
#         logs = AuditLog.objects.filter(firm=request.user.firm)
#     else:
#         return Response(
#             {'error': 'You do not have permission to view audit logs.'},
#             status=status.HTTP_403_FORBIDDEN
#         )
    
#     # Pagination (manual for now, can use DRF pagination later)
#     page_size = int(request.query_params.get('page_size', 50))
#     logs = logs[:page_size]
    
#     serializer = AuditLogSerializer(logs, many=True)
#     return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_detail_api(request, pk):
    """
    GET: Retrieve a specific audit log entry by ID.
    Super admin: any log
    Firm owner / lawyer / assistant: only from their own firm
    """
    log = get_object_or_404(AuditLog, pk=pk)

    # Permission check (can move to object-level permission later)
    if request.user.role != 'super_admin':
        if log.firm != request.user.firm:
            return Response(
                {'error': 'You can only view logs from your own firm.'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = AuditLogSerializer(log)  # ← reuse is correct here
    return Response(serializer.data)