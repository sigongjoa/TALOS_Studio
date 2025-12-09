# TALOS Studio - Project Structure

## Overview

TALOS Studio is an AI-powered animation production platform with a clean, modular architecture. All components are organized into logical directories for easy navigation and maintenance.

## Directory Structure

```
TALOS_Studio/
├── core/                          # Core pipeline infrastructure
│   ├── src/                       # Main pipeline modules
│   │   ├── __init__.py
│   │   ├── error_handler.py       # Exception classes and error handling
│   │   ├── device_manager.py      # GPU/CPU detection and management
│   │   └── pipeline_executor.py   # Pipeline orchestration
│   ├── tests/                     # Test suite
│   │   ├── unit/                  # Unit tests (24 tests)
│   │   ├── integration/           # Integration tests
│   │   └── acceptance/            # End-to-end tests
│   ├── scripts/                   # Utility scripts
│   │   ├── blender_render.py
│   │   └── utilities/
│   ├── config.yml                 # Pipeline configuration
│   ├── pytest.ini                 # Test configuration
│   └── requirements.txt           # Python dependencies
│
├── modules/                       # Animation processing modules
│   ├── axis/                      # Video-based pose estimation
│   │   ├── src/                   # AXIS source code
│   │   ├── scripts/               # Pipeline scripts
│   │   ├── models/                # ML models (submodules)
│   │   ├── tests/                 # Module tests
│   │   └── requirements.txt
│   │
│   ├── axis_motion_engine/        # Physics-based motion generation
│   │   ├── src/                   # Motion engine source
│   │   ├── sim_models/            # Simulation models
│   │   └── requirements.txt
│   │
│   ├── stokes/                    # Fluid simulation and VFX
│   │   ├── backend/               # Flask API server
│   │   ├── frontend/              # React UI
│   │   ├── src/                   # Simulation core
│   │   └── requirements.txt
│   │
│   ├── wonder3d/                  # 3D reconstruction
│   │   ├── mvdiffusion/           # Multi-view diffusion
│   │   └── instant-nsr-pl/        # Neural surface reconstruction
│   │
│   └── line_detection/            # Line detection research
│       ├── libs/                  # Detection models (HAWP, SOLD2, etc.)
│       └── TripoSR/               # 3D reconstruction (current)
│
├── frontend/                      # Web interfaces
│   └── timing-editor/             # React timing control UI
│       ├── src/
│       ├── public/
│       └── package.json
│
├── data/                          # Data and references
│   ├── reference/                 # Reference images and test data
│   │   ├── image_01/
│   │   ├── image_02/
│   │   ├── image_03/
│   │   ├── image_04/
│   │   ├── image_05/
│   │   ├── ref/
│   │   └── vectorization/
│   ├── input/                     # Input files for processing
│   └── test_data/                 # Test datasets
│
├── output/                        # Generated outputs
│   ├── deployment/                # Production-ready outputs
│   ├── results/                   # Test results and reports
│   └── temp/                      # Temporary intermediate files
│
├── experiments/                   # Proof-of-concept and experiments
│   └── manga_to_3d_poc/          # Manga to 3D pipeline POC
│
├── docs/                          # Documentation
│   ├── CLAUDE.md                  # Claude Code guide (symlink)
│   ├── PRODUCTION_READINESS_IMPROVEMENTS.md
│   ├── PYTEST_VALIDATION_REPORT.md
│   ├── EXCEPTION_HANDLING_AUDIT.md
│   ├── TEST_VERIFICATION_SUMMARY.md
│   ├── Function-Based_Control_Architecture.md
│   ├── TALOS_Inter-Module_Communication_Protocol.md
│   ├── TALOS_System_Architecture_and_Workflow.md
│   └── index.html                 # Line detection visualizations
│
├── CLAUDE.md                      # Claude Code guidance (root)
└── run_pipeline_refactored.py    # Main pipeline entry point
```

## Key Design Principles

### 1. Separation of Concerns
- **core/** - Core pipeline infrastructure (orchestration, error handling, device management)
- **modules/** - Self-contained animation processing modules
- **frontend/** - User interfaces
- **data/** - All data inputs and references
- **output/** - All generated outputs

### 2. Module Independence
Each module in `modules/` operates independently with:
- Its own virtual environment
- Own requirements.txt
- Own test suite
- Clear input/output contracts

### 3. Clean Root Directory
Root contains only:
- Entry point script (`run_pipeline_refactored.py`)
- Main documentation (`CLAUDE.md`)
- Top-level directories

### 4. Organized Outputs
All outputs go to `output/`:
- `deployment/` - Production-ready results
- `results/` - Test reports and validation
- `temp/` - Transient files (gitignored)

## Module Overview

### Core Pipeline (core/)
Refactored pipeline infrastructure with:
- Modular error handling (exit codes, proper exceptions)
- Intelligent device management (GPU/CPU fallback)
- Pipeline orchestrator (subprocess management, validation)
- Comprehensive test suite (24 unit tests, 94% pass rate)

### AXIS (modules/axis/)
Video-based pose estimation:
- YOLOv8-Pose for 2D keypoints
- VideoPose3D for 3D uplifting
- Temporal smoothing and BVH export
- **Important:** Uses relative imports, must run with `python -m`

### AXIS Motion Engine (modules/axis_motion_engine/)
Physics-based motion generation:
- LLM-driven parameter generation
- OpenSim biomechanical simulation
- Outputs .sto and .bvh files

### STOKES (modules/stokes/)
Fluid simulation and VFX:
- Navier-Stokes fluid simulation
- Blender Cycles rendering
- REST API + WebSocket updates
- React frontend for real-time control

### Wonder3D (modules/wonder3d/)
Single-image 3D reconstruction:
- Cross-domain diffusion for multi-view generation
- NeuS/Instant-NSR mesh extraction
- High VRAM requirement (24GB+ recommended)

### Line Detection (modules/line_detection/)
Comparative line extraction research:
- Multiple models (HAWP, L-CNN, DeepLSD, SOLD2)
- TripoSR integration (current 3D method)
- Focus on manga/anime-style content

## Running the Pipeline

### Main Entry Point
```bash
# From repository root
python run_pipeline_refactored.py --input_image data/input/test.png

# With custom config
python run_pipeline_refactored.py --config core/config.yml --input_image data/input/test.png
```

### Testing
```bash
# From repository root
cd core
pytest tests/unit -v              # Unit tests only
pytest -v                         # All tests
pytest --cov=src tests/unit -v    # With coverage
```

### Module-Specific Execution
```bash
# AXIS (must use python -m from module directory)
cd modules/axis
python -m scripts.run_pose_estimation <video.mp4>

# STOKES (API server)
cd modules/stokes
python run_pipeline.py

# Frontend
cd frontend/timing-editor
npm run dev
```

## Configuration

- **core/config.yml** - Main pipeline configuration
  - Track A/B parameters for comparison
  - Rendering settings
  - Output paths
- **core/pytest.ini** - Test discovery configuration
- **core/requirements.txt** - Core dependencies
- **modules/*/requirements.txt** - Module-specific dependencies

## Output Organization

```
output/
├── deployment/           # Final production outputs
│   ├── track_a/         # Track A results
│   ├── track_b/         # Track B results
│   └── comparison.html  # Side-by-side comparison
├── results/             # Test results and reports
│   └── test_reports/    # Pytest output files
└── temp/                # Intermediate files (gitignored)
    ├── track_a_3d/
    └── track_b_3d/
```

## Git Workflow

**Current Branch:** master

**Important Notes:**
- Submodules in `modules/axis/models/`, `modules/wonder3d/`, etc.
- Clone with `--recursive` flag
- `.gitignore` configured for all output and temp directories

## Environment Setup

### Core Pipeline
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r core/requirements.txt
```

### Module-Specific
Each module has its own setup instructions in its README.

**Requirements:**
- Python 3.10+ (3.12 recommended)
- CUDA (optional but recommended for GPU acceleration)
- Blender (for STOKES rendering)
- Node.js (for frontend)

## Recent Changes (November 2024)

This structure represents a major refactoring:

1. **Modularization** - Separated core pipeline from modules
2. **Clean Root** - Only essential files at root level
3. **Organized Data** - All data in `data/`, all outputs in `output/`
4. **Better Testing** - Comprehensive test suite in `core/tests/`
5. **Clear Documentation** - All docs in `docs/`

**Previous Structure Issues Fixed:**
- ❌ 20+ directories in root → ✅ 8 organized directories
- ❌ Scattered scripts → ✅ `core/scripts/utilities/`
- ❌ Mixed data files → ✅ `data/reference/`
- ❌ Multiple output dirs → ✅ `output/{deployment,results,temp}/`
- ❌ No clear entry point → ✅ `run_pipeline_refactored.py` at root

## Development Guidelines

- See `CLAUDE.md` for detailed development guidance
- Core pipeline code goes in `core/src/`
- Module code stays in respective `modules/*/` directory
- Tests go in `core/tests/` or `modules/*/tests/`
- All outputs to `output/` directory
- Documentation in `docs/`

---

**Last Updated:** 2024-12-09
**Structure Version:** 2.0 (Refactored)
**Test Coverage:** 24 unit tests, 94% pass rate
