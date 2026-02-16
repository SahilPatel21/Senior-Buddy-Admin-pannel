"""
Senior Care App - Database Models
Django models for managing seniors, NGOs, caretakers, volunteers, and admins
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


# Custom User Model - Supports multiple user types
class User(AbstractUser):
    """
    Extended user model to support different user types
    """
    USER_TYPE_CHOICES = (
        ('senior', 'Senior'),
        ('caretaker', 'Caretaker'),
        ('senior_admin', 'Senior Admin'),
        ('volunteer', 'Volunteer'),
        ('ngo_admin', 'NGO Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    
    # Status and tracking
    is_active_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"


# Senior Profile - Extended information for seniors
class SeniorProfile(models.Model):
    """
    Additional profile information for senior citizens
    """
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='senior_profile')
    
    # Medical Information
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="List of medical conditions")
    allergies = models.TextField(blank=True, help_text="List of allergies")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    
    # Emergency Contacts
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    
    # Living Situation
    living_arrangement = models.CharField(
        max_length=50,
        choices=(
            ('alone', 'Living Alone'),
            ('family', 'With Family'),
            ('care_home', 'Care Home'),
            ('assisted', 'Assisted Living'),
        ),
        default='alone'
    )
    
    # Care needs
    mobility_level = models.CharField(
        max_length=20,
        choices=(
            ('independent', 'Independent'),
            ('walker', 'Uses Walker'),
            ('wheelchair', 'Wheelchair'),
            ('bedridden', 'Bedridden'),
        ),
        default='independent'
    )
    care_level_needed = models.CharField(
        max_length=20,
        choices=(
            ('minimal', 'Minimal'),
            ('moderate', 'Moderate'),
            ('extensive', 'Extensive'),
            ('24/7', '24/7 Care'),
        ),
        default='minimal'
    )
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Additional notes about the senior")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Senior Profile'
        verbose_name_plural = 'Senior Profiles'
    
    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"


# Caretaker Profile
class CaretakerProfile(models.Model):
    """
    Profile for professional caretakers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caretaker_profile')
    
    # Professional Information
    years_of_experience = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True, help_text="List of certifications")
    specializations = models.TextField(blank=True, help_text="Areas of specialization")
    
    # Availability
    is_available = models.BooleanField(default=True)
    working_hours = models.CharField(
        max_length=50,
        choices=(
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('on_call', 'On Call'),
        ),
        default='full_time'
    )
    
    # Employment
    employment_type = models.CharField(
        max_length=20,
        choices=(
            ('staff', 'Staff'),
            ('contract', 'Contract'),
            ('freelance', 'Freelance'),
        ),
        default='staff'
    )
    
    # Performance
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Background check
    background_check_completed = models.BooleanField(default=False)
    background_check_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Caretaker Profile'
        verbose_name_plural = 'Caretaker Profiles'
    
    def __str__(self):
        return f"Caretaker: {self.user.get_full_name()}"


# NGO Organization
class NGO(models.Model):
    """
    NGO/Organization managing volunteers
    """
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=17)
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    # Details
    description = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    logo = models.ImageField(upload_to='ngo_logos/', null=True, blank=True)
    
    # Admin user
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_ngos',
        limit_choices_to={'user_type': 'ngo_admin'}
    )
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    established_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'NGO'
        verbose_name_plural = 'NGOs'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Volunteer Profile
class VolunteerProfile(models.Model):
    """
    Profile for NGO volunteers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='volunteers')
    
    # Volunteer Information
    volunteer_id = models.CharField(max_length=50, unique=True)
    join_date = models.DateField(default=timezone.now)
    
    # Availability
    is_available = models.BooleanField(default=True)
    availability_hours = models.CharField(
        max_length=50,
        choices=(
            ('weekdays', 'Weekdays'),
            ('weekends', 'Weekends'),
            ('flexible', 'Flexible'),
        ),
        default='flexible'
    )
    
    # Skills and interests
    skills = models.TextField(blank=True, help_text="Skills and expertise")
    interests = models.TextField(blank=True, help_text="Areas of interest")
    
    # Statistics
    total_hours = models.PositiveIntegerField(default=0, help_text="Total volunteer hours")
    seniors_helped = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    
    # Performance
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Verification
    background_check_completed = models.BooleanField(default=False)
    background_check_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Volunteer Profile'
        verbose_name_plural = 'Volunteer Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.ngo.name}"


# Care Assignment - Links caretakers to seniors
class CareAssignment(models.Model):
    """
    Assignment of caretakers to seniors
    """
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='care_assignments',
        limit_choices_to={'user_type': 'senior'}
    )
    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='caretaker_assignments',
        limit_choices_to={'user_type': 'caretaker'}
    )
    
    # Assignment details
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_primary_caretaker = models.BooleanField(default=False)
    
    # Schedule
    schedule = models.TextField(blank=True, help_text="Care schedule details")
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Care Assignment'
        verbose_name_plural = 'Care Assignments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.caretaker.get_full_name()} → {self.senior.get_full_name()}"


# Appointments
class Appointment(models.Model):
    """
    Medical and care appointments for seniors
    """
    APPOINTMENT_TYPES = (
        ('doctor', 'Doctor Visit'),
        ('medication', 'Medication Checkup'),
        ('therapy', 'Therapy Session'),
        ('checkup', 'Regular Checkup'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    )
    
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'user_type': 'senior'}
    )
    
    # Appointment details
    title = models.CharField(max_length=200)
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    description = models.TextField(blank=True)
    
    # Date and time
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    
    # Location
    location = models.CharField(max_length=200)
    doctor_name = models.CharField(max_length=200, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=(
            ('scheduled', 'Scheduled'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('rescheduled', 'Rescheduled'),
        ),
        default='scheduled'
    )
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_time = models.DateTimeField(null=True, blank=True)
    
    # Attached caretaker
    caretaker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attended_appointments',
        limit_choices_to={'user_type': 'caretaker'}
    )
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.title} - {self.senior.get_full_name()} ({self.appointment_date})"


# Medication Schedule
class Medication(models.Model):
    """
    Medication tracking for seniors
    """
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medications',
        limit_choices_to={'user_type': 'senior'}
    )
    
    # Medication details
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(
        max_length=20,
        choices=(
            ('daily', 'Daily'),
            ('twice_daily', 'Twice Daily'),
            ('thrice_daily', 'Thrice Daily'),
            ('weekly', 'Weekly'),
            ('as_needed', 'As Needed'),
        )
    )
    
    # Timing
    time_of_day = models.CharField(max_length=200, help_text="E.g., Morning, Afternoon, Night")
    
    # Duration
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Instructions
    instructions = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Prescribed by
    prescribed_by = models.CharField(max_length=200, blank=True)
    prescription_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medication'
        verbose_name_plural = 'Medications'
        ordering = ['senior', 'medication_name']
    
    def __str__(self):
        return f"{self.medication_name} - {self.senior.get_full_name()}"


# Medication Log - Track if medication was taken
class MedicationLog(models.Model):
    """
    Log of medication intake
    """
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='logs')
    
    # When it should be taken
    scheduled_time = models.DateTimeField()
    
    # Was it taken?
    was_taken = models.BooleanField(default=False)
    actual_time = models.DateTimeField(null=True, blank=True)
    
    # Who confirmed?
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medication_confirmations'
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Medication Log'
        verbose_name_plural = 'Medication Logs'
        ordering = ['-scheduled_time']
    
    def __str__(self):
        status = "Taken" if self.was_taken else "Missed"
        return f"{self.medication.medication_name} - {status} ({self.scheduled_time.date()})"


# Volunteer Tasks
class VolunteerTask(models.Model):
    """
    Tasks assigned to volunteers
    """
    TASK_TYPES = (
        ('visit', 'Home Visit'),
        ('errands', 'Errands'),
        ('shopping', 'Shopping'),
        ('medical', 'Medical Assistance'),
        ('companion', 'Companionship'),
        ('call', 'Phone Call Check'),
        ('other', 'Other'),
    )
    
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='volunteer_tasks',
        limit_choices_to={'user_type': 'senior'}
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'user_type': 'volunteer'}
    )
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='tasks')
    
    # Task details
    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    description = models.TextField()
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    
    # Location
    location = models.CharField(max_length=200)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=(
            ('assigned', 'Assigned'),
            ('accepted', 'Accepted'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ),
        default='assigned'
    )
    
    # Completion
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    # Hours tracking
    hours_logged = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Volunteer Task'
        verbose_name_plural = 'Volunteer Tasks'
        ordering = ['scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"{self.title} - {self.volunteer.get_full_name()}"


# Emergency Alerts
class EmergencyAlert(models.Model):
    """
    Emergency alerts triggered by seniors
    """
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_alerts',
        limit_choices_to={'user_type': 'senior'}
    )
    
    # Alert details
    alert_time = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(
        max_length=20,
        choices=(
            ('medical', 'Medical Emergency'),
            ('fall', 'Fall Detected'),
            ('sos', 'SOS Button'),
            ('other', 'Other'),
        )
    )
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    
    # Response
    response_time = models.DurationField(null=True, blank=True)
    responders_notified = models.TextField(blank=True, help_text="List of people notified")
    
    notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Emergency Alert'
        verbose_name_plural = 'Emergency Alerts'
        ordering = ['-alert_time']
    
    def __str__(self):
        status = "Resolved" if self.is_resolved else "Active"
        return f"Emergency: {self.senior.get_full_name()} - {status} ({self.alert_time})"


# Health Records
class HealthRecord(models.Model):
    """
    Health tracking records for seniors
    """
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='health_records',
        limit_choices_to={'user_type': 'senior'}
    )
    
    # Record date
    record_date = models.DateField(default=timezone.now)
    record_time = models.TimeField(auto_now_add=True)
    
    # Vitals
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per minute")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="In Fahrenheit")
    blood_sugar = models.PositiveIntegerField(null=True, blank=True, help_text="mg/dL")
    oxygen_level = models.PositiveIntegerField(null=True, blank=True, help_text="SpO2 percentage")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="In kg")
    
    # Recorded by
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_health_data')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        ordering = ['-record_date', '-record_time']
    
    def __str__(self):
        return f"Health Record: {self.senior.get_full_name()} ({self.record_date})"


# Events (for NGOs)
class Event(models.Model):
    """
    Events organized by NGOs
    """
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(
        max_length=50,
        choices=(
            ('workshop', 'Workshop'),
            ('social', 'Social Gathering'),
            ('health', 'Health Camp'),
            ('fundraiser', 'Fundraiser'),
            ('training', 'Training'),
            ('other', 'Other'),
        )
    )
    
    # Date and time
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Location
    venue = models.CharField(max_length=200)
    address = models.TextField()
    
    # Capacity
    max_participants = models.PositiveIntegerField(default=50)
    current_registrations = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    registration_deadline = models.DateField(null=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['event_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.ngo.name} ({self.event_date})"


# Event Registrations
class EventRegistration(models.Model):
    """
    Track who registered for events
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    
    # Registration details
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Attendance
    attended = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
        unique_together = ['event', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} → {self.event.title}"


# Notifications
class Notification(models.Model):
    """
    In-app notifications for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=(
            ('appointment', 'Appointment'),
            ('medication', 'Medication'),
            ('task', 'Task'),
            ('emergency', 'Emergency'),
            ('event', 'Event'),
            ('general', 'General'),
        )
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Link to related object (optional)
    link_url = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"{self.title} - {self.user.username} ({status})"
