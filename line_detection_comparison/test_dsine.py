import subprocess
import os
import pytest

def test_run_dsine_minimal():
    script_path = "/mnt/d/progress/TALOS_Studio/line_detection_comparison/run_dsine_minimal.py"
    
    # Ensure the script exists
    assert os.path.exists(script_path), f"Script not found at {script_path}"

    # Run the script and capture its output and exit code
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    # Print stdout and stderr for debugging purposes if the test fails
    print("--- STDOUT ---")
    print(result.stdout)
    print("--- STDERR ---")
    print(result.stderr)

    # Assert that the script exited successfully (exit code 0)
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}"
    
    # Optionally, check for specific output to confirm successful execution
    assert "DSINE minimal test completed successfully." in result.stdout
