from django.urls import path, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static

from client_management import views


urlpatterns = [
        path('request_magic_link_api/', views.request_magic_link_api, name='request_magic_link_api'),
        path('magic_link_login_api/', views.magic_link_login_api, name='magic_link_login_api'),
        path('view_client_cases_api/', views.view_client_cases_api, name='view_client_cases_api'),
        path('client_case_detail_api/<int:case_id>/', views.client_case_detail_api, name='client_case_detail_api'),
        path('case_messages_api/<int:case_id>/', views.case_messages_api, name='case_messages_api'),
        path('send_message_api/<int:case_id>/', views.send_message_api, name='send_message_api'),
        path('mark_message_read_api/<int:message_id>/', views.mark_message_read_api, name='mark_message_read_api'),
]