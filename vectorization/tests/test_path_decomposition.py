import os
import cv2
import numpy as np
import pytest

from vectorization.src.path_decomposition import find_contours

@pytest.fixture
def donut_square_image():
    """Create a test image with a smaller square hole inside a larger square."""
    img = np.zeros((100, 100), dtype=np.uint8)
    # Outer square (white)
    cv2.rectangle(img, (10, 10), (90, 90), 255, -1)
    # Inner square (black hole)
    cv2.rectangle(img, (30, 30), (70, 70), 0, -1)
    
    test_image_path = "test_donut.png"
    cv2.imwrite(test_image_path, img)
    yield test_image_path
    os.remove(test_image_path)

@pytest.fixture
def simple_square_image():
    """Create a simple test image with one square."""
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(img, (25, 25), (75, 75), 255, -1)
    test_image_path = "test_square.png"
    cv2.imwrite(test_image_path, img)
    yield test_image_path
    os.remove(test_image_path)

def test_find_contours_simple(simple_square_image):
    """Test basic contour finding."""
    contours, hierarchy = find_contours(simple_square_image)
    assert len(contours) == 1
    assert hierarchy is not None
    assert len(hierarchy) == 1

def test_find_contours_with_hierarchy(donut_square_image):
    """Test that RETR_TREE correctly finds the parent-child hierarchy."""
    contours, hierarchy = find_contours(donut_square_image)
    
    # Should find two contours: the outer and inner squares
    assert len(contours) == 2
    assert hierarchy is not None
    assert len(hierarchy) == 2

    # The hierarchy format is [Next, Previous, First_Child, Parent]
    # We need to find which contour is the parent and which is the child.
    # The parent is the one with no parent (Parent index is -1).
    # The child is the one whose parent is the other contour.

    if hierarchy[0][3] == -1: # if contour 0 is the parent
        parent_idx, child_idx = 0, 1
    else: # if contour 1 is the parent
        parent_idx, child_idx = 1, 0

    # Assert the parent has no parent
    assert hierarchy[parent_idx][3] == -1
    # Assert the parent's child is the child contour
    assert hierarchy[parent_idx][2] == child_idx
    # Assert the child's parent is the parent contour
    assert hierarchy[child_idx][3] == parent_idx