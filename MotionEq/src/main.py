import os
import subprocess
import json

from src.llm_agent.prompt_builder import build_llm_prompt
from src.llm_agent.llm_connector import call_llm_api
from src.llm_agent.json_validator import validate_opensim_json
from src.opensim_agent.simulate_motion import load_opensim_model, apply_json_to_model, run_simulation
from src.data_conversion.convert_motion import convert_opensim_to_bvh
# from src.blender_automation.apply_motion_and_render import automate_blender # This runs inside Blender

"""
main.py

This script serves as the central orchestrator for the MotionEq workflow.
It integrates various components (LLM Agent, OpenSim Agent, Data Conversion, Blender Automation)
to transform natural language motion requests into animated video outputs.

The workflow proceeds through several phases:
1.  **LLM Agent:** Generates structured motion data from natural language input.
2.  **OpenSim Agent:** Simulates human motion based on the structured data using OpenSim.
3.  **Data Conversion:** Converts OpenSim motion data to a format usable by Blender (BVH).
4.  **Blender Automation:** Renders the animated motion into a video file.

This script primarily calls functions from other modules, managing the data flow
and error handling across the entire pipeline.
"""

def main(user_input_text: str) -> str:
    """
    Orchestrates the entire workflow from user input to final video rendering,
    calling functions from other modules.

    Args:
        user_input_text (str): The natural language description of the desired motion.

    Returns:
        str: The path to the final rendered video file.

    Raises:
        Various exceptions from sub-modules, propagated up.
    """
    print(f"Starting MotionEq workflow for: '{user_input_text}'")

    # --- Phase 1: LLM Agent ---
    print("Phase 1: LLM Agent - Generating structured motion data...")
    llm_response_json = {
        "action": "walk",
        "duration": 1.0,
        "parameters": [
            {"joint": "hip_flexion_l", "target_angle_x": 10},
            {"joint": "hip_flexion_r", "target_angle_x": -10},
            {"joint": "knee_angle_l", "target_angle_x": -20},
            {"joint": "knee_angle_r", "target_angle_x": 0},
            {"joint": "ankle_angle_l", "target_angle_x": 10},
            {"joint": "ankle_angle_r", "target_angle_x": -10}
        ]
    }

    if not validate_opensim_json(llm_response_json):
        raise ValueError("LLM response JSON is invalid.")
    print("LLM response validated.")

    # --- Phase 2: OpenSim Agent ---
    print("Phase 2: OpenSim Agent - Simulating motion...")
    opensim_model_path = os.path.join(os.getcwd(), "models", "human_model.osim")
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)


    model = load_opensim_model(opensim_model_path)
    state = model.initSystem() # Initialize state here
    modified_model = apply_json_to_model(model, llm_response_json, state)
    opensim_motion_file = run_simulation(modified_model, llm_response_json, output_dir, state)
    print(f"OpenSim motion file generated: {opensim_motion_file}")

    # --- Phase 3: Data Conversion ---
    print("Phase 3: Data Conversion - Converting OpenSim motion to BVH...")
    bvh_output_path = os.path.join(output_dir, os.path.basename(opensim_motion_file).replace(".sto", ".bvh"))
    # Placeholder joint mapping - this needs to be carefully defined
    joint_mapping = {"shoulder_L": "LeftArm", "elbow_L": "LeftForeArm"}
    converted_bvh_file = convert_opensim_to_bvh(opensim_motion_file, bvh_output_path, joint_mapping)
    print(f"Converted BVH file: {converted_bvh_file}")

    # --- Phase 3 (cont.): Blender Automation ---
    print("Phase 3: Blender Automation - Rendering animation...")
    blender_scene_path = os.path.join(os.getcwd(), "models", "dummy_character.blend") # Placeholder
    final_video_path = os.path.join(output_dir, "rendered_animation.mp4")

    blender_command = [
        "blender",
        "--background",
        blender_scene_path,
        "--python",
        os.path.join(os.getcwd(), "src", "blender_automation", "apply_motion_and_render.py"),
        "--", # Separator for script arguments
        blender_scene_path,
        converted_bvh_file,
        final_video_path
    ]
    try:
        subprocess.run(blender_command, check=True)
        print("Blender rendering command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Blender rendering failed: {e}")
        raise RuntimeError("Blender rendering failed.")

    print("MotionEq workflow completed successfully.")
    return final_video_path

if __name__ == '__main__':
    test_user_input = "캐릭터가 걷는 동작을 만들어줘."
    try:
        final_output = main(test_user_input)
        print(f"\nFinal output video path: {final_output}")
    except Exception as e:
        print(f"Workflow failed: {e}")
