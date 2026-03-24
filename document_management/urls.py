from django.urls import path, re_path
from . import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('upload_documents/<int:case_id>/', views.upload_documents, name='upload_documents'),
    path('get_documents/<int:case_id>/',views.get_documents,name='get_documents'),
    path('view_document/<int:document_id>/',views.view_document,name='view_document'),


]