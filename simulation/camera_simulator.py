import cv2
import time
import requests
import json
from ultralytics import YOLO
import numpy as np
import os
from datetime import datetime

class FireDetectorSimulator:
    def __init__(self):
        # Initialize camera
        self.camera = cv2.VideoCapture(0)  # Use laptop's camera
        
        # Set camera resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Load YOLO model
        self.model = YOLO('fire_s.pt')
        
        # Backend configuration
        self.backend_url = "http://localhost:8000/api"
        self.camera_id = None
        
        # Camera location (simulated location)
        self.latitude = 35.6895
        self.longitude = 139.6917
        
        # Create images directory if it doesn't exist
        self.image_dir = "captured_images"
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Alert cooldown
        self.last_alert_time = 0
        self.alert_cooldown = 500  # seconds

    def register_camera(self):
        """Register this camera with the backend"""
        camera_data = {
            "name": "Laptop-Simulator",
            "location_name": "Test Location",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_active": True
        }

        try:
            response = requests.post(f"{self.backend_url}/cameras/", json=camera_data)
            if response.status_code == 201:
                self.camera_id = response.json()['id']
                print(f"Camera registered successfully with ID: {self.camera_id}")
                return True
            else:
                print(f"Failed to register camera: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error registering camera: {e}")
            return False

    def send_alert(self, image_path, confidence):
        """Send fire alert to backend"""
        if not self.camera_id:
            print("Camera not registered!")
            return False

        try:
            with open(image_path, 'rb') as img:
                files = {'image': ('fire.jpg', img, 'image/jpeg')}
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
                    print(f"🔥 Alert sent successfully! Confidence: {confidence:.2f}")
                    return True
                else:
                    print(f"Failed to send alert: {response.text}")
                    return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending alert: {e}")
            return False

    def draw_detection(self, frame, results):
        """Draw detection boxes and info on frame"""
        annotated = frame.copy()
        
        # Draw boxes
        boxes = results.boxes.xyxy.cpu().numpy()
        for box, conf in zip(boxes, results.boxes.conf):
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Add confidence text
            conf_text = f"{conf:.2f}"
            cv2.putText(annotated, conf_text, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        # Add info text
        cv2.putText(annotated, "Press 'q' to quit", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return annotated

    def run(self):
        """Main detection loop"""
        print("🎥 Starting fire detection simulation...")
        if not self.register_camera():
            print("Failed to register camera. Exiting...")
            return

        print("\n📋 Instructions:")
        print("- Press 'q' to quit")
        print("- Detection runs automatically")
        print("- Alerts are sent when confidence > 50%")
        print("- Alerts have 60-second cooldown\n")

        while True:
            try:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Run detection
                results = self.model(frame)[0]
                
                # Process results
                if len(results.boxes) > 0:
                    confidence = float(results.boxes.conf[0])
                    
                    # Draw detection on frame
                    frame = self.draw_detection(frame, results)
                    
                    # Add confidence display
                    cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                              (0, 255, 0) if confidence < 0.5 else (0, 0, 255), 2)
                    
                    # Check if we should send alert
                    if confidence > 0.5 and time.time() - self.last_alert_time > self.alert_cooldown:
                        # Save the frame
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_path = os.path.join(self.image_dir, f"fire_{timestamp}.jpg")
                        cv2.imwrite(image_path, frame)
                        
                        # Send alert
                        if self.send_alert(image_path, confidence):
                            self.last_alert_time = time.time()
                
                # Display the frame
                cv2.imshow('Fire Detection Simulation', frame)
                
                # Break on 'q' press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Stopping simulation...")
                    break
                
                # Small delay to prevent high CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(1)

        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = FireDetectorSimulator()
    detector.run()
