import numpy as np
import cv2

def simplify_polygon(contour: list, epsilon_ratio: float) -> list:
    """
    Simplifies a contour using the Ramer-Douglas-Peucker algorithm.
    The precision (epsilon) is calculated based on the contour's perimeter.
    This function's output will be treated as the corner points for the next phase.

    Args:
        contour: A list of points representing the contour.
        epsilon_ratio: A percentage of the contour perimeter to use as epsilon.
                       A smaller value means more detail is preserved.

    Returns:
        A simplified list of points, which are the detected corners.
    """
    if not contour or len(contour) < 3:
        return []
    
    contour_np = np.array(contour, dtype=np.int32)
    
    # Calculate epsilon based on the perimeter
    perimeter = cv2.arcLength(contour_np, True)
    epsilon = epsilon_ratio * perimeter
    
    # Use OpenCV's implementation of RDP
    approx_curve = cv2.approxPolyDP(contour_np, epsilon, True)
    
    # Squeeze to remove redundant dimensions and convert to a simple list of lists
    return np.squeeze(approx_curve, axis=1).tolist()