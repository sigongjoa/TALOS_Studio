import pytest
import json
from AXIS.scripts.line_to_bezier import convert_lines_to_bezier

def test_convert_lines_to_bezier_format():
    """
    Test that the output format of convert_lines_to_bezier is correct.
    """
    sample_line_segments = [
        [0, 0, 10, 0],  # Horizontal line
        [0, 0, 0, 10],  # Vertical line
        [0, 0, 10, 10]  # Diagonal line
    ]

    bezier_curves = convert_lines_to_bezier(sample_line_segments)

    assert isinstance(bezier_curves, list)
    assert len(bezier_curves) == len(sample_line_segments)

    for curve in bezier_curves:
        assert isinstance(curve, list)
        assert len(curve) == 4  # Four control points for a cubic Bezier
        for point in curve:
            assert isinstance(point, list)
            assert len(point) == 2  # Each point has x, y coordinates

def test_convert_lines_to_bezier_straight_line():
    """
    Test that a straight line segment is correctly converted to a straight Bezier curve.
    For a straight line from P0 to P3, P1 and P2 should lie on the line segment.
    """
    line_segment = [0, 0, 9, 9]  # Diagonal line
    expected_bezier = [
        [0, 0],
        [3.0, 3.0],
        [6.0, 6.0],
        [9, 9]
    ]

    bezier_curves = convert_lines_to_bezier([line_segment])
    assert len(bezier_curves) == 1
    # Using pytest.approx for floating point comparisons
    for i in range(4):
        assert bezier_curves[0][i][0] == pytest.approx(expected_bezier[i][0])
        assert bezier_curves[0][i][1] == pytest.approx(expected_bezier[i][1])

def test_convert_lines_to_bezier_multiple_segments():
    """
    Test with multiple line segments.
    """
    sample_line_segments = [
        [10, 10, 50, 10],
        [20, 20, 20, 60]
    ]
    bezier_curves = convert_lines_to_bezier(sample_line_segments)
    assert len(bezier_curves) == 2

    # Check first curve
    assert bezier_curves[0][0] == [10, 10]
    assert bezier_curves[0][1] == pytest.approx([10 + 40/3, 10])
    assert bezier_curves[0][2] == pytest.approx([10 + 80/3, 10])
    assert bezier_curves[0][3] == [50, 10]

    # Check second curve
    assert bezier_curves[1][0] == [20, 20]
    assert bezier_curves[1][1] == pytest.approx([20, 20 + 40/3])
    assert bezier_curves[1][2] == pytest.approx([20, 20 + 80/3])
    assert bezier_curves[1][3] == [20, 60]
