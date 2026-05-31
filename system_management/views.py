# Create your views here.
from django.conf import settings # Ensure this import is at the top

import json
import secrets
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.middleware.csrf import get_token
import requests
# from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
# from system_management.general_func_classes import _send_email_thread, api_connection, host_url
from system_management.models import User
from django.http import JsonResponse
import json # You're using json.dumps, so ensure this is imported
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
import json
import requests
# from rest_framework import status # Import DRF status codes for clarity
# from . import constants # Ensure constants module is correctly imported for JSON_APPLICATION
import logging
logger = logging.getLogger(__name__)
import threading
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
# from .decorators import session_timeout, check_token_in_session
from .decorators import check_token_in_session, otp_required, session_timeout
from .general_func_classes import _send_email_thread, api_connection, host_url
import traceback
from rest_framework.response import Response


@ensure_csrf_cookie
def csrf(request):
    """
    Sets the CSRF cookie and returns the token
    """
    token = get_token(request)

    return JsonResponse({'csrfToken': token})


def get_data_on_success(response_data):
    status = response_data.get('status')
    if status == 'success':
        data = response_data.get('data')
    else:
        data = []
    return data


def generate_password(length=12, include_digits=True, include_special_chars=True):
    letters = string.ascii_letters
    digits = string.digits if include_digits else ''
    special_chars = string.punctuation if include_special_chars else ''

    characters = letters + digits + special_chars

    length = max(length, 8)

    password = ''.join(secrets.choice(characters) for _ in range(length))

    return password



def set_csrf_token(request):
     response = JsonResponse({'detail': 'CSRF cookie set'})
     response.set_cookie('csrftoken', get_token(request)) 
     return response



# View that redirects to Next.js
def login_view(request):
    return redirect("http://localhost:3000/")  # Next.js is running here
    # return redirect('http://52.14.111.23:3000/')  # or your real domain



@ensure_csrf_cookie  # This ensures the CSRF cookie is set
def login(request):
    """User login function with API."""
    if request.method != "POST":
        return JsonResponse({
            'status': 'error', 
            'message': 'Only POST requests are allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        # remember_me = data.get('rememberMe', False)

        if not email or not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Email and password are required'
            }, status=400)

        # Get the existing token if any
        token = request.session.get('token')
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Token {token}" if token else ""
        }

        payload = json.dumps({
            'email': email,
            'password': password,
            # 'remember_me': remember_me
        })

        url = f"{host_url(request)}{reverse_lazy('login_api')}"
        
        try:
            response_data = requests.post(
                url, 
                headers=headers, 
                data=payload, 
                timeout=10
            )
            
            if response_data.status_code == 200:
                response_json = response_data.json()
                
                # Store token in session if remember_me is True
                # if remember_me and 'token' in response_json:
                #     request.session['token'] = response_json['token']
                
                return JsonResponse({
                    'status': 'success', 
                    'data': response_json
                })
            
            
            return JsonResponse({
                'status': 'error',
                'message': response_data.json().get('message', 'Login failed'),
            }, status=response_data.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'status': 'error',
                'message': f'API request failed: {str(e)}'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error', 
            'message': 'Invalid JSON data'
        }, status=400)



@csrf_exempt
def register_firm_owner(request):
    print("🟢 Register Firm Owner proxy called")

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        # Parse request body
        data = json.loads(request.body)

        first_name = data.get("first_name")
        last_name  = data.get("last_name")
        email      = data.get("email")
        password   = data.get("password")

        # Basic validation
        if not all([first_name, last_name, email, password]):
            return JsonResponse({
                "status": "error",
                "message": "All fields are required."
            }, status=400)

        # Build DRF API URL
        url = f"{host_url(request)}{reverse_lazy('register_firm_owner_api')}"

        payload = json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

        headers = {
            "Content-Type": "application/json"
        }

        # Forward request to DRF API
        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        if response_data and response_data.get("status") == "success":
            return JsonResponse({
                "status": "success",
                "message": "Firm owner registered successfully",
                "data": response_data.get("data")
            }, status=201)

        return JsonResponse({
            "status": "error",
            "message": response_data.get("message", "Registration failed"),
            "errors": response_data.get("errors", {})
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error occurred: {str(e)}"
        }, status=500)


@csrf_exempt
def firm_onboarding_step_1(request):
    """
    Proxy for firm onboarding step 1.
    """

    print("🟢 Firm onboarding STEP 1 called")

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        auth_header = request.headers.get("Authorization", "")
        token = None

        if auth_header.startswith("Token "):
            token = auth_header.split("Token ")[-1]
        elif auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[-1]

        if not token:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required."
            }, status=401)

        # ✅ Use request.data if available (DRF) or decode JSON safely
        if hasattr(request, "data"):
            body = request.data  # DRF parses automatically
        else:
            try:
                body = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid JSON in request body."
                }, status=400)

        print(f"Received onboarding step 1 data: {body}")  # Debugging line

        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }

        print('headers',headers)

        # url_path = reverse_lazy("onboarding_step_1_api")
        # print('path to our url  ', url_path)  # Debugging line   
        # api_url = f"{host_url(request)}{url_path}"

        url = f"{host_url(request)}{reverse_lazy('onboarding_step_1_api')}"

 

        print('api_url',url)

        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )

        print(f"API response status: {response.status_code}")
        print(f"API response text: {response.text}")  # <-- important

        if response.status_code not in [200, 201]:
            return JsonResponse({
                "status": "error",
                "message": "API error",
                "details": response.text
            }, status=response.status_code)

        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        traceback.print_exc()  # ← Add this line to your existing code
        return JsonResponse({"status": "error", "message": f"Server error: {str(e)}"}, status=500)


    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)
        

@csrf_exempt
def firm_onboarding_step_2(request):
    """
    Proxy for firm onboarding step 2.
    """

    print("🟢 Firm onboarding STEP 2 called")

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        auth_header = request.headers.get("Authorization", "")
        token = None

        if auth_header.startswith("Token "):
            token = auth_header.split("Token ")[-1]
        elif auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[-1]

        if not token:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required."
            }, status=401)

        body = json.loads(request.body or "{}")

        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }

        url_path = reverse_lazy("onboarding_step_2_api")
        api_url = f"{host_url(request)}{url_path}"

        response = requests.post(
            api_url,
            headers=headers,
            json=body,
            timeout=30
        )

        if response.status_code not in [200, 201]:
            return JsonResponse({
                "status": "error",
                "message": "API error",
                "details": response.text
            }, status=response.status_code)

        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }, status=500)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)


@csrf_exempt
def register_firm_owner(request):
    print("🟢 Register Firm Owner proxy called")

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        # Parse request body
        data = json.loads(request.body)

        first_name = data.get("first_name")
        last_name  = data.get("last_name")
        email      = data.get("email")
        password   = data.get("password")

        # Basic validation
        if not all([first_name, last_name, email, password]):
            return JsonResponse({
                "status": "error",
                "message": "All fields are required."
            }, status=400)

        # Build DRF API URL
        url = f"{host_url(request)}{reverse_lazy('register_firm_owner_api')}"

        payload = json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

        headers = {
            "Content-Type": "application/json"
        }

        # Forward request to DRF API
        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        if response_data and response_data.get("status") == "success":
            return JsonResponse({
                "status": "success",
                "message": "Firm owner registered successfully",
                "data": response_data.get("data")
            }, status=201)

        return JsonResponse({
            "status": "error",
            "message": response_data.get("message", "Registration failed"),
            "errors": response_data.get("errors", {})
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error occurred: {str(e)}"
        }, status=500)

@csrf_exempt
def get_firm_user_list(request):
    print("🟢 Firm User List proxy called")

    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        # Get token from request header
        auth_header = request.headers.get("Authorization", "")
        print('auth header', auth_header)
        token = None
        

        if auth_header.startswith("Token "):
            token = auth_header.split("Token ")[-1]
            print('token', token)
        elif auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[-1]
            print('bearer', token)


        if not token:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required."
            }, status=401)

        # Build DRF API URL
        url = f"{host_url(request)}{reverse_lazy('firm_user_list_api')}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        # Call DRF API
        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        if response_data:
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "Failed to retrieve users"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error occurred: {str(e)}"
        }, status=500)
    


from django.http import HttpResponse
from system_management.services.email_service import send_email


@csrf_exempt
def create_firm_user(request):
    print("🟢 Create Firm User proxy called")

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        role = data.get("role")
        phone = data.get("phone")

        if not all([first_name, last_name, email, role, phone]):
            return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        # Call DRF API
        url = f"{host_url(request)}{reverse_lazy('firm_user_create_api')}"
        
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "phone": phone
        }
        print('payload', payload)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        print('headers', headers)

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        # If successful, send email via SendGrid

        # If successful, send email via SendGrid
        if response_data and response_data.get("user"):
            try:
                print("in here to send email")
                password = response_data.get("password")
                print("password", password)
                firm_name = response_data.get("firm_name", "ClearWave")
                print("firm_name", firm_name)
                
                html_tpl_path = "email_temps/firm_user_invite.html"
                print("html path", html_tpl_path)
                subject = f"Welcome to {firm_name} - Your Account Details"
                print('subject', subject)
                
                context_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": role,
                    "password": password,
                    "firm_name": firm_name,
                    "login_url": f"{host_url(request)}"
                }
                print('context data', context_data)
                
                email_url = f"{host_url(request)}{reverse_lazy('send_email_api')}"
                print('email url is', email_url)
                
                email_payload = json.dumps({
                    "html_tpl_path": html_tpl_path,
                    "receiver_email": email,
                    "context_data": context_data,
                    "subject": subject
                })
                print('email payload', email_payload)
                
                # Send email in background thread
                thread = threading.Thread(
                    target=_send_email_thread,
                    args=(email_url, headers, email_payload)
                )
                print('thread created', thread)
                thread.start()
                print('thread started')
                
            except Exception as email_error:
                print(f"❌ Email error: {str(email_error)}")
                import traceback
                traceback.print_exc()
                # Don't fail user creation if email fails
            
            print('success response')
            return JsonResponse({
                "status": "success",
                "message": "User created and invitation sent",
                "data": response_data
            }, status=201)
       

        return JsonResponse({
            "status": "error",
            "message": "Failed to create user"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)


@csrf_exempt
def get_all_roles(request):
    print("🟢 Get All Roles proxy called")

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        url = f"{host_url(request)}{reverse_lazy('get_all_roles_api')}"
        auth_header = request.headers.get("Authorization")

        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header

        response_data = api_connection(method="GET", url=url, headers=headers)
        print("response_data", response_data)

        # Make sure response_data is a dict
        if isinstance(response_data, dict) and "data" in response_data:
            return JsonResponse({
                "status": "success",
                "data": response_data["data"]
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "Failed to fetch roles"
        }, status=400)

    except Exception as e:
        print("Internal Server Error:", str(e))
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)

@csrf_exempt
def firm_user_retrieve(request, user_id):

    print("🟢 Firm User Retrieve proxy called")

    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        url = f"{host_url(request)}{reverse_lazy('firm_user_retrieve_api', kwargs={'pk': user_id})}"

        auth_header = request.headers.get("Authorization")

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        if response_data:
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "User not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@csrf_exempt
def firm_user_update(request, user_id):

    print("🟢 Firm User Update proxy called")

    if request.method != "PATCH":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        body = json.loads(request.body)

        print('body', body)

        url = f"{host_url(request)}{reverse_lazy('firm_user_update_api', kwargs={'pk': user_id})}"
        print('url', url)
        auth_header = request.headers.get("Authorization")
        print('auth_header',auth_header)

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }
        
        response_data = api_connection(
            method="PATCH",
            url=url,
            headers=headers,
            data=body
            
        )

        print('response data', response_data)
        if response_data:
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "Update failed"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def firm_user_toggle_status(request, user_id):

    print("🟢 Firm User Toggle Status proxy called")

    if request.method != "PATCH":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        url = f"{host_url(request)}{reverse_lazy('firm_user_toggle_status_api', kwargs={'pk': user_id})}"

        auth_header = request.headers.get("Authorization")

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="PATCH",
            url=url,
            headers=headers
        )

        if response_data:
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "Status update failed"
        }, status=400)

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@csrf_exempt
def request_password_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email is required."}, status=400)

        url = f"{host_url(request)}{reverse('request_password_reset_api')}"
        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            data={"email": email}
        )
        return JsonResponse({"status": "success", "data": response_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def confirm_password_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        token = data.get("token")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not all([token, new_password, confirm_password]):
            return JsonResponse({
                "error": "Token, new password and confirm password are required."
            }, status=400)

        url = f"{host_url(request)}{reverse('confirm_password_reset_api')}"
        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            data={
                "token": token,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
        )
        return JsonResponse({"status": "success", "data": response_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)