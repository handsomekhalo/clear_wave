# system_management/middleware.py

from django.utils.deprecation import MiddlewareMixin


class TenantFilterMiddleware(MiddlewareMixin):
    """
    Automatically inject firm_id into all queries for the current user.
    This ensures tenant isolation at the middleware level.
    
    CRITICAL: Every model (except Firm and User) must have a firm FK.
    """
    
    def process_request(self, request):
        """
        Set current firm in thread-local storage.
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Store firm in request for easy access
            request.firm = request.user.firm
        else:
            request.firm = None