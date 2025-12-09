# AXIS_Motion_Engine (Biomechanical Simulation)

This module serves as an advanced, physics-based motion generation engine for the AXIS agent. Instead of relying on video input, it uses a biomechanical model (OpenSim) to generate physically realistic human motions from high-level text descriptions, guided by a Large Language Model (LLM).

## Feature Specification

-   **LLM-driven Motion Design:** Takes a natural language prompt (e.g., "a person walking briskly") and uses an LLM to translate it into a structured JSON object defining the target motion parameters (joint angles, duration, etc.).
-   **Biomechanical Simulation:**
    -   Utilizes the OpenSim musculoskeletal model (`human_model.osim`) to represent the human body.
    -   Applies the parameters from the LLM-generated JSON to the model's joints and coordinates.
    -   Runs an Inverse Kinematics (IK) simulation to generate a physically plausible motion that achieves the target poses.
-   **Data Conversion:**
    -   Converts the LLM's JSON output into an OpenSim-compatible `.mot` file to drive the IK simulation.
    -   (Intended) Converts the final simulation output (`.sto` file) into a `.bvh` file for use in 3D animation software like Blender.

## Code Description

-   `src/main.py`: The main orchestrator script that outlines the entire workflow from prompt to final render. It calls the various agents and converters in sequence.
-   `src/llm_agent/`: Contains modules for interacting with the LLM.
    -   `prompt_builder.py`: (Referenced in `main.py`) Constructs the detailed prompt sent to the LLM, instructing it to generate motion parameters in a specific JSON format.
    -   `llm_connector.py`: Handles the actual API call to the LLM (e.g., Ollama) and parses the JSON from its response.
    -   `json_validator.py`: (Referenced in `main.py`) Ensures the LLM's output conforms to the required structure before it's passed to the simulator.
-   `src/opensim_agent/simulate_motion.py`: The core of the simulation.
    -   `load_opensim_model`: Loads the `.osim` model file.
    -   `apply_json_to_model`: Sets the target joint angles on the loaded model based on the LLM's JSON data.
    -   `run_simulation`: Configures and runs the OpenSim Inverse Kinematics tool to generate the final motion data, saving it as a `.sto` file.
-   `src/data_conversion/`: Contains scripts for data format translation.
    -   `json_to_mot_converter.py`: A key utility that creates a `.mot` (motion) file from the LLM's JSON. This file is used to define the goals for the OpenSim IK solver.
    -   `convert_motion.py`: (Referenced in `main.py`) Intended to convert the final `.sto` simulation output into a `.bvh` file.
-   `models/`: Contains the core `human_model.osim` file and associated 3D geometry (`.vtp` files) that define the musculoskeletal model.
-   `api_specifications.md`: A markdown document detailing the intended function signatures and data flow between the different Python modules.

## System Flow

1.  **Input:** A natural language prompt (e.g., "Make the character walk") is provided to `src/main.py`.
2.  **LLM Prompting:**
    -   `prompt_builder.py` creates a detailed prompt that asks the LLM to return a JSON object describing the desired motion (e.g., target angles for `hip_flexion_l`, `knee_angle_r`, etc.).
    -   `llm_connector.py` sends this prompt to the configured LLM API.
3.  **Parameter Generation:** The LLM returns a structured JSON object. This JSON is validated by `json_validator.py`.
4.  **Motion File Generation:**
    -   `json_to_mot_converter.py` reads the LLM's JSON and creates a `.mot` file. This file describes the desired coordinate values over the duration of the animation.
5.  **OpenSim Simulation:**
    -   `simulate_motion.py` loads the `human_model.osim`.
    -   It configures an Inverse Kinematics (IK) tool, telling it to use the generated `.mot` file as the tracking goal.
    -   The IK tool runs, calculating the full-body motion required to meet the specified joint angle targets. The result is saved as a `.sto` (OpenSim Storage) file.
6.  **BVH Conversion (Intended):**
    -   `convert_motion.py` is intended to take the `.sto` file and convert it into a `.bvh` file, which is a standard format for animation.
7.  **Output:** The final output of this engine is a physically-based motion file (`.sto` and eventually `.bvh`) that represents the character's performance, ready to be applied to a 3D model in a rendering environment like Blender.
