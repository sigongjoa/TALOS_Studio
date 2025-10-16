# Refactoring and Testing Strategy for Visualization Models

This document outlines the refactored code structure for the visualization generation pipeline and the strategy for testing models independently.

## 1. Problem: Monolithic Structure

The original `generate_visualizations.py` script was a single, monolithic function. This approach had several drawbacks:

- **Inefficient Testing:** Running `pytest` executed the entire pipeline, including already verified models like `SOLD2`, every single time. This was slow and inefficient.
- **High Coupling:** All model processing steps were tightly coupled. A failure in one model (e.g., a missing dependency for `SOLD2`) prevented all other models (like `DSINE`) from being tested.
- **Poor Maintainability:** Adding a new model required modifying the central function, increasing the risk of introducing bugs into existing, working code.

## 2. Solution: Modular Structure

To solve these issues, the code was refactored into a modular, function-based pipeline.

### 2.1. `generate_visualizations.py`

The main script is now composed of small, independent functions, each responsible for generating a single panel in the visualization:

- `generate_panel_original()`
- `generate_panel_manga_lines()`
- `generate_panel_inverted_lines()`
- `generate_panel_sold2()`
- `generate_panel_canny()`
- `generate_panel_dsine()` (New placeholder)
- `generate_html_report()`

A master function, `generate_visualizations(models_to_run=None)`, orchestrates these smaller functions. It accepts a list of model names to run, allowing for selective execution. If no list is provided, it runs all models by default.

### 2.2. `test_visualizations.py`

The test script was updated to mirror the new modular structure:

- It now contains individual test functions for each panel (e.g., `test_panel_original()`, `test_panel_dsine()`).
- This allows for targeted testing of a single model's functionality.
- A dedicated test, `test_generate_visualizations_for_single_model`, was added to verify that the main orchestrator can run a single model pipeline (like `DSINE`) without executing others.
- Unrelated tests, like `test_panel_sold2`, can be skipped using pytest markers (`@pytest.mark.skip`) to focus on the model currently under development.

## 3. Development and Testing Workflow

### 3.1. Virtual Environment

All Python dependencies for this project should be installed in the dedicated virtual environment.

- **Location:** `line_detection_comparison/venv/`
- **Activation:**
  ```bash
  source /mnt/d/progress/TALOS_Studio/line_detection_comparison/venv/bin/activate
  ```
- **Dependency Installation:**
  If a model (like `SOLD2` or `DSINE`) has a `requirements.txt` file, install its dependencies using pip:
  ```bash
  pip install -r /path/to/model/requirements.txt
  ```
  For single packages:
  ```bash
  pip install <package_name>
  ```

### 3.2. Running Tests

With the new structure, you can run tests for a specific model.

- **To run only the DSINE tests:**
  You can use pytest's `-k` flag to select tests by name.
  ```bash
  # Ensure you are in the root directory /mnt/d/progress/TALOS_Studio/
  # Make sure the virtualenv is NOT active, as we will call the python from it directly.
  
  PYTHONPATH="line_detection_comparison/libs/SOLD2:line_detection_comparison/libs/DSINE" /mnt/d/progress/TALOS_Studio/line_detection_comparison/venv/bin/python -m pytest -k "dsine"
  ```
  This command will execute `test_panel_dsine` and `test_generate_visualizations_for_single_model`.

- **To run all tests (and skip marked tests):**
  ```bash
  PYTHONPATH="line_detection_comparison/libs/SOLD2:line_detection_comparison/libs/DSINE" /mnt/d/progress/TALOS_Studio/line_detection_comparison/venv/bin/python -m pytest
  ```

## 4. How to Add a New Model (e.g., `NewModel`)

1.  **Create Inference Script:** Add your model's inference logic in a script, e.g., `line_detection_comparison/run_newmodel.py`.
2.  **Add Panel Function:** In `generate_visualizations.py`, create a new function `generate_panel_newmodel(...)` that calls your inference script.
3.  **Update Orchestrator:** Add `'newmodel'` to the `generate_visualizations` function's logic.
4.  **Add a Test:** In `test_visualizations.py`, add a new test function `test_panel_newmodel()` to test your new panel in isolation.
