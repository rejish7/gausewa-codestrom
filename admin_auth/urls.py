from django.urls import path
from django.views.generic import RedirectView
from accounts import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='admin_login', permanent=False), name='admin_root'),
    path('register/', views.admin_register_view, name='admin_register'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
