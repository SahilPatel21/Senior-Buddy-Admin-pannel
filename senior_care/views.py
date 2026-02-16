"""
API Views for Senior Care App
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta


from .models import (
    User, SeniorProfile, CaretakerProfile, NGO, VolunteerProfile,
    CareAssignment, Appointment, Medication, MedicationLog,
    VolunteerTask, EmergencyAlert, HealthRecord, Event,
    EventRegistration, Notification
)
from .serializers import (
    UserSerializer, RegisterSerializer, SeniorProfileSerializer,
    CaretakerProfileSerializer, NGOSerializer, VolunteerProfileSerializer,
    CareAssignmentSerializer, AppointmentSerializer, MedicationSerializer,
    MedicationLogSerializer, VolunteerTaskSerializer, EmergencyAlertSerializer,
    HealthRecordSerializer, EventSerializer, EventRegistrationSerializer,
    NotificationSerializer
)


# Authentication Views
class RegisterView(generics.CreateAPIView):
    """
    Register a new user
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    """
    Logout user and delete token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete user's token
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user_type', 'is_active_user']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active_user = True
        user.is_active = True
        user.save()
        return Response({'message': 'User activated successfully.'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        user.is_active_user = False
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully.'})


# Profile ViewSets
class SeniorProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Senior Profiles"""
    queryset = SeniorProfile.objects.all()
    serializer_class = SeniorProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['blood_group', 'living_arrangement', 'mobility_level', 'care_level_needed']
    search_fields = ['user__first_name', 'user__last_name', 'emergency_contact_name']


class CaretakerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Caretaker Profiles"""
    queryset = CaretakerProfile.objects.all()
    serializer_class = CaretakerProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_available', 'employment_type', 'working_hours', 'background_check_completed']
    search_fields = ['user__first_name', 'user__last_name', 'specializations']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available caretakers"""
        caretakers = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(caretakers, many=True)
        return Response(serializer.data)


class VolunteerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Volunteer Profiles"""
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ngo', 'is_available', 'availability_hours', 'background_check_completed']
    search_fields = ['user__first_name', 'user__last_name', 'volunteer_id']
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Get current volunteer's statistics"""
        try:
            profile = VolunteerProfile.objects.get(user=request.user)
            return Response({
                'total_hours': profile.total_hours,
                'seniors_helped': profile.seniors_helped,
                'tasks_completed': profile.tasks_completed,
                'rating': profile.rating
            })
        except VolunteerProfile.DoesNotExist:
            return Response({'error': 'Volunteer profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


# NGO ViewSet
class NGOViewSet(viewsets.ModelViewSet):
    """ViewSet for NGOs"""
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_verified', 'is_active', 'state', 'city']
    search_fields = ['name', 'registration_number', 'email']
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify an NGO"""
        ngo = self.get_object()
        ngo.is_verified = True
        ngo.save()
        return Response({'message': 'NGO verified successfully.'})


# Appointment ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointments"""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'appointment_type', 'senior', 'caretaker']
    search_fields = ['title', 'doctor_name', 'location']
    
    def get_queryset(self):
        """Filter appointments based on user type"""
        user = self.request.user
        if user.user_type == 'senior':
            return self.queryset.filter(senior=user)
        elif user.user_type == 'caretaker':
            return self.queryset.filter(caretaker=user)
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(
            appointment_date__gte=today,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date', 'appointment_time')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        return Response({'message': 'Appointment confirmed.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        return Response({'message': 'Appointment marked as completed.'})


# Medication ViewSets
class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Medications"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'senior', 'frequency']
    search_fields = ['medication_name', 'prescribed_by']
    
    def get_queryset(self):
        """Filter medications based on user"""
        user = self.request.user
        if user.user_type == 'senior':
            return self.queryset.filter(senior=user)
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active medications"""
        medications = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(medications, many=True)
        return Response(serializer.data)


class MedicationLogViewSet(viewsets.ModelViewSet):
    """ViewSet for Medication Logs"""
    queryset = MedicationLog.objects.all()
    serializer_class = MedicationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['was_taken', 'medication__senior']
    
    @action(detail=True, methods=['post'])
    def mark_taken(self, request, pk=None):
        """Mark medication as taken"""
        log = self.get_object()
        log.was_taken = True
        log.actual_time = timezone.now()
        log.confirmed_by = request.user
        log.save()
        return Response({'message': 'Medication marked as taken.'})


# Volunteer Task ViewSet
class VolunteerTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Volunteer Tasks"""
    queryset = VolunteerTask.objects.all()
    serializer_class = VolunteerTaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'task_type', 'volunteer', 'ngo']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        """Filter tasks based on user"""
        user = self.request.user
        if user.user_type == 'volunteer':
            return self.queryset.filter(volunteer=user)
        elif user.user_type == 'senior':
            return self.queryset.filter(senior=user)
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get current user's tasks"""
        tasks = self.get_queryset().filter(
            status__in=['assigned', 'accepted', 'in_progress']
        ).order_by('scheduled_date', 'scheduled_time')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a task"""
        task = self.get_object()
        task.status = 'accepted'
        task.save()
        return Response({'message': 'Task accepted.'})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a task"""
        task = self.get_object()
        task.status = 'in_progress'
        task.actual_start_time = timezone.now()
        task.save()
        return Response({'message': 'Task started.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a task"""
        task = self.get_object()
        task.status = 'completed'
        task.actual_end_time = timezone.now()
        
        # Calculate hours
        if task.actual_start_time and task.actual_end_time:
            duration = task.actual_end_time - task.actual_start_time
            task.hours_logged = duration.total_seconds() / 3600
        
        task.completion_notes = request.data.get('notes', '')
        task.save()
        
        # Update volunteer stats
        try:
            volunteer = VolunteerProfile.objects.get(user=task.volunteer)
            volunteer.total_hours += task.hours_logged
            volunteer.tasks_completed += 1
            volunteer.save()
        except VolunteerProfile.DoesNotExist:
            pass
        
        return Response({'message': 'Task completed successfully.'})


# Emergency Alert ViewSet
class EmergencyAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Emergency Alerts"""
    queryset = EmergencyAlert.objects.all()
    serializer_class = EmergencyAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_resolved', 'alert_type', 'senior']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active emergency alerts"""
        alerts = self.queryset.filter(is_resolved=False).order_by('-alert_time')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an emergency alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.resolution_notes = request.data.get('notes', '')
        
        # Calculate response time
        if alert.alert_time:
            alert.response_time = timezone.now() - alert.alert_time
        
        alert.save()
        return Response({'message': 'Alert resolved successfully.'})


# Health Record ViewSet
class HealthRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Health Records"""
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['senior', 'record_date']
    
    def get_queryset(self):
        """Filter health records based on user"""
        user = self.request.user
        if user.user_type == 'senior':
            return self.queryset.filter(senior=user)
        return self.queryset


# Event ViewSets
class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Events"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ngo', 'event_type', 'is_active']
    search_fields = ['title', 'description', 'venue']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        today = timezone.now().date()
        events = self.queryset.filter(
            event_date__gte=today,
            is_active=True
        ).order_by('event_date', 'start_time')
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Register for an event"""
        event = self.get_object()
        
        # Check if already registered
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            return Response(
                {'error': 'Already registered for this event.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check capacity
        if event.current_registrations >= event.max_participants:
            return Response(
                {'error': 'Event is full.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create registration
        EventRegistration.objects.create(event=event, user=request.user)
        event.current_registrations += 1
        event.save()
        
        return Response({'message': 'Successfully registered for event.'})


# Notification ViewSet
class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user"""
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'message': 'Notification marked as read.'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response({'message': 'All notifications marked as read.'})


# Dashboard Stats View
class DashboardStatsView(generics.GenericAPIView):
    """
    Get dashboard statistics based on user type
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        stats = {}
        
        if user.user_type == 'senior':
            stats = self._get_senior_stats(user)
        elif user.user_type == 'caretaker':
            stats = self._get_caretaker_stats(user)
        elif user.user_type == 'volunteer':
            stats = self._get_volunteer_stats(user)
        elif user.user_type in ['senior_admin', 'ngo_admin']:
            stats = self._get_admin_stats(user)
        
        return Response(stats)
    
    def _get_senior_stats(self, user):
        """Statistics for seniors"""
        today = timezone.now().date()
        return {
            'upcoming_appointments': Appointment.objects.filter(
                senior=user, 
                appointment_date__gte=today,
                status__in=['scheduled', 'confirmed']
            ).count(),
            'active_medications': Medication.objects.filter(
                senior=user, 
                is_active=True
            ).count(),
            'unread_notifications': Notification.objects.filter(
                user=user, 
                is_read=False
            ).count(),
        }
    
    def _get_caretaker_stats(self, user):
        """Statistics for caretakers"""
        return {
            'assigned_seniors': CareAssignment.objects.filter(
                caretaker=user, 
                is_active=True
            ).count(),
            'today_appointments': Appointment.objects.filter(
                caretaker=user,
                appointment_date=timezone.now().date()
            ).count(),
            'pending_tasks': VolunteerTask.objects.filter(
                volunteer=user,
                status__in=['assigned', 'accepted']
            ).count(),
        }
    
    def _get_volunteer_stats(self, user):
        """Statistics for volunteers"""
        try:
            profile = VolunteerProfile.objects.get(user=user)
            return {
                'total_hours': profile.total_hours,
                'seniors_helped': profile.seniors_helped,
                'tasks_completed': profile.tasks_completed,
                'pending_tasks': VolunteerTask.objects.filter(
                    volunteer=user,
                    status__in=['assigned', 'accepted']
                ).count(),
            }
        except VolunteerProfile.DoesNotExist:
            return {}
    
    def _get_admin_stats(self, user):
        """Statistics for admins"""
        if user.user_type == 'senior_admin':
            return {
                'total_seniors': User.objects.filter(user_type='senior').count(),
                'total_caretakers': User.objects.filter(user_type='caretaker').count(),
                'active_assignments': CareAssignment.objects.filter(is_active=True).count(),
                'active_alerts': EmergencyAlert.objects.filter(is_resolved=False).count(),
            }
        else:  # ngo_admin
            ngo = NGO.objects.filter(admin=user).first()
            if ngo:
                return {
                    'total_volunteers': VolunteerProfile.objects.filter(ngo=ngo).count(),
                    'active_tasks': VolunteerTask.objects.filter(
                        ngo=ngo,
                        status__in=['assigned', 'accepted', 'in_progress']
                    ).count(),
                    'upcoming_events': Event.objects.filter(
                        ngo=ngo,
                        event_date__gte=timezone.now().date(),
                        is_active=True
                    ).count(),
                }
        return {}
