"""
This module contains the check_token_in_session decorator for views.
"""
from django.shortcuts import redirect
from datetime import datetime
from system_management.models import User
from rest_framework.authtoken.models import Token



def check_token_in_session(view_func):
    """
    Decorator for views that checks if the user is logged in.
    """
    def wrapper_view(request, *args, **kwargs):
        token = request.session.get('token')

        if token:
            try:
                response = view_func(request, *args, **kwargs)
                return response
            except Exception as e:
                print('Error in view function:', str(e))
                raise
        else:
            return redirect('login_view')
    return wrapper_view


def otp_required(view_func):

    def wrapped_view(request, *args, **kwargs):

        valid_otp = request.session.get("pin")

        if not valid_otp:
            return redirect('login_view')

        response = view_func(request, *args, **kwargs)

        if response is None:
            return redirect('login_view')

        return response

    return wrapped_view


def session_timeout(view_func):
    """
    Decorator to manage user session activity based on inactivity.

    This decorator checks if the user is authenticated. If authenticated, it checks the
    last activity time stored in the session. If the last activity was more than the specified
    number of minutes (default 30 minutes) ago, the user session is invalidated, and a response
    indicating session timeout is returned. Otherwise, it updates the last activity time to
    the current time.

    Args:
        minutes (int): The number of minutes of inactivity after which the session expires.
    
    Returns:
        function: The wrapped view function.
    """

    def wrapped_view(request, *args, **kwargs):
        user = request.session.get('user_id')
        if user:
            now = datetime.now()
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
                if (now - last_activity_time).seconds > 30*60:
                    # Invalidate the session
                    request.session.flush()
                    return redirect('login_view')
            request.session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        return view_func(request, *args, **kwargs)
    return wrapped_view