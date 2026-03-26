"""
General functions and classes are stored here to remove duplicated accross the system.
"""

import json
from django.conf import settings
import requests
from rest_framework import serializers


class BaseFormSerializer(serializers.Serializer):
    """Base form serializer for cleaning incoming and outgoing data"""

    def create(self, validated_data):
        """Override create method to do nothing"""

    def update(self, instance, validated_data):
        """Override create method to do nothing"""



def host_url(request):
    if hasattr(settings, "USE_HTTPS"):
        scheme = "https" if settings.USE_HTTPS else "http"
    else:
        scheme = "https" if request.is_secure() else "http"

    host = request.get_host()
    return f"{scheme}://{host}"




def api_connection(method, url, headers, data=None):
    """
    Connects to an external API and handles JSON data.
    
    Args:
        method (str): The HTTP method (e.g., 'GET', 'POST').
        url (str): The URL of the API endpoint.
        headers (dict): The request headers.
        data (dict, optional): The JSON data to send. Defaults to None.

    Returns:
        dict or list: The JSON response data, or a dictionary with an error message.
    """
    try:
        if data:
            response = requests.request(method, url, headers=headers, json=data, timeout=120)
        else:
            response = requests.request(method, url, headers=headers, timeout=120)

        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        return response.json()

    except requests.exceptions.RequestException as e:
        # Catch network-related errors and HTTP errors
        print(f"Network or HTTP error during API call: {e}")
        return {"status": "error", "message": f"Network or HTTP error: {str(e)}"}
    except json.JSONDecodeError:
        # Catch cases where the response is not valid JSON
        print(f"Error decoding JSON response from API: {response.text}")
        return {"status": "error", "message": "Invalid JSON response from API."}
def api_connection(method, url, headers, data=None, files=None):
    """
    Supports BOTH:
    - JSON requests (existing system)
    - Multipart file uploads (new feature)
    """

    try:
        # ✅ FILE UPLOAD MODE
        if files:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,     # form fields
                files=files,   # file
                timeout=120
            )

        # ✅ JSON MODE (existing behavior)
        elif data:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=120
            )

        # ✅ NO BODY
        else:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=120
            )

        response.raise_for_status()

        try:
            return response.json()
        except:
            return {"raw": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
# def api_connection(method, url, headers, data=None, files=None):
#     """
#     Supports:
#     - JSON requests (existing)
#     - Multipart file uploads (new)
#     """
#     try:
#         # ✅ FILE UPLOAD MODE
#         if files:
#             # Convert Django FILES to requests format
#             files_to_send = {}
            
#             for key, file_obj in files.items():
#                 files_to_send[key] = (
#                     file_obj.name,
#                     file_obj.read(),  # Read file content
#                     file_obj.content_type or 'application/octet-stream'
#                 )

#             # Don't send Content-Type header - requests will set it
#             headers_copy = {k: v for k, v in headers.items() if k.lower() != 'content-type'}

#             response = requests.request(
#                 method,
#                 url,
#                 headers=headers_copy,
#                 data=data,              # Form fields
#                 files=files_to_send,    # Files
#                 timeout=120
#             )

#         # ✅ JSON MODE
#         elif data:
#             response = requests.request(
#                 method,
#                 url,
#                 headers=headers,
#                 json=data,
#                 timeout=120
#             )

#         # ✅ NO BODY
#         else:
#             response = requests.request(
#                 method,
#                 url,
#                 headers=headers,
#                 timeout=120
#             )

#         response.raise_for_status()

#         try:
#             return response.json()
#         except:
#             return {"raw": response.text}

#     except requests.exceptions.RequestException as e:
#         print(f"❌ API connection error: {e}")
#         return {"error": str(e)}

def _send_email_thread(email_url, headers, email_payload):
    try:
        print("📧 Email thread started")
        print(f"URL: {email_url}")
        print(f"Payload: {email_payload}")
        
        response = requests.post(
            email_url,
            data=email_payload,
            headers=headers
        )
        
        print(f"✅ Email API response: {response.status_code}")
        print(f"Response body: {response.text}")
        
    except Exception as e:
        print(f"❌ Email thread error: {str(e)}")
        import traceback
        traceback.print_exc()

# def _send_email_thread(url, headers, payload):
#     """This function is used to send email in a thread."""
#     requests.post(url=url, headers=headers, data=payload, timeout=120)
