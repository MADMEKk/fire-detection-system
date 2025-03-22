from rest_framework import serializers
from .models import FireAlert, UserProfile, Verification, Camera

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'name', 'location_name', 'latitude', 'longitude', 
                 'is_active', 'last_check', 'created_at']
        read_only_fields = ['last_check', 'created_at']

class FireAlertSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    annotated_image = serializers.ImageField(read_only=True)
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = FireAlert
        fields = ['id', 'camera', 'camera_name', 'image', 'annotated_image', 
                 'latitude', 'longitude', 'reporter_name', 'status', 
                 'detection_confidence', 'votes_yes', 'votes_no', 
                 'created_at', 'verification_deadline', 'time_remaining',
                 'weather_data', 'fire_size']
        read_only_fields = ['camera_name', 'reporter_name', 'status', 
                           'detection_confidence', 'votes_yes', 'votes_no', 
                           'created_at', 'verification_deadline', 'time_remaining',
                           'weather_data', 'fire_size']

    def get_time_remaining(self, obj):
        if obj.verification_deadline:
            from django.utils import timezone
            remaining = obj.verification_deadline - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    verification_stats = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'guardian_points', 'rank', 'rank_display',
                 'badges', 'correct_verifications', 'response_time_avg',
                 'is_available', 'verification_stats', 'created_at']
        read_only_fields = ['guardian_points', 'rank', 'badges', 
                           'correct_verifications', 'response_time_avg']

    def get_verification_stats(self, obj):
        return {
            'total_verifications': obj.correct_verifications,
            'avg_response_time': f"{obj.response_time_avg:.1f}s" if obj.response_time_avg else "N/A",
            'current_streak': self.get_verification_streak(obj)
        }

    def get_verification_streak(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        # Count consecutive days with verifications
        streak = 0
        current_date = timezone.now().date()
        
        while True:
            if Verification.objects.filter(
                verifier=obj.user,
                created_at__date=current_date,
                vote__isnull=False
            ).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak

class VerificationSerializer(serializers.ModelSerializer):
    verifier_name = serializers.CharField(source='verifier.username', read_only=True)
    alert_details = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Verification
        fields = ['id', 'alert', 'alert_details', 'verifier_name', 
                 'vote', 'created_at', 'response_time', 'points_awarded',
                 'notification_sent', 'expired', 'time_remaining']
        read_only_fields = ['verifier_name', 'created_at', 'response_time',
                           'points_awarded', 'notification_sent', 'expired']

    def get_alert_details(self, obj):
        return {
            'location': obj.alert.camera.location_name,
            'confidence': obj.alert.detection_confidence,
            'status': obj.alert.status,
            'image_url': self.context['request'].build_absolute_uri(obj.alert.image.url),
            'annotated_url': (self.context['request'].build_absolute_uri(obj.alert.annotated_image.url) 
                            if obj.alert.annotated_image else None)
        }

    def get_time_remaining(self, obj):
        if obj.alert.verification_deadline:
            from django.utils import timezone
            remaining = obj.alert.verification_deadline - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return None
