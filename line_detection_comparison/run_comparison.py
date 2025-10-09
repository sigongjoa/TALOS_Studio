import subprocess
import os

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- HAWP Configuration ---
HAWP_DIR = os.path.join(BASE_DIR, "libs", "Hawp")
HAWP_VENV = os.path.join(HAWP_DIR, "venv_hawp", "bin", "python")
HAWP_CKPT = os.path.join(HAWP_DIR, "checkpoints", "hawpv3-imagenet-03a84.pth")

# --- Input/Output Configuration ---
INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def run_hawp():
    """
    Runs the HAWP inference script using its dedicated virtual environment.
    """
    print("--- Running HAWP (v3) Inference ---")
    
    # The HAWP script saves files directly in the --saveto directory
    # with names based on the input image.
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
        # We need to run this from within the HAWP directory for it to find its modules
        subprocess.run(command, check=True, cwd=HAWP_DIR)
        print("--- HAWP Inference Complete ---")
        # The output file will be named something like 'test_image.png' in the output dir.
        # We will rename it to be more specific for the montage script later.
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


if __name__ == "__main__":
    # For now, we only run HAWP. This will be expanded later.
    run_hawp()

    # TODO: Add calls for other libraries (DHT, L-CNN, etc.)

    # TODO: Call the montage script to create the final comparison grid.
    print("\nComparison script finished.")
