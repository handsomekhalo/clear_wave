from django.urls import path
import client_management.api.views as views


urlpatterns = [
        path('request_magic_link_api/', views.request_magic_link_api, name='request_magic_link_api'),
        path('sign_in_with_link_api/', views.sign_in_with_link_api, name='sign_in_with_link_api'),
        path('list_client_cases_api/', views.list_client_cases_api, name='list_client_cases_api'),
        path('view_client_cases_api/', views.view_client_cases_api, name='view_client_cases_api'),
        path('client_case_detail_api/<int:case_id>/', views.client_case_detail_api, name='client_case_detail_api'),
        path('list_client_documents_api/<int:case_id>/',views.list_client_documents_api,name='list_client_documents_api'
),
        path('list_case_messages_api/<int:case_id>/', views.list_case_messages_api, name='list_case_messages_api'),
        path('send_case_message_api/<int:case_id>/', views.send_case_message_api, name='send_case_message_api'),
        path('mark_message_read_api/<int:message_id>/', views.mark_message_read_api, name='mark_message_read_api'),
        path('list_client_form_assignments_api/', views.list_client_form_assignments_api, name='list_client_form_assignments_api'),
        path('client_upload_document_api/<int:case_id>/', views.client_upload_document_api, name="client_upload_document_api"),
        # Add to client_management/api/urls.py (the DRF api urls file)

        path('get_client_magic_link_status/<int:client_id>/', views.get_client_magic_link_status_api, name='get_client_magic_link_status_api'),
        path('send_client_magic_link/<int:client_id>/', views.send_client_magic_link_api, name='send_client_magic_link_api'),
        path('debug_me/', views.debug_me, name='debug_me'),
]