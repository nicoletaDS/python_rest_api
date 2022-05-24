from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from . import models


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for all the user of the system.
    """

    class Meta:
        model = models.User
        fields = ('id','username', 'email', 'password', 'first_name', 'last_name', 'is_doctor')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data, *args, **kwargs):
        user=models.User(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name') 
        )
        password=validated_data.pop('password')
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email=validated_data.pop('email', instance.email)
        instance.first_name=validated_data.pop('first_name', instance.first_name)
        instance.last_name=validated_data.pop('last_name', instance.last_name)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for a doctor user.
    """
    user = UserSerializer()
    patients = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = models.Doctor
        fields = ('user', 'speciality', 'patients')

    def update(self, instance, validated_data):
        user_data=validated_data.pop('user', instance.user)
        instance.user = UserSerializer.update(UserSerializer(),instance=instance.user, validated_data=user_data)
        instance.speciality=validated_data.pop('speciality', instance.speciality)
        instance.save()
        return instance


class LimitSerializer(serializers.ModelSerializer):
    """
    Serializer for the limits values of a patient.
    """
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = models.Limit
        fields = '__all__'

    def create(self, validated_data, *args, **kwargs):
        limit=models.Limit(patient=kwargs['patient'])
        limit.save()
        return limit

    def update(self, instance, validated_data):
        instance.ecg_low=validated_data.pop('ecg_low', instance.ecg_low)
        instance.ecg_high=validated_data.pop('ecg_high', instance.ecg_high)
        instance.humidity_low=validated_data.pop('humidity_low', instance.humidity_low)
        instance.humidity_high=validated_data.pop('humidity_high', instance.humidity_high)
        instance.temperature_low=validated_data.pop('temperature_low', instance.temperature_low)
        instance.temperature_high=validated_data.pop('temperature_high', instance.temperature_high)
        instance.pulse_low=validated_data.pop('pulse_low', instance.pulse_low)
        instance.pulse_high=validated_data.pop('pulse_high', instance.pulse_high)
        instance.save()
        return instance


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for a patient user profile.
    """
    user = UserSerializer()
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    limits = LimitSerializer()

    class Meta:
        model = models.Patient
        fields = ('user', 'doctor', 'cnp', 'birthday', 'street', 'city', 'state',
                'phone', 'profession', 'workplace', 'records', 'alergies', 'cardio_check', 'limits')
    
    def update(self, instance, validated_data):
        user_data=validated_data.pop('user', None)
        if user_data:
            instance.user = UserSerializer.update(UserSerializer(),instance=instance.user, validated_data=user_data)
        limit_data=validated_data.pop('limits', None)
        if limit_data:
            instance.limits = LimitSerializer.update(LimitSerializer(),instance=instance.limits, validated_data=limit_data)
        instance.cnp=validated_data.pop('cnp', instance.cnp)
        instance.birthday=validated_data.pop('birthday', instance.birthday)
        instance.street=validated_data.pop('street', instance.street)
        instance.city=validated_data.pop('city', instance.city)
        instance.state=validated_data.pop('state', instance.state)
        instance.phone=validated_data.pop('phone', instance.phone)
        instance.profession=validated_data.pop('profession', instance.profession)
        instance.workplace=validated_data.pop('workplace', instance.workplace)
        instance.records=validated_data.pop('records', instance.records)
        instance.alergies=validated_data.pop('alergies', instance.alergies)
        instance.cardio_check=validated_data.pop('cardio_check', instance.cardio_check)
        instance.save()
        return instance
    

class DoctorSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for a doctor signup form.
    """
    user = UserSerializer(required=True)
    
    class Meta:
        model = models.Doctor
        fields = ('user', 'speciality')
        extra_kwargs = {
            'password': {'write_only': True}, 
            'username': {'write_only': True},
            'email': {'write_only': True},
            'first_name': {'write_only': True}, 
            'last_name': {'write_only': True},
            }

    def create(self, validated_data, *args, **kwargs):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(
            UserSerializer(), validated_data=user_data)
        user.is_doctor = True
        user.save()
        doctor, created = models.Doctor.objects.update_or_create(
            user=user,
            speciality=validated_data.pop('speciality', None),
        )
        return doctor


class PatientSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for a patient signup form.
    """
    user = UserSerializer(required=True)
    limits = LimitSerializer(required=False)

    class Meta:
        model = models.Patient
        fields = ('user', 'doctor', 'cnp', 'birthday', 'street', 'city', 'state',
                'phone', 'profession', 'workplace', 'records', 'alergies', 'cardio_check', 'limits')
        extra_kwargs = {
            'password': {'write_only': True}, 
            'username': {'write_only': True},
            'first_name': {'write_only': True}, 
            'last_name': {'write_only': True},}

    def create(self, validated_data, *args, **kwargs):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(
            UserSerializer(), validated_data=user_data)
        user.is_patient = True
        user.save()
        patient, created = models.Patient.objects.update_or_create(
            user=user,
            cnp=validated_data.pop('cnp'),
            birthday=validated_data.pop('birthday'),
            street=validated_data.pop('street'),
            city=validated_data.pop('city'),
            state=validated_data.pop('state'),
            phone=validated_data.pop('phone'),
            profession=validated_data.pop('profession'),
            workplace=validated_data.pop('workplace'),
            records=validated_data.pop('records', None),
            alergies=validated_data.pop('alergies', None),
            cardio_check=validated_data.pop('cardio_check', None),
        )
        limit = LimitSerializer.create(
            LimitSerializer(), validated_data, patient=patient)
        patient.limit = limit
        patient.save()
        return patient


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Serializer for a patinet's measurement.
    """
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = models.Measurement
        fields = '__all__'
        lookup_field = 'patient_id'


class DoctorNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for a doctor to create, get or update a notification for one of his patients.
    """
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Notification
        fields = '__all__'

    def create(self, validated_data, *args, **kwargs):
        notification = models.Notification(
            message=validated_data.pop('message'),
            start_date=validated_data.pop('start_date', None),
            end_date=validated_data.pop('end_date', None),
        )
        notification.save()
        return notification

    def update(self, instance, validated_data):
        instance.message=validated_data.pop('message', instance.message)
        instance.start_date=validated_data.pop('start_date', instance.start_date)
        instance.end_date=validated_data.pop('end_date', instance.end_date)
        instance.save()
        return instance


class PatientNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for a patient to get or activate a notification.
    """
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Notification
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.active=validated_data.pop('active', instance.message)
        instance.save()
        return instance


    