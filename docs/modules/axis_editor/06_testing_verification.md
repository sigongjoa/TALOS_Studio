# 6. Test and Verification Plan

## 6.1. Objective
To verify that the integrated AXIS data pipeline and web visualizer system function correctly, producing accurate and synchronized visual output.

## 6.2. End-to-End Test Procedure

This procedure tests the entire workflow from video input to browser visualization.

### Step 1: Data Generation (Backend)
1.  **Command:** Open a terminal in the project root (`TALOS_Studio`).
2.  Execute the `main.py` script as a module, providing the path to the test video and the designated output path for the data file.
    ```bash
    python -m AXIS.src.main --video AXIS/input_videos/test_video_boxing.mp4 --output axis-interactive-timing-editor/public/scene_data.json
    ```
3.  **Verification:**
    - Confirm that the script runs to completion without errors.
    - Verify that the `scene_data.json` file has been created at the specified output path.
    - Open the JSON file and inspect its contents to ensure it is a non-empty array of `FrameData` objects, conforming to the data specification.

### Step 2: Frontend Execution
1.  **Command:** Open a new terminal in the frontend project directory (`axis-interactive-timing-editor/`).
2.  Install dependencies if not already installed:
    ```bash
    npm install
    ```
3.  Start the Vite development server:
    ```bash
    npm run dev
    ```
4.  **Verification:**
    - The terminal should display a message indicating the server is running, typically on `http://localhost:5173` (or another port).

### Step 3: Visual Verification (Browser)
1.  **Action:** Open a web browser and navigate to the localhost URL provided by the Vite server.
2.  **Initial State Verification:**
    - The page should load correctly, displaying the title, the video player, and the black canvas area.
    - The video should be at frame 0.
    - The canvas should be empty or show the lines for frame 0 if any exist.
3.  **Playback Verification:**
    - Click the "Play" button.
    - **Expected Result:** The video begins to play, and the canvas simultaneously renders the tracked lines for each frame.
    - **Key Check:** Observe a prominent, easily identifiable line in the video. The colored line corresponding to it on the canvas should **maintain the same color** throughout its appearance, confirming that the `line_id` is persistent and the tracking is working.
4.  **Scrubbing Verification:**
    - Pause the video.
    - Drag the scrub bar (slider) back and forth.
    - **Expected Result:** The video frame should jump to the corresponding position, and the canvas should immediately update to display the tracked lines for that specific frame.

## 6.3. Success Criteria
The test is considered successful if all of the following conditions are met:
- The `scene_data.json` is generated correctly.
- The web application loads and runs without console errors.
- The line rendering on the canvas is correctly synchronized with both video playback and scrubbing.
- The color-coding of tracked lines remains consistent over time, visually confirming the success of the `LineTrackingStep`.
