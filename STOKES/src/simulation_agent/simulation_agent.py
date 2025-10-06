import json
import os

class SimulationAgent:
    def __init__(self):
        """
        Initializes the SimulationAgent.
        In a real scenario, this might involve setting up a simulation engine.
        """
        pass

    def run_simulation(self, parameters: dict, formula: str, output_dir: str = "outputs/fluid_data") -> str:
        """
        Runs a fluid simulation based on the provided parameters and formula.

        Args:
            parameters: A dictionary of simulation parameters.
            formula: The mathematical formula guiding the simulation.
            output_dir: The directory to save the simulation data.

        Returns:
            The absolute path to the generated simulation data file.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Placeholder for actual Navier-Stokes based fluid simulation
        print(f"Simulating fluid dynamics with parameters: {parameters} and formula: {formula}")

        simulation_data = {
            "simulation_type": parameters.get("type", "default"),
            "formula_used": formula,
            "frames": []
        }

        # Generate some dummy frame data
        for i in range(10): # 10 frames
            frame_data = {
                "frame_number": i,
                "particles": [
                    {"id": 1, "x": i * 0.1, "y": 0.5, "z": 0.0, "velocity": [0.1, 0, 0]},
                    {"id": 2, "x": 0.5, "y": i * 0.1, "z": 0.0, "velocity": [0, 0.1, 0]}
                ],
                "metadata": {
                    "time": i * 0.1,
                    "description": f"Frame {i} data based on {formula}"
                }
            }
            simulation_data["frames"].append(frame_data)

        output_file_path = os.path.join(output_dir, "simulation_data.json")
        with open(output_file_path, "w") as f:
            json.dump(simulation_data, f, indent=4)
        
        print(f"Simulation data saved to: {output_file_path}")
        return output_file_path
