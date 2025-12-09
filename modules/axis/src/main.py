import cv2
import os
import argparse
import numpy as np
import json
import dataclasses
from typing import List

from AXIS.src.pipeline import Pipeline, FrameContextBuilder
from AXIS.src.data_models import Line3D, Curve2D
from AXIS.src.steps.detection import EdgeDetectionStep
from AXIS.src.steps.estimation import DepthEstimationStep, FlowEstimationStep
from AXIS.src.steps.vectorization import LineVectorizationStep
from AXIS.src.steps.fitting import CurveFittingStep
from AXIS.src.steps.projection import Backprojection3DStep, CAMERA_INTRINSICS
from AXIS.src.steps.tracking import LineTrackingStep
from AXIS.src.strategies.detectors import CannyDetector
from AXIS.src.strategies.estimators import MiDaSEstimator, RAFTEstimator

def _project_3d_to_2d(lines_3d: List[Line3D], h: int, w: int) -> List[np.ndarray]:
    k = CAMERA_INTRINSICS
    scale_x, scale_y = w / (k[0, 2] * 2), h / (k[1, 2] * 2)
    fx, fy = k[0, 0] * scale_x, k[1, 1] * scale_y
    cx, cy = k[0, 2] * scale_x, k[1, 2] * scale_y
    projected_line_points = []
    for line in lines_3d:
        points_2d = []
        for x, y, z in line.points_3d:
            if z > 1e-3:
                u = fx * x / z + cx
                v = fy * y / z + cy
                points_2d.append([u, v])
        if points_2d:
            projected_line_points.append(np.array(points_2d))
    return projected_line_points

def save_frame_visuals(context, base_output_dir: str):
    frame_idx = context.frame_index
    output_dir = os.path.join(base_output_dir, f"frame_{frame_idx:04d}")
    os.makedirs(output_dir, exist_ok=True)

    h, w, _ = context.original_frame.shape

    # 1. Save original frame
    cv2.imwrite(os.path.join(output_dir, "original.png"), context.original_frame)

    # 2. Save lines (vectorized)
    lines_canvas = np.zeros((h, w, 4), dtype=np.uint8)
    if context.lines_2d:
        for line in context.lines_2d:
            cv2.polylines(lines_canvas, [np.int32(line.points)], isClosed=False, color=(0, 255, 0, 255), thickness=2)
    cv2.imwrite(os.path.join(output_dir, "lines.png"), lines_canvas)

    # 3. Save curves (fitted)
    curves_canvas = np.zeros((h, w, 4), dtype=np.uint8)
    if context.curves_2d:
        for curve in context.curves_2d:
            cv2.polylines(curves_canvas, [np.int32(curve.points)], isClosed=False, color=(255, 0, 0, 255), thickness=2)
    cv2.imwrite(os.path.join(output_dir, "curves.png"), curves_canvas)

    # 4. Save overlay
    overlay_canvas = context.original_frame.copy()
    if context.lines_2d:
        for line in context.lines_2d:
            cv2.polylines(overlay_canvas, [np.int32(line.points)], isClosed=False, color=(0, 255, 0, 255), thickness=1)
    if context.curves_2d:
        for curve in context.curves_2d:
            cv2.polylines(overlay_canvas, [np.int32(curve.points)], isClosed=False, color=(255, 0, 0, 255), thickness=1)
    cv2.imwrite(os.path.join(output_dir, "overlay.png"), overlay_canvas)

def main():
    parser = argparse.ArgumentParser(description="Generate visualization data from a video.")
    parser.add_argument('--video', type=str, required=True, help="Path to the input video file.")
    parser.add_argument('--output_json', type=str, required=True, help="Path to save the output scene_data.json file.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save the output PNG images.")
    parser.add_argument('--max_frames', type=int, default=None, help='Maximum number of frames to process for testing.')
    args = parser.parse_args()

    print(f"--- Generating visualization data for {args.video} ---")
    
    if not os.path.exists(args.video):
        print(f"Error: Input video not found at {args.video}")
        return

    os.makedirs(args.output_dir, exist_ok=True)

    print("Initializing strategies...")
    pipeline = Pipeline(steps=[
        EdgeDetectionStep(strategy=CannyDetector()),
        LineVectorizationStep(),
        CurveFittingStep(), # New step
        # DepthEstimationStep(strategy=MiDaSEstimator()),
        # FlowEstimationStep(strategy=RAFTEstimator(model_name="raft_small")),
        # Backprojection3DStep(),
        # LineTrackingStep(),
    ])

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
        if not ret: break

        max_height = 512
        h, w, _ = frame.shape
        if h > max_height:
            scale = max_height / h
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        builder = FrameContextBuilder(frame_index=frame_idx, original_frame=frame, prev_frame=prev_frame)
        print(f"Running pipeline for frame {frame_idx}...")
        processed_context = pipeline.run(builder)

        save_frame_visuals(processed_context, args.output_dir)

        frame_data = {"frame_index": frame_idx}
        if processed_context.lines_2d:
            frame_data["lines"] = [{"id": i, "points": line.points.tolist()} for i, line in enumerate(processed_context.lines_2d)]
        if processed_context.curves_2d:
            frame_data["curves"] = [{"id": i, "points": curve.points.tolist()} for i, curve in enumerate(processed_context.curves_2d)]
        all_frames_data.append(frame_data)

        prev_frame = frame
        frame_idx += 1

    cap.release()
    print("Video processing finished.")

    output_json_dir = os.path.dirname(args.output_json)
    if output_json_dir: os.makedirs(output_json_dir, exist_ok=True)
        
    with open(args.output_json, 'w') as f:
        json.dump(all_frames_data, f)
    print(f"Successfully saved JSON data to {args.output_json}")

if __name__ == "__main__":
    main()