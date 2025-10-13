import subprocess
import os
import sys

def run_dsine_minimal():
    dsine_library_root = "/mnt/d/progress/TALOS_Studio/line_detection_comparison/libs/DSINE"
    dsine_project_path = os.path.join(dsine_library_root, "projects", "dsine")
    
    if not os.path.isdir(dsine_project_path):
        print(f"Error: DSINE project path not found at {dsine_project_path}")
        sys.exit(1)

    original_cwd = os.getcwd()
    sys.path.insert(0, dsine_library_root) # Add DSINE root to sys.path
    os.chdir(dsine_library_root) # Change to DSINE root to run as module

    # Set PYTHONPATH for the subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = dsine_library_root + os.pathsep + env.get("PYTHONPATH", "")

    try:
        print(f"Running test_minimal.py as a module from {os.getcwd()}")
        
        command = [
            sys.executable, 
            "-m", # Run as a module
            "projects.dsine.test_minimal",
            "./projects/dsine/experiments/exp001_cvpr2024/dsine.txt"
        ]
        
        process = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
        print("STDOUT:")
        print(process.stdout)
        print("STDERR:")
        print(process.stderr)
        print("DSINE minimal test completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running DSINE minimal test: {e}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    run_dsine_minimal()
