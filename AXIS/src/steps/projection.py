# src/steps/projection.py

import numpy as np
from typing import List

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Line2D, Line3D

# Placeholder for camera intrinsics (K matrix)
# In a real scenario, this would come from the cut spec or a calibration process.
# Assuming a simple camera with the principal point at the center of a 1280x720 image.
# Focal length is often approximated as the image width.
IMG_WIDTH = 1280
IMG_HEIGHT = 720
FX = FY = 1280 
CX = IMG_WIDTH / 2
CY = IMG_HEIGHT / 2

CAMERA_INTRINSICS = np.array([
    [FX, 0,  CX],
    [0,  FY, CY],
    [0,  0,  1 ]
])

class Backprojection3DStep(ProcessingStep):
    """2D 라인을 뎁스 맵을 이용해 3D 라인으로 역투영하는 파이프라인 스텝"""
    def __init__(self, camera_matrix: np.ndarray = CAMERA_INTRINSICS):
        self._k = camera_matrix
        self._fx = self._k[0, 0]
        self._fy = self._k[1, 1]
        self._cx = self._k[0, 2]
        self._cy = self._k[1, 2]

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running Backprojection3DStep...")
        lines_2d: List[Line2D] | None = builder.get("lines_2d")
        depth_map: np.ndarray | None = builder.get("depth_map")

        if not lines_2d or depth_map is None:
            print("Skipping Backprojection3DStep: lines_2d or depth_map is not available.")
            return builder

        # Adjust camera intrinsics for the actual (resized) frame dimensions
        h, w = depth_map.shape
        scale_x = w / IMG_WIDTH
        scale_y = h / IMG_HEIGHT
        
        fx = self._fx * scale_x
        fy = self._fy * scale_y
        cx = self._cx * scale_x
        cy = self._cy * scale_y

        lines_3d: List[Line3D] = []
        for i, line_2d in enumerate(lines_2d):
            points_3d = []
            for u, v in line_2d.points:
                # Ensure coordinates are within the depth map bounds
                if 0 <= v < h and 0 <= u < w:
                    z = depth_map[v, u]
                    if z > 0: # Ensure depth is valid
                        # Back-projection formula
                        x = (u - cx) * z / fx
                        y = (v - cy) * z / fy
                        points_3d.append([x, y, z])
            
            if points_3d:
                # For now, assign a placeholder ID and default pressure
                line_id = f"line_{builder.get('frame_index')}_{i}"
                lines_3d.append(Line3D(
                    line_id=line_id,
                    layer="default",
                    points_3d=np.array(points_3d),
                    pressure=np.ones(len(points_3d)) # Default pressure
                ))

        print(f"Projected {len(lines_3d)} lines to 3D.")
        builder.set("lines", lines_3d) # Note: we use "lines" for the List[Line3D]
        return builder
