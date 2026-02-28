# system_management/permissions.py

from rest_framework import permissions

# system_management/permissions.py


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission class: Only super admins can access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'super_admin'
        )


class IsFirmOwner(permissions.BasePermission):
    """
    Permission class: Only firm owners can access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['firm_owner', 'super_admin']
        )


class IsSameFirm(permissions.BasePermission):
    """
    Permission class: User can only access resources from their own firm.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Super admin can access all
        if request.user.role == 'super_admin':
            return True
        
        # Check if object has firm attribute
        if hasattr(obj, 'firm'):
            return obj.firm == request.user.firm
        
        # If object IS a firm
        if obj.__class__.__name__ == 'Firm':
            return obj == request.user.firm
        
        # If object IS a user
        if obj.__class__.__name__ == 'User':
            return obj.firm == request.user.firm
        
        return False


class CanManageCase(permissions.BasePermission):
    """
    Permission class: User can manage cases.
    Firm owner, lawyer can manage. Assistant and client cannot.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['super_admin', 'firm_owner', 'lawyer']
        )
    
    def has_object_permission(self, request, view, obj):
        # Must be same firm
        if not IsSameFirm().has_object_permission(request, view, obj):
            return False
        
        # Firm owner and lawyer can manage
        return request.user.role in ['super_admin', 'firm_owner', 'lawyer']

class IsAdminUserType(permissions.BasePermission):
    """
    Custom permission to only allow access to users with the 'Admin' user type.
    """
    message = 'Access denied. Only users with the Admin role are permitted to update their profile here.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        user_type_name = getattr(request.user.role, 'name', None)
        return user_type_name == 'Admin'


class CanViewAuditLogs(permissions.BasePermission):
    def has_permission(self, request, view):
        # allowed = ['super_admin', 'firm_owner', 'lawyer']
        allowed_roles = {'super_admin', 'firm_owner', 'lawyer', 'assistant'}

        return request.user.is_authenticated and request.user.role in allowed_roles
    

    

class CanAccessCaseDocuments(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, case):
        if request.user.role in ['super_admin', 'firm_owner']:
            return True
        if request.user.role == 'lawyer':
            return case.assigned_lawyer == request.user
        if request.user.role == 'assistant':
            return case.assigned_assistant == request.user
        if request.user.role == 'client':
            return case.client == request.user
        return False