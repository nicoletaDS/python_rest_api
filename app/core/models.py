from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token

from django.conf import settings


class User(AbstractUser):

        """Database model for users in the system."""

        is_doctor = models.BooleanField(default=False)
        is_patient = models.BooleanField(default=False)
        email = models.EmailField(blank=False, null=False)
        first_name = models.CharField(max_length=255, blank=False, null=False)
        last_name = models.CharField(max_length=255, blank=False, null=False)

        def __str__(self):
                """Return string representation of the user"""
                return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Doctor(models.Model):

        """Database model for doctor-users in the system."""

        user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="doctor", 
                on_delete=models.CASCADE, primary_key=True)
        speciality = models.CharField(max_length=255, blank=True, null=True)


class Patient(models.Model):

        """Database model for patient-users in the system."""

        user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="patient",
            on_delete=models.CASCADE, primary_key=True)
        doctor = models.ForeignKey(Doctor, related_name='patients', on_delete=models.SET_NULL,
            blank=True, null=True)

        cnp = models.CharField(max_length=13, unique=True)
        birthday = models.DateField()
        street = models.CharField(max_length=50)
        city = models.CharField(max_length=20)
        state = models.CharField(max_length=20)
        phone = models.CharField(max_length=12, unique=True)
        profession = models.CharField(max_length=50)
        workplace = models.CharField(max_length=255)

        records = models.TextField(blank=True, null=True)
        alergies = models.TextField(blank=True, null=True)
        cardio_check = models.TextField(blank=True, null=True)


class Measurement(models.Model):

        """Database model for patients measurements in the system."""

        created_on = models.DateTimeField(auto_now_add=True, primary_key=True, blank=False)
        patient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="measurements",
                on_delete=models.CASCADE)
        ecg = models.IntegerField(blank=True, null=True)
        humidity = models.IntegerField(blank=True, null=True)
        temperature = models.FloatField(blank=True, null=True)
        pulse = models.IntegerField(blank=True, null=True)


class Limit(models.Model):

        """Database model for patients limits in the system."""

        patient = models.OneToOneField(Patient, related_name="limits",
                on_delete=models.CASCADE, primary_key=True)
        ecg_low =models.IntegerField(default=60)
        ecg_high =models.IntegerField(default=100)
        humidity_low =models.IntegerField(default=30)
        humidity_high =models.IntegerField(default=50)
        temperature_low =models.FloatField(default=36.1)
        temperature_high =models.FloatField(default=37.2)
        pulse_low =models.IntegerField(default=60)
        pulse_high =models.IntegerField(default=100)


class Notification(models.Model):

        """Database model for notifications created by doctors for patients in the system."""

        patient = models.ForeignKey(Patient, related_name="notifications",
                on_delete=models.CASCADE, blank=True, null=True)
        doctor = models.ForeignKey(Doctor, related_name="notifications",
                on_delete=models.SET_NULL, blank=True, null=True)
        message = models.TextField()
        created_on = models.DateTimeField(auto_now_add=True)
        active = models.BooleanField(default=False)
        start_date = models.DateField(blank=True, null=True)
        end_date = models.DateField(blank=True, null=True)
        

