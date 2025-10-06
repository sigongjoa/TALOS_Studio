import math
import json
import os

def json_to_mot(json_data, coordinate_names, output_file, time_step=0.01):
    """
    Convert JSON motion data to OpenSim-compatible .mot file.

    Args:
        json_data (dict): JSON containing 'duration' and 'parameters'.
        coordinate_names (list[str]): Ordered coordinate names from the model.
        output_file (str): Path to save the generated .mot file.
        time_step (float): Time step between rows (default 0.01s).
    """

    duration = json_data.get("duration", 1.0)
    n_steps = int(duration / time_step) + 1

    # Build lookup of joint -> angle (degrees)
    angle_map = {}
    for param in json_data.get("parameters", []):
        joint = param.get("joint")
        angle_deg = param.get("target_angle_x")
        if joint and angle_deg is not None:
            angle_map[joint] = math.radians(angle_deg)  # convert to radians

    with open(output_file, "w") as f:
        # Write header
        f.write("name generated_motion\n")
        f.write(f"datacolumns {len(coordinate_names) + 1}\n")  # +1 for time
        f.write(f"datarows {n_steps}\n")
        f.write(f"range 0 {duration:.5f}\n")
        f.write("endheader\n")

        # Column names
        f.write("time\t" + "\t".join(coordinate_names) + "\n")

        # Data rows
        for i in range(n_steps):
            t = i * time_step
            row = [f"{t:.5f}"]

            for coord in coordinate_names:
                val = angle_map.get(coord, 0.0)
                row.append(f"{val:.6f}")
            
            f.write("\t".join(row) + "\n")