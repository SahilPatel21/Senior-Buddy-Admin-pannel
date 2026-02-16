"""
Serializers for Senior Care API
Convert Django models to JSON and vice versa
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, SeniorProfile, CaretakerProfile, NGO, VolunteerProfile,
    CareAssignment, Appointment, Medication, MedicationLog,
    VolunteerTask, EmergencyAlert, HealthRecord, Event,
    EventRegistration, Notification
)


# User Serializers
class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone_number', 'profile_picture', 'date_of_birth',
                  'address', 'city', 'state', 'zip_code', 'is_active_user',
                  'created_at', 'last_active']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 
                  'last_name', 'user_type', 'phone_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# Profile Serializers
class SeniorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Senior Profile"""
    user = UserSerializer(read_only=True)
    senior_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = SeniorProfile
        fields = '__all__'


class CaretakerProfileSerializer(serializers.ModelSerializer):
    """Serializer for Caretaker Profile"""
    user = UserSerializer(read_only=True)
    caretaker_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CaretakerProfile
        fields = '__all__'


class VolunteerProfileSerializer(serializers.ModelSerializer):
    """Serializer for Volunteer Profile"""
    user = UserSerializer(read_only=True)
    volunteer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    ngo_name = serializers.CharField(source='ngo.name', read_only=True)
    
    class Meta:
        model = VolunteerProfile
        fields = '__all__'


# NGO Serializer
class NGOSerializer(serializers.ModelSerializer):
    """Serializer for NGO"""
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    volunteer_count = serializers.IntegerField(source='volunteers.count', read_only=True)
    
    class Meta:
        model = NGO
        fields = '__all__'


# Care Assignment Serializer
class CareAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Care Assignment"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    caretaker_name = serializers.CharField(source='caretaker.get_full_name', read_only=True)
    
    class Meta:
        model = CareAssignment
        fields = '__all__'


# Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointments"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    caretaker_name = serializers.CharField(source='caretaker.get_full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'


# Medication Serializers
class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    
    class Meta:
        model = Medication
        fields = '__all__'


class MedicationLogSerializer(serializers.ModelSerializer):
    """Serializer for Medication Log"""
    medication_name = serializers.CharField(source='medication.medication_name', read_only=True)
    senior_name = serializers.CharField(source='medication.senior.get_full_name', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.get_full_name', read_only=True)
    
    class Meta:
        model = MedicationLog
        fields = '__all__'


# Volunteer Task Serializer
class VolunteerTaskSerializer(serializers.ModelSerializer):
    """Serializer for Volunteer Tasks"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    volunteer_name = serializers.CharField(source='volunteer.get_full_name', read_only=True)
    ngo_name = serializers.CharField(source='ngo.name', read_only=True)
    
    class Meta:
        model = VolunteerTask
        fields = '__all__'


# Emergency Alert Serializer
class EmergencyAlertSerializer(serializers.ModelSerializer):
    """Serializer for Emergency Alerts"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmergencyAlert
        fields = '__all__'


# Health Record Serializer
class HealthRecordSerializer(serializers.ModelSerializer):
    """Serializer for Health Records"""
    senior_name = serializers.CharField(source='senior.get_full_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = '__all__'


# Event Serializers
class EventSerializer(serializers.ModelSerializer):
    """Serializer for Events"""
    ngo_name = serializers.CharField(source='ngo.name', read_only=True)
    spaces_available = serializers.IntegerField(
        source='max_participants',
        read_only=True
    )
    
    class Meta:
        model = Event
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Event Registrations"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = '__all__'


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notifications"""
    
    class Meta:
        model = Notification
        fields = '__all__'
