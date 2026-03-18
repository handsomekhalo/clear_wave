from django.urls import path, re_path
from system_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static
  

urlpatterns = [
    path('login_view/', views.login_view, name='login_view'),
    
    path('register_firm_owner/',views.register_firm_owner, name='register_firm_owner'),
    path('firm_onboarding_step_1/', views.firm_onboarding_step_1, name='firm_onboarding_step_1'),
    path('firm_onboarding_step_2/', views.firm_onboarding_step_2, name='firm_onboarding_step_2'),
    path('csrf/', views.csrf, name='csrf'),
    path('get_firm_user_list/', views.get_firm_user_list, name='get_firm_user_list'),
    path('create_firm_user/',views.create_firm_user, name='create_firm_user'),
    path('get_all_roles/',views.get_all_roles, name='get_all_roles'),
    path('firm_user_retrieve/<int:user_id>/', views.firm_user_retrieve, name="firm_user_retrieve"),
    path('firm_user_update/<int:user_id>/', views.firm_user_update, name='firm_user_update'),
    path("firm_user_toggle_status/<int:user_id>/",views.firm_user_toggle_status,name="firm_user_toggle_status"
),
    
    
    # path("register_firm_owner/", views.register_firm_owner, name="register_firm_owner"),
    # path('artist_onboarding_step_1/', views.artist_onboarding_step_1, name='artist_onboarding_step_1'),
    # path('artist_onboarding_step_2/', views.artist_onboarding_step_2, name='artist_onboarding_step_2'),
    # path('get_artist_profile/', views.get_artist_profile, name='get_artist_profile'),
    # path('update_profile/', views.update_profile, name='update_profile'),
    # path('get_all_admins/', views.get_all_admins, name='get_all_admins'),
    # path('get_all_artists/', views.get_all_artists, name='get_all_artists'),
    # path('toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    
    path('login/', views.login, name='login'),
    # path('get_roles/', views.get_roles, name='get_roles'),
    # path('get_all_users/', views.get_all_users, name='get_all_users'),
    # # path('update_user/', views.update_user, name='update_user'),
    # path('update_user/<int:user_id>/', views.update_user, name='update_user')

] 
