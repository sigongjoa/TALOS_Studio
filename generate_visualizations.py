import os
import shutil
import cv2
import numpy as np
import json
import sys

# Add project root to sys.path for module discovery
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# General imports
from AXIS.scripts.line_to_bezier import convert_lines_to_bezier

# --- Configuration ---
INPUT_IMAGE_PATHS = [
    "/mnt/d/progress/TALOS_Studio/ref/image_01.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/image_02.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/image_03.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/image_04.jpg",
    "/mnt/d/progress/TALOS_Studio/ref/image_05.jpg",
]
OUTPUT_BASE_DIR = "output_visualizations"

# --- Panel Generation Functions ---

def generate_panel_original(input_image_path, output_dir):
    """Copies the original image to the output directory."""
    filename = "original.png"
    output_path = os.path.join(output_dir, filename)
    shutil.copy(input_image_path, output_path)
    print(f"Saved Panel 1 (Original) to {output_path}")
    return filename

def generate_panel_manga_lines(input_image_path, output_dir):
    """Generates the manga line extraction panel."""
    from line_detection_comparison.run_manga_line_extraction import run_manga_line_extraction_inference
    filename = "manga_lines.png"
    output_path = os.path.join(output_dir, filename)
    run_manga_line_extraction_inference(input_image_path, output_path)
    print(f"Saved Panel 2 (Manga Lines) to {output_path}")
    return filename, output_path # Return path for subsequent steps

def generate_panel_inverted_lines(manga_line_image_path, output_dir):
    """Generates the inverted black and white lines panel."""
    filename = "inverted_lines.png"
    output_path = os.path.join(output_dir, filename)
    img = cv2.imread(manga_line_image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load image for Panel 3 from {manga_line_image_path}")
        return None
    processed_img = np.where(img < 200, 0, 255).astype(np.uint8)
    inverted_img = 255 - processed_img
    cv2.imwrite(output_path, inverted_img)
    print(f"Saved Panel 3 (Inverted) to {output_path}")
    return filename

def generate_panel_sold2(manga_line_image_path, output_dir):
    """Generates the SOLD2 detection panel and Bezier curve data."""
    from line_detection_comparison.run_sold2 import run_sold2_inference
    img_filename = "sold2_detection.png"
    json_filename = "sold2_bezier_curves.json"
    img_output_path = os.path.join(output_dir, img_filename)
    
    line_segments = run_sold2_inference(manga_line_image_path, img_output_path)
    print(f"Saved Panel 4 (SOLD2) to {img_output_path}")

    if line_segments:
        bezier_curves = convert_lines_to_bezier(line_segments)
        json_output_path = os.path.join(output_dir, json_filename)
        with open(json_output_path, "w") as f:
            json.dump(bezier_curves, f, indent=4)
        print(f"Saved Bezier curves to {json_output_path}")
    
    return img_filename

def generate_panel_canny(manga_line_image_path, output_dir):
    """Generates the Canny edge detection panel."""
    filename = "canny_detection.png"
    output_path = os.path.join(output_dir, filename)
    img = cv2.imread(manga_line_image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load image for Panel 5 from {manga_line_image_path}")
        return None
    edges = cv2.Canny(img, 100, 200)
    cv2.imwrite(output_path, edges)
    print(f"Saved Panel 5 (Canny) to {output_path}")
    return filename

def generate_panel_dsine(input_image_path, output_dir):
    """Generates the DSINE detection panel using the real model."""
    from line_detection_comparison.run_dsine import run_dsine_inference
    filename = "dsine_detection.png"
    output_path = os.path.join(output_dir, filename)
    run_dsine_inference(input_image_path, output_path)
    return filename

# --- HTML Generation ---

def generate_html_report(image_data):
    """Generates an HTML report from the visualization data."""
    
    headers = {
        "original": "Original Image",
        "manga_lines": "Manga Line Extraction",
        "inverted_lines": "Inverted B/W Lines",
        "sold2": "Line Detection (SOLD2)",
        "canny": "Curve Detection (Canny)",
        "dsine": "Depth/Normals (DSINE)"
    }
    
    # Generate headers row
    header_html = "".join([f'<div class="grid-item header">{headers.get(key, "Unknown")}</div>' for key in headers.keys()])

    # Generate image rows
    rows_html = ""
    for image_id, panels in image_data.items():
        rows_html += '<div class="grid-row">\n'
        for key in headers.keys():
            filename = panels.get(key)
            if filename:
                rows_html += f'<div class="grid-item"><img src="{image_id}/{filename}" alt="{headers.get(key)}"></div>\n'
            else:
                rows_html += f'<div class="grid-item">Not Generated</div>\n'
        rows_html += "</div>\n"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Line Detection Visualizations</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
        .grid-container {{ display: grid; grid-auto-rows: auto; gap: 10px; }}
        .grid-row {{ display: contents; }}
        .grid-item {{ border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #fff; }}
        .grid-item img {{ max-width: 100%; height: auto; display: block; margin: 0 auto; }}
        .header {{ font-weight: bold; background-color: #e0e0e0; }}
        /* Set grid columns based on number of headers */
        .grid-container {{ grid-template-columns: repeat({len(headers)}, 1fr); }}
    </style>
</head>
<body>
    <h1>Line Detection Visualizations</h1>
    <div class="grid-container">
        {header_html}
        {rows_html}
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_file_path = os.path.join(OUTPUT_BASE_DIR, "index.html")
    with open(html_file_path, "w") as f:
        f.write(html_content)
    print(f"Generated HTML visualization page at {html_file_path}")


# --- Main Execution Logic ---

def generate_visualizations(models_to_run=None):
    """
    Generates visualizations for a list of models.
    :param models_to_run: A list of strings, e.g., ['original', 'manga_lines', 'sold2']. 
                          If None, all models are run.
    """
    if models_to_run is None:
        models_to_run = ['original', 'manga_lines', 'inverted_lines', 'sold2', 'canny', 'dsine']

    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    
    all_image_data = {}

    for i, input_image_path in enumerate(INPUT_IMAGE_PATHS):
        image_id = f"image_{{i+1:02d}}"
        output_sub_dir = os.path.join(OUTPUT_BASE_DIR, image_id)
        os.makedirs(output_sub_dir, exist_ok=True)
        
        image_panels = {}

        if 'original' in models_to_run:
            image_panels['original'] = generate_panel_original(input_image_path, output_sub_dir)

        # Manga lines are required for several other panels
        manga_lines_img_path = None
        if any(m in models_to_run for m in ['manga_lines', 'inverted_lines', 'sold2', 'canny']):
            image_panels['manga_lines'], manga_lines_img_path = generate_panel_manga_lines(input_image_path, output_sub_dir)

        if 'inverted_lines' in models_to_run and manga_lines_img_path:
            image_panels['inverted_lines'] = generate_panel_inverted_lines(manga_lines_img_path, output_sub_dir)

        if 'sold2' in models_to_run and manga_lines_img_path:
            image_panels['sold2'] = generate_panel_sold2(manga_lines_img_path, output_sub_dir)

        if 'canny' in models_to_run and manga_lines_img_path:
            image_panels['canny'] = generate_panel_canny(manga_lines_img_path, output_sub_dir)
            
        if 'dsine' in models_to_run:
            # Note: DSINE might work better on the original image
            image_panels['dsine'] = generate_panel_dsine(input_image_path, output_sub_dir)

        all_image_data[image_id] = image_panels

    generate_html_report(all_image_data)

if __name__ == "__main__":
    # Example: Run only specific models
    # generate_visualizations(models_to_run=['original', 'manga_lines', 'dsine'])
    
    # Run all visualizations by default
    generate_visualizations()