import threading
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

from case_management.api.serializers import AddNoteSerializer, AssignToCaseSerializer, ChangeStatusSerializer, CreateCaseSerializer, CreateClientSerializer, CreateMatterTypeSerializer, GetAllClientsSerializer, GetCaseDetailSerializer, GetCaseListSerializer, MatterTypeSerializer, UpdateCaseSerializer
from case_management.models import Case, CaseType
from system_management.case_permissions import CanAccessCase
from system_management.general_func_classes import _send_email_thread
from system_management.models import AuditLog, User



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_client_api(request):

    if request.user.role not in ["super_admin", "firm_owner", "lawyer", "assistant"]:
        return Response(
            {"error": "You do not have permission to create clients."},
            status=status.HTTP_403_FORBIDDEN
        )
    print('serializing')
    serializer = CreateClientSerializer(
        data=request.data,
        context={"request": request}
    )

    if serializer.is_valid():
        print('valid seroa;zoer')

        client = serializer.save()

        # Audit Log
        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="client_created",
            model_type="client",
            model_id=client.id,
            changes={
                "first_name": client.first_name,
                "last_name": client.last_name,
                "email": client.email
            },
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response(
            {
                "message": "Client created successfully.",
                "client_id": client.id,
                "email": client.email,
                "phone": client.phone,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "password": client.generated_password
    
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_client_api(request):
#     """
#     Create a new client for the current firm.
#     Only Firm Owner and Lawyer can create clients.
#     """

#     if request.user.role not in ["super_admin", "firm_owner", "lawyer", "assistant"]:
#         return Response(
#             {"error": "You do not have permission to create clients."},
#             status=status.HTTP_403_FORBIDDEN
#         )

#     serializer = CreateClientSerializer(
#         data=request.data,
#         context={"request": request}
#     )

#     if serializer.is_valid():
#         client = serializer.save()
#         return Response(
#             {
#                 "message": "Client created successfully.",
#                 "client_id": client.id,
#                 "email": client.email,
#                 'phone':client.phone,
#                 "first_name": client.first_name,
#                 "last_name": client.last_name,
#             },
#             status=status.HTTP_201_CREATED
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_case_api(request):

    if request.user.role not in ['super_admin', 'firm_owner', 'lawyer', 'assistant']:
        return Response(
            {"error": "You do not have permission to create a case."},
            status=status.HTTP_403_FORBIDDEN
        )
    print('serializing')
    serializer = CreateCaseSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        print('valid serializer')

        case = serializer.save(
            firm=request.user.firm,
            created_by=request.user,
            assigned_lawyer=request.user if request.user.role in ['lawyer', 'firm_owner'] else None,
        )

        # Audit Log
        AuditLog.objects.create(
            firm=request.user.firm,
            user=request.user,
            action="case_created",
            model_type="case",
            model_id=case.id,
            changes={
                "title": case.title,
                "status": case.status,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response(
            {
                "message": "Case created successfully.",
                "case_id": case.id,
                "title": case.title,
                "status": case.status,
                "status_display": case.get_status_display()
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_clients_api(request):
    
    # Check user has a firm
    if not request.user.firm:
        return Response(
            {'error': 'You are not associated with any firm.'},
            status=403
        )
    
    # Get only clients from user's firm
    clients = User.objects.filter(
        firm=request.user.firm,
        role=User.CLIENT,  # Use constant instead of string
        is_active=True,
        deleted_at__isnull=True  # Exclude soft-deleted
    ).order_by("first_name")

    serializer = GetAllClientsSerializer(clients, many=True)

    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_matter_type_api(request):
    if request.user.role not in ['super_admin', 'firm_owner', 'lawyer', 'assistant']:
        return Response(
            {'error': 'You do not have permission to create matter types.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not request.user.firm:
        return Response(
            {'error': 'You must be associated with a firm to create matter types.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    

    serializer = CreateMatterTypeSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        matter_type = serializer.save()
        return Response(
            {
                'message': 'Matter type created successfully.',
                'id': matter_type.id,
                'name': matter_type.name
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_cases_by_firm_api(request):
    """
    Firm dashboard case list.
    """

    user = request.user

    # Base queryset (TENANT ISOLATION)
    queryset = Case.objects.filter(firm=user.firm)

    # Role filtering
    if user.role == "firm_owner":
        cases = queryset

    elif user.role == "lawyer":
        cases = queryset.filter(
            assigned_lawyer=user
        ) | queryset.filter(
            created_by=user
        )

    elif user.role == "assistant":
        cases = queryset.filter(
            assigned_assistant=user
        )

    elif user.role == "client":
        cases = queryset.filter(
            client=user
        )

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

    data = [
        {
            "id": case.id,
            "title": case.title,
            # "status": case.status.name
            "status": case.status  # It's already a string

        }
        for case in cases.distinct()
    ]

    return Response(data, status=status.HTTP_200_OK)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_matter_types_api(request):
    """
    Get matter types for current firm only.
    """

    if not request.user.firm:
            return Response(
                {'error': 'You are not associated with a firm.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    matter_types = CaseType.objects.filter(
        firm=request.user.firm
    )

    serializer = MatterTypeSerializer(matter_types, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessCase])
def case_detail_api(request, case_id):
    print('case detail api called')
    
    # Only filter by pk — let CanAccessCase handle firm & access check
    case = get_object_or_404(Case, pk=case_id)
    
    print('case -----', case)

    permission = CanAccessCase()
    print('permissions')
    if not permission.has_object_permission(request, None, case):
        return Response(status=403)

    serializer = GetCaseDetailSerializer(case)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_case_api(request, case_id):

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    # Permission logic
    if request.user.role == "firm_owner":
        pass

    elif request.user.role == "lawyer":
        if case.assigned_lawyer != request.user:
            return Response({"error": "Not your case."}, status=403)

    else:
        return Response({"error": "Permission denied."}, status=403)

    serializer = UpdateCaseSerializer(
        case,
        data=request.data,
        partial=True,
        context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Case updated successfully."})

    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_to_case_api(request, case_id):
    """
    Assign lawyer or assistant to a case.

    Rules:
    - Firm Owner can assign lawyer or assistant
    - Lawyer can assign assistant (only on their own case)
    """

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    serializer = AssignToCaseSerializer(
        data=request.data,
        context={"request": request, "case": case}
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    target_user = serializer.validated_data["target_user"]

    # ===== ROLE LOGIC =====

    # Firm Owner
    if request.user.role == "firm_owner":

        if target_user.role in ["lawyer"]:
            case.assigned_lawyer = target_user
            case.save()
            return Response({"message": "Lawyer assigned successfully."})

        if target_user.role == "assistant":
            case.assigned_assistant = target_user  # only if model supports it
            case.save()
            return Response({"message": "Assistant assigned successfully."})

        return Response({"error": "Invalid role for assignment."}, status=403)

    # Lawyer
    if request.user.role == "lawyer":

        # Must be assigned lawyer on this case
        if case.assigned_lawyer != request.user:
            return Response({"error": "You are not assigned to this case."}, status=403)

        if target_user.role == "assistant":
            case.assigned_assistant = target_user  # if exists
            case.save()
            return Response({"message": "Assistant assigned successfully."})

        return Response({"error": "Lawyers can only assign assistants."}, status=403)

    return Response({"error": "You do not have permission."}, status=403)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessCase])
def get_all_cases_api(request):
    user = request.user
    queryset = Case.objects.none()

    # Role-based filtering
    if user.role == 'firm_owner':
        queryset = Case.objects.filter(firm=user.firm)
    elif user.role == 'lawyer':
        queryset = Case.objects.filter(assigned_lawyer=user)
    elif user.role == 'assistant':
        # Assuming you added assistant field to Case
        queryset = Case.objects.filter(assigned_assistant=user)
    elif user.role == 'client': 
        queryset = Case.objects.filter(client=user)

    serializer = GetCaseListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_status_api(request, case_id):

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    # Permission
    if request.user.role == "firm_owner":
        pass

    elif request.user.role == "lawyer":
        if case.assigned_lawyer != request.user:
            return Response({"error": "Not your case."}, status=403)

    else:
        return Response({"error": "Permission denied."}, status=403)

    serializer = ChangeStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    new_status = serializer.validated_data["status"]

    # Use model logic
    if new_status == Case.CLOSED:
        case.close()
    elif case.status == Case.CLOSED and new_status != Case.CLOSED:
        case.reopen()
        case.status = new_status
        case.save()
    else:
        case.status = new_status
        case.save()

    return Response({
        "message": "Status updated.",
        "status": case.status,
        "status_display": case.get_status_display()
    })




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_note_api(request, case_id):

    case = get_object_or_404(
        Case,
        pk=case_id,
        firm=request.user.firm
    )

    # Permission
    if request.user.role == "firm_owner":
        pass

    elif request.user.role == "lawyer":
        if case.assigned_lawyer != request.user:
            return Response({"error": "Not your case."}, status=403)

    elif request.user.role == "assistant":
        if case.assigned_assistant != request.user:
            return Response({"error": "Not your case."}, status=403)

    else:
        return Response({"error": "Permission denied."}, status=403)

    serializer = AddNoteSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(
            case=case,
            created_by=request.user
        )
        return Response({"message": "Note added successfully."})

    return Response(serializer.errors, status=400)