import cv2
import os
import argparse
import numpy as np
import json
from typing import List

from AXIS.src.pipeline import Pipeline, FrameContextBuilder
from AXIS.src.data_models import Line3D
from AXIS.src.steps.detection import EdgeDetectionStep
from AXIS.src.steps.estimation import DepthEstimationStep, FlowEstimationStep
from AXIS.src.steps.vectorization import LineVectorizationStep
from AXIS.src.steps.projection import Backprojection3DStep, CAMERA_INTRINSICS
from AXIS.src.steps.tracking import LineTrackingStep
from AXIS.src.strategies.detectors import CannyDetector
from AXIS.src.strategies.estimators import MiDaSEstimator, RAFTEstimator

def _project_3d_to_2d(lines_3d: List[Line3D], h: int, w: int) -> List[np.ndarray]:
    """Helper to project a list of 3D lines to 2D screen space for visualization."""
    k = CAMERA_INTRINSICS
    # Adjust camera intrinsics for the actual (resized) frame dimensions
    scale_x = w / (k[0, 2] * 2)
    scale_y = h / (k[1, 2] * 2)
    fx, fy = k[0, 0] * scale_x, k[1, 1] * scale_y
    cx, cy = k[0, 2] * scale_x, k[1, 2] * scale_y

    projected_line_points = []
    for line in lines_3d:
        points_2d = []
        for x, y, z in line.points_3d:
            if z > 1e-3: # Avoid division by zero or very small numbers
                u = fx * x / z + cx
                v = fy * y / z + cy
                points_2d.append([u, v])
        if points_2d:
            projected_line_points.append(np.array(points_2d))
    return projected_line_points

def main():
    """Processes a video to generate a JSON data file for the web visualizer."""
    parser = argparse.ArgumentParser(description="Generate visualization data from a video.")
    parser.add_argument('--video', type=str, required=True, help="Path to the input video file.")
    parser.add_argument('--output', type=str, required=True, help="Path to save the output scene_data.json file.")
    parser.add_argument('--max_frames', type=int, default=None, help='Maximum number of frames to process for testing.')
    args = parser.parse_args()

    print(f"--- Generating visualization data for {args.video} ---")
    
    if not os.path.exists(args.video):
        print(f"Error: Input video not found at {args.video}")
        return

    # 1. Initialize strategies and the stateful tracking step
    print("Initializing strategies...")
    tracking_step = LineTrackingStep()

    # 2. Create the pipeline
    pipeline = Pipeline(steps=[
        EdgeDetectionStep(strategy=CannyDetector()),
        DepthEstimationStep(strategy=MiDaSEstimator()),
        FlowEstimationStep(strategy=RAFTEstimator(model_name="raft_small")),
        LineVectorizationStep(),
        Backprojection3DStep(),
        tracking_step
    ])

    # 3. Open video and process all frames
    cap = cv2.VideoCapture(args.video)
    prev_frame = None
    frame_idx = 0
    all_frames_data = []
    
    print("Starting video processing...")
    while cap.isOpened():
        if args.max_frames is not None and frame_idx >= args.max_frames:
            print(f"Reached max_frames limit of {args.max_frames}.")
            break

        ret, frame = cap.read()
        if not ret:
            break

        max_height = 512
        h, w, _ = frame.shape
        if h > max_height:
            scale = max_height / h
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        h, w, _ = frame.shape # Get new dimensions

        builder = FrameContextBuilder(frame_index=frame_idx, original_frame=frame, prev_frame=prev_frame)
        print(f"Running pipeline for frame {frame_idx}...")
        processed_context = pipeline.run(builder)

        # Transform and collect data for this frame
        if processed_context.lines:
            projected_points_list = _project_3d_to_2d(processed_context.lines, h, w)
            frame_data = {
                "frame_index": frame_idx,
                "lines": [
                    {
                        "id": line.line_id,
                        "points": points.tolist()
                    }
                    for line, points in zip(processed_context.lines, projected_points_list)
                ]
            }
            all_frames_data.append(frame_data)

        prev_frame = frame
        frame_idx += 1

    cap.release()
    print("Video processing finished.")

    # 4. Save all data to the output file
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(args.output, 'w') as f:
        json.dump(all_frames_data, f)
    print(f"Successfully saved visualization data to {args.output}")

if __name__ == "__main__":
    main()