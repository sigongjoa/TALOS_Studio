import subprocess
import os
import shutil
import glob
import matplotlib
matplotlib.use('Agg')

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- HAWP Configuration ---
HAWP_DIR = os.path.join(BASE_DIR, "libs", "Hawp")
HAWP_VENV = os.path.join(HAWP_DIR, "venv_hawp", "bin", "python")
HAWP_CKPT = os.path.join(HAWP_DIR, "checkpoints", "hawpv3-imagenet-03a84.pth")

# --- L-CNN Configuration ---
LCNN_DIR = os.path.join(BASE_DIR, "libs", "L-CNN")
LCNN_VENV = os.path.join(LCNN_DIR, "venv_lcnn", "bin", "python")
LCNN_CKPT = os.path.join(LCNN_DIR, "checkpoints", "190418-201834-f8934c6-lr4d10-312k.pth")
LCNN_CONFIG = os.path.join(LCNN_DIR, "config", "wireframe.yaml")

# --- DSINE Configuration ---
DSINE_LIB_ROOT = os.path.join(BASE_DIR, "libs", "DSINE")
DSINE_PROJECT_PATH = os.path.join(DSINE_LIB_ROOT, "projects", "dsine")
DSINE_OUTPUT_SRC_DIR = os.path.join(DSINE_LIB_ROOT, "samples", "output")


# --- Input/Output Configuration ---
INPUT_IMAGE_NAME = "test_image.jpg"
INPUT_IMAGE_PATH = os.path.join(BASE_DIR, "input", INPUT_IMAGE_NAME)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEPLOYMENT_DIR = os.path.join(BASE_DIR, "..", "output_for_deployment")


def run_hawp():
    print("--- Running HAWP (v3) Inference ---")
    command = [
        HAWP_VENV, "-m", "hawp.ssl.predict", "--ckpt", HAWP_CKPT,
        "--img", INPUT_IMAGE_PATH, "--saveto", OUTPUT_DIR,
        "--threshold", "0.05", "--ext", "png",
    ]
    try:
        subprocess.run(command, check=True, cwd=HAWP_DIR)
        print("--- HAWP Inference Complete ---")
        # Rename output file
        original_output = os.path.join(OUTPUT_DIR, os.path.splitext(INPUT_IMAGE_NAME)[0] + ".png")
        hawp_output = os.path.join(OUTPUT_DIR, "hawp_detection.png")
        if os.path.exists(original_output):
            os.rename(original_output, hawp_output)
            print(f"Renamed output to {hawp_output}")
    except Exception as e:
        print(f"Error running HAWP: {e}")

def run_lcnn():
    print("--- Running L-CNN Inference ---")
    command = [
        LCNN_VENV, os.path.join(LCNN_DIR, "demo.py"), LCNN_CONFIG,
        LCNN_CKPT, INPUT_IMAGE_PATH, "-d", "cpu",
    ]
    try:
        subprocess.run(command, check=True, cwd=LCNN_DIR)
        print("--- L-CNN Inference Complete ---")
        # Move and rename output file
        temp_output = os.path.join(LCNN_DIR, "lcnn_detection_temp.png")
        lcnn_output = os.path.join(OUTPUT_DIR, "lcnn_detection.png")
        if os.path.exists(temp_output):
            shutil.move(temp_output, lcnn_output)
            print(f"Moved and renamed output to {lcnn_output}")
    except Exception as e:
        print(f"Error running L-CNN: {e}")

def run_dsine():
    print("--- Running DSINE (Minimal) Inference ---")
    env = os.environ.copy()
    env["PYTHONPATH"] = DSINE_LIB_ROOT + os.pathsep + env.get("PYTHONPATH", "")
    output_path = os.path.join(DSINE_OUTPUT_SRC_DIR, "dsine_detection.png")
    command = [
        "python3", "test_minimal.py",
        "./experiments/exp001_cvpr2024/dsine.txt",
        "--img_path", INPUT_IMAGE_PATH,
        "--output_path", output_path
    ]
    try:
        # Clear previous DSINE output
        if os.path.exists(DSINE_OUTPUT_SRC_DIR):
            shutil.rmtree(DSINE_OUTPUT_SRC_DIR)
        os.makedirs(DSINE_OUTPUT_SRC_DIR)

        subprocess.run(command, check=True, cwd=DSINE_PROJECT_PATH, env=env)
        print("--- DSINE Inference Complete ---")

        # Move and rename output file
        dsine_output = os.path.join(OUTPUT_DIR, "dsine_detection.png")
        shutil.copy(output_path, dsine_output)
        print(f"Copied and renamed DSINE output to {dsine_output}")

    except Exception as e:
        print(f"Error running DSINE: {e}")

def create_montage():
    print("\n--- Creating Montage ---")
    montage_script = os.path.join(BASE_DIR, "create_montage.py")
    # Note: This montage currently only includes HAWP and L-CNN
    # To include DSINE, create_montage.py would need to be updated.
    subprocess.run([
        "python3", montage_script, "--input", INPUT_IMAGE_PATH, "--dir", OUTPUT_DIR
    ], check=True)

def prepare_for_deployment():
    print("\n--- Preparing Files for Deployment ---")
    # Clean and create deployment directory
    if os.path.exists(DEPLOYMENT_DIR):
        shutil.rmtree(DEPLOYMENT_DIR)
    os.makedirs(DEPLOYMENT_DIR)

    # --- File Copying ---
    files_to_copy = {
        INPUT_IMAGE_PATH: "original.png",
        os.path.join(OUTPUT_DIR, "hawp_detection.png"): "hawp_detection.png",
        os.path.join(OUTPUT_DIR, "lcnn_detection.png"): "lcnn_detection.png",
        os.path.join(OUTPUT_DIR, "dsine_detection.png"): "dsine_detection.png",
        os.path.join(OUTPUT_DIR, "montage.png"): "montage.png",
    }
    for src, dest_name in files_to_copy.items():
        if os.path.exists(src):
            shutil.copy(src, os.path.join(DEPLOYMENT_DIR, dest_name))
            print(f"Copied {src} to {dest_name}")
        else:
            print(f"Warning: Source file not found, skipping: {src}")

    # --- HTML Generation ---
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Line Detection Comparison</title>
    <style>
        body { font-family: sans-serif; margin: 2em; background-color: #f8f9fa; color: #212529; }
        .container { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2em; }
        .card { background-color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .card h2 { font-size: 1.2em; padding: 1em; margin: 0; border-bottom: 1px solid #e9ecef; }
        .card img { max-width: 100%; height: auto; display: block; }
        h1 { text-align: center; margin-bottom: 2em; }
    </style>
</head>
<body>
    <h1>Line Detection Model Comparison</h1>
    <div class="container">
        <div class="card"><h2>Original Image</h2><img src="original.png" alt="Original"></div>
        <div class="card"><h2>Montage (HAWP vs L-CNN)</h2><img src="montage.png" alt="Montage"></div>
        <div class="card"><h2>HAWP Detection</h2><img src="hawp_detection.png" alt="HAWP"></div>
        <div class="card"><h2>L-CNN Detection</h2><img src="lcnn_detection.png" alt="L-CNN"></div>
        <div class="card"><h2>DSINE Detection</h2><img src="dsine_detection.png" alt="DSINE"></div>
    </div>
</body>
</html>
"""
    with open(os.path.join(DEPLOYMENT_DIR, "index.html"), "w") as f:
        f.write(html_content)
    print(f"Generated index.html in {DEPLOYMENT_DIR}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run all models
    run_hawp()
    run_lcnn()
    run_dsine()

    # Create comparison visuals
    create_montage()

    # Prepare for deployment
    prepare_for_deployment()

    print("\nComparison and deployment preparation script finished.")
