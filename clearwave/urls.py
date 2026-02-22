"""
URL configuration for clearwave project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import system_management.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login_view'),
    path('system_management/',include('system_management.urls')),
    path('system_management_api/',include('system_management.api.urls')),
    path('case_management/',include('case_management.urls')),
    path('case_management_api/',include('case_management.api.urls')),



]
