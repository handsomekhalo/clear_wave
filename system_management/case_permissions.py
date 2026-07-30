from system_management import permissions



from rest_framework import permissions


class CanCreateCase(permissions.BasePermission):
    """
    Firm owner and lawyer can create cases.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            user.role in ['super_admin', 'firm_owner', 'lawyer']
        )



class CanAccessCase(permissions.BasePermission):
    """
    Controls who can view a specific case.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        # Super admin bypass
        if user.role == 'super_admin':
            return True

        # Must belong to same firm
        if obj.firm != user.firm:
            return False

        # Firm owner = access all
        if user.role == 'firm_owner':
            return True

        # Lawyer = assigned only
        if user.role == 'lawyer':
            return obj.assigned_lawyer == user

        # Assistant = assigned only
        if user.role == 'assistant':
            return obj.assigned_lawyer == user

        # Client = own case only
        if user.role == 'client':
            return obj.client == user

        return False




class CanModifyCase(permissions.BasePermission):
    """
    Controls who can update case fields.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == 'super_admin':
            return True

        if obj.firm != user.firm:
            return False

        if user.role == 'firm_owner':
            return True

        if user.role == 'lawyer' and obj.assigned_lawyer == user:
            return True

        return False


class CanCloseCase(permissions.BasePermission):
    """
    Only firm owner or assigned lawyer can close.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == 'super_admin':
            return True

        if obj.firm != user.firm:
            return False

        if user.role == 'firm_owner':
            return True

        if user.role == 'lawyer' and obj.assigned_lawyer == user:
            return True

        return False
    


class CanAssignLawyer(permissions.BasePermission):
    """
    Only firm owner can assign or reassign lawyers.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        return (
            user.is_authenticated and
            user.role in ['super_admin', 'firm_owner'] and
            obj.firm == user.firm
        )


class CanAddNote(permissions.BasePermission):
    """
    Owner, assigned lawyer, or assigned assistant can add notes.
    Client cannot.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == 'super_admin':
            return True

        if obj.firm != user.firm:
            return False

        if user.role == 'firm_owner':
            return True

        if user.role == 'lawyer' and obj.assigned_lawyer == user:
            return True

        if user.role == 'assistant' and obj.assigned_lawyer == user:
            return True

        return False


class CanUploadDocument(permissions.BasePermission):
    """
    Controls document upload access.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == 'super_admin':
            return True

        if obj.firm != user.firm:
            return False

        if user.role == 'firm_owner':
            return True

        if user.role == 'lawyer' and obj.assigned_lawyer == user:
            return True

        if user.role == 'assistant' and obj.assigned_lawyer == user:
            return True

        if user.role == 'client' and obj.client == user:
            return True

        return False
# class CanAccessCase(permissions.BasePermission):
#     """
#     Object-level permission for cases.
#     Enforces role + ownership + tenant isolation.
#     """

#     def has_object_permission(self, request, view, obj):
#         user = request.user

#         if not user.is_authenticated:
#             return False

#         # Super admin bypass
#         if user.role == 'super_admin':
#             return True

#         # Must be same firm
#         if obj.firm != user.firm:
#             return False

#         # Firm owner can access all cases in firm
#         if user.role == 'firm_owner':
#             return True

#         # Lawyer can access assigned cases only
#         if user.role == 'lawyer':
#             return obj.assigned_lawyer == user

#         # Assistant (if later you formalize assignment)
#         if user.role == 'assistant':
#             return obj.assigned_lawyer == user  # temporary logic

#         # Client can access own case only
#         if user.role == 'client':
#             return obj.client == user

#         return False