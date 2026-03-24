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

# Create your views here.


@csrf_exempt
def upload_documents(request, case_id):

    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        print('auth_header ', auth_header)

        url = f"{host_url(request)}{reverse_lazy('upload_document_api', args=[case_id])}"
        print('url', url)

        headers = {
            "Authorization": auth_header
        }

        print('headers', headers)

        # ✅ DEBUG PROPERLY
        print("FILES:", request.FILES)
        print("POST:", request.POST)

        response_data = api_connection(
            method="POST",
            url=url,
            headers=headers,
            files=request.FILES,   # ✅ FILES go here
            data=request.POST      # ✅ form fields go here
        )

        return JsonResponse({
            "status": "success",
            "data": response_data
        }, status=200)

    except Exception as e:
        print("UPLOAD ERROR:", str(e))  # 👈 ADD THIS
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
def get_documents(request, case_id):

    if request.method != "GET":
        return JsonResponse({"status": "error"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse_lazy('get_documents_api', args=[case_id])}"

        headers = {
            "Authorization": auth_header
        }

        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers
        )

        print('doc response data', response_data)

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
def view_document(request, document_id):

    if request.method != "GET":
        return JsonResponse({"status": "error"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        url = f"{host_url(request)}{reverse_lazy('view_document_api', args=[document_id])}"

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