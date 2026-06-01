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

# Create your views here.


@csrf_exempt
def get_all_clients(request):


    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        url = f"{host_url(request)}{reverse_lazy('get_all_clients_api')}"

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
        return JsonResponse(
            {
            "status": "success",
            "data": response_data
        }, status=200)
    

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    
@csrf_exempt
def create_client(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        data = json.loads(request.body)

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone = data.get("phone")

        if not all([first_name, last_name]):
            return JsonResponse({
                "status": "error",
                "message": "Missing required fields"
            }, status=400)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_client_api')}"

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=201)

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)



@csrf_exempt
def create_case(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        data = json.loads(request.body)
        title = data.get("title")
        client_id = data.get("client_id")
        case_number = data.get("case_number")
        status_value = data.get("status")
        deadline = data.get("deadline")
        description = data.get("description")
        matter_type = data.get("matter_type")


        if not title or not client_id:
            return JsonResponse({
                "status": "error",
                "message": "Title and client are required"
            }, status=400)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_case_api')}"

        # payload = {
        #     "title": title,
        #     "client_id": client_id,
        #     "case_number": case_number,
        #     "status": status_value,
        #     "deadline": deadline,
        #     "description": description,
        #     "matter_type": matter_type
        payload = {
            "title": title,
            "client": client_id,  # <-- Change from client_id to client
            "status": status_value,
            "deadline": deadline,
            "description": description,
            "matter_type": matter_type
        }
        # }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=201)

    except Exception as e:

        print("❌ Error:", str(e))

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def get_all_matter_types(request):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        url = f"{host_url(request)}{reverse_lazy('get_all_matter_types_api')}"
        auth_header = request.headers.get("Authorization")

        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header

        response_data = api_connection(method="GET", url=url, headers=headers)

        # ✅ HANDLE LIST (this is the fix)
        if isinstance(response_data, list):
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        # ✅ HANDLE DICT
        if isinstance(response_data, dict):
            return JsonResponse({
                "status": "success",
                "data": response_data.get("data", [])
            }, status=200)

        # fallback
        return JsonResponse({
            "status": "success",
            "data": []
        }, status=200)

    except Exception as e:
        print("Internal Server Error:", str(e))
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)


@csrf_exempt
def create_matter_type(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        data = json.loads(request.body)

        name = data.get("name")  # ✅ FIXED

        if not name:
            return JsonResponse({
                "status": "error",
                "message": "Name is required"
            }, status=400)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_matter_type_api')}"

        payload = {
            "name": name  # ✅ FIXED
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=201)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@csrf_exempt
def get_all_cases(request):


    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        url = f"{host_url(request)}{reverse_lazy('get_all_cases_api')}"

        auth_header = request.headers.get("Authorization")

        headers = {
            "Content-Type": "application/json"
        }

        if auth_header:
            headers["Authorization"] = auth_header

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        # Handle list response directly (DRF returns array)
        if isinstance(response_data, list):
            return JsonResponse({
                "status": "success",
                "data": response_data
            }, status=200)

        return JsonResponse({
            "status": "error",
            "message": "Unexpected response format"
        }, status=400)

    except Exception as e:
        print("❌ Error fetching cases:", str(e))

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@csrf_exempt
def get_case_details(request, case_id):

    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        # 👇 IMPORTANT: pass case_id into URL
        url = f"{host_url(request)}{reverse_lazy('get_case_detail_api', args=[case_id])}"
        
        headers = {
            "Content-Type": "application/json",
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
        }, status=200)

    except Exception as e:

        print("❌ Error:", str(e))

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@csrf_exempt
def update_case(request, case_id):

    if request.method != "PATCH":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_case_api', args=[case_id])}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="PATCH",
            url=url,
            headers=headers,
            data=data
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@csrf_exempt
def get_firm_members(request):

    if request.method != "GET":
        return JsonResponse({"status": "error"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse_lazy('get_firm_members_api')}"

        headers = {
            "Content-Type": "application/json",
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
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def assign_to_case(request, case_id):

    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse_lazy('assign_to_case_api', args=[case_id])}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=data
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def add_note(request, case_id):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        data = json.loads(request.body)

        content = data.get("content")
        is_pinned = data.get("is_pinned", False)

        if not content:
            return JsonResponse({
                "status": "error",
                "message": "Note content is required"
            }, status=400)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('add_note_api', kwargs={'case_id': case_id})}"

        payload = {
            "content": content,
            "is_pinned": is_pinned
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            data=payload
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=201)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def get_case_notes(request, case_id):

    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token required"
            }, status=401)

        url = f"{host_url(request)}{reverse_lazy('get_case_notes_api', kwargs={'case_id': case_id})}"

        headers = {
            "Content-Type": "application/json",
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
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def add_time_log(request, case_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)

        if not all([data.get('date'), data.get('duration'), data.get('description')]):
            return JsonResponse({"error": "date, duration and description are required."}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse('add_time_log_api', args=[case_id])}"

        response_data = api_connection(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header},
            data={
                "date": data.get("date"),
                "duration": data.get("duration"),
                "activity_type": data.get("activity_type", "other"),
                "description": data.get("description"),
                "is_billable": data.get("is_billable", True),
            }
        )
        return JsonResponse({"status": "success", "data": response_data}, status=201)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_time_logs(request, case_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse('list_time_logs_api', args=[case_id])}"
        response_data = api_connection(
            method="GET",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header}
        )
        return JsonResponse({"status": "success", "data": response_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_time_log(request, case_id, log_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse('update_time_log_api', args=[case_id, log_id])}"
        payload = {k: v for k, v in {
            "date": data.get("date"),
            "duration": data.get("duration"),
            "activity_type": data.get("activity_type"),
            "description": data.get("description"),
            "is_billable": data.get("is_billable"),
        }.items() if v is not None}

        response_data = api_connection(
            method="PATCH",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header},
            data=payload
        )
        return JsonResponse({"status": "success", "data": response_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def delete_time_log(request, case_id, log_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse('delete_time_log_api', args=[case_id, log_id])}"
        response_data = api_connection(
            method="DELETE",
            url=url,
            headers={"Content-Type": "application/json", "Authorization": auth_header}
        )
        return JsonResponse({"status": "success", "data": response_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)