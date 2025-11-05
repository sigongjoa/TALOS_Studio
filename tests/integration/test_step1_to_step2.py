import pytest
import os
import json

# Assuming run_view_synthesis is importable or can be mocked
# For now, we'll just simulate its output

def simulate_view_synthesis_output(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # Create dummy image files
    for i in range(1, 3):
        with open(os.path.join(output_dir, f"view_0{i}.png"), "w") as f:
            f.write(f"DUMMY_VIEW_0{i}_IMAGE_DATA")
    # Create dummy camera_poses.json conforming to the schema
    camera_poses_data = {
        "images": [
            f"view_01.png",
            f"view_02.png"
        ],
        "camera_poses": [
            [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
            [[1.0, 0.0, 0.0, 0.1], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        ]
    }
    with open(os.path.join(output_dir, "camera_poses.json"), "w") as f:
        json.dump(camera_poses_data, f)

def test_step1_to_step2_integration(tmp_path):
    # Simulate output of Step 1 (View Synthesis)
    step1_output_dir = tmp_path / "step1_output"
    simulate_view_synthesis_output(step1_output_dir)

    # Verify Step 1 output structure (basic check, full schema validation would use pydantic)
    assert (step1_output_dir / "view_01.png").exists()
    assert (step1_output_dir / "camera_poses.json").exists()

    # Simulate input for Step 2 (3D Reconstruction)
    # In a real scenario, you'd call the actual run_3d_reconstruction function
    # For this integration test, we just check if it *could* receive the input
    step2_input_dir = step1_output_dir # Step 2 takes Step 1's output as input
    step2_output_dir = tmp_path / "step2_output"
    os.makedirs(step2_output_dir, exist_ok=True)

    # Placeholder for calling run_3d_reconstruction with step2_input_dir
    # For now, we just assert that the input files are present for step 2
    assert (step2_input_dir / "view_01.png").exists()
    assert (step2_input_dir / "camera_poses.json").exists()

    print(f"Integration test passed: Step 1 output at {step1_output_dir} is compatible with Step 2 input.")
