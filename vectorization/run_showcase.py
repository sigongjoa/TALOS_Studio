import os
import subprocess
import shutil
import numpy as np
import cv2

# --- Import our vectorization modules ---
from src.path_decomposition import find_contours
from src.polygon_optimization import simplify_polygon
from src.curve_fitting import fit_curve
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
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                <div>
                    <h3 class="font-semibold">Original</h3>
                    <img src="{base_name}/original.png" alt="Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">Line Art (Input)</h3>
                    <img src="{base_name}/line_art.png" alt="Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">Simplified Polygons</h3>
                    <img src="{base_name}/polygons.png" alt="Polygons" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">Final Vector (SVG)</h3>
                    <img src="{base_name}/vector.svg" alt="Vector SVG" class="inline-block w-full h-auto border"/>
                </div>
            </div>
        </div>
        '''

    html_content += "</div></body></html>"

    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html_content)

def main():
    # --- Configuration ---
    INPUT_DIR = "ref"
    # Let's use the main output_visualizations dir to integrate with CI/CD
    OUTPUT_DIR = "output_visualizations"
    
    # Clean up previous results
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    image_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    processed_image_dirs = []

    for image_file in image_files:
        print(f"--- Processing {image_file} ---")
        base_name = os.path.splitext(image_file)[0]
        
        # Create a dedicated output folder for this image
        image_output_dir = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(image_output_dir, exist_ok=True)
        processed_image_dirs.append(image_output_dir)

        original_img_path = os.path.join(INPUT_DIR, image_file)
        line_art_path = os.path.join(image_output_dir, "line_art.png")

        # --- Step 1: Prepare Input (Manga Line Extraction) ---
        print("Step 1: Extracting lines...")
        run_manga_line_extraction_inference(original_img_path, line_art_path)
        shutil.copy(original_img_path, os.path.join(image_output_dir, "original.png"))

        # --- Step 2: Run Vectorization Pipeline ---
        print("Step 2: Running vectorization pipeline...")
        input_image_for_vec = cv2.imread(line_art_path)
        height, width, _ = input_image_for_vec.shape

        contours = find_contours(line_art_path)
        if not contours:
            print("No contours found in line art. Skipping vectorization.")
            continue

        all_bezier_curves = []
        all_simplified_polygons = []
        for contour in contours:
            simplified = simplify_polygon(contour, epsilon_ratio=0.015)
            if len(simplified) < 2:
                continue
            all_simplified_polygons.append(simplified)
            
            nodes = np.asfortranarray(np.array(simplified).T)
            curves = fit_curve(nodes.T, max_error=1.0)
            all_bezier_curves.extend(curves)

        # --- Step 3: Save intermediate and final results ---
        print("Step 3: Saving results...")
        # Save simplified polygons visualization
        poly_vis_img = np.zeros((height, width, 3), dtype=np.uint8)
        drawable_polygons = [np.array(p, dtype=np.int32) for p in all_simplified_polygons]
        cv2.drawContours(poly_vis_img, drawable_polygons, -1, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(image_output_dir, "polygons.png"), poly_vis_img)

        # Save final SVG
        save_svg(all_bezier_curves, os.path.join(image_output_dir, "vector.svg"), width, height)

    # --- Step 4: Create final showcase HTML ---
    print("Step 4: Creating showcase HTML...")
    create_visualization_html(OUTPUT_DIR, processed_image_dirs)

    print("\nShowcase generation complete!")

if __name__ == "__main__":
    main()
