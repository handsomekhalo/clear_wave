from django.shortcuts import render

# Create your views here.
from django.urls import path, re_path
from system_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login_view/', views.login_view, name='login_view'),

] 
