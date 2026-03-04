from django.urls import path, re_path
from system_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login_view/', views.login_view, name='login_view'),
    # path('register_user/', views.register_user, name='register_user'),
    # path('register_artist/', views.register_artist, name='register_artist'),
    path('csrf/', views.csrf, name='csrf'),
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
