import json

def convert_lines_to_bezier(line_segments):
    """
    Converts a list of line segments into a list of cubic Bezier curve control points.
    For a straight line segment (P0, P3), P1 and P2 are placed to maintain a straight line.

    Args:
        line_segments (list): A list of line segments, where each segment is
                              [x1, y1, x2, y2].

    Returns:
        list: A list of cubic Bezier curves. Each curve is represented by its
              four control points: [[P0x, P0y], [P1x, P1y], [P2x, P2y], [P3x, P3y]].
    """
    bezier_curves = []
    for x1, y1, x2, y2 in line_segments:
        p0 = [x1, y1]
        p3 = [x2, y2]

        # For a straight line, P1 and P2 can be interpolated along the line
        # This effectively represents the straight line as a Bezier curve
        p1 = [x1 + (x2 - x1) / 3, y1 + (y2 - y1) / 3]
        p2 = [x1 + 2 * (x2 - x1) / 3, y1 + 2 * (y2 - y1) / 3]

        bezier_curves.append([p0, p1, p2, p3])
    return bezier_curves

if __name__ == "__main__":
    # Example usage
    sample_line_segments = [
        [10, 10, 50, 10],  # Horizontal line
        [20, 20, 20, 60],  # Vertical line
        [70, 30, 90, 50]   # Diagonal line
    ]

    bezier_output = convert_lines_to_bezier(sample_line_segments)

    print(json.dumps(bezier_output, indent=4))

    # Example of saving to a file
    output_filename = "bezier_curves.json"
    with open(output_filename, "w") as f:
        json.dump(bezier_output, f, indent=4)
    print(f"Bezier curves saved to {output_filename}")
