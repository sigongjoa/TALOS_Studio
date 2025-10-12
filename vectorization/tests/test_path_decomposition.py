import os
import cv2
import numpy as np
import pytest

# Import the function to be tested
from vectorization.src.path_decomposition import find_contours

@pytest.fixture
def create_test_image():
    """Create a simple test image for contour finding and clean it up afterward."""
    # Define image properties
    img_size = (100, 100)
    rect_start = (25, 25)
    rect_end = (75, 75)
    color = 255  # White
    
    # Create a black image
    img = np.zeros(img_size, dtype=np.uint8)
    
    # Draw a white rectangle
    cv2.rectangle(img, rect_start, rect_end, color, -1)  # Filled rectangle
    
    # Save the image
    test_image_path = "test_square.png"
    cv2.imwrite(test_image_path, img)
    
    # Provide the path to the test
    yield test_image_path
    
    # Teardown: remove the image file after the test is done
    os.remove(test_image_path)

def test_find_contours_on_simple_square(create_test_image):
    """
    Tests the find_contours function on a synthetically generated square image.
    """
    test_image_path = create_test_image
    
    # Run the function
    contours = find_contours(test_image_path)
    
    # --- Assertions ---
    
    # 1. Should find exactly one contour
    assert len(contours) == 1, f"Expected 1 contour, but found {len(contours)}"
    
    # 2. The contour should have 4 points (a square)
    found_contour = contours[0]
    assert len(found_contour) == 4, f"Expected 4 points for a square, but found {len(found_contour)}"
    
    # 3. The points should match the corners of the rectangle
    # The order of points found by findContours can vary, so we check for presence
    # of all expected corners by sorting them.
    expected_points = [[25, 25], [25, 75], [75, 75], [75, 25]]
    
    # Sort both lists of points to have a consistent order for comparison
    sorted_found_points = sorted(found_contour)
    sorted_expected_points = sorted(expected_points)
    
    assert sorted_found_points == sorted_expected_points, \
        f"Found points {sorted_found_points} do not match expected points {sorted_expected_points}"
