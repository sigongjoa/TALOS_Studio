import os
import sys

# Add conda environment's site-packages to the path
site_packages_path = '/home/zesky/miniconda/envs/vectorization/lib/python3.12/site-packages'
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

import shutil
import numpy as np
import cv2
import potracer # Import the new library

# --- Import our vectorization modules ---
from src.path_decomposition import find_contours
# simplify_polygon and fit_curve are no longer needed
from src.svg_exporter import save_svg

# --- We need to add the line_detection_comparison path to import its script ---
import sys
sys.path.append('line_detection_comparison')
from run_manga_line_extraction import run_manga_line_extraction_inference

def create_visualization_html(output_dir, image_dirs):
    """Generates the final index.html to display all results."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en"><head>
    <meta charset="utf-8"/>
    <title>Vectorization Showcase</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
    </head>
    <body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold text-center mb-8">Image Vectorization Showcase</h1>
    """

    for img_dir in sorted(image_dirs):
        base_name = os.path.basename(img_dir)
        html_content += f'''
        <div class="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h2 class="text-2xl font-bold mb-4">{base_name}</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                    <h3 class="font-semibold">1. Original</h3>
                    <img src="{base_name}/original.png" alt="Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">2. Line Art (Input)</h3>
                    <img src="{base_name}/line_art.png" alt="Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">3. Final Vector (SVG)</h3>
                    <img src="{base_name}/vector.svg" alt="Vector SVG" class="inline-block w-full h-auto border"/>
                </div>
            </div>
        </div>
        '''

    html_content += "</div></body></html>"

    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html_content)

def main():
    INPUT_DIR = "ref"
    OUTPUT_DIR = "output_visualizations"
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    image_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    processed_image_dirs = []

    for image_file in image_files:
        print(f"--- Processing {image_file} ---")
        base_name = os.path.splitext(image_file)[0]
        
        image_output_dir = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(image_output_dir, exist_ok=True)
        processed_image_dirs.append(base_name)

        original_img_path = os.path.join(INPUT_DIR, image_file)
        line_art_path = os.path.join(image_output_dir, "line_art.png")

        shutil.copy(original_img_path, os.path.join(image_output_dir, "original.png"))
        input_image = cv2.imread(original_img_path)
        h, w, _ = input_image.shape

        print("Step 1: Extracting Lines...")
        run_manga_line_extraction_inference(original_img_path, line_art_path)
        
        print("Step 2: Vectorizing with Potracer...")
        # Load the line art image as a numpy array for potracer
        data = cv2.imread(line_art_path, cv2.IMREAD_GRAYSCALE)
        # Potracer works best with inverted images (black lines on white background)
        data = 255 - data

        # Create a potrace Bitmap from the data
        bitmap = potracer.Bitmap(data)

        # Trace the bitmap
        path = bitmap.trace()

        # --- Step 3: Save final SVG --- 
        print("Step 3: Saving results...")
        svg_path = os.path.join(image_output_dir, "vector.svg")
        with open(svg_path, "w") as f:
            f.write(f"<svg width='{w}' height='{h}' xmlns='http://www.w3.org/2000/svg'>")
            # The path object has a `vertices` property that can be used to generate an SVG path string
            parts = []
            for curve in path.curves:
                parts.append(f"M{curve.start_point.x:.2f},{curve.start_point.y:.2f}")
                for segment in curve.segments:
                    x1, y1 = segment.c1.x, segment.c1.y
                    x2, y2 = segment.c2.x, segment.c2.y
                    x3, y3 = segment.end_point.x, segment.end_point.y
                    parts.append(f"C{x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f} {x3:.2f},{y3:.2f}")
            f.write(f'<path d="{" ".join(parts)}" stroke="black" fill="none" stroke-width="0.5"/>')
            f.write('</svg>')
        print(f"Saved SVG to {svg_path}")

    print("Step 4: Creating showcase HTML...")
    create_visualization_html(OUTPUT_DIR, processed_image_dirs)

    print("\nShowcase generation complete!")

if __name__ == "__main__":
    main()