from django.urls import path
from . import views

urlpatterns = [
    # User complaint views
    path('submit/', views.submit_complaint_view, name='submit_complaint'),
    path('my-complaints/', views.my_complaints_view, name='my_complaints'),
    path('complaint/<uuid:complaint_id>/', views.complaint_detail_view, name='complaint_detail'),
    
    # API endpoints for offline sync
    path('api/sync/', views.sync_offline_complaint, name='sync_offline_complaint'),
    path('api/categories/', views.get_categories_api, name='get_categories_api'),
    path('api/check-user/', views.check_user_exists, name='check_user_exists'),
]
