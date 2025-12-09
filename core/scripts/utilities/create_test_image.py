import numpy as np
import cv2
import os

# Define image properties
img_size = (100, 100)
rect_start = (25, 25)
rect_end = (75, 75)
color = 255  # White

# Create a black image
img = np.zeros(img_size, dtype=np.uint8)

# Draw a white rectangle
cv2.rectangle(img, rect_start, rect_end, color, -1)  # Filled rectangle

# Save the image
output_dir = "/mnt/d/progress/TALOS_Studio/vectorization/input/"
os.makedirs(output_dir, exist_ok=True)
test_image_path = os.path.join(output_dir, "test_square.png")
cv2.imwrite(test_image_path, img)

print(f"Created test image at {test_image_path}")
