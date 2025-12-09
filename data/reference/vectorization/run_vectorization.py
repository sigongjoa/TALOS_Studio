import argparse
import cv2
import numpy as np

# Import all the necessary functions from our modules
from src.path_decomposition import find_contours
from src.polygon_optimization import simplify_polygon
from src.curve_fitting import fit_curve
from src.svg_exporter import save_svg

def run_vectorization_pipeline(input_path: str, output_path: str, epsilon_ratio: float, max_error: float):
    """Runs the full vectorization pipeline from an image to an SVG file."""
    print(f"Starting vectorization for {input_path}...")

    # Get image dimensions for SVG canvas
    input_image = cv2.imread(input_path)
    if input_image is None:
        print(f"Error: Could not read input image at {input_path}")
        return
    height, width, _ = input_image.shape

    # --- Phase 1: Path Decomposition ---
    print("Phase 1: Finding contours...")
    contours = find_contours(input_path)
    if not contours:
        print("No contours found. Exiting.")
        return
    print(f"Found {len(contours)} contours.")

    all_bezier_curves = []
    for i, contour in enumerate(contours):
        print(f"  Processing contour {i+1}/{len(contours)} with {len(contour)} points...")

        # --- Phase 2: Polygon Optimization ---
        print("    Phase 2: Simplifying polygon to find corners...")
        corners = simplify_polygon(contour, epsilon_ratio=epsilon_ratio)
        if len(corners) < 2:
            print("    Not enough corners after simplification. Skipping contour.")
            continue
        print(f"    Simplified to {len(corners)} corners.")

        # --- Phase 3: Curve Fitting ---
        # In this version, we fit curves to the simplified polygon (the corners).
        # A more advanced version would fit curves to the original contour points between the corners.
        print("    Phase 3: Fitting curves...")
        points_to_fit = np.array(corners)
        
        # The bezier library expects nodes in (dimension, num_points) shape
        nodes_for_fitting = np.asfortranarray(points_to_fit.T)
        
        bezier_curves = fit_curve(nodes_for_fitting.T, max_error=max_error)
        all_bezier_curves.extend(bezier_curves)
        print(f"    Fitted {len(bezier_curves)} Bezier curves.")

    # --- Phase 4: SVG Export ---
    print("Phase 4: Exporting to SVG...")
    save_svg(all_bezier_curves, output_path, width=width, height=height)
    
    print(f"\nVectorization complete. Output saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A command-line tool to vectorize a skeleton image into an SVG file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_path", help="Path to the input image file (e.g., a black and white skeleton).")
    parser.add_argument("output_path", help="Path to save the output SVG file.")
    parser.add_argument(
        "--epsilon", 
        type=float, 
        default=0.015, 
        help="Epsilon ratio for polygon simplification (RDP). Default: 0.015. \n" 
             "A smaller value (e.g., 0.005) preserves more detail, a larger value (e.g., 0.03) simplifies more."
    )
    parser.add_argument(
        "--error", 
        type=float, 
        default=1.0, 
        help="Maximum error for curve fitting. Default: 1.0. \n" 
             "This is currently a placeholder value as the fitting logic is simplified."
    )
    args = parser.parse_args()

    run_vectorization_pipeline(args.input_path, args.output_path, args.epsilon, args.error)
