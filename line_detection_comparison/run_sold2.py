#!/usr/bin/env python

import subprocess
import os

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- SOLD2 Configuration ---
SOLD2_DIR = os.path.join(BASE_DIR, "libs", "SOLD2")
SOLD2_VENV = os.path.join(SOLD2_DIR, "venv_sold2", "bin", "python")

# --- Input/Output Configuration ---
INPUT_IMAGE = os.path.join(BASE_DIR, "output", "intermediate_image.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def run_sold2():
    """
    Runs the SOLD2 inference script using its dedicated virtual environment.
    """
    print("--- Running SOLD2 Inference ---")
    
    inference_script = os.path.join(SOLD2_DIR, "run_sold2_inference.py")

    command = [
        SOLD2_VENV, inference_script,
        "--input_image", INPUT_IMAGE,
        "--output_dir", OUTPUT_DIR,
    ]
    
    try:
        subprocess.run(command, check=True, cwd=SOLD2_DIR)
        print("--- SOLD2 Inference Complete ---")
    except subprocess.CalledProcessError as e:
        print(f"Error running SOLD2: {e}")
    except FileNotFoundError:
        print(f"Error: Could not find the python executable for the SOLD2 environment: {SOLD2_VENV}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_sold2()
    print("\nSOLD2 script finished.")
