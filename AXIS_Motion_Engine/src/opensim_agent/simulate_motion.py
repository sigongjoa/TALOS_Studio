import os
import math
import opensim
from src.data_conversion.json_to_mot_converter import json_to_mot

# Mapping from LLM-generated joint names to OpenSim model joint names
JOINT_NAME_MAP = {
    # Lower Body - Left
    "hip_L_flexion": "hip_flexion_l",
    "hip_L_adduction": "hip_adduction_l",
    "hip_L_rotation": "hip_rotation_l",
    "knee_L_flexion": "knee_angle_l",
    "ankle_L_flexion": "ankle_angle_l",
    "ankle_L_inversion": "subtalar_angle_l", # Assuming subtalar for inversion/eversion
    "ankle_L_eversion": "subtalar_angle_l", # Assuming subtalar for inversion/eversion

    # Lower Body - Right
    "hip_R_flexion": "hip_flexion_r",
    "hip_R_adduction": "hip_adduction_r",
    "hip_R_rotation": "hip_rotation_r",
    "knee_R_flexion": "knee_angle_r",
    "ankle_R_flexion": "ankle_angle_r",
    "ankle_R_inversion": "subtalar_angle_r",
    "ankle_R_eversion": "subtalar_angle_r",

    # Upper Body - Left (assuming some common LLM names)
    "shoulder_L_flexion": "shoulder_flexion_l", # Placeholder, gait2392 might not have explicit shoulder coordinates
    "shoulder_L_adduction": "shoulder_adduction_l", # Placeholder
    "shoulder_L_rotation": "shoulder_rotation_l", # Placeholder
    "elbow_L_flexion": "elbow_flexion_l",
    "wrist_L_flexion": "wrist_flexion_l", # Placeholder
    "wrist_L_deviation": "wrist_deviation_l", # Placeholder

    # Upper Body - Right
    "shoulder_R_flexion": "shoulder_flexion_r", # Placeholder
    "shoulder_R_adduction": "shoulder_adduction_r", # Placeholder
    "shoulder_R_rotation": "shoulder_rotation_r", # Placeholder
    "elbow_R_flexion": "elbow_flexion_r",
    "wrist_R_flexion": "wrist_flexion_r", # Placeholder
    "wrist_R_deviation": "wrist_deviation_r", # Placeholder

    # Generic names that might come from LLM
    "hip_flexion_l": "hip_flexion_l",
    "knee_angle_l": "knee_angle_l",
    "elbow_L": "elbow_flexion_l",
    "shoulder_R": "shoulder_adduction_r",
    "left_elbow": "elbow_flexion_l",
    "right_shoulder": "shoulder_adduction_r",
    # Add more mappings as needed based on LLM output and model joints
    # Note: gait2392_simbody.osim is primarily a lower-body model.
    # Upper body mappings are illustrative and might need adjustment or a different model.
}

"""
Module for simulating motion using OpenSim.
"""

def load_opensim_model(model_path: str) -> opensim.Model:
    """
    Loads an OpenSim musculoskeletal model from a specified `.osim` file.

    Args:
        model_path (str): The absolute path to the `.osim` model file.

    Returns:
        opensim.Model: An OpenSim Model object.

    Raises:
        FileNotFoundError: If the `.osim` file does not exist.
        opensim.OpenSimException: For errors during model loading.
    """
    print(f"Loading OpenSim model from: {model_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"OpenSim model file not found: {model_path}")
    try:
        model = opensim.Model(model_path)
        print("OpenSim model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading OpenSim model: {e}")
        raise

def apply_json_to_model(model: opensim.Model, json_data: dict, state: opensim.State) -> opensim.Model:
    """
    Applies the motion parameters from the LLM-generated JSON data to the OpenSim model,
    setting target joint angles or positions.

    Args:
        model (opensim.Model): The loaded OpenSim Model object.
        json_data (dict): The validated JSON data containing motion parameters.
        state (opensim.State): The current state of the OpenSim model.

    Returns:
        opensim.Model: The modified OpenSim Model object with applied parameters.

    Raises:
        ValueError: If a specified joint or parameter is not found in the model.
    """
    print("Applying JSON data to OpenSim model...")
    for param in json_data.get("parameters", []):
        llm_joint_name = param.get("joint")
        if not llm_joint_name:
            continue

        # Map LLM joint name to OpenSim model joint name
        joint_name = JOINT_NAME_MAP.get(llm_joint_name, llm_joint_name) # Use original if not in map

        try:
            coordinate = model.updCoordinateSet().get(joint_name)
            if "target_angle_x" in param:
                coordinate.setValue(state, param["target_angle_x"] * math.pi / 180)
            if "target_angle_y" in param:
                print(f"Warning: target_angle_y provided for {llm_joint_name} (mapped to {joint_name}). For gait2392, separate coordinates like hip_adduction_l should be used for different axes of rotation.")
            if "target_angle_z" in param:
                print(f"Warning: target_angle_z provided for {llm_joint_name} (mapped to {joint_name}). For gait2392, separate coordinates like hip_rotation_l should be used for different axes of rotation.")
            print(f"Applied parameters for joint: {joint_name}")
        except Exception as e: # Catching generic Exception for mock, opensim.OpenSimException in real
            print(f"Warning: Could not apply parameter for joint {llm_joint_name} (mapped to {joint_name}): {e}")
            # raise ValueError(f"Joint {joint_name} or its parameter not found in model.")

    print("JSON data applied to model.")
    return model

def run_simulation(model: opensim.Model, json_data: dict, output_dir: str, state: opensim.State) -> str:
    """
    Executes an OpenSim simulation (e.g., Inverse Kinematics, Inverse Dynamics)
    based on the modified model and generates motion data files.

    Args:
        model (opensim.Model): The OpenSim Model object with applied motion parameters.
        json_data (dict): The validated JSON data (used for duration, specific simulation settings).
        output_dir (str): The directory where the generated motion files (`.sto`, `.trc`) will be saved.

    Returns:
        str: The path to the generated OpenSim motion file (e.g., `.sto`).

    Raises:
        opensim.OpenSimException: For errors during simulation execution.
    """
    print("Running OpenSim Inverse Kinematics simulation...")
    output_file_name = f"{json_data['action'].replace(' ', '_')}_motion.sto"
    output_file_path = os.path.join(output_dir, output_file_name)

    # Create an InverseKinematicsTool
    ik_tool = opensim.tools.InverseKinematicsTool()
    ik_tool.setModel(model.clone()) # Clone the model to avoid potential issues with modifying the original
    ik_tool.setStartTime(0)
    ik_tool.setEndTime(json_data['duration'])
    ik_tool.setOutputMotionFileName(output_file_path)
    ik_tool.setMarkerDataFileName("") # Explicitly set to empty as we are not using marker data

    # For simplicity, we'll assume the LLM output directly provides target coordinate values.
    # In a more complex scenario, you might generate a .trc file from LLM output
    # or use a custom IK solver.

    # Create an IK task set and add coordinate tasks based on LLM output
    # Get the IKTaskSet from the tool
    ik_task_set = ik_tool.getIKTaskSet()

    # Create a temporary .mot file from the JSON data to serve as coordinate input
    temp_mot_file_path = os.path.join(output_dir, "temp_ik_coordinates.mot")

    # Get coordinate names for column labels (only unlocked coordinates)
    opensim_coordinate_array = opensim.ArrayStr()
    for i in range(model.getNumCoordinates()):
        coord = model.getCoordinateSet().get(i)
        if not coord.getLocked(state):
            opensim_coordinate_array.append(coord.getName())

    # Convert opensim.ArrayStr to Python list of strings
    python_coordinate_names = [opensim_coordinate_array.get(i) for i in range(opensim_coordinate_array.getSize())]

    print(f"Total coordinates in model: {model.getNumCoordinates()}")
    print(f"Unlocked coordinates to be used for .mot file: {len(python_coordinate_names)}")
    for name in python_coordinate_names:
        print(f"  - {name}")

    # Call the new json_to_mot function
    json_to_mot(json_data, python_coordinate_names, temp_mot_file_path)

    # Update ik_tool to use the generated .mot file
    ik_tool.set_coordinate_file(temp_mot_file_path)

    print(f"Attempting to run IK with coordinate file: {temp_sto_file_path}")
    # Running the IK tool
    try:
        ik_tool.run()
        print(f"OpenSim Inverse Kinematics simulation completed. Motion data saved to: {output_file_path}")
    except opensim.OpenSimException as e:
        print(f"Error during OpenSim IK simulation: {e}")
        raise
    finally:
        # Clean up the temporary .mot file
        if os.path.exists(temp_mot_file_path):
            os.remove(temp_mot_file_path)

    return output_file_path

if __name__ == '__main__':
    model_path = "/mnt/d/progress/MotionEq/models/human_model.osim"

    test_json_data = {
        "action": "test_gait_motion",
        "duration": 3.0,
        "parameters": [
            {"joint": "hip_flexion_l", "target_angle_x": 60},
            {"joint": "knee_angle_l", "target_angle_x": 30}
        ]
    }
    output_dir = "/mnt/d/progress/MotionEq/output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        model = load_opensim_model(model_path)
        modified_model = apply_json_to_model(model, test_json_data)
        motion_file = run_simulation(modified_model, test_json_data, output_dir)
        print(f"Test completed. Generated motion file: {motion_file}")
    except (FileNotFoundError, opensim.OpenSimException, ValueError) as e:
        print(f"OpenSim agent test failed: {e}")