"""
API URLs for Senior Care App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'seniors', views.SeniorProfileViewSet, basename='senior')
router.register(r'caretakers', views.CaretakerProfileViewSet, basename='caretaker')
router.register(r'ngos', views.NGOViewSet, basename='ngo')
router.register(r'volunteers', views.VolunteerProfileViewSet, basename='volunteer')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'medications', views.MedicationViewSet, basename='medication')
router.register(r'medication-logs', views.MedicationLogViewSet, basename='medication-log')
router.register(r'tasks', views.VolunteerTaskViewSet, basename='task')
router.register(r'emergency-alerts', views.EmergencyAlertViewSet, basename='emergency-alert')
router.register(r'health-records', views.HealthRecordViewSet, basename='health-record')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Authentication
    path('auth/login/', obtain_auth_token, name='api-login'),
    path('auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('auth/logout/', views.LogoutView.as_view(), name='api-logout'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
]