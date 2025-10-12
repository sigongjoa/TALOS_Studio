import os
import pytest
import numpy as np
import bezier

from vectorization.src.svg_exporter import save_svg

@pytest.fixture
def setup_test_environment():
    """Provide a test output path and ensure cleanup."""
    output_path = "test_output.svg"
    yield output_path
    # Teardown: remove the file after test
    if os.path.exists(output_path):
        os.remove(output_path)

def test_save_svg_line(setup_test_environment):
    """Test saving a single straight line (degree 1 Bezier)."""
    output_path = setup_test_environment
    
    # Create a line from (10, 20) to (100, 120)
    nodes = np.asfortranarray([
        [10.0, 100.0],
        [20.0, 120.0],
    ])
    line = bezier.Curve(nodes, degree=1)
    
    save_svg([line], output_path, width=200, height=200)
    
    assert os.path.exists(output_path)
    
    with open(output_path, "r") as f:
        content = f.read()
        
    assert '<svg width="200" height="200"' in content
    # Check for the specific SVG path data for a line
    assert 'd="M 10.00,20.00 L 100.00,120.00"' in content
    assert 'stroke="black"' in content
    assert '</svg>' in content

def test_save_svg_cubic(setup_test_environment):
    """Test saving a single cubic Bezier curve."""
    output_path = setup_test_environment
    
    # Create a cubic curve
    nodes = np.asfortranarray([
        [0.0, 50.0, 150.0, 200.0],
        [100.0, 20.0, 180.0, 100.0],
    ])
    cubic_curve = bezier.Curve(nodes, degree=3)
    
    save_svg([cubic_curve], output_path, width=200, height=200)
    
    assert os.path.exists(output_path)
    
    with open(output_path, "r") as f:
        content = f.read()

    # Check for the specific SVG path data for a cubic curve
    expected_path = 'd="M 0.00,100.00 C 50.00,20.00 150.00,180.00 200.00,100.00"'
    assert expected_path in content
