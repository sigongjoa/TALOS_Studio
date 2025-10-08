# src/steps/tracking.py

import numpy as np
from typing import List, Dict, Tuple
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import directed_hausdorff

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Line2D, Line3D

class LineTrackingStep(ProcessingStep):
    """시간에 따라 3D 라인을 추적하고 일관된 ID를 부여하는 파이프라인 스텝"""
    def __init__(self, matching_threshold=25.0):
        self.line_registry: Dict[int, Line3D] = {}
        self.next_line_id = 0
        self.prev_lines_2d: List[Line2D] = []
        self.matching_threshold = matching_threshold

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running LineTrackingStep...")
        lines_2d: List[Line2D] | None = builder.get("lines_2d")
        flow_map: np.ndarray | None = builder.get("flow_map")

        if not lines_2d:
            print("Skipping LineTrackingStep: No 2D lines available.")
            self.prev_lines_2d = []
            return builder

        if flow_map is None or not self.prev_lines_2d:
            print("Skipping LineTrackingStep: Flow map or previous lines not available.")
            # Assign new IDs to all current lines
            # This part will be refined later
            self.prev_lines_2d = lines_2d
            return builder

        # 1. Predict previous lines' positions in the current frame
        predicted_lines_2d = []
        for prev_line in self.prev_lines_2d:
            moved_points = []
            for u, v in prev_line.points:
                if 0 <= v < flow_map.shape[0] and 0 <= u < flow_map.shape[1]:
                    dx, dy = flow_map[v, u]
                    moved_points.append([u + dx, v + dy])
            if moved_points:
                predicted_lines_2d.append(Line2D(points=np.array(moved_points)))

        if not predicted_lines_2d:
            self.prev_lines_2d = lines_2d
            return builder

        # 2. Calculate cost matrix using Hausdorff distance
        num_current = len(lines_2d)
        num_predicted = len(predicted_lines_2d)
        cost_matrix = np.full((num_current, num_predicted), self.matching_threshold * 1.5)

        for i in range(num_current):
            for j in range(num_predicted):
                dist = directed_hausdorff(lines_2d[i].points, predicted_lines_2d[j].points)[0]
                if dist < self.matching_threshold:
                    cost_matrix[i, j] = dist

        # 3. Find optimal matching using Hungarian algorithm
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # This is a simplified tracking logic. A more robust implementation
        # would manage a global registry of lines with lifecycles.
        # For now, we just demonstrate the matching concept.
        
        # Update for next frame
        self.prev_lines_2d = lines_2d

        print(f"Line tracking matched {len(row_ind)} lines.")
        # The actual ID assignment and state management will be added next.
        # For now, we just set the original lines back to demonstrate the step runs.
        builder.set("tracked_lines", builder.get("lines"))

        return builder
