# AXIS/src/steps/fitting.py

import numpy as np
from typing import List
from scipy.interpolate import splev, splprep

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Curve2D

class CurveFittingStep(ProcessingStep):
    """A pipeline step to fit smooth B-spline curves to 2D lines."""
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        context = builder.build()
        lines_2d = context.lines_2d

        if not lines_2d:
            print("No 2D lines to fit curves to.")
            builder.set_curves_2d([])
            return builder

        detected_curves: List[Curve2D] = []
        for line in lines_2d:
            points = line.points.T
            # B-spline fitting requires at least 4 points and for k < m (k=degree, m=num_points)
            if points.shape[1] >= 4:
                try:
                    # Create B-spline model
                    tck, u = splprep(points, s=2.0, k=3) # s: smoothing factor, k: degree
                    
                    # Sample 100 points along the curve
                    u_new = np.linspace(u.min(), u.max(), 100)
                    new_points = splev(u_new, tck)
                    
                    # Transpose back to (N, 2) shape
                    detected_curves.append(Curve2D(points=np.array(new_points).T))
                except Exception as e:
                    # Catch potential errors from splprep, e.g., if points are collinear
                    # print(f"Could not fit curve for a line: {e}")
                    pass # Simply skip this line if fitting fails
        
        print(f"Fitted {len(detected_curves)} curves.")
        builder.set_curves_2d(detected_curves)
        return builder
