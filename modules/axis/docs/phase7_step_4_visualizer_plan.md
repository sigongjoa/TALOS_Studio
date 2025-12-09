# Phase 7, Step 4: 2D Web Visualizer Implementation Plan

## 1. Goal

Create a web-based tool to visualize the 2D projection of tracked 3D lines, synchronized with the source video. This provides clear, intuitive feedback on the performance of the entire data processing pipeline, especially the line tracking consistency.

## 2. Guiding Principles

- **Naming Conventions**: `PascalCase` for classes, `snake_case` for functions/variables.
- **Import Style**: Grouped by standard, third-party, and local application. Use relative imports within the `src` package.
- **Execution**: Scripts within `src` will be run as modules (e.g., `python -m AXIS.src.main`). Standalone server scripts can be run directly.

---

## 3. Component Breakdown

The visualizer will be a simple web application composed of a Python backend (for data generation and serving) and a vanilla JavaScript frontend (for rendering).

### A. Backend (Python)

#### 1. Data Generation Script (`src/main.py`)

- **Role**: To be refactored into a dedicated command-line tool that processes a video and outputs a single JSON file for the visualizer.
- **Arguments**: Will accept `--video` (input path) and `--output` (path for the output JSON, e.g., `web_visualizer/data.json`).
- **Logic**:
    1.  Initialize the full pipeline (`EdgeDetection`, `DepthEstimation`, `FlowEstimation`, `LineVectorization`, `Backprojection3D`, `LineTracking`).
    2.  Create an empty list, `all_frames_data = []`.
    3.  Loop through every frame of the input video.
    4.  For each frame, execute the pipeline.
    5.  After processing, get the tracked `lines` (list of `Line3D` objects) from the context.
    6.  **Project the 3D lines back to 2D screen space** using the camera matrix. This reuses the projection logic from the tracking step.
    7.  Create a `frame_data` dictionary containing the `frame_index` and a list of `lines`, where each line has its persistent `id` and 2D `points`.
    8.  Append `frame_data` to `all_frames_data`.
    9.  After the loop, dump the entire `all_frames_data` list into the specified output JSON file.

#### 2. Web Server Script (`server.py`)

- **Role**: A simple, zero-dependency script to serve the static files for the visualizer.
- **Implementation**: Utilizes Python's built-in `http.server` and `socketserver`.
- **Execution**: Can be run directly via `python AXIS/server.py`. It will serve files from the `AXIS/web_visualizer` directory on `http://localhost:8000`.

### B. Frontend (HTML/CSS/JS)

All frontend files will reside in a new `AXIS/web_visualizer/` directory.

#### 1. `index.html`

- **Role**: The main HTML structure of the application.
- **Key Elements**:
    - A `<video>` element to display the source video.
    - A `<canvas>` element where the 2D lines will be rendered.
    - A controls section with a Play/Pause `<button>` and a frame scrubbing `<input type="range">`.

#### 2. `style.css`

- **Role**: To provide basic styling and layout, such as placing the video and canvas side-by-side for easy comparison.

#### 3. `visualizer.js`

- **Role**: The core client-side logic for rendering and synchronization.
- **Logic Flow**:
    1.  **Fetch Data**: Asynchronously fetch the `data.json` file.
    2.  **Initialize**: Set the canvas dimensions to match the video dimensions once the video's metadata is loaded.
    3.  **Sync & Draw Loop**: Use `requestAnimationFrame` to create a rendering loop that is tied to the browser's refresh rate.
        - Inside the loop, calculate the current frame index based on the video's `currentTime`.
        - Clear the canvas.
        - Retrieve the line data for the current frame from the fetched JSON data.
        - Iterate through the lines and draw them on the canvas using `ctx.beginPath()`, `ctx.moveTo()`, `ctx.lineTo()`, and `ctx.stroke()`.
    4.  **Color Coding**: Maintain a map of `line_id` to a color. When drawing a line, look up its color. If it's a new ID, generate a new random color for it. This ensures that a single tracked line maintains its color across all frames.
    5.  **Handle Controls**: Implement event listeners for the play/pause button and the scrub bar to control video playback and trigger canvas redraws.

---

## 4. Implementation Order

1.  Create the `web_visualizer` directory and the empty `index.html`, `style.css`, and `visualizer.js` files.
2.  Implement the `server.py` script.
3.  Refactor `src/main.py` to act as the data generation tool.
4.  Implement the full rendering and synchronization logic in `visualizer.js`.
