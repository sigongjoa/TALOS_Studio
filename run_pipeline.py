import argparse
import yaml
import os
import sys
import json
import shutil
import subprocess
import logging
from typing import Dict, Optional

# Setup logging with timestamps and severity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Imports for actual view synthesis logic
# These are wrapped in a try-except block to allow the script to run
# in environments where these libraries are not installed.
try:
    import torch
    from diffusers import DiffusionPipeline, EulerDiscreteScheduler
    from PIL import Image
except ImportError:
    logger.warning("One or more required libraries not found. Some functionalities will be simulated.")
 

def run_triposr_reconstruction(config: Dict, input_image_path: str, output_dir: str) -> str:
    """
    Generates a 3D model from a single image using the TripoSR script.

    Args:
        config: Configuration dictionary with model_save_format and chunk_size
        input_image_path: Path to the input image
        output_dir: Directory where output model will be saved

    Returns:
        Path to output directory

    Raises:
        FileNotFoundError: If required executable or input file not found
        subprocess.CalledProcessError: If TripoSR subprocess fails
        RuntimeError: If output validation fails
    """
    logger.info(f"Starting TripoSR 3D Reconstruction for {input_image_path}")
    logger.debug(f"Using config: {config}")

    # Validate input image exists
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found: {input_image_path}")

    # Define the absolute path to the conda environment's python executable and the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    triposr_python_executable = os.path.join(base_dir, "line_detection_comparison/TripoSR/python/bin/python")
    triposr_script_path = os.path.join(base_dir, "run_triposr.py")

    if not os.path.exists(triposr_python_executable):
        raise FileNotFoundError(
            f"TripoSR Python executable not found at {triposr_python_executable}. "
            f"Please ensure the conda environment was created correctly."
        )

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

    logger.info(f"Running TripoSR command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            check=True,
            cwd=triposr_root_dir,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        logger.info(f"TripoSR subprocess completed successfully")
        logger.debug(f"TripoSR stdout:\n{result.stdout}")
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"TripoSR reconstruction timed out after 3600 seconds. "
            f"Consider increasing timeout or reducing chunk_size."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"TripoSR reconstruction failed with return code {e.returncode}.\n"
            f"stderr: {e.stderr}\n"
            f"stdout: {e.stdout}\n"
            f"This may be due to an error in the TripoSR script or missing dependencies."
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Failed to find TripoSR executable. Ensure TripoSR conda environment is set up correctly."
        )

    # Validate output
    expected_model_path = os.path.join(output_dir, f"model.{model_format}")
    if not os.path.exists(expected_model_path):
        raise RuntimeError(
            f"TripoSR reconstruction completed but output model not found at {expected_model_path}. "
            f"Check TripoSR output directory for errors."
        )

    logger.info(f"TripoSR reconstruction output to {output_dir}")
    logger.info(f"--- Finished TripoSR 3D Reconstruction for {input_image_path} ---")
    return output_dir

def run_rendering(config: Dict, input_model_path: str, output_dir: str) -> str:
    """
    Renders a 2D image from a 3D model using Blender.

    Args:
        config: Configuration dictionary with camera_angle and output_resolution
        input_model_path: Path to the 3D model file (supports .obj, .glb, etc.)
        output_dir: Directory where rendered image will be saved

    Returns:
        Path to output directory

    Raises:
        FileNotFoundError: If Blender or model file not found
        subprocess.CalledProcessError: If Blender rendering fails
        RuntimeError: If output validation fails
    """
    logger.info(f"Starting 2D Rendering of {input_model_path}")
    logger.debug(f"Using config: {config}")

    # Validate input model exists
    if not os.path.exists(input_model_path):
        raise FileNotFoundError(f"Input 3D model not found: {input_model_path}")

    # 1. Check if Blender is available
    blender_executable = shutil.which("blender")
    if not blender_executable:
        raise FileNotFoundError(
            "Blender executable not found in PATH. "
            "Please install Blender or add it to your PATH."
        )

    # 2. Define paths and arguments
    script_path = "scripts/blender_render.py"
    if not os.path.exists(script_path):
        raise FileNotFoundError(
            f"Blender rendering script not found at {script_path}. "
            f"Ensure you are running from the project root directory."
        )

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

    logger.info(f"Running Blender command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for rendering
        )
        logger.info("Blender rendering completed successfully")
        logger.debug(f"Blender stdout:\n{result.stdout}")
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            "Blender rendering timed out after 600 seconds. "
            "Consider checking the 3D model or increasing timeout."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Blender rendering failed with return code {e.returncode}.\n"
            f"stderr: {e.stderr}\n"
            f"stdout: {e.stdout}"
        )

    # Validate output
    if not os.path.exists(output_image_path):
        raise RuntimeError(
            f"Blender rendering completed but output image not found at {output_image_path}. "
            f"Check Blender script for errors."
        )

    logger.info(f"2D Rendering output to {output_dir}")
    logger.info(f"--- Finished 2D Rendering for {input_model_path} ---")
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
    """Main pipeline orchestrator."""
    try:
        parser = argparse.ArgumentParser(description="Run the Manga to 3D PoC Pipeline.")
        parser.add_argument("--config", type=str, default="config.yml", help="Path to the configuration file.")
        parser.add_argument("--input_image", type=str, default="input/original.png", help="Path to the input original image.")
        parser.add_argument("--output_dir", type=str, default=None, help="Optional: Path to the output deployment directory. Overrides config.")

        args = parser.parse_args()

        # Validate configuration file
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Configuration file not found at {args.config}")

        try:
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Configuration file must contain a valid YAML dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

        logger.info(f"Starting PoC Pipeline with config: {args.config}")
        logger.debug(f"Configuration loaded: {config}")

        # Validate input image exists
        if not os.path.exists(args.input_image):
            raise FileNotFoundError(
                f"Input image not found at {args.input_image}. "
                f"Please provide a valid image file."
            )

        # Define output directories
        temp_dir = config.get("pipeline_temp_dir", "temp")
        output_deployment_dir = args.output_dir if args.output_dir else config.get("output_deployment_dir", "output_for_deployment")

        logger.info(f"Output will be saved to: {output_deployment_dir}")

        # --- Step 1 & 2: 3D Reconstruction with TripoSR ---
        logger.info("Running 3D Reconstruction with TripoSR")
        track_a_3d_dir = os.path.join(temp_dir, "track_a_3d")
        track_b_3d_dir = os.path.join(temp_dir, "track_b_3d")

        track_a_cfg = config.get("track_a_config", {})
        try:
            run_triposr_reconstruction(track_a_cfg.copy(), args.input_image, track_a_3d_dir)
        except Exception as e:
            logger.error(f"Track A 3D reconstruction failed: {e}")
            raise

        track_b_cfg = config.get("track_b_config", {})
        try:
            run_triposr_reconstruction(track_b_cfg.copy(), args.input_image, track_b_3d_dir)
        except Exception as e:
            logger.error(f"Track B 3D reconstruction failed: {e}")
            raise

        # --- Step 3: 2D Rendering ---
        logger.info("Running 2D Rendering")
        track_a_render_dir = os.path.join(temp_dir, "track_a_render")
        track_b_render_dir = os.path.join(temp_dir, "track_b_render")

        rendering_config = config.get("rendering_config", {})

        # Check for model files before rendering
        track_a_model = os.path.join(track_a_3d_dir, "model.glb")
        if not os.path.exists(track_a_model):
            raise FileNotFoundError(f"Expected TripoSR output model at {track_a_model}")

        track_b_model = os.path.join(track_b_3d_dir, "model.glb")
        if not os.path.exists(track_b_model):
            raise FileNotFoundError(f"Expected TripoSR output model at {track_b_model}")

        try:
            run_rendering(rendering_config.copy(), track_a_model, track_a_render_dir)
        except Exception as e:
            logger.error(f"Track A rendering failed: {e}")
            raise

        try:
            run_rendering(rendering_config.copy(), track_b_model, track_b_render_dir)
        except Exception as e:
            logger.error(f"Track B rendering failed: {e}")
            raise

        # --- Step 4: Packaging Results ---
        logger.info("Packaging Results")
        packaging_config = config.get("packaging_config", {})
        package_results(
            packaging_config.copy(),
            temp_dir,
            output_deployment_dir,
            args.input_image
        )

        logger.info("PoC Pipeline Finished Successfully!")
        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error(f"Pipeline failed: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
