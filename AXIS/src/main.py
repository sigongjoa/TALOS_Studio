import cv2
import os
import argparse
import numpy as np
import json

from .pipeline import Pipeline, FrameContextBuilder
from .steps.detection import EdgeDetectionStep
from .steps.estimation import DepthEstimationStep, FlowEstimationStep
from .steps.vectorization import LineVectorizationStep
from .steps.projection import Backprojection3DStep
from .steps.tracking import LineTrackingStep
from .strategies.detectors import CannyDetector
from .strategies.estimators import MiDaSEstimator, RAFTEstimator

def main():
    """A test script to verify the full pipeline with video input."""
    parser = argparse.ArgumentParser(description="Run the full AXIS pipeline on a video.")
    parser.add_argument('--video', type=str, required=True, help="Path to the input video file.")
    args = parser.parse_args()

    print("--- Starting Full Pipeline Test with Line Tracking ---")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # AXIS directory
    output_dir = os.path.join(base_dir, 'tests/data')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(args.video):
        print(f"Error: Input video not found at {args.video}")
        return

    # 1. Initialize strategies and the stateful tracking step
    print("Initializing strategies...")
    edge_strategy = CannyDetector()
    depth_strategy = MiDaSEstimator()
    flow_strategy = RAFTEstimator(model_name="raft_small")
    tracking_step = LineTrackingStep() # Stateful step

    # 2. Create the pipeline with all steps in logical order
    pipeline = Pipeline(steps=[
        EdgeDetectionStep(strategy=edge_strategy),
        DepthEstimationStep(strategy=depth_strategy),
        FlowEstimationStep(strategy=flow_strategy),
        LineVectorizationStep(),
        Backprojection3DStep(),
        tracking_step # Use the same instance in every loop
    ])

    # 3. Open video and process frame by frame
    cap = cv2.VideoCapture(args.video)
    prev_frame = None
    frame_idx = 0
    
    print("Starting video processing...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- Resize frame to reduce memory usage ---
        max_height = 512
        h, w, _ = frame.shape
        if h > max_height:
            scale = max_height / h
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create the builder for the current frame
        builder = FrameContextBuilder(frame_index=frame_idx, original_frame=frame, prev_frame=prev_frame)

        # Run the pipeline
        print(f"Running pipeline for frame {frame_idx}...")
        processed_context = pipeline.run(builder)

        # Save results for frames 5 and 6 for verification
        if frame_idx == 5 or frame_idx == 6:
            print(f"--- Saving results for frame {frame_idx} ---")
            
            if processed_context.lines is not None:
                lines_for_json = [
                    {
                        "line_id": line.line_id,
                        "points_3d_count": len(line.points_3d)
                    }
                    for line in processed_context.lines
                ]
                json_path = os.path.join(output_dir, f"frame_{frame_idx}_tracked_lines.json")
                with open(json_path, 'w') as f:
                    json.dump(lines_for_json, f, indent=2)
                print(f"Saved tracked lines summary to {json_path}")

        prev_frame = frame
        frame_idx += 1

    cap.release()
    print("--- Video processing finished ---")

if __name__ == "__main__":
    main()