from django.urls import path, re_path
from client_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('client_case_detail/<int:case_id>/', views.client_case_detail, name='client_case_detail'),
        path('list_client_cases/', views.list_client_cases, name='list_client_cases'),


    path('list_case_messages/<int:case_id>/', views.list_case_messages, name='list_case_messages'),


]