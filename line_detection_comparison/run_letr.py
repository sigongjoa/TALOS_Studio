#!/usr/bin/env python

import subprocess
import os

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- LETR Configuration ---
LETR_DIR = os.path.join(BASE_DIR, "libs", "LETR")
CONDA_ENV_NAME = "letr"
CHECKPOINT_PATH = os.path.join(LETR_DIR, "checkpoints", "exp", "res101_stage2_focal", "checkpoints", "checkpoint0024.pth")

# --- Input/Output Configuration ---
INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def run_letr():
    """
    Runs the LETR inference script using its dedicated conda environment.
    """
    print("--- Running LETR (Wireframe Transformer) Inference ---")
    
    inference_script = os.path.join(LETR_DIR, "src", "run_letr_inference.py")
    
    command = [
        "conda", "run", "-n", CONDA_ENV_NAME,
        "python", inference_script,
        "--input_image", INPUT_IMAGE,
        "--output_dir", OUTPUT_DIR,
        "--checkpoint_path", CHECKPOINT_PATH,
    ]
    
    try:
        # The script needs to be run from the `src` directory to find the model definitions
        subprocess.run(command, check=True, cwd=os.path.join(LETR_DIR, "src"))
        print("--- LETR Inference Complete ---")
    except subprocess.CalledProcessError as e:
        print(f"Error running LETR: {e}")
    except FileNotFoundError:
        print(f"Error: Could not find the conda executable or the inference script.")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_letr()
    print("\nLETR script finished.")
