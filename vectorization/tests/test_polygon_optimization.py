import pytest
import numpy as np

from vectorization.src.polygon_optimization import simplify_polygon

@pytest.fixture
def noisy_square_contour():
    """Returns a square contour with extra points along the edges."""
    return [
        [0, 0], [5, 0], [10, 0],  # Top edge
        [10, 5], [10, 10],       # Right edge
        [5, 10], [0, 10],        # Bottom edge
        [0, 5]                   # Left edge
    ]

def test_simplify_polygon(noisy_square_contour):
    """Test if RDP simplification correctly identifies the 4 corners of a noisy square."""
    # A relatively small epsilon should be enough to remove the intermediate points
    simplified = simplify_polygon(noisy_square_contour, epsilon_ratio=0.02)
    
    # The result should be the 4 corner points
    assert len(simplified) == 4, "Simplification should result in 4 points for a square."
    
    # Check if the points are the corners, order might vary
    expected_corners = [[0, 0], [10, 0], [10, 10], [0, 10]]
    
    # Convert to sets of tuples to compare regardless of order
    found_set = set(map(tuple, simplified))
    expected_set = set(map(tuple, expected_corners))
    
    assert found_set == expected_set, "The simplified points are not the expected corners."