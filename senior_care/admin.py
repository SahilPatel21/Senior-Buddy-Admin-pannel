"""
Senior Care App - Django Admin Configuration
Enhanced admin panel with filters, search, and custom actions
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    User, SeniorProfile, CaretakerProfile, NGO, VolunteerProfile,
    CareAssignment, Appointment, Medication, MedicationLog,
    VolunteerTask, EmergencyAlert, HealthRecord, Event,
    EventRegistration, Notification
)


# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Enhanced admin for User model with custom filters and actions
    """
    list_display = ['username', 'full_name', 'user_type_badge', 'email', 'phone_number', 
                    'is_active_user', 'last_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'profile_picture', 'date_of_birth',
                      'address', 'city', 'state', 'zip_code')
        }),
        ('Status', {
            'fields': ('is_active_user', 'last_active')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'email')
        }),
    )
    
    # Custom display methods
    def full_name(self, obj):
        return obj.get_full_name() or obj.username
    full_name.short_description = 'Full Name'
    
    def user_type_badge(self, obj):
        """Display user type with color badge"""
        colors = {
            'senior': '#4CAF50',
            'caretaker': '#2196F3',
            'senior_admin': '#FF9800',
            'volunteer': '#9C27B0',
            'ngo_admin': '#F44336',
        }
        color = colors.get(obj.user_type, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'User Type'
    
    # Custom actions
    actions = ['activate_users', 'deactivate_users', 'send_welcome_email']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active_user=True, is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active_user=False, is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def send_welcome_email(self, request, queryset):
        # Placeholder for email functionality
        count = queryset.count()
        self.message_user(request, f'Welcome email would be sent to {count} users.')
    send_welcome_email.short_description = 'Send welcome email'


# Senior Profile Admin
@admin.register(SeniorProfile)
class SeniorProfileAdmin(admin.ModelAdmin):
    list_display = ['senior_name', 'blood_group', 'living_arrangement', 'mobility_level', 
                    'care_level_needed', 'emergency_contact_name', 'emergency_contact_phone']
    list_filter = ['blood_group', 'living_arrangement', 'mobility_level', 'care_level_needed']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 
                     'emergency_contact_name', 'emergency_contact_phone']
    
    fieldsets = (
        ('Senior Information', {
            'fields': ('user',)
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'medical_conditions', 'allergies', 'current_medications')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Living Situation', {
            'fields': ('living_arrangement', 'mobility_level', 'care_level_needed')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
    
    def senior_name(self, obj):
        return obj.user.get_full_name()
    senior_name.short_description = 'Senior Name'
    senior_name.admin_order_field = 'user__first_name'


# Caretaker Profile Admin
@admin.register(CaretakerProfile)
class CaretakerProfileAdmin(admin.ModelAdmin):
    list_display = ['caretaker_name', 'years_of_experience', 'employment_type', 
                    'working_hours', 'is_available', 'rating_display', 'background_check_status']
    list_filter = ['is_available', 'employment_type', 'working_hours', 'background_check_completed']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'specializations']
    
    fieldsets = (
        ('Caretaker Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('years_of_experience', 'certifications', 'specializations')
        }),
        ('Availability', {
            'fields': ('is_available', 'working_hours', 'employment_type')
        }),
        ('Performance', {
            'fields': ('rating', 'total_reviews')
        }),
        ('Background Check', {
            'fields': ('background_check_completed', 'background_check_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def caretaker_name(self, obj):
        return obj.user.get_full_name()
    caretaker_name.short_description = 'Caretaker Name'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '⭐' * int(obj.rating)
        return f'{obj.rating} {stars}'
    rating_display.short_description = 'Rating'
    
    def background_check_status(self, obj):
        if obj.background_check_completed:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')
    background_check_status.short_description = 'Background Check'


# NGO Admin
@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'admin_name', 'is_verified', 
                    'is_active', 'volunteer_count', 'established_date']
    list_filter = ['is_verified', 'is_active', 'state', 'created_at']
    search_fields = ['name', 'registration_number', 'email', 'city']
    
    fieldsets = (
        ('Organization Details', {
            'fields': ('name', 'registration_number', 'logo', 'description', 'mission')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Administration', {
            'fields': ('admin',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'established_date')
        }),
    )
    
    def admin_name(self, obj):
        return obj.admin.get_full_name() if obj.admin else 'No Admin'
    admin_name.short_description = 'Admin'
    
    def volunteer_count(self, obj):
        return obj.volunteers.count()
    volunteer_count.short_description = 'Volunteers'
    
    actions = ['verify_ngos', 'activate_ngos', 'deactivate_ngos']
    
    def verify_ngos(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} NGOs verified successfully.')
    verify_ngos.short_description = 'Verify selected NGOs'
    
    def activate_ngos(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} NGOs activated.')
    activate_ngos.short_description = 'Activate NGOs'
    
    def deactivate_ngos(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} NGOs deactivated.')
    deactivate_ngos.short_description = 'Deactivate NGOs'


# Volunteer Profile Admin
@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['volunteer_name', 'ngo_name', 'volunteer_id', 'is_available', 
                    'total_hours', 'seniors_helped', 'tasks_completed', 'rating_display']
    list_filter = ['is_available', 'ngo', 'background_check_completed', 'availability_hours']
    search_fields = ['user__first_name', 'user__last_name', 'volunteer_id', 'user__email']
    
    fieldsets = (
        ('Volunteer Information', {
            'fields': ('user', 'ngo', 'volunteer_id', 'join_date')
        }),
        ('Availability', {
            'fields': ('is_available', 'availability_hours')
        }),
        ('Skills & Interests', {
            'fields': ('skills', 'interests')
        }),
        ('Statistics', {
            'fields': ('total_hours', 'seniors_helped', 'tasks_completed')
        }),
        ('Performance', {
            'fields': ('rating', 'total_reviews')
        }),
        ('Verification', {
            'fields': ('background_check_completed', 'background_check_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def volunteer_name(self, obj):
        return obj.user.get_full_name()
    volunteer_name.short_description = 'Volunteer Name'
    
    def ngo_name(self, obj):
        return obj.ngo.name
    ngo_name.short_description = 'NGO'
    
    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating)
        return f'{obj.rating} {stars}'
    rating_display.short_description = 'Rating'


# Care Assignment Admin
@admin.register(CareAssignment)
class CareAssignmentAdmin(admin.ModelAdmin):
    list_display = ['senior_name', 'caretaker_name', 'start_date', 'end_date', 
                    'is_active', 'is_primary_caretaker']
    list_filter = ['is_active', 'is_primary_caretaker', 'start_date']
    search_fields = ['senior__first_name', 'senior__last_name', 
                     'caretaker__first_name', 'caretaker__last_name']
    date_hierarchy = 'start_date'
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def caretaker_name(self, obj):
        return obj.caretaker.get_full_name()
    caretaker_name.short_description = 'Caretaker'


# Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'senior_name', 'appointment_type', 'appointment_date', 
                    'appointment_time', 'status_badge', 'doctor_name']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['title', 'senior__first_name', 'senior__last_name', 'doctor_name']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('senior', 'title', 'appointment_type', 'description')
        }),
        ('Date & Time', {
            'fields': ('appointment_date', 'appointment_time', 'duration_minutes')
        }),
        ('Location & Doctor', {
            'fields': ('location', 'doctor_name')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Caretaker', {
            'fields': ('caretaker',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent', 'reminder_time')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def status_badge(self, obj):
        colors = {
            'scheduled': '#2196F3',
            'confirmed': '#4CAF50',
            'completed': '#9E9E9E',
            'cancelled': '#F44336',
            'rescheduled': '#FF9800',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'send_reminders']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} appointments confirmed.')
    mark_as_confirmed.short_description = 'Mark as confirmed'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} appointments marked completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def send_reminders(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'Reminders would be sent for {count} appointments.')
    send_reminders.short_description = 'Send reminders'


# Medication Admin
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['medication_name', 'senior_name', 'dosage', 'frequency', 
                    'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'frequency', 'start_date']
    search_fields = ['medication_name', 'senior__first_name', 'senior__last_name', 'prescribed_by']
    date_hierarchy = 'start_date'
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'


# Medication Log Admin
@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = ['medication_name', 'senior_name', 'scheduled_time', 
                    'was_taken_badge', 'actual_time', 'confirmed_by_name']
    list_filter = ['was_taken', 'scheduled_time']
    search_fields = ['medication__medication_name', 'medication__senior__first_name']
    date_hierarchy = 'scheduled_time'
    
    def medication_name(self, obj):
        return obj.medication.medication_name
    medication_name.short_description = 'Medication'
    
    def senior_name(self, obj):
        return obj.medication.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def was_taken_badge(self, obj):
        if obj.was_taken:
            return format_html('<span style="color: green;">✓ Taken</span>')
        return format_html('<span style="color: red;">✗ Missed</span>')
    was_taken_badge.short_description = 'Status'
    
    def confirmed_by_name(self, obj):
        return obj.confirmed_by.get_full_name() if obj.confirmed_by else '-'
    confirmed_by_name.short_description = 'Confirmed By'


# Volunteer Task Admin
@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'senior_name', 'volunteer_name', 
                    'scheduled_date', 'scheduled_time', 'status_badge', 'hours_logged']
    list_filter = ['status', 'task_type', 'scheduled_date', 'ngo']
    search_fields = ['title', 'senior__first_name', 'volunteer__first_name']
    date_hierarchy = 'scheduled_date'
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def volunteer_name(self, obj):
        return obj.volunteer.get_full_name()
    volunteer_name.short_description = 'Volunteer'
    
    def status_badge(self, obj):
        colors = {
            'assigned': '#2196F3',
            'accepted': '#FF9800',
            'in_progress': '#9C27B0',
            'completed': '#4CAF50',
            'cancelled': '#F44336',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_completed', 'mark_cancelled']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed', actual_end_time=timezone.now())
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} tasks cancelled.')
    mark_cancelled.short_description = 'Cancel tasks'


# Emergency Alert Admin
@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ['senior_name', 'alert_type', 'alert_time', 'location', 
                    'is_resolved_badge', 'resolved_by_name', 'response_time']
    list_filter = ['is_resolved', 'alert_type', 'alert_time']
    search_fields = ['senior__first_name', 'senior__last_name', 'location']
    date_hierarchy = 'alert_time'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('senior', 'alert_type', 'alert_time')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'response_time')
        }),
        ('Notes', {
            'fields': ('notes', 'resolution_notes', 'responders_notified')
        }),
    )
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def is_resolved_badge(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color: green;">✓ Resolved</span>')
        return format_html('<span style="color: red; font-weight: bold;">⚠ ACTIVE</span>')
    is_resolved_badge.short_description = 'Status'
    
    def resolved_by_name(self, obj):
        return obj.resolved_by.get_full_name() if obj.resolved_by else '-'
    resolved_by_name.short_description = 'Resolved By'
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_resolved.short_description = 'Mark as resolved'


# Health Record Admin
@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['senior_name', 'record_date', 'blood_pressure', 'heart_rate', 
                    'temperature', 'blood_sugar', 'oxygen_level', 'recorded_by_name']
    list_filter = ['record_date']
    search_fields = ['senior__first_name', 'senior__last_name']
    date_hierarchy = 'record_date'
    
    def senior_name(self, obj):
        return obj.senior.get_full_name()
    senior_name.short_description = 'Senior'
    
    def blood_pressure(self, obj):
        if obj.blood_pressure_systolic and obj.blood_pressure_diastolic:
            return f'{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic}'
        return '-'
    blood_pressure.short_description = 'BP (sys/dia)'
    
    def recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else '-'
    recorded_by_name.short_description = 'Recorded By'


# Event Admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'ngo_name', 'event_type', 'event_date', 'start_time', 
                    'venue', 'registration_status', 'is_active']
    list_filter = ['event_type', 'is_active', 'event_date', 'ngo']
    search_fields = ['title', 'description', 'venue', 'ngo__name']
    date_hierarchy = 'event_date'
    
    def ngo_name(self, obj):
        return obj.ngo.name
    ngo_name.short_description = 'NGO'
    
    def registration_status(self, obj):
        return f'{obj.current_registrations}/{obj.max_participants}'
    registration_status.short_description = 'Registrations'


# Event Registration Admin
@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'event_title', 'registration_date', 
                    'attended_badge', 'check_in_time']
    list_filter = ['attended', 'registration_date', 'event__ngo']
    search_fields = ['user__first_name', 'user__last_name', 'event__title']
    
    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'User'
    
    def event_title(self, obj):
        return obj.event.title
    event_title.short_description = 'Event'
    
    def attended_badge(self, obj):
        if obj.attended:
            return format_html('<span style="color: green;">✓ Attended</span>')
        return format_html('<span style="color: orange;">Registered</span>')
    attended_badge.short_description = 'Attendance'


# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user_name', 'notification_type', 'is_read_badge', 
                    'created_at', 'read_at']
    list_filter = ['is_read', 'notification_type', 'created_at']
    search_fields = ['title', 'message', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'
    
    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'User'
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: gray;">Read</span>')
        return format_html('<span style="color: blue; font-weight: bold;">Unread</span>')
    is_read_badge.short_description = 'Status'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'


# Customize Admin Site
admin.site.site_header = "Senior Care Admin Panel"
admin.site.site_title = "Senior Care Admin"
admin.site.index_title = "Welcome to Senior Care Administration"
