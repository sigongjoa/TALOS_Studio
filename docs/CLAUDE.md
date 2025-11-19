# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TALOS_Studio** is an AI-powered animation production platform implementing a sophisticated **multi-agent architecture** for creating animated content. The system decomposes animation creation into specialized, independently executable modules that communicate through asynchronous APIs and file-based data interchange.

**Mission:** Build a production-ready AI animation studio where each stage (2D pose detection, 3D reconstruction, physics simulation, rendering, VFX) is handled by specialized agents with deterministic, parameter-controlled outputs.

## Repository Architecture

The repository contains distinct modules, each operating semi-independently with its own virtual environment, models, and tests:

### Core Animation Modules

1. **AXIS** (`./AXIS/`) - Video-based pose estimation
   - Extracts 2D keypoints using YOLOv8-Pose
   - Lifts to 3D using VideoPose3D
   - Outputs BVH (Biovision Hierarchy) animation files
   - Entry point: `AXIS/run_yolo_videopose3d_pipeline.py`

2. **AXIS_Motion_Engine** (`./AXIS_Motion_Engine/`) - Physics-based motion generation
   - Converts text prompts to motion parameters via LLM
   - Uses OpenSim for biomechanical simulation
   - Generates `.sto` and `.bvh` motion files
   - Modular phase-based implementation

3. **STOKES** (`./STOKES/`) - Fluid simulation and rendering
   - Implements Navier-Stokes equations for VFX
   - Blender-based rendering backend
   - REST API for remote control + React frontend
   - Entry point: `STOKES/run_pipeline.py`

4. **Wonder3D** (`./Wonder3D/`) - Single-image 3D reconstruction
   - Cross-domain diffusion model for multi-view generation
   - Normal map and color image generation
   - Integration with NeuS/Instant-NSR for mesh extraction

5. **line_detection_comparison** (`./line_detection_comparison/`) - Line detection analysis
   - Comparative evaluation of line extraction models (HAWP, L-CNN, DeepLSD, SOLD2, TripoSR)
   - Emphasis on manga/anime-style content
   - TripoSR integration for 3D reconstruction from images

6. **axis-interactive-timing-editor** (`./axis-interactive-timing-editor/`) - Animation timing control
   - Node.js/React frontend for keyframe timing
   - Gemini API integration for intelligent timing suggestions
   - Build: `npm run build`; Dev: `npm run dev`

### Data Flow

```
Input Specification
    ↓
[AXIS or AXIS_Motion_Engine] → Animation Data (.bvh)
    ↓
[STOKES or Wonder3D] → Rendered Frames/3D Models
    ↓
[Final Output] → Video/Model Files
```

Current focus (PoC phase): Single-image → 3D model via TripoSR, with multi-track comparison rendering.

## Development Commands

### Root Directory Commands

**Setup Environment:**
```bash
# Create Python virtual environment (Python 3.10+)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install base dependencies
pip install -r requirements.txt
```

**Run Main Pipeline (PoC):**
```bash
# Full PoC pipeline: Image → 3D via TripoSR → Render multi-track comparison
python run_pipeline.py

# TripoSR-specific: Image → 3D model
python run_triposr.py
```

**Configuration:**
- Edit `config.yml` to set pipeline parameters (model format, chunk sizes, rendering resolution, comparison mode)
- Tracks A/B allow comparing different parameter configurations

### AXIS Module Commands

Located in `./AXIS/`. Each must be run from the `AXIS/` directory using Python's `-m` flag (due to relative imports).

**Setup:**
```bash
cd AXIS
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Run Pose Estimation Pipeline:**
```bash
# From AXIS/ directory
python -m src.main  # Main entry point (if available)
# OR
python run_yolo_videopose3d_pipeline.py <input_video.mp4>
```

**Individual Pipeline Steps:**
```bash
# Step 1: 2D Keypoint Detection (YOLOv8-Pose)
python -m scripts.run_pose_estimation <input_video.mp4>

# Step 2: Convert YOLO output to VideoPose3D format
python -m scripts.prepare_yolo_for_videopose3d <input_2d_keypoints.json>

# Step 3: 3D Pose Uplifting
python -m scripts.uplift_to_3d <input.npz>

# Step 4: Temporal Smoothing
python -m scripts.apply_smoothing <input_3d_keypoints.json>

# Step 5: Convert to BVH Animation
python -m scripts.convert_json_to_bvh_bvhio <input_3d_keypoints.json>

# Step 6: Visualize BVH (overlay on original video)
python -m scripts.visualize_data <input.bvh>
```

**Testing:**
```bash
cd AXIS
pytest tests/
```

**IMPORTANT:** All AXIS scripts use relative imports (`from ..pipeline import ...`). Running scripts directly with `python script.py` will fail. Always use `python -m <module.path>` from the AXIS root directory.

### AXIS_Motion_Engine Commands

Located in `./AXIS_Motion_Engine/`. Phase-based modular implementation.

```bash
cd AXIS_Motion_Engine
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Run motion generation pipeline
python main.py
```

### STOKES Commands

Located in `./STOKES/`. Features REST API + real-time WebSocket updates.

```bash
cd STOKES
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Start simulation server (default port 5000)
python run_pipeline.py

# Access web UI at http://localhost:5000/
```

**API Endpoints:**
- `POST /simulate` - Initiate fluid simulation (returns 202 Accepted + callback URL)
- WebSocket `/ws` - Real-time updates

### axis-interactive-timing-editor Commands

Located in `./axis-interactive-timing-editor/`. React + TypeScript frontend.

```bash
cd axis-interactive-timing-editor

# Install dependencies
npm install

# Development server (Vite, port 5173)
npm run dev

# Production build
npm build

# Preview production build
npm run preview
```

### Testing

**Root-level tests:**
```bash
# Run all tests (excludes heavy submodule tests by default per pytest.ini)
pytest

# Run specific test file
pytest tests/test_visualizations.py

# Run with verbose output
pytest -v
```

**Module-specific tests:**
Each major module has its own test suite in a `tests/` subdirectory. Run from the module root.

## Code Conventions (AXIS Module)

Per `AXIS/docs/CODING_CONVENTIONS.md`:

**Naming:**
- Classes: `PascalCase` (e.g., `FrameContext`, `EdgeDetectionStep`)
- Functions/Methods: `snake_case` (e.g., `run_pipeline`, `estimate`)
- Variables: `snake_case` (e.g., `original_frame`, `flow_map`)
- Constants: `UPPER_SNAKE_CASE` (defined at module top)
- Internal members: prefix with `_` (e.g., `_context_data`, `_notify`)

**Imports:**
```python
# Standard library first
import os
import sys

# Third-party next
import cv2
import numpy as np

# Local imports last (use relative paths)
from .pipeline import Pipeline
from ..strategies.base import BaseEstimator
```

**Type Hints:**
All functions must include type hints. Example:
```python
def estimate(self, frame: np.ndarray, threshold: int = 100) -> np.ndarray:
    pass
```

**Documentation:**
- Public classes/functions require docstrings
- Comments explain **why**, not **what**
- Avoid `# removed` stubs; delete unused code completely

## Key Design Patterns

### 1. Function-Based Control Philosophy
AI outputs represented as deterministic functions: `Y = F_θ(X, P)` where `P` are externally controllable parameters. Enables reproducibility and fine-grained user control. See `docs/Function-Based_Control_Architecture.md` for details.

### 2. Chunked Processing
Large videos processed in overlapping chunks to manage memory. Overlapping regions are stitched together to maintain temporal continuity (e.g., Savitzky-Golay smoothing across boundaries).

### 3. Graceful Degradation
Scripts handle missing dependencies via try-except blocks. Allow "simulated" execution (dummy outputs) when heavy libraries (PyTorch, CUDA) unavailable. Enables development without full environment.

### 4. Asynchronous Module Communication
Modules communicate via:
- REST APIs returning `202 Accepted` (non-blocking task dispatch)
- Callback POSTs to orchestrator on task completion
- File-based data interchange (URLs to shared storage preferred over large payloads)
- Status tracking in central job queue

### 5. Multi-Track Comparison
Support parameterized execution of multiple configurations (Track A, B, etc.). Useful for comparing different model settings or inference strategies. See `config.yml` for track configuration.

## Output Organization

```
TALOS_Studio/
├── output_for_deployment/     # Production-ready outputs
│   ├── track_a/               # Results from Track A config
│   ├── track_b/               # Results from Track B config
│   └── comparison.html        # Side-by-side comparison UI
├── temp/                       # Temporary intermediate files
└── [module]/output_data/       # Module-specific outputs
    ├── *_keypoints.json       # Pose data
    ├── *.bvh                  # Animation files
    ├── *.mp4                  # Visualization videos
    └── frames_*/              # Frame sequences
```

## Configuration Files

- **`config.yml`** - Global pipeline settings (track configs, rendering params, packaging mode)
- **`AXIS/requirements.txt`** - AXIS dependencies
- **`AXIS_Motion_Engine/requirements.txt`** - Motion engine dependencies
- **`STOKES/requirements.txt`** - STOKES dependencies
- **`axis-interactive-timing-editor/package.json`** - Node.js dependencies
- **`pytest.ini`** - Test discovery configuration (excludes heavy submodules)

## Git Workflow Notes

Current branch: `master`

Recent commits show:
- Pivot to TripoSR for 3D reconstruction
- Consolidation of results into unified showcase
- PoC phase focusing on practical functionality

Each module may have its own git submodules (e.g., AXIS/models/ contains YOLO, VideoPose3D). Clone with:
```bash
git clone --recursive <repo_url>
```

## Environment Notes

- **Python:** 3.10+ required (3.12 recommended)
- **CUDA:** Optional but recommended for AXIS, STOKES, Wonder3D (GPU acceleration)
- **Blender:** Required for STOKES rendering and Blender-based visualization (headless mode via subprocess)
- **Node.js:** Required for axis-interactive-timing-editor (dev)

## Common Tasks

### Adding a New Pipeline Module
1. Create module directory at repository root
2. Include `requirements.txt` and `README.md`
3. Add venv setup script or include in setup docs
4. Implement entry point script (`run_pipeline.py` convention)
5. Export output to `output_for_deployment/` or module-specific output directory
6. Update `config.yml` if module is part of main orchestration

### Debugging Pipeline Output
- Check intermediate JSON files in `output_data/` for data shape/validity
- Review visualization videos for visual debugging (2D/3D overlay)
- Enable verbose logging by adding `logging.DEBUG` or print statements
- Test pipeline steps independently before running full pipeline

### Profiling/Performance
- Use Python's `cProfile` for bottlenecks: `python -m cProfile -s cumtime script.py`
- Monitor GPU memory with `nvidia-smi` during CUDA operations
- Check frame processing rate logs to identify slow steps

## Known Limitations

- AXIS RelativeImport model requires module-style execution (`python -m`)
- STOKES rendering limited by Blender API (single-threaded, CPU-bound for small models)
- Wonder3D requires significant VRAM (recommend 24GB+ for full resolution)
- TripoSR chunk size trade-off: smaller = faster but less detail; larger = slower but better quality
- Current PoC focuses on single-image input; video-wide processing requires chunking

## Documentation Files

- `AXIS/README.md` - Detailed AXIS module specification
- `AXIS/docs/CODING_CONVENTIONS.md` - Python coding guidelines (Korean but self-explanatory with examples)
- `AXIS/plan.md` - Historical development plan and status
- `AXIS_Motion_Engine/implementation_plan.md` - Phase-based motion engine roadmap
- `docs/Function-Based_Control_Architecture.md` - Control philosophy and parameter design
- `README.md` (if exists at root) - High-level project overview
