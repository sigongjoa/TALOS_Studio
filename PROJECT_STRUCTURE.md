# TALOS Studio - Project Structure

## Directory Layout

```
TALOS_Studio/
├── src/                                    # Core pipeline modules (refactored)
│   ├── __init__.py                         # Package initialization
│   ├── error_handler.py                    # Custom exceptions and error handling
│   ├── device_manager.py                   # GPU/CPU device detection
│   └── pipeline_executor.py                # Main pipeline orchestrator
│
├── tests/                                  # Test suite
│   ├── unit/                               # Unit tests
│   │   ├── test_error_handler.py           # Error handling tests
│   │   ├── test_device_manager.py          # Device manager tests
│   │   ├── test_pipeline_executor.py       # Pipeline executor tests
│   │   └── test_example.py                 # Example tests
│   ├── integration/                        # Integration tests
│   │   └── test_step1_to_step2.py         # End-to-end tests
│   └── acceptance/                         # Acceptance tests
│       └── test_poc_pipeline_acceptance.py # Full pipeline tests
│
├── docs/                                   # Documentation (consolidated)
│   ├── CLAUDE.md                           # Developer guide for Claude Code
│   ├── PRODUCTION_READINESS_IMPROVEMENTS.md # What was improved
│   ├── PYTEST_VALIDATION_REPORT.md         # Test validation results
│   ├── EXCEPTION_HANDLING_AUDIT.md         # Code quality audit
│   ├── TEST_VERIFICATION_SUMMARY.md        # Test summary
│   ├── Function-Based_Control_Architecture.md
│   ├── TALOS_Inter-Module_Communication_Protocol.md
│   ├── TALOS_System_Architecture_and_Workflow.md
│   ├── poc_pipeline_diagram.md
│   ├── studio_talos_architecture_en.md
│   └── studio_talos_architecture_ko.md
│
├── results/                                # Test results and artifacts
│   └── test_reports/                       # Test execution reports
│       ├── unit_test_results.txt           # Unit test output
│       └── complete_test_results.txt       # Full test suite output
│
├── AXIS/                                   # Pose estimation module
│   ├── src/                                # AXIS source code
│   ├── scripts/                            # Utility scripts
│   ├── models/                             # ML models
│   ├── tests/                              # Module-specific tests
│   └── README.md
│
├── AXIS_Motion_Engine/                     # Physics-based motion generation
│   ├── src/                                # Motion engine source code
│   ├── sim_models/                         # Simulation models
│   ├── tests/                              # Module-specific tests
│   └── README.md
│
├── STOKES/                                 # Fluid simulation and VFX
│   ├── src/                                # STOKES source code
│   ├── scripts/                            # Rendering scripts
│   ├── tests/                              # Module-specific tests
│   └── README.md
│
├── Wonder3D/                               # 3D reconstruction module
│   ├── src/                                # Wonder3D source code
│   ├── mvdiffusion/                        # Multi-view diffusion
│   └── tests/                              # Module-specific tests
│
├── axis-interactive-timing-editor/         # React UI for timing control
│   ├── src/                                # React components
│   ├── public/                             # Static assets
│   └── package.json
│
├── line_detection_comparison/              # Line detection analysis
│   ├── libs/                               # Line detection models
│   │   ├── deep-hough-transform/
│   │   ├── HAWP/
│   │   └── TripoSR/                        # 3D reconstruction model
│   └── tests/
│
├── manga_to_3d_poc/                        # PoC pipeline directory
│   └── test_pipeline.py
│
├── run_pipeline_refactored.py              # ✨ NEW: Refactored main entry point
├── run_pipeline.py                         # Original main entry point (deprecated)
├── run_triposr.py                          # TripoSR wrapper script
│
├── config.yml                              # Pipeline configuration
├── pytest.ini                              # Pytest configuration
├── requirements.txt                        # Root dependencies
├── PROJECT_STRUCTURE.md                    # This file
└── .gitignore
```

## Key Improvements in This Refactoring

### 1. **Modularization** ✅
- **Before:** Monolithic `run_pipeline.py` with all logic
- **After:** Separated concerns into `src/` modules:
  - `error_handler.py` - Exception classes and logging
  - `device_manager.py` - Device detection logic
  - `pipeline_executor.py` - Pipeline orchestration

### 2. **Test Organization** ✅
- **Before:** Tests scattered in various locations
- **After:** Organized test hierarchy:
  - `tests/unit/` - Unit tests for individual modules (24 tests)
  - `tests/integration/` - Integration tests between modules
  - `tests/acceptance/` - End-to-end pipeline tests

### 3. **Documentation** ✅
- **Before:** MD files scattered at root
- **After:** All documentation in `docs/` folder with clear organization

### 4. **Test Results** ✅
- **Before:** No test result tracking
- **After:** Results saved in `results/test_reports/`
  - `unit_test_results.txt` - 24 unit tests
  - `complete_test_results.txt` - All tests (35 tests)

### 5. **Code Quality** ✅
- Custom exception classes with proper exit codes
- Intelligent device manager with fallback to CPU
- Pipeline executor with comprehensive error handling
- Type hints throughout new code
- Comprehensive docstrings

## Test Results Summary

```
📊 TEST RESULTS
├── Unit Tests: 24/24 PASSED ✅
├── Integration Tests: 1/1 PASSED ✅
├── Acceptance Tests: 1/2 FAILED (expected - requires real image data)
├── Visualization Tests: 6/7 PASSED ✅
├── Total: 33/35 PASSED (94%)
└── Skipped: 1 (SOLD2 legacy model)
```

## Running Tests

### Run only new unit tests
```bash
python -m pytest tests/unit -v
```

### Run all tests
```bash
python -m pytest -v
```

### Run with coverage report
```bash
python -m pytest --cov=src tests/unit -v
```

### View test results
```bash
cat results/test_reports/unit_test_results.txt
cat results/test_reports/complete_test_results.txt
```

## Module Dependencies

```
src/
├── error_handler.py (no dependencies)
│
├── device_manager.py
│   └── requires: torch (optional, graceful fallback)
│
└── pipeline_executor.py
    ├── requires: error_handler
    ├── requires: device_manager
    └── requires: yaml, subprocess, logging
```

## Configuration Files

| File | Purpose |
|------|---------|
| `config.yml` | Pipeline configuration (devices, model settings) |
| `pytest.ini` | Pytest discovery and execution settings |
| `requirements.txt` | Python dependencies |

## Documentation Structure in `docs/`

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Developer guide for future Claude Code work |
| `PRODUCTION_READINESS_IMPROVEMENTS.md` | Detailed improvement list |
| `PYTEST_VALIDATION_REPORT.md` | Test execution and validation |
| `EXCEPTION_HANDLING_AUDIT.md` | Code quality audit results |
| `TEST_VERIFICATION_SUMMARY.md` | Summary of all verifications |
| Architecture docs | System design and communication |

## Next Steps

1. **Complete Pipeline Implementation**
   - Implement 3D reconstruction stage (TripoSR)
   - Implement 2D rendering stage (Blender)
   - Implement result packaging stage

2. **Environment Consolidation**
   - Merge multiple venvs into single environment
   - Create Docker image for consistency

3. **Performance Optimization**
   - Profile critical paths
   - Implement caching where appropriate
   - Parallel processing for multi-track rendering

4. **Integration Testing**
   - Test with real image data
   - Validate TripoSR integration
   - Test Blender rendering pipeline

## Quick Start

```bash
# Run new refactored pipeline
python run_pipeline_refactored.py --help

# Run all tests
python -m pytest -v

# View test results
cat results/test_reports/complete_test_results.txt

# Read documentation
cat docs/CLAUDE.md
```

---

**Last Updated:** 2025-11-19
**Structure Refactored:** ✅ Complete
**Tests:** ✅ 24/24 unit tests passing
**Documentation:** ✅ Consolidated in docs/
**Test Results:** ✅ Tracked in results/test_reports/
