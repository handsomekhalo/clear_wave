from django.shortcuts import render

from system_management.general_func_classes import api_connection, host_url

# Create your views here.
"""
ClearWave — forms_engine/proxy_views.py

Proxy views following exact ClearWave pattern from client_management.
One function, one thing. csrf_exempt, method check, auth check,
build payload, call api_connection, return JsonResponse.

Frontend (Next.js) → Proxy → API view → Database

NOTE: Replace 'your_app.utils' with wherever host_url and
api_connection actually live in your project.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy


# ---------------------------------------------------------------------------
# FORM TEMPLATES
# ---------------------------------------------------------------------------

@csrf_exempt
def create_form_template(request):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get("name")

        if not name:
            return JsonResponse({"status": "error", "message": "Template name is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_form_template_api')}"

        payload = {
            "name": name,
            "description": data.get("description"),
            "case_type": data.get("case_type"),
            "is_active": data.get("is_active", True),
        }

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_form_templates(request):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_form_templates_api')}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def get_form_template(request, template_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('get_form_template_api', kwargs={'template_id': template_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_form_template(request, template_id):

    if request.method != "PATCH":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_form_template_api', kwargs={'template_id': template_id})}"

        payload = {
            "name": data.get("name"),
            "description": data.get("description"),
            "case_type": data.get("case_type"),
            "is_active": data.get("is_active"),
        }

        # PATCH — only send fields that were actually provided
        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="PATCH", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# FORM SECTIONS
# ---------------------------------------------------------------------------

@csrf_exempt
def create_form_section(request, template_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get("name")

        if not name:
            return JsonResponse({"status": "error", "message": "Section name is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_form_section_api', kwargs={'template_id': template_id})}"

        payload = {
            "name": name,
            "description": data.get("description"),
            "order": data.get("order", 0),
            "is_active": data.get("is_active", True),
        }

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_form_sections(request, template_id):
    print('Listing sections for template_id:', template_id)  # Debug log

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        print('Authorization header:', auth_header)  # Debug log
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_form_sections_api', kwargs={'template_id': template_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_form_section(request, template_id, section_id):

    if request.method != "PATCH":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_form_section_api', kwargs={'template_id': template_id, 'section_id': section_id})}"

        payload = {
            "name": data.get("name"),
            "description": data.get("description"),
            "order": data.get("order"),
            "is_active": data.get("is_active"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="PATCH", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# QUESTION BANK
# ---------------------------------------------------------------------------

@csrf_exempt
def create_question(request):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        text = data.get("text")
        input_type = data.get("input_type")

        if not text or not input_type:
            return JsonResponse({"status": "error", "message": "text and input_type are required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('create_question_api')}"

        payload = {
            "text": text,
            "input_type": input_type,
            "is_required": data.get("is_required", True),
            "allow_other_option": data.get("allow_other_option", False),
            "helper_text": data.get("helper_text"),
        }

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_questions(request):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_questions_api')}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def get_question(request, question_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('get_question_api', kwargs={'question_id': question_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_question(request, question_id):

    if request.method != "PATCH":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_question_api', kwargs={'question_id': question_id})}"

        payload = {
            "text": data.get("text"),
            "input_type": data.get("input_type"),
            "is_required": data.get("is_required"),
            "is_active": data.get("is_active"),
            "allow_other_option": data.get("allow_other_option"),
            "helper_text": data.get("helper_text"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="PATCH", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# QUESTION OPTIONS
# ---------------------------------------------------------------------------

@csrf_exempt
def add_question_option(request, question_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        text = data.get("text")

        if not text:
            return JsonResponse({"status": "error", "message": "Option text is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('add_question_option_api', kwargs={'question_id': question_id})}"

        payload = {
            "text": text,
            "order": data.get("order", 0),
            "is_default": data.get("is_default", False),
        }

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_question_options(request, question_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_question_options_api', kwargs={'question_id': question_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_question_option(request, question_id, option_id):

    if request.method != "PATCH":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_question_option_api', kwargs={'question_id': question_id, 'option_id': option_id})}"

        payload = {
            "text": data.get("text"),
            "order": data.get("order"),
            "is_default": data.get("is_default"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="PATCH", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def delete_question_option(request, question_id, option_id):

    if request.method != "DELETE":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('delete_question_option_api', kwargs={'question_id': question_id, 'option_id': option_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="DELETE", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# SECTION QUESTION ASSIGNMENT
# ---------------------------------------------------------------------------

@csrf_exempt
def assign_question_to_section(request, template_id, section_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        question = data.get("question")

        if not question:
            return JsonResponse({"status": "error", "message": "question is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('assign_question_to_section_api', kwargs={'template_id': template_id, 'section_id': section_id})}"

        payload = {
            "question": question,
            "order": data.get("order", 0),
            "is_required_override": data.get("is_required_override"),
        }

        # is_required_override can legitimately be False — only strip None
        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_section_questions(request, template_id, section_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_section_questions_api', kwargs={'template_id': template_id, 'section_id': section_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_section_question(request, template_id, section_id, sq_id):

    if request.method != "PATCH":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('update_section_question_api', kwargs={'template_id': template_id, 'section_id': section_id, 'sq_id': sq_id})}"

        payload = {
            "order": data.get("order"),
            "is_required_override": data.get("is_required_override"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="PATCH", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def remove_question_from_section(request, template_id, section_id, sq_id):

    if request.method != "DELETE":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('remove_question_from_section_api', kwargs={'template_id': template_id, 'section_id': section_id, 'sq_id': sq_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="DELETE", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# CASE FORM ASSIGNMENT
# ---------------------------------------------------------------------------

@csrf_exempt
def assign_form_to_case(request, case_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        template = data.get("template")

        if not template:
            return JsonResponse({"status": "error", "message": "template is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('assign_form_to_case_api', kwargs={'case_id': case_id})}"

        payload = {
            "template": template,
            "due_date": data.get("due_date"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_case_form_assignments(request, case_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_case_form_assignments_api', kwargs={'case_id': case_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def get_case_form_assignment(request, case_id, assignment_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('get_case_form_assignment_api', kwargs={'case_id': case_id, 'assignment_id': assignment_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def review_case_form_assignment(request, case_id, assignment_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        status_value = data.get("status")

        if not status_value:
            return JsonResponse({"status": "error", "message": "status is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('review_case_form_assignment_api', kwargs={'case_id': case_id, 'assignment_id': assignment_id})}"

        payload = {
            "status": status_value,
            "review_notes": data.get("review_notes"),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# FORM SUBMISSION — CLIENT PORTAL
# ---------------------------------------------------------------------------

@csrf_exempt
def start_form_submission(request, assignment_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('start_form_submission_api', kwargs={'assignment_id': assignment_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def get_form_submission(request, assignment_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('get_form_submission_api', kwargs={'assignment_id': assignment_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------------------------------------------------------
# FORM RESPONSES
# ---------------------------------------------------------------------------

@csrf_exempt
def save_form_response(request, submission_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)

        question = data.get("question")

        if not question:
            return JsonResponse({"status": "error", "message": "question is required"}, status=400)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('save_form_response_api', kwargs={'submission_id': submission_id})}"

        payload = {
            "question": question,
            "section": data.get("section"),
            "response_text": data.get("response_text"),
            "response_number": data.get("response_number"),
            "response_date": data.get("response_date"),
            "response_boolean": data.get("response_boolean"),
            "selected_option": data.get("selected_option"),
            "document": data.get("document"),
            "other_text": data.get("other_text"),
        }

        # Strip None but keep False and 0 — valid answers
        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def list_form_responses(request, submission_id):

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('list_form_responses_api', kwargs={'submission_id': submission_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="GET", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def submit_form(request, submission_id):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "error", "message": "Authorization token required"}, status=401)

        url = f"{host_url(request)}{reverse_lazy('submit_form_api', kwargs={'submission_id': submission_id})}"

        headers = {"Content-Type": "application/json", "Authorization": auth_header}

        response_data = api_connection(method="POST", url=url, headers=headers)

        return JsonResponse({"status": "success", "data": response_data}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)