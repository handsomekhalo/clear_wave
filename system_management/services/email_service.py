from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


from django.conf import settings

# def send_email(to_email, subject, html_content):

#     print("SENDGRID KEY:", settings.SENDGRID_API_KEY)

#     message = Mail(
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to_emails=to_email,
#         subject=subject,
#         html_content=html_content,
#     )

#     try:
#         sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
#         response = sg.send(message)

#         print("SENDGRID STATUS:", response.status_code)

#         return response.status_code

#     except Exception as e:
#         print("SendGrid error:", str(e))
#         return None

def send_email(to_email, subject, html_content):

    if isinstance(to_email, list):
        to_email = ",".join(to_email)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print("SendGrid error:", str(e))
        return None
    
