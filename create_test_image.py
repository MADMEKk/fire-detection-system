import cv2
import numpy as np

# Create a blank image (300x300) with a red-orange region simulating fire
img = np.zeros((300, 300, 3), dtype=np.uint8)

# Add some trees (green)
cv2.rectangle(img, (50, 100), (100, 200), (0, 255, 0), -1)
cv2.rectangle(img, (200, 100), (250, 200), (0, 255, 0), -1)

# Add fire (red-orange gradient)
for i in range(100):
    color = (0, 100 + i, 255)  # BGR format
    cv2.circle(img, (150, 150), 50-i//2, color, 2)

# Add smoke (gray)
cv2.rectangle(img, (100, 50), (200, 100), (128, 128, 128), -1)

# Save the image
cv2.imwrite('test_fire.jpg', img)
