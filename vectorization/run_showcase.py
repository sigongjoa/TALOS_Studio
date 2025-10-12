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
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
                <div>
                    <h3 class="font-semibold">1. Original</h3>
                    <img src="{base_name}/original.png" alt="Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">2. Polygons from Original</h3>
                    <img src="{base_name}/polygons_from_original.png" alt="Polygons from Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">3. Line Art</h3>
                    <img src="{base_name}/line_art.png" alt="Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">4. Polygons from Line Art</h3>
                    <img src="{base_name}/polygons_from_line_art.png" alt="Polygons from Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">5. Final Vector (SVG)</h3>
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
        
        image_output_dir = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(image_output_dir, exist_ok=True)
        processed_image_dirs.append(base_name)

        original_img_path = os.path.join(INPUT_DIR, image_file)
        line_art_path = os.path.join(image_output_dir, "line_art.png")

        # --- Step 1: Process Original Image ---
        print("Step 1: Processing Original Image...")
        shutil.copy(original_img_path, os.path.join(image_output_dir, "original.png"))
        original_image_for_vec = cv2.imread(original_img_path)
        h, w, _ = original_image_for_vec.shape
        
        orig_contours = find_contours(original_img_path)
        simplified_from_orig = [simplify_polygon(c, 0.015) for c in orig_contours]
        
        poly_vis_orig = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.drawContours(poly_vis_orig, [np.array(p, dtype=np.int32) for p in simplified_from_orig if p], -1, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(image_output_dir, "polygons_from_original.png"), poly_vis_orig)

        # --- Step 2: Process Line Art Image ---
        print("Step 2: Extracting Lines and Processing Line Art...")
        run_manga_line_extraction_inference(original_img_path, line_art_path)
        
        line_art_contours = find_contours(line_art_path)
        if not line_art_contours:
            print("No contours found in line art. Skipping further vectorization.")
            continue

        all_bezier_curves = []
        simplified_from_line_art = []
        for contour in line_art_contours:
            simplified = simplify_polygon(contour, epsilon_ratio=0.015)
            if len(simplified) < 2:
                continue
            simplified_from_line_art.append(simplified)
            
            nodes = np.asfortranarray(np.array(simplified).T)
            curves = fit_curve(nodes.T, max_error=1.0)
            all_bezier_curves.extend(curves)

        # --- Step 3: Save final results ---
        print("Step 3: Saving final results...")
        poly_vis_line_art = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.drawContours(poly_vis_line_art, [np.array(p, dtype=np.int32) for p in simplified_from_line_art if p], -1, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(image_output_dir, "polygons_from_line_art.png"), poly_vis_line_art)

        save_svg(all_bezier_curves, os.path.join(image_output_dir, "vector.svg"), width=w, height=h)

    # --- Step 4: Create final showcase HTML ---
    print("Step 4: Creating showcase HTML...")
    create_visualization_html(OUTPUT_DIR, processed_image_dirs)

    print("\nShowcase generation complete!")

if __name__ == "__main__":
    main()