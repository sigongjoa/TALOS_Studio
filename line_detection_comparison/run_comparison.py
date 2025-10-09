import subprocess
import os
import shutil # For moving files

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- HAWP Configuration ---
HAWP_DIR = os.path.join(BASE_DIR, "libs", "Hawp")
HAWP_VENV = os.path.join(HAWP_DIR, "venv_hawp", "bin", "python")
HAWP_CKPT = os.path.join(HAWP_DIR, "checkpoints", "hawpv3-imagenet-03a84.pth")

# --- L-CNN Configuration ---
LCNN_DIR = os.path.join(BASE_DIR, "libs", "L-CNN")
LCNN_VENV = os.path.join(LCNN_DIR, "venv_lcnn", "bin", "python")
LCNN_CKPT = os.path.join(LCNN_DIR, "checkpoints", "190418-201834-f8934c6-lr4d10-312k.pth") # User provided this file
LCNN_CONFIG = os.path.join(LCNN_DIR, "config", "wireframe.yaml")

# --- Input/Output Configuration ---
INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def run_hawp():
    """
    Runs the HAWP inference script using its dedicated virtual environment.
    """
    print("--- Running HAWP (v3) Inference ---")
    
    command = [
        HAWP_VENV,
        "-m", "hawp.ssl.predict",
        "--ckpt", HAWP_CKPT,
        "--img", INPUT_IMAGE,
        "--saveto", OUTPUT_DIR,
        "--threshold", "0.05", # Using the default threshold from the readme
        "--ext", "png", # Explicitly request PNG output
    ]
    
    try:
        subprocess.run(command, check=True, cwd=HAWP_DIR)
        print("--- HAWP Inference Complete ---")
        
        original_output_path = os.path.join(OUTPUT_DIR, "test_image.png")
        hawp_output_path = os.path.join(OUTPUT_DIR, "hawp_detection.png")
        if os.path.exists(original_output_path):
            os.rename(original_output_path, hawp_output_path)
            print(f"Renamed output to {hawp_output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error running HAWP: {e}")
    except FileNotFoundError:
        print("Error: Could not find the python executable for the HAWP environment.")
        print("Please ensure the virtual environment is set up correctly at:", HAWP_VENV)

def run_lcnn():
    """
    Runs the L-CNN inference script using its dedicated virtual environment.
    """
    print("---" + " Running L-CNN Inference ---")

    # The demo.py script takes: <yaml-config> <checkpoint> <images>...
    # It saves 'lcnn_detection_temp.png' in its current working directory.
    command = [
        LCNN_VENV,
        os.path.join(LCNN_DIR, "demo.py"),
        LCNN_CONFIG,
        LCNN_CKPT,
        INPUT_IMAGE,
        "-d", "cpu" # Force CPU inference to avoid CUDA issues if not configured
    ]

    try:
        subprocess.run(command, check=True, cwd=LCNN_DIR)
        print("--- L-CNN Inference Complete ---")

        temp_output_path = os.path.join(LCNN_DIR, "lcnn_detection_temp.png")
        lcnn_output_path = os.path.join(OUTPUT_DIR, "lcnn_detection.png")
        if os.path.exists(temp_output_path):
            shutil.move(temp_output_path, lcnn_output_path)
            print(f"Moved and renamed output to {lcnn_output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error running L-CNN: {e}")
    except FileNotFoundError:
        print("Error: Could not find the python executable for the L-CNN environment.")
        print("Please ensure the virtual environment is set up correctly at:", LCNN_VENV)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Ensure output directory exists
    
    run_hawp()
    run_lcnn()

    # Call the montage script to create the final comparison grid.
    print("\n--- Creating Montage ---")
    montage_script_path = os.path.join(BASE_DIR, "create_montage.py")
    subprocess.run([
        "python3", # Use system python for montage script, assuming Pillow is installed
        montage_script_path,
        "--input", INPUT_IMAGE,
        "--dir", OUTPUT_DIR
    ], check=True)

    print("\nComparison script finished.")