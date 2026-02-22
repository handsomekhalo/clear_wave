"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views



urlpatterns = [
    path('login_api/', views.login_api, name="login_api"),
   


]
