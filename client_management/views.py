from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.urls import path, re_path
from system_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
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
from system_management.general_func_classes import api_connection, host_url
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

import traceback
from rest_framework.response import Response



@csrf_exempt
def client_case_detail(request, case_id):

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse('client_case_detail_api', args=[case_id])}"

        headers = {
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)




@csrf_exempt
def list_client_cases(request):

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse('list_client_cases_api')}"

        headers = {
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@csrf_exempt
def list_case_messages(request, case_id):

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse('list_case_messages_api', args=[case_id])}"

        headers = {
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@csrf_exempt
def list_client_documents(request, case_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse('list_client_documents_api', args=[case_id])}"

        headers = {
            "Authorization": auth_header
        }

        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()

        print(f"Received response with status {response.status_code} for documents API")
        return JsonResponse({
            "status": "success",
            "data": response.json()
        },
        print(f"Response JSON: {response.json()}")
        )
    

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------
 
@csrf_exempt
def request_magic_link(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)
 
        url = f"{host_url(request)}{reverse('request_magic_link_api')}"
        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            data={"email": email}
        )

        print(f"Magic link request response: {response_data}")  # Debug log
        return JsonResponse({"status": "success", "data": response_data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
 
 
@csrf_exempt
def sign_in_with_link(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        token = data.get("token")
        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)
 
        url = f"{host_url(request)}{reverse('sign_in_with_link_api')}"
        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            data={"token": token}
        )
        return JsonResponse({"status": "success", "data": response_data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
 
 
# ---------------------------------------------------------------------------
# MESSAGING
# ---------------------------------------------------------------------------
 
@csrf_exempt
def send_case_message(request, case_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        content = data.get("content")
        if not content:
            return JsonResponse({"error": "Message content is required"}, status=400)
 
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)
 
        url = f"{host_url(request)}{reverse('send_case_message_api', args=[case_id])}"
        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header},
            data={"content": content}
        )
        return JsonResponse({"status": "success", "data": response_data}, status=201)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
 
 
@csrf_exempt
def mark_message_read(request, message_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)
 
        url = f"{host_url(request)}{reverse('mark_message_read_api', args=[message_id])}"
        response_data = api_connection(
            method="PATCH",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header}
        )
        return JsonResponse({"status": "success", "data": response_data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
 
 
# ---------------------------------------------------------------------------
# CLIENT FORMS
# Aggregates form assignments across all client cases.
# Feeds FormsList.js on the client dashboard.
# ---------------------------------------------------------------------------
 
@csrf_exempt
def list_client_form_assignments(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse('list_client_form_assignments_api')}"

        headers = {
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500) 
 
# ---------------------------------------------------------------------------
# DEBUG — remove before production
# ---------------------------------------------------------------------------
 
@csrf_exempt
def debug_me(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)
 
        url = f"{host_url(request)}{reverse('debug_me')}"
        response_data = api_connection(
            method="GET",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header}
        )
        return JsonResponse({"status": "success", "data": response_data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def client_upload_document(request, case_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse('client_upload_document_api', args=[case_id])}"

        # Forward as multipart — don't use api_connection here
        # api_connection sends JSON, files need multipart
        import requests as req
        response = req.post(
            url,
            files={"file": request.FILES.get("file")},
            data={"description": request.POST.get("description", "")},
            headers={"Authorization": auth_header},
            timeout=60
        )
        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)