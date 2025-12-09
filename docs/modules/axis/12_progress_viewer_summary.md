# AXIS Project Progress Summary (Until Viewer Implementation)

## 1. Overall Goal

- To implement the core functionality of the AXIS pipeline, which involves extracting information such as edges, depth, and motion from video footage, and consistently tracking the generated 3D vector lines between frames.
- Ultimately, to build an interactive web application capable of visualizing and controlling this data.

## 2. Completed Core Features

**Data Processing Pipeline (Backend - Python)**
- **`EdgeDetectionStep`**: Extracts an edge map from frames using the Canny Edge Detector.
- **`DepthEstimationStep`**: Estimates a depth map using the MiDaS model.
- **`FlowEstimationStep`**: Calculates the optical flow between frames using the RAFT model.
- **`LineVectorizationStep`**: Converts the edge map into 2D vector lines (`Line2D`).
- **`Backprojection3DStep`**: Back-projects 2D lines into 3D lines (`Line3D`) using the depth map.
- **`LineTrackingStep`**: Assigns and tracks consistent IDs for 3D lines across frames using optical flow and the Hungarian algorithm.
- **Data Generator (`main.py`)**: The functionality to run the entire pipeline, process a full video, and generate a `scene_data.json` file required for frontend visualization has been completed.

## 3. Major Issues Resolved & Optimizations

- **Resolved Various Runtime Errors**: Addressed multiple Python runtime errors encountered during the pipeline construction, including `NameError`, `TypeError`, and `FileNotFoundError`.
- **Solved GPU Memory Issues**: To resolve `CUDA out of memory` errors, the pipeline was stabilized by replacing the `raft_large` model with `raft_small` and implementing a 'resize' logic to dynamically reduce the resolution of input frames.
- **Analyzed Performance Bottleneck**: Identified that the current performance bottleneck is not the GPU but the complex, CPU-bound distance calculation logic within the `LineTrackingStep`. A detailed 'Spatial Partitioning Optimization' plan (`phase7_step_5_performance_optimization_plan.md`) has been established to address this.

## 4. Current Phase: Visualizer Implementation

- **Solidified Direction**: The plan was specified to integrate with the user-provided `axis-interactive-timing-editor` React project, moving beyond a simple viewer.
- **Backend (Completed)**: `main.py` has been refactored to generate data in the exact `scene_data.json` format required by the React frontend.
- **Frontend (Code Provided)**: In line with the React architecture, complete code for `App.tsx` and `SceneLayoutView.tsx` has been provided. This code simplifies the existing editor logic and focuses on rendering the output from the pipeline.

## 5. Next Steps

1.  **Integration Test (User Task)**: Apply the provided code changes to the `axis-interactive-timing-editor` project and run `npm run dev` to finally verify that the backend data and frontend viewer integrate correctly.
2.  **Performance Optimization**: After the integration test is complete, proceed with improving the algorithm in `LineTrackingStep` as planned to increase the data generation speed.
3.  **Implement Editing Features**: Once the viewer functionality is stable, evolve it into a full interactive editor by adding a timeline and graph editor features, as laid out in the `AXIS_Visualizer_And_Timing_Editor_Design.md` document.
