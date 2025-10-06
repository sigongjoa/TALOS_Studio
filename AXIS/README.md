# AXIS Module (Video-based Pose Estimation)

This module is responsible for extracting 2D and 3D human pose data from a given video file. It serves as the primary engine for generating the foundational motion data (keyframe poses) for the animation pipeline.

## Feature Specification

-   **Video Input:** Accepts a video file (e.g., `.mp4`) as input.
-   **2D Pose Estimation:** Uses the YOLOv8-Pose model to detect human figures and extract 2D keypoints for each frame.
-   **Chunk Processing:** Processes long videos in overlapping chunks to manage memory and ensure temporal consistency.
-   **3D Pose Uplifting:** Utilizes the VideoPose3D model to "lift" the 2D keypoints into 3D space.
-   **Temporal Smoothing:** Applies various smoothing algorithms (e.g., Moving Average, Savitzky-Golay) to the 3D motion data to reduce jitter.
-   **BVH Conversion:** Converts the final 3D pose data into a `.bvh` (Biovision Hierarchy) file, a standard format for motion capture animation.
-   **Blender Retargeting:** Provides a script to import the generated `.bvh` file into Blender and retarget the animation onto an existing character rig.
-   **Visualization:** Generates overlay videos showing the detected 2D and 3D skeletons on top of the original video for debugging and verification.

## Code Description

-   `run_yolo_videopose3d_pipeline.py`: The main entry point for the entire pipeline. It orchestrates the execution of all other scripts in the correct order.
-   `run_full_pipeline.py`: An alternative pipeline script, seems to use a different pose estimation model (`lightweight-human-pose-estimation-3d-demo`).
-   `scripts/`: Contains the individual, modular scripts that perform specific tasks in the pipeline.
    -   `run_pose_estimation.py`: Handles 2D pose detection using YOLO.
    -   `prepare_yolo_for_videopose3d.py`: Converts the YOLO output format into the `.npz` format required by VideoPose3D.
    -   `uplift_to_3d.py`: Executes the VideoPose3D model to get 3D coordinates.
    -   `apply_smoothing.py`: Smooths the 3D keypoint data over time.
    -   `convert_json_to_bvh_bvhio.py`: Creates the final `.bvh` animation file from the 3D keypoint data.
    -   `retarget_in_blender.py`: A utility script to be run within Blender for applying the motion to a character.
    -   `visualize_data.py`: Creates the 2D/3D overlay videos.
-   `models/`: Contains the machine learning models, managed as Git submodules (YOLO, VideoPose3D, etc.).
-   `output_data/`: The default directory where all generated files (JSON keypoints, NPZ files, BVH files, overlay videos) are saved.

## System Flow

The data flows through the system as follows:

1.  **Input:** A video file is provided to `run_yolo_videopose3d_pipeline.py`.
2.  **2D Keypoint Extraction:**
    -   The video is split into overlapping chunks.
    -   For each chunk, `scripts/run_pose_estimation.py` is called.
    -   YOLOv8-Pose runs on the frames, and the 2D keypoints are saved as a `_2d_keypoints.json` file for each chunk.
3.  **Data Preparation:**
    -   For each chunk's JSON file, `scripts/prepare_yolo_for_videopose3d.py` is called.
    -   It converts the 2D data into a NumPy `.npz` file, which is the format required by the next step.
4.  **3D Uplifting:**
    -   `scripts/uplift_to_3d.py` takes the `.npz` file and runs the VideoPose3D model.
    -   The model outputs the 3D keypoints, which are saved as a `_3d_keypoints.json` file for each chunk.
5.  **Smoothing:**
    -   `scripts/apply_smoothing.py` is run on each chunk's 3D JSON file to smooth the motion and reduce jitter. The result is saved as a `_smoothed_3d_keypoints.json` file.
6.  **Stitching & BVH Conversion:**
    -   The main pipeline script gathers the smoothed 3D data from all chunks.
    -   It "stitches" the overlapping sections together to create a single, continuous motion sequence.
    -   This final sequence is passed to `scripts/convert_json_to_bvh_bvhio.py`, which generates the final `.bvh` animation file.
7.  **Output:** The primary output is the `.bvh` file. Secondary outputs include intermediate JSON/NPZ files and visualization videos, all saved in the `output_data` directory.
