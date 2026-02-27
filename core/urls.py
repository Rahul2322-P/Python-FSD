from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('modules/', views.module_list, name='modules'),
    path('modules/<int:pk>/', views.module_detail, name='module_detail'),
    path('modules/<int:pk>/complete/', views.complete_module, name='complete_module'),
    path('challenges/', views.challenge_list, name='challenges'),
    path('challenges/<int:pk>/complete/', views.complete_challenge, name='complete_challenge'),
    
    path('management/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('management/module/create/', views.custom_admin_module_create, name='custom_admin_module_create'),
    path('management/module/<int:pk>/edit/', views.custom_admin_module_edit, name='custom_admin_module_edit'),
    path('management/module/<int:pk>/delete/', views.custom_admin_module_delete, name='custom_admin_module_delete'),
    path('management/challenge/create/', views.custom_admin_challenge_create, name='custom_admin_challenge_create'),
    path('management/challenge/<int:pk>/edit/', views.custom_admin_challenge_edit, name='custom_admin_challenge_edit'),
    path('management/challenge/<int:pk>/delete/', views.custom_admin_challenge_delete, name='custom_admin_challenge_delete'),
]
