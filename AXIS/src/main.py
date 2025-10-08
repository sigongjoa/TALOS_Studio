import cv2
import os
import argparse
import numpy as np

from .pipeline import Pipeline, FrameContextBuilder
from .steps.detection import EdgeDetectionStep
from .steps.estimation import DepthEstimationStep, FlowEstimationStep
from .strategies.detectors import CannyDetector
from .strategies.estimators import MiDaSEstimator, RAFTEstimator

def visualize_flow(flow):
    """Converts an optical flow map to a color image for visualization."""
    # Use Hue, Saturation, Value (HSV) color space
    # Hue corresponds to direction, Value to magnitude
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    hsv[..., 0] = angle * 180 / np.pi / 2
    hsv[..., 1] = 255
    hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def main():
    """A test script to verify the full pipeline with video input."""
    parser = argparse.ArgumentParser(description="Run the full AXIS pipeline on a video.")
    parser.add_argument('--video', type=str, required=True, help="Path to the input video file.")
    args = parser.parse_args()

    print("--- Starting Full Pipeline Test (Edge, Depth, Flow) ---")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # AXIS directory
    output_dir = os.path.join(base_dir, 'tests/data')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(args.video):
        print(f"Error: Input video not found at {args.video}")
        return

    # 1. Initialize strategies
    print("Initializing strategies...")
    edge_strategy = CannyDetector()
    depth_strategy = MiDaSEstimator()
    flow_strategy = RAFTEstimator(model_name="raft_small")

    # 2. Create the pipeline with all steps
    pipeline = Pipeline(steps=[
        EdgeDetectionStep(strategy=edge_strategy),
        DepthEstimationStep(strategy=depth_strategy),
        FlowEstimationStep(strategy=flow_strategy)
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

        # Save results for a specific frame (e.g., frame 5) for verification
        if frame_idx == 5:
            print(f"--- Saving results for frame {frame_idx} ---")
            if processed_context.edge_map is not None:
                path = os.path.join(output_dir, f"frame_{frame_idx}_edge.png")
                cv2.imwrite(path, processed_context.edge_map)
                print(f"Saved edge map to {path}")

            if processed_context.depth_map is not None:
                path = os.path.join(output_dir, f"frame_{frame_idx}_depth.png")
                cv2.imwrite(path, processed_context.depth_map)
                print(f"Saved depth map to {path}")

            if processed_context.flow_map is not None:
                flow_viz = visualize_flow(processed_context.flow_map)
                path = os.path.join(output_dir, f"frame_{frame_idx}_flow.png")
                cv2.imwrite(path, flow_viz)
                print(f"Saved flow map to {path}")

        prev_frame = frame
        frame_idx += 1

    cap.release()
    print("--- Video processing finished ---")

if __name__ == "__main__":
    main()
