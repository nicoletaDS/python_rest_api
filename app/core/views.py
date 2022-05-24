from datetime import datetime
from django.http import Http404
from rest_framework import generics, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework import viewsets

from . import serializers
from . import models
from .permissions import IsDoctorUser, IsPatientUser, CanGetMeasurement, CanUpdateNotification


class DoctorSignupView(generics.GenericAPIView):
    """
    Create a new doctor user in the system.
    """
    serializer_class=serializers.DoctorSignupSerializer
    
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor=serializer.save()
        
        return Response({
             "user_id": doctor.user.id,
             "username": doctor.user.username,
             "is_doctor": doctor.user.is_doctor,
             "token":Token.objects.get(user=doctor.user).key,
             "message":"account created successully"
        })
       

class PatientSignupView(generics.GenericAPIView):
    """
    Create a new patient user in the system.
    Only a doctor user can add a new patient user.
    """
    serializer_class=serializers.PatientSignupSerializer
    permission_classes=[permissions.IsAuthenticated&IsDoctorUser]
    
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient=serializer.save()

        # set up the authenticated user as the patient's doctor
        doctor = models.Doctor.objects.get(pk=request.user)
        patient.doctor=doctor
        patient.save()
        
        return Response({
             "user_id": patient.user.id,
             "is_doctor": patient.user.is_doctor,
             "username": patient.user.username,
             "token":Token.objects.get(user=patient.user).key,
             "message":"account created successully"
        })


class CustomAuthToken(ObtainAuthToken):
    """
    The login page. Returns the token.key if the provided credentials are valid.
    """
    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token':token.key,
            'user_id':user.pk,
            'username':user.username,
            'is_doctor':user.is_doctor
        })


class LogoutView(APIView):
    """
    The logout page.
    """
    def post(self, request, format=None):
        try:
            request.auth.delete()
            return Response(status=status.status.HTTP_204_NO_CONTENT)
        except AttributeError:
            return Response({'message':'user must be authenticated to log out.'}, status=status.HTTP_400_BAD_REQUEST)


class DoctorView(generics.RetrieveAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Doctor profiles view page. 
    A doctor cand get, update or delete his profile.
    If a doctor deletes his profile, all his patients profiles will also be deleted.
    """
    permission_classes=[permissions.IsAuthenticated&IsDoctorUser]
    serializer_class=serializers.DoctorSerializer

    def get_object(self):
        doctor = Doctor.objects.get(pk=self.request.user)
        return doctor

    def destroy(self, request, *args, **kwargs):
        # delete all patients of this doctor object
        for patient_id in self.get_object().patients:
            models.User.objects.filter(pk=patient_id).delete()

        # delete the doctor object
        models.User.objects.filter(pk=request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class PatientView(generics.RetrieveAPIView):
    """
    Patient profile view page.
    A patient cand only see his profile.
    """
    permission_classes=[permissions.IsAuthenticated&IsPatientUser]
    serializer_class=serializers.PatientSerializer

    def get_object(self):
        patient = models.Patient.objects.get(pk=self.request.user)
        return patient


class PatientViewSet(viewsets.ModelViewSet):
    """
    A doctor patients list, containtig the profile of all his patients.
    The doctor can add, get, update or delete patients by providing the patient_id.
    """
    permission_classes=[permissions.IsAuthenticated&IsDoctorUser]
    serializer_class=serializers.PatientSerializer

    def get_queryset(self):
        """
        Return a list with all the patients of the current doctor.
        """
        doctor = models.Doctor.objects.get(pk=self.request.user)
        return doctor.patients.all()

    def destroy(self, request, *args, **kwargs):
        """
        Delete the User-model from the system, and the Patient, will automaticaly be deleted.
        """
        try:
            patient_id = kwargs["pk"]
            models.User.objects.filter(id=patient_id).delete()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePassword(APIView):
    """
    An endpoint for changing the user password.
    """
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = serializers.ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientMeasurementViewSet(viewsets.ModelViewSet):
    """
    An endpoint for patients to add or get measurements for ecg, temperature, humidity, pulse.
    """
    serializer_class = serializers.MeasurementSerializer
    permission_classes=[permissions.IsAuthenticated&IsPatientUser]

    def get_queryset(self):
        """Retrieve the measurements data for the authenticated user, for the specified date."""
        date_string = self.request.query_params.get('date')
        if date_string:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
            queryset = models.Measurement.objects\
                                        .filter(patient=self.request.user)\
                                        .filter(created_on__date=date_obj)\
                                        .values('created_on', 'ecg', 'humidity', 'temperature', 'pulse')
            return queryset             

    def perform_create(self, serializer):
        # add the current authenticated patient as the patient for this measurement.
        serializer.save(patient=self.request.user)


class DoctorMeasurementView(generics.ListAPIView):
    """
    An endpoint for doctors to get measurements from their patients.
    """
    serializer_class = serializers.MeasurementSerializer
    permission_classes = [permissions.IsAuthenticated&CanGetMeasurement]
    lookup_field = 'patient_id'

    def get_queryset(self):
        patient_id = int(self.kwargs['patient_id'])
        user = models.User.objects.get(pk=patient_id)
        
        # get all measurements for the specified patient, from the provided date
        date_string = self.request.query_params.get('date')
        if date_string:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
            queryset = models.Measurement.objects\
                                        .filter(patient=user)\
                                        .filter(created_on__date=date_obj)\
                                        .values('created_on', 'ecg', 'humidity', 'temperature', 'pulse')
            return queryset


class PatientNotificationViewSet(viewsets.ModelViewSet):
    """
    An endpoint for patients to get or activate their notifications.
    """
    serializer_class = serializers.PatientNotificationSerializer
    permission_classes=[permissions.IsAuthenticated&CanUpdateNotification]

    def get_queryset(self):
        patient = models.Patient.objects.get(pk=self.request.user)
        return models.Notification.objects.filter(patient=patient)


class DoctorNotificationViewSet(viewsets.ModelViewSet):
    """
    An endpoint for doctors to create, edit or delete notifications for their patients.
    """
    permission_classes=[permissions.IsAuthenticated&IsDoctorUser]
    serializer_class=serializers.DoctorNotificationSerializer

    def get_queryset(self):
        """
        Return a list with all the notifications created by the current doctor.
        """
        doctor = models.Doctor.objects.get(pk=self.request.user)
        return models.Notification.objects.filter(doctor=doctor)

    
    def create(self, request, *args, **kwargs):
        """
        Create a new notification for patient with 'patient_id' if he belongs to the current doctor.
        """
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            patient_id = int(request.data['patient_id'])
            patient = models.Patient.objects.get(pk=models.User.objects.get(pk=patient_id))

        except:
            return Response(
                {"message":"you have to provide the 'patient_id':<int:id> of one of your patients"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification=serializer.save()
        notification.patient=patient
        notification.doctor=models.Doctor.objects.get(pk=self.request.user)
        notification.save()
        notification_data = serializers.DoctorNotificationSerializer(notification, context=self.get_serializer_context()).data
        
        return Response(notification_data)

