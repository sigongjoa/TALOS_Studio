import os
import shutil
import cv2
import numpy as np
from PIL import Image
import sys

# Add project root to sys.path for module discovery
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import helper inference functions
from line_detection_comparison.run_manga_line_extraction import run_manga_line_extraction_inference
from line_detection_comparison.run_sold2 import run_sold2_inference

# --- Configuration ---
INPUT_IMAGE_PATHS = [
    "/mnt/d/progress/TALOS_Studio/ref/9007332256_494354581_52d22d527725b5f1e148fbfc4cd38644.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/9007332256_494354581_55bd5db1c16c0c5d0878ec89a08eb0fa.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/9007332256_494354581_688778cbd035d6d37a3ffc3b408f1b40.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/9007332256_494354581_b4431b5b6edd1e0871d023193f40ffff.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/9007332256_494354581_fe61fe9b128055cdb3949527920d057d.jpg",
]
OUTPUT_BASE_DIR = "output_visualizations"

# --- Helper Functions for Image Processing ---
def process_for_panel3(manga_line_image_path, output_path):
    print(f"Processing for Panel 3: {manga_line_image_path}")
    img = cv2.imread(manga_line_image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load image for Panel 3 from {manga_line_image_path}")
        return

    # Convert non-white to black, white to white
    # Assuming manga_line_image is mostly white background with black lines
    # If pixel is not almost white (e.g., < 200), make it black (0), else white (255)
    processed_img = np.where(img < 200, 0, 255).astype(np.uint8)

    # Invert colors
    inverted_img = 255 - processed_img
    cv2.imwrite(output_path, inverted_img)
    print(f"Saved Panel 3 output to {output_path}")

def process_for_panel5(manga_line_image_path, output_path):
    print(f"Processing for Panel 5 (Canny): {manga_line_image_path}")
    img = cv2.imread(manga_line_image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load image for Panel 5 from {manga_line_image_path}")
        return

    # Apply Canny edge detection
    edges = cv2.Canny(img, 100, 200) # Adjust thresholds as needed
    cv2.imwrite(output_path, edges)
    print(f"Saved Panel 5 output to {output_path}")

# --- Main Visualization Generation Logic ---
def generate_visualizations():
    # Ensure base output directory exists
    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Line Detection Visualizations</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .grid-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
        .grid-item { border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #fff; }
        .grid-item img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
        .header { font-weight: bold; background-color: #e0e0e0; }
    </style>
</head>
<body>
    <h1>Line Detection Visualizations</h1>
    <div class="grid-container">
        <div class="grid-item header">Original Image</div>
        <div class="grid-item header">Manga Line Extraction</div>
        <div class="grid-item header">Inverted B/W Lines</div>
        <div class="grid-item header">Line Detection (SOLD2)</div>
        <div class="grid-item header">Curve Detection (Canny)</div>
"""

    for i, input_image_path in enumerate(INPUT_IMAGE_PATHS):
        image_id = f"image_{i+1:02d}"
        output_sub_dir = os.path.join(OUTPUT_BASE_DIR, image_id)
        os.makedirs(output_sub_dir, exist_ok=True)

        # Panel 1: Original Image
        original_img_name = "original.png"
        original_img_path = os.path.join(output_sub_dir, original_img_name)
        shutil.copy(input_image_path, original_img_path)
        print(f"Copied original image to {original_img_path}")

        # Panel 2: Manga Line Extraction
        manga_lines_img_name = "manga_lines.png"
        manga_lines_img_path = os.path.join(output_sub_dir, manga_lines_img_name)
        run_manga_line_extraction_inference(input_image_path, manga_lines_img_path)

        # Panel 3: Black/White & Inverted Lines
        inverted_lines_img_name = "inverted_lines.png"
        inverted_lines_img_path = os.path.join(output_sub_dir, inverted_lines_img_name)
        process_for_panel3(manga_lines_img_path, inverted_lines_img_path)

        # Panel 4: Line Detection (SOLD2)
        sold2_detection_img_name = "sold2_detection.png"
        sold2_detection_img_path = os.path.join(output_sub_dir, sold2_detection_img_name)
        run_sold2_inference(manga_lines_img_path, sold2_detection_img_path)

        # Panel 5: Curve Detection (Canny)
        canny_detection_img_name = "canny_detection.png"
        canny_detection_img_path = os.path.join(output_sub_dir, canny_detection_img_name)
        process_for_panel5(manga_lines_img_path, canny_detection_img_path)

        # Add row to HTML content
        html_content += f"""
        <div class="grid-item"><img src="{image_id}/{original_img_name}" alt="Original"></div>
        <div class="grid-item"><img src="{image_id}/{manga_lines_img_name}" alt="Manga Lines"></div>
        <div class="grid-item"><img src="{image_id}/{inverted_lines_img_name}" alt="Inverted B/W Lines"></div>
        <div class="grid-item"><img src="{image_id}/{sold2_detection_img_name}" alt="Line Detection (SOLD2)"></div>
        <div class="grid-item"><img src="{image_id}/{canny_detection_img_name}" alt="Curve Detection (Canny)"></div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    # Save HTML file
    html_file_path = os.path.join(OUTPUT_BASE_DIR, "index.html")
    with open(html_file_path, "w") as f:
        f.write(html_content)
    print(f"Generated HTML visualization page at {html_file_path}")

if __name__ == "__main__":
    generate_visualizations()