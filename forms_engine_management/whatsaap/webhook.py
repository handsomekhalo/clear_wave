
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from forms_engine_management.models import WhatsAppMessage, WhatsAppSession
from forms_engine_management.whatsaap.bot import process_inbound_message, send_whatsapp_message
 

logger = logging.getLogger(__name__)
 
 
@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Twilio sends a POST here on every inbound WhatsApp message.
    Parse → look up session → hand off to bot → respond.
    """
    from_number = request.POST.get("From", "").replace("whatsapp:", "")
    body        = request.POST.get("Body", "").strip()
    media_url   = request.POST.get("MediaUrl0")       # file attachment if any
    message_sid = request.POST.get("MessageSid", "")
 
    if not from_number:
        return HttpResponse(status=400)
 
    logger.info(f"WhatsApp inbound: {from_number} → {body[:60]}")
 
    try:
        # Find active session for this phone number
        session = WhatsAppSession.objects.filter(
            phone_number=from_number,
            status="active"
        ).select_related(
            "assignment__case__firm",
            "assignment__template",
            "client",
        ).first()
 
        if not session:
            # No active session — ignore or send a "no active form" reply
            send_whatsapp_message(
                to=from_number,
                body="Hi! You don't have any active forms right now. "
                     "Your lawyer will send you a link when one is ready."
            )
            return HttpResponse(status=200)
 
        # Log inbound message
        WhatsAppMessage.objects.create(
            session=session,
            direction="inbound",
            message_type="media" if media_url else "text",
            body=body,
            provider_message_id=message_sid,
        )
 
        # Hand off to bot runner
        process_inbound_message(session=session, body=body, media_url=media_url)
 
    except Exception as e:
        logger.exception(f"WhatsApp webhook error: {e}")
 
    # Twilio expects 200 even on errors (it will retry otherwise)
    return HttpResponse(status=200)
