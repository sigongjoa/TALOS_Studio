# AXIS/src/steps/fitting.py

import numpy as np
import logging
from typing import List

from scipy.interpolate import splev, splprep

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Curve2D

logger = logging.getLogger(__name__)


class CurveFittingError(Exception):
    """Raised when B-spline curve fitting fails."""
    pass


class CurveFittingStep(ProcessingStep):
    """
    Pipeline step to fit smooth B-spline curves to 2D lines.

    Uses scipy's splprep to fit cubic B-splines with configurable smoothing.
    Lines with fewer than 4 points are skipped (insufficient for cubic spline fitting).
    """

    def __init__(self, smoothing_factor: float = 2.0, spline_degree: int = 3, num_samples: int = 100):
        """
        Initialize the curve fitting step.

        Args:
            smoothing_factor: Smoothing factor for splprep (higher = more smoothing)
            spline_degree: Degree of the B-spline (3 = cubic)
            num_samples: Number of points to sample from fitted curve
        """
        self.smoothing_factor = smoothing_factor
        self.spline_degree = spline_degree
        self.num_samples = num_samples

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        """
        Fit B-spline curves to detected 2D lines.

        Args:
            builder: Frame context builder

        Returns:
            Updated builder with fitted curves

        Raises:
            ValueError: If input context is invalid
        """
        context = builder.build()
        lines_2d = context.lines_2d

        if not lines_2d:
            logger.debug("No 2D lines to fit curves to.")
            builder.set_curves_2d([])
            return builder

        detected_curves: List[Curve2D] = []
        skipped_count = 0

        for idx, line in enumerate(lines_2d):
            try:
                points = line.points.T  # Convert to (2, N) shape for splprep

                # B-spline fitting requires at least (degree + 1) points
                min_points = self.spline_degree + 1
                if points.shape[1] < min_points:
                    logger.debug(
                        f"Line {idx} has only {points.shape[1]} points. "
                        f"Skipping (need at least {min_points} for degree {self.spline_degree} spline)."
                    )
                    skipped_count += 1
                    continue

                # Try to fit B-spline curve
                tck, u = splprep(
                    points,
                    s=self.smoothing_factor,
                    k=self.spline_degree
                )

                # Sample uniform points along the curve
                u_new = np.linspace(u.min(), u.max(), self.num_samples)
                new_points = splev(u_new, tck)

                # Convert back to (N, 2) shape
                detected_curves.append(Curve2D(points=np.array(new_points).T))
                logger.debug(f"Line {idx} fitted successfully")

            except ValueError as e:
                # Specific error from splprep (e.g., collinear points, NaN values)
                logger.warning(f"Line {idx} fitting failed (likely collinear/degenerate points): {e}")
                skipped_count += 1
            except Exception as e:
                # Unexpected error
                logger.error(f"Unexpected error fitting line {idx}: {type(e).__name__}: {e}")
                skipped_count += 1

        logger.info(
            f"Curve fitting complete: {len(detected_curves)} curves fitted, "
            f"{skipped_count} lines skipped."
        )
        builder.set_curves_2d(detected_curves)
        return builder
