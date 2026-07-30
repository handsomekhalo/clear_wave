"""
Global api(s) for the use through the system.
"""
from rest_framework import status
import json
from system_management.api.serializers import SendEmailSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings
from django.template import TemplateDoesNotExist
from smtplib import SMTPException

from system_management.services.email_service import send_email


@api_view(["POST"])
@permission_classes((AllowAny,))
def send_email_api(request):

    body = json.loads(request.body)

    html_tpl_path = body.get("html_tpl_path")
    receiver_email = body.get("receiver_email")
    subject = body.get("subject")
    context_data = body.get("context_data")

    if not html_tpl_path or not receiver_email or not subject:
        return Response(
            {"status": "error", "message": "Missing required fields"},
            status=400,
        )

    try:
        html_template = get_template(html_tpl_path).render(context_data)

    except TemplateDoesNotExist:
        return Response(
            {"status": "error", "message": "Template not found"},
            status=400,
        )

    status_code = send_email(receiver_email, subject, html_template)

    if status_code == 202:
        return Response({"status": "success"})

    return Response(
        {"status": "error", "message": "Email sending failed"},
        status=500,
    )
