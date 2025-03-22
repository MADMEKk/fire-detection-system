from ultralytics import YOLO
from PIL import Image
import cv2

# Load the model
model = YOLO('fire_m.pt')

# Open the video file
video_path = '130076-746154338_tiny.mp4'
cap = cv2.VideoCapture(video_path)

# Define the desired window size
window_width = 1080
window_height = 620

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame, conf=0.2, iou=0.1)

    # Display the results on the frame
    annotated_frame = results[0].plot()

    # Resize the frame to fit the window
    resized_frame = cv2.resize(annotated_frame, (window_width, window_height))

    # Show the frame
    cv2.imshow('YOLOv8 Inference', resized_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
