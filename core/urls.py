from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.user_login_view, name='user_login'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('register/', views.user_register_view, name='user_register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.user_logout_view, name='logout'),
    
    # Include complains URLs
    path('complaints/', include('complains.urls')),
]
