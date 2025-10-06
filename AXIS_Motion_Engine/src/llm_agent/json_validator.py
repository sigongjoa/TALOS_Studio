import json

"""
json_validator.py

This module provides functions to validate the structure and content of JSON data
received from the Large Language Model (LLM). It ensures that the LLM's output
conforms to the expected schema required for OpenSim processing, preventing
errors in subsequent simulation steps.
"""

def validate_opensim_json(json_data: dict) -> bool:
    """
    Validates the structure and data types of the JSON output received from the LLM
    to ensure it's suitable for OpenSim processing.

    Args:
        json_data (dict): The JSON data received from the LLM.

    Returns:
        bool: `True` if the JSON data is valid, `False` otherwise.
    """
    print("Validating OpenSim JSON data...")
    if not isinstance(json_data, dict):
        print("Validation Error: json_data is not a dictionary.")
        return False

    required_keys = ["action", "duration", "parameters"]
    for key in required_keys:
        if key not in json_data:
            print(f"Validation Error: Missing required key '{key}'.")
            return False

    if not isinstance(json_data["action"], str):
        print("Validation Error: 'action' must be a string.")
        return False

    if not isinstance(json_data["duration"], (int, float)) or json_data["duration"] <= 0:
        print("Validation Error: 'duration' must be a positive number.")
        return False

    if not isinstance(json_data["parameters"], list):
        print("Validation Error: 'parameters' must be a list.")
        return False

    for param in json_data["parameters"]:
        if not isinstance(param, dict):
            print("Validation Error: Each parameter entry must be a dictionary.")
            return False
        if "joint" not in param or not isinstance(param["joint"], str):
            print("Validation Error: Each parameter entry must have a 'joint' string.")
            return False
        # Further validation for target_angle_x/y/z, muscle_activation, target_position_x/y/z
        # For brevity, only basic checks are included here.
        for key in ["target_angle_x", "target_angle_y", "target_angle_z",
                    "muscle_activation",
                    "target_position_x", "target_position_y", "target_position_z"]:
            if key in param and not isinstance(param[key], (int, float)):
                print(f"Validation Error: Parameter '{key}' must be a number if present.")
                return False

    print("JSON data validated successfully.")
    return True

if __name__ == '__main__':
    valid_data = {
        "action": "test_action",
        "duration": 2.5,
        "parameters": [
            {"joint": "shoulder_L", "target_angle_x": 90, "muscle_activation": 0.7},
            {"joint": "elbow_L", "target_angle_y": 10, "muscle_activation": 0.6}
        ]
    }
    invalid_data_missing_key = {"action": "test", "duration": 1.0, "params": []}
    invalid_data_bad_type = {"action": "test", "duration": "two", "parameters": []}

    print(f"Valid data test: {validate_opensim_json(valid_data)}")
    print(f"Invalid data (missing key) test: {validate_opensim_json(invalid_data_missing_key)}")
    print(f"Invalid data (bad type) test: {validate_opensim_json(invalid_data_bad_type)}")
