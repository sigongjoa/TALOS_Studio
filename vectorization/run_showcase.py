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
<<<<<<< HEAD
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
=======
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
>>>>>>> edecff8 (Feat: Add comparison between original and line art polygons [publish])
                <div>
                    <h3 class="font-semibold">1. Original</h3>
                    <img src="{base_name}/original.png" alt="Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
<<<<<<< HEAD
                    <h3 class="font-semibold">2. Line Art (Input)</h3>
                    <img src="{base_name}/line_art.png" alt="Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">3. Final Vector (SVG)</h3>
=======
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
>>>>>>> edecff8 (Feat: Add comparison between original and line art polygons [publish])
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

<<<<<<< HEAD
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

=======
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
>>>>>>> edecff8 (Feat: Add comparison between original and line art polygons [publish])
    print("Step 4: Creating showcase HTML...")
    create_visualization_html(OUTPUT_DIR, processed_image_dirs)

    print("\nShowcase generation complete!")

if __name__ == "__main__":
    main()