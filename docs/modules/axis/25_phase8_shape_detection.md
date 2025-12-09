# Phase 8: Shape Detection Feature Implementation Plan

## 1. Objective

Extend the AXIS backend pipeline to detect circles and triangles in addition to lines. The backend will output this data in two formats: a structured `scene_data.json` for interactivity, and pre-rendered PNG images for each data type for immediate visual debugging. The frontend will be updated to display these four image outputs in a 2x2 grid.

---

## 2. Backend Implementation Plan (`AXIS/src`)

### 2.1. Define New Data Models (`data_models.py`)

- Create new dataclasses for `Circle` (center, radius) and `Triangle` (3 vertices).
- Update `FrameContext` to include `circles: List[Circle] | None` and `triangles: List[Triangle] | None`.

### 2.2. Implement New Detection Steps (`steps/shape_detection.py`)

- **`CircleDetectionStep`**: Implement a new pipeline step that uses `cv2.HoughCircles` to detect circles in the input frame.
- **`TriangleDetectionStep`**: Implement a new pipeline step that uses `cv2.findContours` and `cv2.approxPolyDP` to detect triangles.

### 2.3. Update Main Pipeline (`main.py`)

- Add the new `CircleDetectionStep` and `TriangleDetectionStep` to the main pipeline.
- **Dual Output Logic**:
    1.  **JSON Output**: The existing logic will be extended to aggregate `circles` and `triangles` data alongside `lines` data into the `scene_data.json` file.
    2.  **PNG Output**: For each frame, a new function will be called to perform the following:
        - Create an output directory: `output_images/frame_{frame_index:04d}/`.
        - Save the original frame as `original.png`.
        - Create a transparent RGBA canvas (numpy array).
        - Draw the detected lines onto the canvas and save as `lines.png`.
        - Create another transparent canvas, draw circles, and save as `circles.png`.
        - Create a final transparent canvas, draw triangles, and save as `triangles.png`.

---

## 3. Frontend Implementation Plan (`axis-interactive-timing-editor`)

### 3.1. Data Management (`App.tsx`)

- The logic to fetch and transform `scene_data.json` to populate the Dope Sheet will be kept, ensuring that the interactivity and object management goals are met.

### 3.2. 2x2 Grid View (`App.tsx`)

- The 2x2 grid layout will be implemented as previously planned.
- The four cells of the grid will now contain simple `<img>` tags instead of canvas components.
- The `src` attribute of each `<img>` tag will be dynamically updated based on the `currentFrame` state.
    - Example: `src={\"/output_images/frame_${String(currentFrame).padStart(4, \'0\')}/lines.png?t=${Date.now()}\"}` (A cache-busting query parameter is added).

### 3.3. Component Cleanup

- The custom components `VideoView.tsx` and `LineCanvas.tsx` are no longer needed in this image-based approach and will be removed to keep the codebase clean.
- The main video element will be a simple `<img>` tag for the `original.png`.
- Playback synchronization will be simplified, as we are just changing image sources based on the `currentFrame` state controlled by the `PlaybackControls`.
