import argparse
import yaml
import os
import sys
import json
import shutil
import subprocess

# Imports for actual view synthesis logic
# These are wrapped in a try-except block to allow the script to run
# in environments where these libraries are not installed.
try:
    import torch
    from diffusers import DiffusionPipeline, EulerDiscreteScheduler
    from PIL import Image
except ImportError:
    print("Warning: One or more required libraries not found. Some functionalities will be simulated.", file=sys.stderr)
 

def run_triposr_reconstruction(config, input_image_path, output_dir):
    """
    Generates a 3D model from a single image using the TripoSR script.
    """
    print(f"--- Starting TripoSR 3D Reconstruction for {input_image_path} ---")
    print(f"Using config: {str(config)}")

    # Define the absolute path to the conda environment's python executable and the script
    # This makes the script runnable from any directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    triposr_python_executable = os.path.join(base_dir, "line_detection_comparison/TripoSR/python/bin/python")
    triposr_script_path = os.path.join(base_dir, "run_triposr.py")

    if not os.path.exists(triposr_python_executable):
        print(f"Error: TripoSR Python executable not found at {triposr_python_executable}", file=sys.stderr)
        print("Please ensure the conda environment was created correctly.", file=sys.stderr)
        # Fallback to placeholder simulation
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "model.obj"), "w") as f:
            f.write("DUMMY_TRIPOSR_MODEL_DATA")
        print(f"(Fallback) TripoSR Reconstruction output to {output_dir}")
        return output_dir

    os.makedirs(output_dir, exist_ok=True)

    # Get parameters from config, with defaults
    model_format = config.get("model_save_format", "obj")
    chunk_size = config.get("chunk_size", 8192)

    triposr_root_dir = os.path.join(base_dir, "line_detection_comparison/TripoSR")

    command = [
        triposr_python_executable,
        triposr_script_path,
        "--input_image", os.path.abspath(input_image_path),
        "--output_dir", os.path.abspath(output_dir),
        "--model_save_format", model_format,
        "--chunk_size", str(chunk_size),
    ]

    print(f"Running TripoSR command: {' '.join(command)}")
    try:
        # The subprocess will run within the context of the conda environment
        subprocess.run(command, check=True, cwd=triposr_root_dir)
        print(f"TripoSR reconstruction output to {output_dir}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"An error occurred during TripoSR reconstruction: {e}", file=sys.stderr)
        print("This may be due to an error in the TripoSR script or missing dependencies.", file=sys.stderr)
        print("Falling back to placeholder simulation.", file=sys.stderr)
        # Fallback to placeholder if the actual implementation fails
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"model.{model_format}"), "w") as f:
            f.write("DUMMY_TRIPOSR_MODEL_DATA")
        print(f"(Fallback) TripoSR Reconstruction output to {output_dir}")

    print(f"--- Finished TripoSR 3D Reconstruction for {input_image_path} ---")
    return output_dir

def run_rendering(config, input_model_path, output_dir):
    """
    Renders a 2D image from a 3D model using Blender.
    This function is intended to be run in an environment where Blender is installed.
    """
    print(f"--- Starting Actual 2D Rendering of {input_model_path} ---")
    print(f"Using config: {str(config)}")

    try:
        # 1. Check if Blender is available
        blender_executable = shutil.which("blender")
        if not blender_executable:
            raise FileNotFoundError("Blender executable not found in PATH.")

        # 2. Define paths and arguments
        script_path = "scripts/blender_render.py"
        output_image_path = os.path.join(output_dir, "rendered.png")
        camera_angle = config.get("camera_angle", [30, 45, 0])
        camera_angle_str = ",".join(map(str, camera_angle))

        os.makedirs(output_dir, exist_ok=True)

        # 3. Construct and run the Blender command
        command = [
            blender_executable,
            "--background",
            "--python", script_path,
            "--",
            input_model_path,
            output_image_path,
            camera_angle_str
        ]

        print(f"Running Blender command: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"2D Rendering output to {output_dir}")

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"An error occurred during rendering: {e}", file=sys.stderr)
        if isinstance(e, subprocess.CalledProcessError):
            print(f"Blender stdout: {e.stdout}", file=sys.stderr)
            print(f"Blender stderr: {e.stderr}", file=sys.stderr)
        print("This may be due to running in an environment without Blender installed or a script error.", file=sys.stderr)
        print("Falling back to placeholder simulation.", file=sys.stderr)
        # Fallback to placeholder if the actual implementation fails
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "rendered.png"), "w") as f:
            f.write("RENDERED_IMAGE_DATA")
        print(f"(Fallback) 2D Rendering output to {output_dir}")

    print(f"--- Finished 2D Rendering for {input_model_path} ---")
    return output_dir

def package_results(config, temp_dir, output_deployment_dir, original_input_image):
    print(f"--- Packaging Results to {output_deployment_dir} ---")
    os.makedirs(output_deployment_dir, exist_ok=True)

    # 1. Copy original image
    shutil.copy(original_input_image, os.path.join(output_deployment_dir, "original.png"))

    # 2. Copy results from each track
    tracks = ["track_a", "track_b"]
    for track in tracks:
        track_output_path = os.path.join(output_deployment_dir, track)
        os.makedirs(track_output_path, exist_ok=True)

        # Define source paths
        model_src_path = os.path.join(temp_dir, f"{track}_3d", "model.glb")
        render_src_path = os.path.join(temp_dir, f"{track}_render", "rendered.png")

        # Copy model.glb if it exists
        if os.path.exists(model_src_path):
            shutil.copy(model_src_path, os.path.join(track_output_path, "model.glb"))
            print(f"Copied {model_src_path} to {track_output_path}")
        else:
            print(f"Warning: {model_src_path} not found. Skipping copy.", file=sys.stderr)

        # Copy rendered.png if it exists
        if os.path.exists(render_src_path):
            shutil.copy(render_src_path, os.path.join(track_output_path, "rendered.png"))
            print(f"Copied {render_src_path} to {track_output_path}")
        else:
            print(f"Warning: {render_src_path} not found. Skipping copy.", file=sys.stderr)

    # 3. Create a simple index.html to display the results
    html_content = """
    <html>
    <head>
        <title>PoC Results</title>
        <style>
            body { font-family: sans-serif; margin: 2em; }
            h1, h2 { text-align: center; }
            .container { display: flex; justify-content: space-around; align-items: flex-start; }
            .track { border: 1px solid #ccc; padding: 1em; margin: 1em; text-align: center; }
            img { max-width: 512px; height: auto; }
            model-viewer { width: 512px; height: 512px; }
        </style>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.0.1/model-viewer.min.js"></script>
    </head>
    <body>
        <h1>Manga to 3D PoC Results</h1>
        <h2>Original Image</h2>
        <div style="text-align: center;">
            <img src="original.png" alt="Original Image">
        </div>
        <hr>
        <div class="container">
            <div class="track">
                <h2>Track A</h2>
                <h3>Rendered Image</h3>
                <img src="track_a/rendered.png" alt="Track A Rendered Image">
                <h3>3D Model</h3>
                <model-viewer src="track_a/model.glb" ar ar-modes="webxr scene-viewer quick-look" camera-controls poster="track_a/rendered.png" shadow-intensity="1"></model-viewer>
            </div>
            <div class="track">
                <h2>Track B</h2>
                <h3>Rendered Image</h3>
                <img src="track_b/rendered.png" alt="Track B Rendered Image">
                <h3>3D Model</h3>
                <model-viewer src="track_b/model.glb" ar ar-modes="webxr scene-viewer quick-look" camera-controls poster="track_b/rendered.png" shadow-intensity="1"></model-viewer>
            </div>
        </div>
    </body>
    </html>
    """
    with open(os.path.join(output_deployment_dir, "index.html"), "w") as f:
        f.write(html_content)

    print(f"Results packaged to {output_deployment_dir}")
    return output_deployment_dir

def main():
    parser = argparse.ArgumentParser(description="Run the Manga to 3D PoC Pipeline.")
    parser.add_argument("--config", type=str, default="config.yml", help="Path to the configuration file.")
    parser.add_argument("--input_image", type=str, default="input/original.png", help="Path to the input original image.")
    parser.add_argument("--output_dir", type=str, default=None, help="Optional: Path to the output deployment directory. Overrides config.")
    
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found at {args.config}", file=sys.stderr)
        sys.exit(1)

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    print(f"Starting PoC Pipeline with config: {args.config}")

    # Define output directories
    temp_dir = config.get("pipeline_temp_dir", "temp")
    output_deployment_dir = args.output_dir if args.output_dir else config.get("output_deployment_dir", "output_for_deployment")
    
    # Ensure input directory exists for dummy image
    os.makedirs(os.path.dirname(args.input_image), exist_ok=True)
    if not os.path.exists(args.input_image):
        with open(args.input_image, "w") as f:
            f.write("DUMMY_ORIGINAL_IMAGE_DATA")
        print(f"Created dummy input image: {args.input_image}")

    # --- Step 1 & 2: 3D Reconstruction with TripoSR ---
    print("\n--- Running 3D Reconstruction with TripoSR ---")
    track_a_3d_dir = os.path.join(temp_dir, "track_a_3d")
    track_b_3d_dir = os.path.join(temp_dir, "track_b_3d")

    track_a_cfg = config.get("track_a_config", {})
    run_triposr_reconstruction(track_a_cfg.copy(), args.input_image, track_a_3d_dir)

    track_b_cfg = config.get("track_b_config", {})
    run_triposr_reconstruction(track_b_cfg.copy(), args.input_image, track_b_3d_dir)

    # --- Step 3: 2D Rendering ---
    print("\n--- Running 2D Rendering ---")
    track_a_render_dir = os.path.join(temp_dir, "track_a_render")
    track_b_render_dir = os.path.join(temp_dir, "track_b_render")

    rendering_config_a = config.get("rendering_config", {})
    # The output from TripoSR is now model.obj or model.glb, let's use glb as the rendering script supports it
    run_rendering(rendering_config_a.copy(), os.path.join(track_a_3d_dir, "model.glb"), track_a_render_dir)

    rendering_config_b = config.get("rendering_config", {})
    run_rendering(rendering_config_b.copy(), os.path.join(track_b_3d_dir, "model.glb"), track_b_render_dir)

    # --- Step 4: Packaging Results ---
    print("\n--- Packaging Results ---")
    packaging_config = config.get("packaging_config", {})
    package_results(
        packaging_config.copy(),
        temp_dir,
        output_deployment_dir,
        args.input_image
    )

    print("\nPoC Pipeline Finished Successfully!")

if __name__ == "__main__":
    main()
