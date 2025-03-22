from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

RANKS = [
    ('rookie', 'Rookie Guardian'),
    ('trusted', 'Trusted Guardian'),
    ('expert', 'Expert Guardian'),
    ('master', 'Master Guardian'),
    ('legend', 'Legendary Guardian'),
]

class Camera(models.Model):
    name = models.CharField(max_length=100)
    location_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    last_check = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} at {self.location_name}"

class FireAlert(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='alerts/')
    annotated_image = models.ImageField(upload_to='alerts/', null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    detection_confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Verification'),
        ('confirmed', 'Fire Confirmed'),
        ('false_alarm', 'False Alarm')
    ], default='pending')
    votes_yes = models.IntegerField(default=0)
    votes_no = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verification_deadline = models.DateTimeField(null=True)
    weather_data = models.JSONField(null=True, blank=True)
    fire_size = models.CharField(max_length=20, choices=[
        ('small', 'Small Fire'),
        ('medium', 'Medium Fire'),
        ('large', 'Large Fire')
    ], null=True, blank=True)

    def is_verification_expired(self):
        if not self.verification_deadline:
            return False
        return timezone.now() > self.verification_deadline

    def __str__(self):
        return f"Fire Alert {self.id} - {self.status}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    guardian_points = models.IntegerField(default=0)
    rank = models.CharField(max_length=20, choices=RANKS, default='rookie')
    badges = models.JSONField(default=list)
    correct_verifications = models.IntegerField(default=0)
    response_time_avg = models.FloatField(default=0)
    is_available = models.BooleanField(default=True)
    last_verification = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)  # For Firebase notifications

    def update_rank(self):
        points = self.guardian_points
        if points >= 10000:
            self.rank = 'legend'
        elif points >= 5000:
            self.rank = 'master'
        elif points >= 2000:
            self.rank = 'expert'
        elif points >= 500:
            self.rank = 'trusted'
        else:
            self.rank = 'rookie'

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Verification(models.Model):
    alert = models.ForeignKey(FireAlert, on_delete=models.CASCADE)
    verifier = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.IntegerField(null=True)  # in seconds
    points_awarded = models.IntegerField(default=0)
    notification_sent = models.DateTimeField(null=True)
    expired = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification by {self.verifier.username} for Alert {self.alert.id}"

    class Meta:
        unique_together = ('alert', 'verifier')
