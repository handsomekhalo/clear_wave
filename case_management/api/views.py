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

from case_management.api.serializers import AddNoteSerializer, AssignToCaseSerializer, ChangeStatusSerializer, CreateCaseSerializer, CreateClientSerializer, GetCaseDetailSerializer, GetCaseListSerializer, MatterTypeSerializer, UpdateCaseSerializer
from case_management.models import Case, CaseType
from system_management.case_permissions import CanAccessCase




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_client_api(request):
    """
    Create a new client for the current firm.
    Only Firm Owner and Lawyer can create clients.
    """

    if request.user.role not in ["super_admin", "firm_owner", "lawyer", "assistant"]:
        return Response(
            {"error": "You do not have permission to create clients."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CreateClientSerializer(
        data=request.data,
        context={"request": request}
    )

    if serializer.is_valid():
        client = serializer.save()
        return Response(
            {
                "message": "Client created successfully.",
                "client_id": client.id,
                "email": client.email
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_case_api(request):
    """
    Create a new case for a specific client (Firm Owner or Lawyer only)
    """
    if request.user.role not in ['super_admin', 'firm_owner', 'lawyer', 'assistant']:
        return Response(
            {"error": "You do not have permission to create a case."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CreateCaseSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Default status
       
        # Save case
        case = serializer.save(
            firm=request.user.firm,
            created_by=request.user,
        )


        return Response(
            {
                "message": "Case created successfully.",
                "case_id": case.id,
                "client": case.client.email,
                "title": case.title,
                "status": case.status,
                "status_display": case.get_status_display()
            },
            status=status.HTTP_201_CREATED
)

        # return Response(
        #     {
        #         "message": "Case created successfully.",
        #         "case_id": case.id,
        #         "client": case.client.email,
        #         "title": case.title,
        #         "status": case.status.name
        #     },
        #     status=status.HTTP_201_CREATED
        # )

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
            "status": case.status.name
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

    matter_types = CaseType.objects.filter(
        firm=request.user.firm
    )

    serializer = MatterTypeSerializer(matter_types, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessCase])
def case_detail_api(request, pk):
    # case = get_object_or_404(Case, pk=pk)
    case = get_object_or_404( Case,pk=pk,
    firm=request.user.firm
)

    permission = CanAccessCase()
    if not permission.has_object_permission(request, None, case):
        return Response(status=403)

    serializer = GetCaseDetailSerializer(case)
    return Response(serializer.data)



@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_case_api(request, pk):

    case = get_object_or_404(
        Case,
        pk=pk,
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
def assign_to_case_api(request, pk):
    """
    Assign lawyer or assistant to a case.

    Rules:
    - Firm Owner can assign lawyer or assistant
    - Lawyer can assign assistant (only on their own case)
    """

    case = get_object_or_404(
        Case,
        pk=pk,
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

        if target_user.role in ["lawyer", "firm_owner"]:
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
def change_status_api(request, pk):

    case = get_object_or_404(
        Case,
        pk=pk,
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
def add_note_api(request, pk):

    case = get_object_or_404(
        Case,
        pk=pk,
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