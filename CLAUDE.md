# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TALOS_Studio** is an AI-powered animation production platform implementing a **multi-agent architecture** for creating animated content from images and video. The system uses specialized modules for pose estimation, 3D reconstruction, physics simulation, and rendering.

**Current Phase:** Proof-of-concept (PoC) focusing on single-image → 3D model pipeline using TripoSR, with recent refactoring for production readiness.

## Repository Architecture

### Clean Modular Structure (December 2024)

The repository is organized into logical top-level directories:

```
TALOS_Studio/
├── core/                      # Core pipeline infrastructure
│   ├── src/                   # Pipeline modules (error_handler, device_manager, pipeline_executor)
│   ├── tests/                 # Test suite (unit, integration, acceptance)
│   ├── scripts/               # Utility scripts
│   ├── config.yml             # Configuration
│   ├── pytest.ini             # Test config
│   └── requirements.txt       # Dependencies
│
├── modules/                   # Animation processing modules
│   ├── axis/                  # Video pose estimation
│   ├── axis_motion_engine/    # Physics-based motion
│   ├── stokes/                # Fluid simulation & VFX
│   ├── wonder3d/              # 3D reconstruction
│   └── line_detection/        # Line detection research
│
├── frontend/                  # Web interfaces
│   └── timing-editor/         # React timing control UI
│
├── data/                      # All data and references
│   ├── reference/             # Test images and references
│   ├── input/                 # Input files
│   └── test_data/             # Test datasets
│
├── output/                    # All generated outputs
│   ├── deployment/            # Production outputs
│   ├── results/               # Test results
│   └── temp/                  # Temporary files
│
├── experiments/               # POC and experimental code
│   └── manga_to_3d_poc/
│
└── docs/                      # Documentation
```

**Entry Point:**
- `run_pipeline_refactored.py` - Main pipeline entry (root level)

### Animation Modules

1. **AXIS** (`modules/axis/`) - Video-based pose estimation
   - YOLOv8-Pose for 2D keypoint detection
   - VideoPose3D for 3D uplifting
   - Outputs `.bvh` animation files
   - **CRITICAL:** Uses relative imports - MUST run with `python -m` from AXIS directory

2. **AXIS_Motion_Engine** (`modules/axis_motion_engine/`) - Physics-based motion generation
   - Text → motion parameters via LLM
   - OpenSim biomechanical simulation
   - Generates `.sto` and `.bvh` files

3. **STOKES** (`modules/stokes/`) - Fluid simulation and VFX rendering
   - Navier-Stokes fluid simulation
   - Blender Cycles rendering backend
   - REST API + WebSocket real-time updates
   - React frontend for parameter control

4. **Wonder3D** (`modules/wonder3d/`) - Multi-view 3D reconstruction
   - Cross-domain diffusion for multi-view generation
   - NeuS/Instant-NSR mesh extraction
   - High VRAM requirement (24GB+ recommended)

5. **Line Detection** (`modules/line_detection/`) - Line extraction research
   - Comparative analysis of line detection models
   - TripoSR integration (current 3D reconstruction method)
   - Focus on manga/anime-style content

6. **Timing Editor** (`frontend/timing-editor/`) - Animation timing UI
   - React/TypeScript frontend
   - Gemini API for intelligent timing suggestions

## Development Commands

### Main Pipeline (Refactored)

**Setup:**
```bash
# Create virtual environment (Python 3.10+)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install core dependencies
pip install -r core/requirements.txt
```

**Run Pipeline:**
```bash
# Refactored pipeline with proper error handling
python run_pipeline_refactored.py --input_image data/input/image.png

# With custom config and output directory
python run_pipeline_refactored.py --config core/config.yml --input_image data/input/test.png --output_dir output/results

# Enable debug logging
python run_pipeline_refactored.py --input_image data/input/test.png --log_level DEBUG
```

### Testing

**Run tests:**
```bash
# All tests (35 tests total, excludes heavy submodules)
cd core
pytest -v

# Unit tests only (24 tests for src/ modules)
cd core
pytest tests/unit -v

# Integration tests
cd core
pytest tests/integration -v

# With coverage report
cd core
pytest --cov=src tests/unit -v

# Run specific test file
cd core
pytest tests/unit/test_device_manager.py -v
```

**View test results:**
```bash
cat output/results/test_reports/unit_test_results.txt
cat output/results/test_reports/complete_test_results.txt
```

### AXIS Module

**CRITICAL:** All AXIS scripts use relative imports and MUST be run with `python -m` from the AXIS directory.

**Setup:**
```bash
cd modules/axis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run pipeline:**
```bash
# Full pipeline: video → 2D keypoints → 3D pose → BVH
cd modules/axis
python run_yolo_videopose3d_pipeline.py <input_video.mp4>

# Or use individual steps:
cd modules/axis
python -m scripts.run_pose_estimation <video.mp4>
python -m scripts.prepare_yolo_for_videopose3d <keypoints.json>
python -m scripts.uplift_to_3d <input.npz>
python -m scripts.apply_smoothing <3d_keypoints.json>
python -m scripts.convert_json_to_bvh_bvhio <smoothed_keypoints.json>
```

**Test:**
```bash
cd modules/axis
pytest tests/ -v
```

### STOKES Module

**Setup and run:**
```bash
cd modules/stokes
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start API server (port 5000)
python run_pipeline.py

# Access web UI at http://localhost:5000/
```

**API Endpoints:**
- `POST /api/run_pipeline` - Full simulation + rendering (returns 202 Accepted)
- `POST /api/run_preview` - Quick preview with matplotlib plots
- `POST /api/stop_pipeline` - Terminate running pipeline
- WebSocket `/ws` - Real-time progress updates

### Timing Editor

**Setup and run:**
```bash
cd frontend/timing-editor
npm install

# Development server (Vite, port 5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## Configuration

**`core/config.yml`** - Global pipeline configuration:
```yaml
pipeline_temp_dir: ../output/temp          # Intermediate files
output_deployment_dir: ../output/deployment

track_a_config:                            # Track A parameters
  model_save_format: "obj"
  chunk_size: 8192

track_b_config:                            # Track B parameters (comparison)
  model_save_format: "glb"
  chunk_size: 4096

rendering_config:                          # 2D rendering settings
  renderer: blender
  camera_angle: [30, 45, 0]
  output_resolution: 1024
```

**`core/pytest.ini`** - Test configuration:
- Excludes heavy submodules (DeepLSD, HAWP, DSINE, etc.)
- Run `cd core && pytest -v` to execute all configured tests

## Code Architecture

### Error Handling Pattern (core/src/error_handler.py)

Custom exception hierarchy with exit codes:

```python
from core.src.error_handler import PipelineError, ValidationError, SubprocessError

# ValidationError - invalid inputs (exit code 2)
raise ValidationError("Input image not found: image.png")

# SubprocessError - external process failures (exit code 3)
raise SubprocessError("python script.py", 1, "CUDA out of memory")

# ConfigurationError - invalid config (exit code 4)
raise ConfigurationError("config.yml", "Invalid YAML syntax")
```

All exceptions have `.log_and_exit()` method for graceful termination.

### Device Management Pattern (core/src/device_manager.py)

Intelligent GPU/CPU detection with fallback:

```python
from core.src.device_manager import DeviceManager

device_mgr = DeviceManager()
device_mgr.print_device_info()  # Logs available devices

device = device_mgr.get_device()  # Auto-select best device
# Returns: "cuda:0" if available, else "cpu"

device = device_mgr.get_device(prefer="cuda:1")  # Request specific GPU
# Falls back to cuda:0 or cpu if unavailable
```

### Pipeline Execution Pattern (core/src/pipeline_executor.py)

Main orchestration logic:

```python
from core.src.pipeline_executor import PipelineExecutor

executor = PipelineExecutor(config_path="core/config.yml")

# Execute full pipeline
output_dir = executor.execute(
    input_image="data/input/test.png",
    output_dir="output/results"  # Optional override
)

# Run subprocess with error handling
executor.run_subprocess(
    command=["python", "script.py", "--input_image", "test.png"],
    description="Running 3D reconstruction",
    timeout=3600  # 1 hour timeout
)
```

### Function-Based Control Philosophy

AI outputs represented as deterministic functions: `Y = F_θ(X, P)` where:
- `X` = input data
- `P` = externally controllable parameters
- `θ` = model weights (fixed)

This enables:
- **Reproducibility:** Same inputs + parameters = identical outputs
- **Fine-grained control:** Adjust parameters without retraining
- **Debugging:** Isolate issues by parameter variation

See `docs/Function-Based_Control_Architecture.md` for details.

## Common Patterns

### Chunked Processing

Large videos processed in overlapping chunks to manage memory:

```python
# AXIS example
chunk_size = 300  # frames
overlap = 50      # frames of overlap for smooth stitching

# Process chunks independently
# Stitch overlapping regions using Savitzky-Golay smoothing
```

### Multi-Track Comparison

Execute pipeline with multiple parameter sets (Track A, B, etc.):

```python
# config.yml defines track_a_config and track_b_config
# Pipeline runs both and generates comparison HTML
# Useful for A/B testing model parameters
```

### Asynchronous Module Communication

Modules communicate via:
- **REST APIs:** Non-blocking task dispatch (202 Accepted)
- **Callbacks:** POST to orchestrator on completion
- **File interchange:** URLs to shared storage (not large payloads)
- **Status tracking:** Central job queue

## Output Structure

```
output/
├── deployment/                 # Production outputs
│   ├── track_a/               # Track A results
│   │   ├── model.obj          # 3D model
│   │   └── render.png         # 2D render
│   ├── track_b/               # Track B results
│   └── comparison.html        # Side-by-side comparison
├── results/                   # Test results and reports
│   └── test_reports/          # Pytest output files
└── temp/                      # Temporary intermediate files
    ├── track_a_3d/
    └── track_b_3d/

modules/[module]/output_data/  # Module-specific outputs
├── *_keypoints.json           # AXIS pose data
├── *.bvh                      # Animation files
├── *.mp4                      # Visualization videos
└── frames_*/                  # Frame sequences
```

## AXIS Coding Conventions

**Naming:**
- Classes: `PascalCase` (e.g., `FrameContext`)
- Functions/Methods: `snake_case` (e.g., `run_pipeline`)
- Variables: `snake_case` (e.g., `original_frame`)
- Constants: `UPPER_SNAKE_CASE` (module-level)
- Internal members: prefix `_` (e.g., `_context_data`)

**Imports:**
```python
# Standard library first
import os
import sys

# Third-party next
import cv2
import numpy as np

# Local imports last (relative paths)
from .pipeline import Pipeline
from ..strategies.base import BaseEstimator
```

**Type Hints:**
```python
def estimate(self, frame: np.ndarray, threshold: int = 100) -> np.ndarray:
    """Estimate edges from frame."""
    pass
```

**Documentation:**
- Public classes/functions require docstrings
- Comments explain **why**, not **what**
- No `# removed` stubs - delete unused code

## Known Issues and Limitations

### Critical Requirements

1. **AXIS Relative Imports:**
   - Scripts MUST be run with `python -m module.path` from AXIS directory
   - Running `python script.py` directly will fail with ImportError

2. **VRAM Requirements:**
   - Wonder3D: 24GB+ recommended for full resolution
   - TripoSR: 8GB minimum (adjust chunk_size for less VRAM)
   - STOKES Blender rendering: CPU-bound for small models

3. **Chunk Size Trade-off:**
   - Smaller chunk_size: Faster, less VRAM, lower quality
   - Larger chunk_size: Slower, more VRAM, better quality
   - Default 8192 is balanced for RTX 3080+ GPUs

4. **Silent Failures Fixed (Nov 2024):**
   - Legacy `run_pipeline.py` used dummy file creation on errors
   - Refactored version raises proper exceptions
   - Tests now fail fast instead of passing with invalid data

### Environment Notes

- **Python:** 3.10+ required (3.12 recommended)
- **CUDA:** Optional but strongly recommended for GPU acceleration
- **Blender:** Required for STOKES rendering (headless subprocess mode)
- **Node.js:** Required for axis-interactive-timing-editor

## Git Workflow

**Current branch:** `master`

**Recent major changes:**
- Comprehensive refactoring: modular `src/` architecture (Nov 2024)
- Production readiness: proper error handling, logging, validation
- Pytest suite: 24 unit tests, 11 integration/acceptance tests
- TripoSR pivot: primary 3D reconstruction method

**Submodules:**
Some modules contain git submodules (e.g., AXIS/models/). Clone with:
```bash
git clone --recursive <repo_url>
```

## Debugging and Performance

### Debugging Pipeline Issues

```bash
# Enable debug logging
python run_pipeline_refactored.py --input_image data/input/test.png --log_level DEBUG

# Check logs
tail -f output/temp/pipeline.log

# Inspect intermediate outputs
ls -la output/temp/
cat output/temp/track_a_3d/model.obj  # Verify 3D model exists

# Test individual stages by running specific modules
cd modules/line_detection/TripoSR
python run.py --input_image ../../../data/input/test.png
```

### Profiling Performance

```bash
# Python profiling
python -m cProfile -s cumtime run_pipeline_refactored.py --input_image test.png

# Monitor GPU usage
nvidia-smi -l 1  # Update every second

# Check frame processing rate in logs
grep "finished in" pipeline.log
```

### Common Errors

**ImportError in AXIS:**
```bash
# Wrong: python scripts/run_pose_estimation.py
# Right:
cd modules/axis
python -m scripts.run_pose_estimation
```

**CUDA out of memory (3D Reconstruction):**
```bash
# Reduce chunk size in core/config.yml
track_a_config:
  chunk_size: 4096  # Lower value = less VRAM
```

**Subprocess timeout:**
```bash
# Check logs for which subprocess timed out
# Adjust timeout in core/src/pipeline_executor.py if needed (default 3600s)
```

## Testing Guidelines

### Writing Tests

Tests should use pytest fixtures and follow the existing patterns:

```python
# core/tests/unit/test_new_module.py
import pytest
from core.src.new_module import NewClass

def test_initialization():
    """Test NewClass initializes correctly."""
    obj = NewClass(param="value")
    assert obj.param == "value"

def test_error_handling():
    """Test NewClass raises appropriate errors."""
    with pytest.raises(ValueError, match="Invalid param"):
        NewClass(param=None)
```

**Run tests before committing:**
```bash
cd core
pytest tests/unit -v  # Fast unit tests
pytest -v             # Full test suite
```

### Test Organization

- `core/tests/unit/` - Fast, isolated tests for individual modules
- `core/tests/integration/` - Tests across module boundaries
- `core/tests/acceptance/` - End-to-end pipeline tests (may be slow)

## Additional Resources

- `docs/PRODUCTION_READINESS_IMPROVEMENTS.md` - Recent improvements and fixes
- `docs/PYTEST_VALIDATION_REPORT.md` - Test validation results
- `docs/EXCEPTION_HANDLING_AUDIT.md` - Code quality audit
- `docs/Function-Based_Control_Architecture.md` - Control philosophy
- `docs/TALOS_System_Architecture_and_Workflow.md` - High-level system design
- `PROJECT_STRUCTURE.md` - Detailed directory structure

## Summary of Key Changes

### December 2024: Major Directory Restructuring

1. **Clean Root Directory:** Reduced from 20+ items to 8 organized directories
   - `core/` - All pipeline infrastructure
   - `modules/` - All animation modules
   - `frontend/` - All web interfaces
   - `data/` - All data and references
   - `output/` - All generated outputs
   - `experiments/` - POC and research code
   - `docs/` - All documentation

2. **Organized Modules:** All animation modules under `modules/`
   - `modules/axis/` (formerly `AXIS/`)
   - `modules/axis_motion_engine/` (formerly `AXIS_Motion_Engine/`)
   - `modules/stokes/` (formerly `STOKES/`)
   - `modules/wonder3d/` (formerly `Wonder3D/`)
   - `modules/line_detection/` (formerly `line_detection_comparison/`)

3. **Unified Data:** All data under `data/`
   - `data/reference/` - Test images, reference data
   - `data/input/` - Input files
   - `data/test_data/` - Test datasets

4. **Unified Outputs:** All outputs under `output/`
   - `output/deployment/` - Production outputs
   - `output/results/` - Test results
   - `output/temp/` - Temporary files

5. **Deleted Legacy Code:**
   - Removed `run_pipeline.py` (superseded by `run_pipeline_refactored.py`)
   - Removed `run_triposr.py` (integrated into pipeline)
   - Cleaned up scattered utility scripts to `core/scripts/utilities/`

### November 2024: Core Pipeline Refactoring

1. **Modularization:** Separated concerns into `core/src/` modules (error_handler, device_manager, pipeline_executor)
2. **Error Handling:** Removed silent failures, added proper exception raising with exit codes
3. **Logging:** Added comprehensive logging system with timestamps and severity levels
4. **Testing:** 24 unit tests, 11 integration/acceptance tests (94% pass rate)
5. **Documentation:** Consolidated docs into `docs/` directory
6. **Entry Point:** New `run_pipeline_refactored.py` with proper argument parsing
