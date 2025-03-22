import cv2
import time
import requests
import json
from ultralytics import YOLO
import numpy as np
from picamera2 import Picamera2
import os
from datetime import datetime

class FireDetector:
    def __init__(self):
        # Initialize camera
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
        self.camera.start()
        time.sleep(2)  # Give camera time to warm up

        # Load YOLO model
        self.model = YOLO('fire_m.pt')

        # Backend configuration
        self.backend_url = "http://your-backend-url:8000/api"  # Change this to your backend URL
        self.camera_id = None
        
        # Camera location (update these with your actual coordinates)
        self.latitude = 0.0  # Replace with actual latitude
        self.longitude = 0.0  # Replace with actual longitude
        
        # Create images directory if it doesn't exist
        self.image_dir = "captured_images"
        os.makedirs(self.image_dir, exist_ok=True)

    def register_camera(self):
        """Register this camera with the backend"""
        camera_data = {
            "name": "RaspberryPi-FireDetector",
            "location_name": "Forest Area 1",  # Update this
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_active": True
        }

        try:
            response = requests.post(f"{self.backend_url}/cameras/", json=camera_data)
            if response.status_code == 201:
                self.camera_id = response.json()['id']
                print(f"Camera registered successfully with ID: {self.camera_id}")
            else:
                print(f"Failed to register camera: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error registering camera: {e}")

    def send_alert(self, image_path, confidence):
        """Send fire alert to backend"""
        if not self.camera_id:
            print("Camera not registered!")
            return

        try:
            with open(image_path, 'rb') as img:
                files = {'image': img}
                data = {
                    'camera': self.camera_id,
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                }
                
                response = requests.post(
                    f"{self.backend_url}/fire-alerts/",
                    files=files,
                    data=data
                )
                
                if response.status_code == 201:
                    print(f"Alert sent successfully! Confidence: {confidence:.2f}")
                else:
                    print(f"Failed to send alert: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending alert: {e}")

    def detect_fire(self, frame):
        """Run fire detection on frame"""
        results = self.model(frame)[0]
        
        if len(results.boxes) > 0:
            confidence = float(results.boxes.conf[0])
            if confidence > 0.5:  # Confidence threshold
                return True, confidence, results
        return False, 0.0, None

    def draw_detection(self, frame, results):
        """Draw detection boxes on frame"""
        annotated = frame.copy()
        boxes = results.boxes.xyxy.cpu().numpy()
        for box, conf in zip(boxes, results.boxes.conf):
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated, f"{conf:.2f}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        return annotated

    def run(self):
        """Main detection loop"""
        print("Starting fire detection...")
        self.register_camera()
        
        last_alert_time = 0
        alert_cooldown = 60  # Minimum seconds between alerts
        
        while True:
            try:
                # Capture frame
                frame = self.camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect fire
                fire_detected, confidence, results = self.detect_fire(frame)
                
                if fire_detected and time.time() - last_alert_time > alert_cooldown:
                    # Save the original image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(self.image_dir, f"fire_{timestamp}.jpg")
                    
                    # Draw detection boxes
                    annotated_frame = self.draw_detection(frame, results)
                    
                    # Save both original and annotated images
                    cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    cv2.imwrite(image_path.replace('.jpg', '_annotated.jpg'), 
                              cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
                    
                    # Send alert
                    self.send_alert(image_path, confidence)
                    last_alert_time = time.time()
                
                # Optional: Display the frame (if you have a display connected)
                # cv2.imshow('Fire Detection', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(5)  # Wait before retrying

        self.camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = FireDetector()
    detector.run()
