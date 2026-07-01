from django.urls import path, re_path
from client_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('client_case_detail/<int:case_id>/', views.client_case_detail, name='client_case_detail'),
    path('list_client_cases/', views.list_client_cases, name='list_client_cases'),
    path('list_client_documents/<int:case_id>/', views.list_client_documents, name='list_client_documents'),

    path('list_case_messages/<int:case_id>/', views.list_case_messages, name='list_case_messages'),
    path('list_client_form_assignments/',views.list_client_form_assignments, name='list_client_form_assignments'),
    path('client_upload_document/<int:case_id>/', views.client_upload_document, name='client_upload_document'),
    path('sign_in_with_link/', views.sign_in_with_link, name='sign_in_with_link'),
    path('request_magic_link/', views.request_magic_link, name='request_magic_link'),
    path('send_case_message/<int:case_id>/', views.send_case_message, name='send_case_message'),
    # Add to client_management/urls.py (the proxy urls file, not the api/urls.py)

    path('get_client_magic_link_status/<int:client_id>/', views.get_client_magic_link_status, name='get_client_magic_link_status'),
    path('send_client_magic_link/<int:client_id>/', views.send_client_magic_link, name='send_client_magic_link'),
        # path('client_form_assignment_detail/<int:assignment_id>/', views.client_form_assignment_detail
    
    # path('send_message/<int:case_id>/', views.send_message, name='send_message'),

]