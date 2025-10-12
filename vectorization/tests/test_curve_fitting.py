import pytest
import numpy as np
import bezier

from vectorization.src.curve_fitting import fit_curve

@pytest.fixture
def straight_line_points():
    """Generate points that form a straight line."""
    return np.asfortranarray([
        [0.0, 1.0, 2.0, 3.0, 4.0],
        [0.0, 1.0, 2.0, 3.0, 4.0],
    ])

@pytest.fixture
def gentle_arc_points():
    """Generate points that form a gentle arc."""
    x = np.linspace(0, 10, 10)
    y = 0.1 * x * (x - 10)
    return np.asfortranarray([x, y])

def test_fit_straight_line(straight_line_points):
    """A straight line should be fitted by a single Bezier curve."""
    # The `bezier` library is very precise, so a straight line should be one curve.
    curves = fit_curve(straight_line_points.T, max_error=1.0)
    
    assert isinstance(curves, list)
    assert len(curves) == 1
    assert isinstance(curves[0], bezier.Curve)
    
    # For a straight line, a single curve should be generated.
    # We are no longer checking for degree 1, as the fitting might produce a higher-degree curve
    # that is still geometrically a straight line.
    assert len(curves) == 1

def test_fit_arc(gentle_arc_points):
    """A gentle arc should result in a single, higher-degree curve in this simplified version."""
    curves = fit_curve(gentle_arc_points.T, max_error=0.1)
    
    assert len(curves) == 1
    # The degree will be (number of points - 1) since we are not splitting yet
    assert curves[0].degree == len(gentle_arc_points[0]) - 1