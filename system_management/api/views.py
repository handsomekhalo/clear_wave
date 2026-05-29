# system_management/views.py

import json
from pytz import timezone
from case_management.models import CaseType
from rest_framework.authtoken.models import Token
import hashlib
import secrets
# from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

# from datetime import timezone
import datetime
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token

from django.utils import timezone


from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate


from system_management.models import Firm, PasswordResetToken, User, AuditLog
from .serializers import (
    ChangePasswordSerializer,
    CreateFirmSerializer,
    FirmListSerializer,
    FirmOnboardingSerializer,
    FirmUpdateDetailsSerializer,
    FirmUserListSerializer,
    GetAllRolesSerializer,
    GetFirmDetailSerializer,
    GetFirmUserListSerializer,
    LoginSerializer,
    MatterTypesOnboardingSerializer,
    MyProfileSerializer,
    RegisterFirmByOwnerSerializer,
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
from django.db import transaction
from system_management.permissions import  MagicLinkThrottle
from rest_framework.decorators import api_view, permission_classes, throttle_classes

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
    data = request.data
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
                    # ✅ Add onboarding fields
        'is_onboarded': user.firm.is_onboarded,
        'onboarding_step': user.firm.onboarding_step or 1,
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
            'user': UserSerializer(user).data,
            'firm': CreateFirmSerializer(firm).data,
            'password': getattr(user, '_plaintext_password', None),
        }, status=status.HTTP_201_CREATED)




@api_view(['POST'])
@permission_classes([AllowAny])
def register_firm_owner_api(request):

    data = request.data

    if isinstance(data, str):
        data = json.loads(data)

    try:
        with transaction.atomic():

            # -------------------------
            # Create temporary firm
            # -------------------------
            firm_data = {
                "name": "New Firm",
                "subscription_plan": "solo",
            }

            firm_serializer = RegisterFirmByOwnerSerializer(data=firm_data)

            if not firm_serializer.is_valid():
                print(firm_serializer.errors)
                return Response(firm_serializer.errors, status=400)

            firm = firm_serializer.save()

            # -------------------------
            # Create owner user
            # -------------------------
            user = User.objects.create(
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                role="firm_owner",
                firm=firm
            )

            user.set_password(data.get("password"))
            user.save()

            # -------------------------
            # Assign firm owner
            # -------------------------
            firm.owner = user
            firm.save()

            # -------------------------
            # Audit log
            # -------------------------
            AuditLog.objects.create(
                firm=firm,
                user=user,
                action="firm_self_registered",
                model_type="firm",
                model_id=firm.id,
                changes={"firm_name": firm.name},
                ip_address=request.META.get("REMOTE_ADDR"),
            )

            return Response({
                "status": "success",
                "message": "Account created successfully",
                "firm_id": firm.id,
                "user_id": user.id
            }, status=201)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)
    

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
def admin_firm_delete_api(request, pk):
    if request.user.role != 'super_admin':
        return Response({'error': 'Only super admins can access this endpoint.'}, status=403)

    firm = get_object_or_404(Firm, pk=pk)

    # Soft delete
    if not firm.is_active:
        return Response({'error': 'Firm is already deactivated.'}, status=400)

    firm.is_active = False
    # firm.deleted_at = timezone.now()
    firm.deleted_at= timezone.now()

    firm.save()

    # Log soft deletion
    AuditLog.objects.create(
        firm=firm,
        user=request.user,
        action='firm_deactivated',
        model_type='firm',
        model_id=firm.id,
        changes={
            'name': firm.name,
            'user_count': firm.users.count(),
        },
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    return Response({'message': 'Firm deactivated successfully'}, status=200)


# ============================================================================
# FIRM OWNER - USER MANAGEMENT
# ============================================================================



# ────────────────────────────────────────────────
# 1. List users in firm / all users (GET only)
# ────────────────────────────────────────────────

# views.py (add to your existing file)

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

    serializer = FirmUserListSerializer(users, many=True)
    return Response(serializer.data)


# ────────────────────────────────────────────────
# 2. Create new user in firm (POST only)
# ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def firm_user_create_api(request):
    
    if request.user.role not in ['super_admin', 'firm_owner']:
        return Response({'error': 'Only firm owners can manage users'}, status=403)
    
    if request.user.role == 'firm_owner':
        if not request.user.firm.can_add_user():
            return Response({
                'error': 'User limit reached for your plan.',
                'max_users': request.user.firm.max_users,
                'current_users': request.user.firm.users.count(),
            }, status=403)
    
    serializer = UserCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        if request.user.role == 'firm_owner':
            serializer.validated_data['firm'] = request.user.firm
        
        user = serializer.save()
        
        AuditLog.objects.create(
            firm=user.firm,
            user=request.user,
            action='user_created',
            model_type='user',
            model_id=user.id,
            changes={'email': user.email, 'role': user.role},
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        # Return user + password for frontend to send email
        return Response({
            'user': UserSerializer(user).data,
            'password': getattr(user, '_plaintext_password', None),  # <-- Frontend needs this
            'firm_name': user.firm.name if user.firm else 'ClearWave',
        }, status=201)
    
    return Response(serializer.errors, status=400)


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
        # if user.role == "firm_owner":
        #     block
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
    user = get_object_or_404(User, pk=pk)

    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response({'error': 'You can only manage users in your own firm.'}, status=403)

    if user == request.user:
        return Response({'error': 'You cannot delete your own account.'}, status=403)

    if not user.is_active:
        return Response({'error': 'User is already deactivated.'}, status=400)

    # Soft deactivate
    user.is_active = False
    user.deleted_at = timezone.now()

    user.save()

    # Log
    AuditLog.objects.create(
        firm=user.firm,
        user=request.user,
        action='user_deactivated',
        model_type='user',
        model_id=user.id,
        changes={'email': user.email, 'role': user.role},
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    return Response({'message': 'User deactivated successfully'}, status=200)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def firm_user_toggle_status_api(request, pk):

    user = get_object_or_404(User, pk=pk)

    if request.user.role != 'super_admin':
        if user.firm != request.user.firm:
            return Response(
                {'error': 'You can only manage users in your own firm.'},
                status=403
            )

    if user == request.user:
        return Response(
            {'error': 'You cannot deactivate your own account.'},
            status=403
        )

    # Toggle status
    if user.is_active:
        user.is_active = False
        user.deleted_at = timezone.now()
        action = "user_deactivated"

    else:
        user.is_active = True
        user.deleted_at = None
        action = "user_activated"

    user.save()

    # Audit log
    AuditLog.objects.create(
        firm=user.firm,
        user=request.user,
        action=action,
        model_type='user',
        model_id=user.id,
        changes={'email': user.email, 'role': user.role},
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    return Response({
        "status": "success",
        "message": "User status updated",
        "is_active": user.is_active
    }, status=200)



@api_view(['GET'])
def get_all_roles_api(request):
    if request.method == "GET":
        roles = [
            {"key": role[0], "label": role[1]}
            for role in User.ROLE_CHOICES
        ]

        if request.user.role == User.FIRM_OWNER:
            roles = [r for r in roles if r["key"] in [User.LAWYER, User.ASSISTANT]]

        serializer = GetAllRolesSerializer(roles, many=True)

        try:
            # ✅ Pass dict directly, not json.dumps()
            return Response({
                'status': "success",
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except KeyError:
            return Response({
                'status': "error",
                'message': "Error during getting roles."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({
            'status': "error",
            'message': "INVALID REQUEST METHOD"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
    PATCH: Update my firm settings (firm owner only, limited fields)
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
    
    allowed_fields = ['name']
    filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}
    
    # NEW: Check if any updatable fields were provided
    if not filtered_data:
        return Response(
            {'detail': 'No updatable fields provided.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    firm = request.user.firm
    serializer = UpdateMyFirmSerializer(firm, data=filtered_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        AuditLog.objects.create(
            firm=firm,
            user=request.user,
            action='firm_settings_updated',
            model_type='firm',
            model_id=firm.id,
            changes=filtered_data,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return Response(UpdateMyFirmSerializer(firm).data)
    
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
    PATCH: Update own profile (first_name, last_name, phone only)
    """
    allowed_fields = ['first_name', 'last_name', 'phone']
    filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}
    
    # NEW: Check if any updatable fields were provided
    if not filtered_data:
        return Response(
            {'detail': 'No updatable fields provided.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = UpdateMyProfileSerializer(
        request.user,
        data=filtered_data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        
        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action='profile_updated',
            model_type='user',
            model_id=request.user.id,
            changes=filtered_data,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return Response(MyProfileSerializer(request.user).data)
    
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



# system_management/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding_step_1_api(request):
    """Step 1: Firm name"""

    if request.user.role != 'firm_owner':
        return Response({'error': 'Only firm owners onboard'}, status=403)

    firm = getattr(request.user, 'firm', None)
    if not firm:
        return Response({'error': 'Firm not found for this user'}, status=400)

    if firm.onboarding_step > 1:
        return Response({'error': 'Step 1 already completed'}, status=400)

    serializer = FirmOnboardingSerializer(firm, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save(onboarding_step=2)
        return Response({
            'status': 'success',
            'message': 'Step 1 completed',
            'next_step': 2
        })

    return Response(serializer.errors, status=400)
#     return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding_step_2_api(request):
    """Step 2: Finish onboarding (no matter types needed)"""
    firm = getattr(request.user, 'firm', None)
    
    if not firm:
        return Response({'error': 'Firm not found for this user'}, status=400)

    if firm.onboarding_step < 2:
        return Response({'error': 'Complete step 1 first'}, status=400)

    if firm.is_onboarded:
        return Response({'error': 'Already onboarded'}, status=400)

    # ✅ Just mark the firm as fully onboarded
    firm.is_onboarded = True
    firm.onboarding_step = 99  # Arbitrary number to indicate completion
    firm.save()

    return Response({
        'status': 'success',
        'message': 'Firm onboarding completed',
        'next_step': None
    })

# system_management/api/views.py


# ---------------------------------------------------------------------------
# PASSWORD RESET REQUEST
# ---------------------------------------------------------------------------

@api_view(["POST"])
@throttle_classes([MagicLinkThrottle])
@permission_classes([AllowAny])
def request_password_reset_api(request):
    """
    Takes email. Generates a reset token. Sends email.
    For testing — prints token to console if email fails.
    """
    email = request.data.get("email", "").strip().lower()

    if not email:
         return Response({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Security — don't reveal if email exists
        return Response({
            "message": "If this email exists a reset link has been sent."
        })

    # Generate token
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = timezone.now() + timedelta(hours=1)

    # Store on user — add these fields to User model if not there
    # OR use a separate PasswordResetToken model below
    PasswordResetToken.objects.filter(user=user).delete()  # invalidate old ones
    PasswordResetToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    # Try email — fall back to console for testing
    try:
        send_mail(
            subject="ClearWave — Password Reset",
            message=f"Click the link to reset your password:\n\n{reset_url}\n\nExpires in 1 hour.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        # No SendGrid yet — print to console for testing
        print(f"\n🔑 PASSWORD RESET URL: {reset_url}\n")

    return Response({
        "message": "If this email exists a reset link has been sent."
    })


# ---------------------------------------------------------------------------
# PASSWORD RESET CONFIRM
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_password_reset_api(request):
    """
    Takes token + new_password + confirm_password.
    Validates token, updates password, invalidates token.
    """
    data = request.data
    print('data requested is', data)
    token_str = request.data.get("token", "").strip()
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")

    if not all([token_str, new_password, confirm_password]):
        return Response({
            "error": "Token, new password and confirm password are required."
        }, status=400)

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=400)

    if len(new_password) < 8:
        return Response({
            "error": "Password must be at least 8 characters."
        }, status=400)

    token_hash = hashlib.sha256(token_str.encode()).hexdigest()

    try:
        reset_token = PasswordResetToken.objects.get(token_hash=token_hash)
    except PasswordResetToken.DoesNotExist:
        return Response({"error": "Invalid reset link."}, status=400)

    if reset_token.expires_at < timezone.now():
        reset_token.delete()
        return Response({"error": "Reset link has expired."}, status=400)

    if reset_token.is_used:
        return Response({"error": "Reset link has already been used."}, status=400)

    # Set new password
    user = reset_token.user
    user.set_password(new_password)
    user.save()

    # Invalidate token
    reset_token.is_used = True
    reset_token.save()

    # Invalidate all existing auth tokens so old sessions are kicked out
    Token.objects.filter(user=user).delete()

    AuditLog.objects.create(
        firm=user.firm,
        user=user,
        action="password_reset",
        model_type="user",
        model_id=user.id,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return Response({"message": "Password reset successfully. Please log in."})
