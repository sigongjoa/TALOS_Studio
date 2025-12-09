import pytest
import os
import subprocess
import shutil

def test_poc_pipeline_acceptance(tmp_path):
    # Define paths relative to the project root
    project_root = os.getcwd()
    run_pipeline_script = os.path.join(project_root, "run_pipeline.py")
    config_file = os.path.join(project_root, "config.yml")
    input_image_path = os.path.join(tmp_path, "input", "original.png")
    output_deployment_dir = os.path.join(tmp_path, "output_for_deployment")

    # Create dummy input image
    os.makedirs(os.path.dirname(input_image_path), exist_ok=True)
    with open(input_image_path, "w") as f:
        f.write("DUMMY_ORIGINAL_IMAGE_DATA")

    # Ensure the config file exists for the test run
    if not os.path.exists(config_file):
        # This should ideally not happen if config.yml was created correctly
        pytest.fail(f"Config file not found: {config_file}")

    # Run the pipeline
    print(f"Running pipeline: python {run_pipeline_script} --config {config_file} --input_image {input_image_path} --output_dir {output_deployment_dir}")
    result = subprocess.run(
        ["python", run_pipeline_script, "--config", config_file, "--input_image", input_image_path, "--output_dir", output_deployment_dir],
        capture_output=True,
        text=True,
        cwd=project_root # Run from project root to ensure paths are correct
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    assert result.returncode == 0, f"Pipeline failed with error: {result.stderr}"
    assert "PoC Pipeline Finished Successfully!" in result.stdout

    # Verify final output structure based on ci_cd_deployment_plan.md
    assert os.path.exists(output_deployment_dir)
    assert os.path.exists(os.path.join(output_deployment_dir, "index.html"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_a", "model.glb"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_a", "rendered.png"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_a", "view_01.png"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_b", "model.glb"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_b", "rendered.png"))
    assert os.path.exists(os.path.join(output_deployment_dir, "track_b", "view_01.png"))

    print("Acceptance test passed: All expected output files were generated.")
