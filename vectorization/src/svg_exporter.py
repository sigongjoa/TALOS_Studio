import bezier
import numpy as np

def save_svg(curves: list, output_path: str, width: int, height: int):
    """Saves a list of Bezier curves to an SVG file.

    Args:
        curves: A list of `bezier.Curve` objects.
        output_path: The path to save the SVG file.
        width: The width of the SVG canvas.
        height: The height of the SVG canvas.
    """
    path_strings = []
    for curve in curves:
        nodes = curve.nodes.T  # Transpose to get (num_points, 2) shape
        
        # Start a new path with the first point
        path_data = [f"M {nodes[0][0]:.2f},{nodes[0][1]:.2f}"]
        
        if curve.degree == 1:
            # Line segment
            path_data.append(f"L {nodes[1][0]:.2f},{nodes[1][1]:.2f}")
        elif curve.degree == 2:
            # Quadratic Bezier
            path_data.append(f"Q {nodes[1][0]:.2f},{nodes[1][1]:.2f} {nodes[2][0]:.2f},{nodes[2][1]:.2f}")
        elif curve.degree == 3:
            # Cubic Bezier
            path_data.append(f"C {nodes[1][0]:.2f},{nodes[1][1]:.2f} {nodes[2][0]:.2f},{nodes[2][1]:.2f} {nodes[3][0]:.2f},{nodes[3][1]:.2f}")
        else:
            # For higher-degree curves, we approximate by sampling points and drawing lines
            # This ensures compatibility with all SVG viewers.
            sampled_points = curve.evaluate_multi(np.linspace(0.0, 1.0, 30))
            for point in sampled_points.T[1:]: # Skip the first point (M)
                path_data.append(f"L {point[0]:.2f},{point[1]:.2f}")
        
        path_strings.append(" ".join(path_data))

    # Write to SVG file
    with open(output_path, "w") as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
        # Each curve becomes a separate path element for simplicity
        for d_attr in path_strings:
            f.write(f'<path d="{d_attr}" stroke="black" fill="none" stroke-width="0.5"/>')
        f.write('</svg>')
    
    print(f"Saved SVG to {output_path}")
