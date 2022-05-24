from posixpath import basename
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

"""
URLs for each endpoint of the application. See README for more documentation, on each endpoint.
"""

router = DefaultRouter()
router.register('doctor/patients', views.PatientViewSet, basename='patients')
router.register('patient/measurements', views.PatientMeasurementViewSet, basename='measurements')
router.register('doctor/notifications', views.DoctorNotificationViewSet, basename='doctor-notifications')
router.register('patient/notifications', views.PatientNotificationViewSet, basename='patient-notifications')

urlpatterns=[
    path('signup/doctor/', views.DoctorSignupView.as_view(), name='signup-doctor'),
    path('signup/patient/', views.PatientSignupView.as_view(), name='signup-patient'),
    path('login/', views.CustomAuthToken.as_view(), name='auth-token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePassword.as_view(), name='change-password'),
    path('doctor/profile/', views.DoctorView.as_view(), name='doctor-profile'),
    path('patient/profile/', views.PatientView.as_view(), name='patient-profile'),
    path('doctor/<int:patient_id>/measurements/', views.DoctorMeasurementView.as_view(), name='doc-measurements'),
    path('', include(router.urls))
]