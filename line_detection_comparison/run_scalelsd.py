#!/usr/bin/env python

import subprocess
import os

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- ScaleLSD Configuration ---
SCALELSD_DIR = os.path.join(BASE_DIR, "libs", "ScaleLSD")
CONDA_ENV_NAME = "scalelsd"
# The default model is used, so no explicit checkpoint path is needed unless we want to override.

# --- Input/Output Configuration ---
def run_scalelsd(input_image_path, output_dir):
    """
    Runs the ScaleLSD inference script using its dedicated conda environment.
    """
    print("--- Running ScaleLSD Inference ---")
    
    # The inference command is `python -m predictor.predict --img [IMAGE_PATH]`
    # It saves outputs to the same directory as the script by default.
    # We will run it from within the ScaleLSD directory.
    output_filename = "intermediate_image.png" # This is based on the input filename
    final_filename = "scalelsd_detection.png"
    
    command = [
        "conda", "run", "-n", CONDA_ENV_NAME,
        "python", "-m", "predictor.predict",
        "--img", input_image_path,
        "--saveto", output_dir,
        "--ext", "png",
    ]
    
    try:
        # The script should be run from the ScaleLSD directory
        subprocess.run(command, check=True, cwd=SCALELSD_DIR)
        print("--- ScaleLSD Inference Complete ---")
        
        # Rename the output file to our desired name
        original_output_path = os.path.join(output_dir, output_filename)
        final_output_path = os.path.join(output_dir, final_filename)
        
        if os.path.exists(original_output_path):
            os.rename(original_output_path, final_output_path)
            print(f"Renamed output to {final_output_path}")
        else:
            print(f"Warning: Expected output file not found at {original_output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error running ScaleLSD: {e}")
    except FileNotFoundError:
        print(f"Error: Could not find the conda executable or the inference script.")

if __name__ == "__main__":
    # For standalone testing, use the default input/output paths
    default_input_image = os.path.join(BASE_DIR, "input", "test_image.jpg") # Assuming a default test image
    default_output_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(default_output_dir, exist_ok=True)
    run_scalelsd(default_input_image, default_output_dir)
    print("\nScaleLSD script finished.")
