from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Camera, FireAlert, UserProfile, Verification
from .serializers import CameraSerializer, FireAlertSerializer, UserProfileSerializer
from django.utils import timezone
from datetime import timedelta
import cv2
import os
from django.conf import settings
import threading
import time
from ultralytics import YOLO

# Initialize YOLO model
model = YOLO('fire_s.pt')

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

    def perform_create(self, serializer):
        camera = serializer.save()
        print(f"Camera {camera.name} created at {camera.location_name}")

class FireAlertViewSet(viewsets.ModelViewSet):
    queryset = FireAlert.objects.all()
    serializer_class = FireAlertSerializer

    def perform_create(self, serializer):
        alert = serializer.save()
        self.detect_fire(alert)

    def detect_fire(self, alert):
        img = cv2.imread(alert.image.path)
        results = model(img)[0]
        
        if len(results.boxes) > 0:
            max_conf = float(results.boxes.conf[0])
            
            if max_conf > 0.5:  # Confidence threshold
                # Create annotated image
                annotated_img = img.copy()
                boxes = results.boxes.xyxy.cpu().numpy()
                for box, conf in zip(boxes, results.boxes.conf):
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    conf_text = f"{conf:.2f}"
                    cv2.putText(annotated_img, conf_text, (x1, y1-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                # Save annotated image
                annotated_path = os.path.join(settings.MEDIA_ROOT, 'alerts',
                                          f'alert_{alert.id}_annotated.jpg')
                cv2.imwrite(annotated_path, annotated_img)
                
                # Update alert
                alert.annotated_image = annotated_path
                alert.detection_confidence = max_conf
                alert.verification_deadline = timezone.now() + timedelta(minutes=5)
                alert.save()
                
                # Start verification process
                self.start_verification_process(alert)
            else:
                alert.detection_confidence = max_conf
                alert.save()

    def start_verification_process(self, alert):
        """Start the three-wave verification process"""
        # First wave: Try regular users
        verified = self.request_verification_wave(alert, is_ranked=False)
        if verified:
            return

        # Wait 30 seconds for first wave response
        time.sleep(30)
        alert.refresh_from_db()
        if alert.status != 'pending':
            return  # Alert was verified

        # Second wave: Try new regular users
        verified = self.request_verification_wave(alert, is_ranked=False)
        if verified:
            return

        # Wait 30 seconds for second wave response
        time.sleep(30)
        alert.refresh_from_db()
        if alert.status != 'pending':
            return  # Alert was verified

        # Final wave: Send to ranked users
        self.request_verification_wave(alert, is_ranked=True)

    def request_verification_wave(self, alert, is_ranked=False):
        """Request verification from a wave of users"""
        # Get available users based on rank
        if is_ranked:
            nearby_users = UserProfile.objects.filter(
                is_available=True,
                last_verification__lte=timezone.now() - timedelta(minutes=10),
                rank__in=['expert', 'master']
            ).order_by('-guardian_points')
        else:
            nearby_users = UserProfile.objects.filter(
                is_available=True,
                last_verification__lte=timezone.now() - timedelta(minutes=10),
                rank__in=['rookie', 'guardian']
            ).order_by('?')[:5]  # Random 5 users

        verifications_created = 0
        for user_profile in nearby_users:
            verification = Verification.objects.create(
                alert=alert,
                verifier=user_profile.user,
                notification_sent=timezone.now()
            )
            verifications_created += 1
            
            # Update user's availability
            user_profile.is_available = False
            user_profile.last_verification = timezone.now()
            user_profile.save()

        return verifications_created > 0

@api_view(['POST'])
def verify_fire(request):
    alert_id = request.data.get('alert_id')
    vote = request.data.get('vote')
    user_id = request.data.get('user_id')

    try:
        verification = Verification.objects.get(
            alert_id=alert_id,
            verifier_id=user_id,
            vote__isnull=True  # Only allow unvoted verifications
        )
        
        # Record the vote
        verification.vote = vote
        verification.vote_time = timezone.now()
        verification.save()
        
        # Update user profile
        user_profile = UserProfile.objects.get(user_id=user_id)
        user_profile.is_available = True
        
        # Award points based on speed and rank
        time_taken = (verification.vote_time - verification.notification_sent).total_seconds()
        speed_bonus = max(0, 30 - time_taken)  # Bonus points for fast response
        
        if user_profile.rank in ['expert', 'master']:
            points = 20 + speed_bonus  # More points for ranked users
        else:
            points = 10 + speed_bonus
            
        user_profile.guardian_points += points
        user_profile.save()
        
        # Update alert status if enough votes
        alert = verification.alert
        total_votes = Verification.objects.filter(
            alert=alert,
            vote__isnull=False
        ).count()
        
        if total_votes >= 3:  # Consider alert verified after 3 votes
            positive_votes = Verification.objects.filter(
                alert=alert,
                vote=True
            ).count()
            
            alert.status = 'confirmed' if positive_votes >= 2 else 'false_alarm'
            alert.save()
        
        return Response({
            'status': 'success',
            'points_earned': points,
            'new_total_points': user_profile.guardian_points
        })
        
    except Verification.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Verification not found or already voted'
        }, status=400)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)
