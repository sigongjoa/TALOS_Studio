# src/steps/tracking.py

import numpy as np
from typing import List, Dict, Tuple
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import directed_hausdorff

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Line2D, Line3D
from .projection import CAMERA_INTRINSICS # Import placeholder K

class LineTrackingStep(ProcessingStep):
    """시간에 따라 3D 라인을 추적하고 일관된 ID를 부여하는 파이프라인 스텝"""
    def __init__(self, matching_threshold=30.0, camera_matrix: np.ndarray = CAMERA_INTRINSICS):
        self.live_lines: Dict[int, Line3D] = {}
        self.next_line_id = 0
        self.matching_threshold = matching_threshold
        self._k = camera_matrix

    def _project_3d_to_2d(self, lines_3d: List[Line3D], h: int, w: int) -> List[Line2D]:
        """Helper to project a list of 3D lines to 2D screen space."""
        # Adjust camera intrinsics for the actual frame dimensions
        scale_x = w / self._k[0, 2] / 2
        scale_y = h / self._k[1, 2] / 2
        fx, fy = self._k[0, 0] * scale_x, self._k[1, 1] * scale_y
        cx, cy = self._k[0, 2] * scale_x, self._k[1, 2] * scale_y

        projected_lines = []
        for line in lines_3d:
            points_2d = []
            for x, y, z in line.points_3d:
                if z > 0: # Avoid division by zero
                    u = fx * x / z + cx
                    v = fy * y / z + cy
                    points_2d.append([u, v])
            if points_2d:
                projected_lines.append(Line2D(points=np.array(points_2d)))
        return projected_lines

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running LineTrackingStep...")
        current_lines: List[Line3D] | None = builder.get("lines")
        flow_map: np.ndarray | None = builder.get("flow_map")
        h, w, _ = builder.get("original_frame").shape

        if not current_lines:
            print("Skipping LineTrackingStep: No current lines to track.")
            self.live_lines = {}
            return builder

        # Project current 3D lines to 2D for matching
        current_lines_2d = self._project_3d_to_2d(current_lines, h, w)

        # If no previous lines or no flow map, assign all as new
        if not self.live_lines or flow_map is None:
            print(f"Initializing tracker with {len(current_lines)} new lines.")
            final_lines = []
            for line in current_lines:
                new_id = self.next_line_id
                final_lines.append(Line3D(new_id, line.layer, line.points_3d, line.pressure))
                self.live_lines[new_id] = final_lines[-1]
                self.next_line_id += 1
            builder.set("lines", final_lines)
            return builder

        # 1. Predict previous lines' positions using optical flow
        prev_lines_for_matching = list(self.live_lines.values())
        prev_lines_2d = self._project_3d_to_2d(prev_lines_for_matching, h, w)
        
        predicted_lines_2d = []
        for prev_line in prev_lines_2d:
            moved_points = []
            for u, v in prev_line.points:
                u_int, v_int = int(u), int(v)
                if 0 <= v_int < h and 0 <= u_int < w:
                    dx, dy = flow_map[v_int, u_int]
                    moved_points.append([u + dx, v + dy])
            if moved_points:
                predicted_lines_2d.append(Line2D(points=np.array(moved_points)))

        if not predicted_lines_2d:
            # Handle case where no lines could be predicted
            builder.set("lines", [])
            self.live_lines = {}
            return builder

        # 2. Calculate cost matrix
        cost_matrix = np.full((len(current_lines_2d), len(predicted_lines_2d)), self.matching_threshold)
        for i, current_line in enumerate(current_lines_2d):
            for j, predicted_line in enumerate(predicted_lines_2d):
                dist = directed_hausdorff(current_line.points, predicted_line.points)[0]
                cost_matrix[i, j] = dist

        # 3. Hungarian algorithm for optimal matching
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # 4. Update IDs and state
        final_lines = []
        new_live_lines: Dict[int, Line3D] = {}
        matched_current_indices = set()

        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < self.matching_threshold:
                prev_line_id = prev_lines_for_matching[c].line_id
                current_line = current_lines[r]
                
                tracked_line = Line3D(prev_line_id, current_line.layer, current_line.points_3d, current_line.pressure)
                final_lines.append(tracked_line)
                new_live_lines[prev_line_id] = tracked_line
                matched_current_indices.add(r)

        # Handle new (unmatched) lines
        for i, line in enumerate(current_lines):
            if i not in matched_current_indices:
                new_id = self.next_line_id
                new_line = Line3D(new_id, line.layer, line.points_3d, line.pressure)
                final_lines.append(new_line)
                new_live_lines[new_id] = new_line
                self.next_line_id += 1

        print(f"Line tracking: Matched {len(matched_current_indices)} lines, created {len(final_lines) - len(matched_current_indices)} new lines.")
        self.live_lines = new_live_lines
        builder.set("lines", final_lines)

        return builder