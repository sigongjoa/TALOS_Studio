# 2. System Architecture

## 2.1. Overview
The AXIS Visualizer & Timing Editor operates on a simple client-server architecture composed of two main components: a Python backend responsible for data processing, and a static JavaScript frontend for visualization.

## 2.2. Component Diagram

```
+-------------------------+      +--------------------------------+      +-------------------------+
|                         |      |                                |      |                         |
|  Video File (e.g. .mp4) |----->|   Backend (Python)             |----->|  scene_data.json        |
|                         |      |   (AXIS Pipeline / main.py)    |      |  (Data File)            |
+-------------------------+      +--------------------------------+      +-------------------------+
                                                                                   |
                                                                                   | (Served via HTTP)
                                                                                   |
                                                                                   v
+-------------------------+      +--------------------------------+      +-------------------------+
|                         |      |                                |      |                         |
|  User's Web Browser     |<-----|   Web Server (server.py)       |<-----|  Frontend (HTML/CSS/JS) |
|  (Renders visualization)|      |   (Serves static files)        |      |  (Editor Interface)     |
+-------------------------+      +--------------------------------+      +-------------------------+

```

## 2.3. Component Descriptions

### 2.3.1. Backend (Python Data Generator)
- **Script:** `AXIS/src/main.py`
- **Role:** A command-line tool that executes the full AXIS pipeline (Edge, Depth, Flow, Vectorization, Projection, Tracking) on a source video.
- **Output:** It produces a single, comprehensive JSON file (`scene_data.json`) that contains all the per-frame tracking information required by the frontend. It does not serve data in real-time.

### 2.3.2. Web Server
- **Script:** `AXIS/server.py`
- **Role:** A minimal, zero-dependency HTTP server using Python's built-in libraries. Its sole purpose is to serve the static files of the frontend application (HTML, CSS, JS, and the `scene_data.json` file) to the user's web browser.

### 2.3.3. Frontend (JavaScript Viewer)
- **Location:** `axis-interactive-timing-editor/`
- **Role:** A static web application that runs entirely in the browser.
- **Logic:**
    1. It fetches the `scene_data.json` file.
    2. It loads the source video file.
    3. It renders the line data for the current frame onto a `<canvas>` element, synchronized with the video's playback time.
    4. It provides UI controls for playback (play/pause, scrub bar).

## 2.4. Data Flow
1. The user executes `main.py` with a video file as input.
2. `main.py` processes the entire video and saves the `scene_data.json` file into the frontend's `public` directory.
3. The user starts the `server.py`.
4. The user opens `http://localhost:8000` in their browser.
5. The browser loads `index.html`, which in turn loads `visualizer.js`.
6. `visualizer.js` fetches `scene_data.json` and the video file, and begins the synchronized rendering loop.
