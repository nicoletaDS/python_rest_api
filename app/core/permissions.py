from rest_framework import permissions
from . import models


class IsDoctorUser(permissions.BasePermission):

    """
    Custom permission for doctor user: doctor has all permissions, 
    on their profiles and on their patients profiles.
    """

    def has_permission(self, request, view):
        # Doctors have all permissions on their account
        return bool(request.user and request.user.is_doctor)

    def has_object_permission(self, request, view, obj):
        # Registered doctors have all permissions on their patients(Read, Update, Delete)
        if (request.user.is_doctor
            and request.user.id == obj.doctor.user.id):
            return True
        # return bool(request.user and request.user.is_patient)
        else:
            return False

class IsPatientUser(permissions.BasePermission):

    """
    Custom permission for patient user: a patient can only see their profiles.
    """

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_doctor)

    def has_object_permission(self, request, view, obj):
        # Patients have read-only permissions for their profile
        if (request.method in permissions.SAFE_METHODS 
            and request.user.is_patient
            and request.user.id == obj.id):
            return True
        else:
            return False


class CanGetMeasurement(permissions.BasePermission):

    """
    Custom permission for doctor user: doctor can get measurements 
    only for their patients.
    """

    def has_permission(self, request, view):
        # check if the current user is a doctor
        if not (request.user and request.user.is_doctor):
            return False

        # check if a patient_id was provided in the url
        patient_id = request.parser_context['kwargs']['patient_id']
        if not patient_id:
            return False

        # check if the provided patient_id belongs to a registered patient
        try:
            user = models.User.objects.get(pk=patient_id)
            patient = models.Patient.objects.get(pk=user)
        except:
            return False
        
        # check if the patient belongs to the current doctor(request.user)
        if patient.doctor.user.id is not request.user.id:
            return False

        return True


class CanUpdateNotification(permissions.BasePermission):

    """
    Custom permission for patient user: patient can get his notifications,
    and activate(update)  a notification. 
    """

    def has_object_permission(self, request, view, obj):
        methods_allowed = ['GET', 'PATCH']
        if (request.method in methods_allowed
            and request.user.is_patient
            and request.user.id == obj.patient.user.id):
            return True
        else:
            return False