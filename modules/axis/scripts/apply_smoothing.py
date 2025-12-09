import json
import os
import numpy as np
import argparse
from smoothing_utils import moving_average_filter, savgol_filtering, OneEuroFilter

def apply_filter_to_frames(frames, method="moving_average", window_size=5, window_length=11, polyorder=2):
    if not frames:
        return []

    # Assuming single person tracking for this application
    # Convert list of dicts to a numpy array for easier processing
    keypoints_list = []
    for frame in frames:
        if frame['keypoints_3d']:
            # Create a (33, 3) array for each frame from the x, y, z values
            frame_kps = np.array([[kp['x'], kp['y'], kp['z']] for kp in frame['keypoints_3d']])
            keypoints_list.append(frame_kps)
        else:
            # Append zeros if no keypoints in a frame
            keypoints_list.append(np.zeros((33, 3))) # Assuming 33 keypoints
    
    keypoints_array = np.array(keypoints_list)

    # Apply the selected filter
    if method == "moving_average":
        smoothed_array = moving_average_filter(keypoints_array, window_size=window_size)
    elif method == "savgol":
        smoothed_array = savgol_filtering(keypoints_array, window_length=window_length, polyorder=polyorder)
    elif method == "one_euro":
        original_shape = keypoints_array.shape
        flattened_keypoints = keypoints_array.reshape(original_shape[0], -1)
        euro_filters = [OneEuroFilter(freq=30, min_cutoff=1.0, beta=0.01) for _ in range(flattened_keypoints.shape[1])]
        smoothed_flattened = np.zeros_like(flattened_keypoints)
        for i in range(flattened_keypoints.shape[0]):
            for j in range(flattened_keypoints.shape[1]):
                smoothed_flattened[i, j] = euro_filters[j](flattened_keypoints[i, j])
        smoothed_array = smoothed_flattened.reshape(original_shape)
    else: # "none"
        smoothed_array = keypoints_array

    # Reconstruct the frames with the smoothed data
    new_frames = []
    for i, frame in enumerate(frames):
        new_frame = {
            "frame_index": frame["frame_index"],
            "keypoints_3d": []
        }
        # If there were keypoints in the original frame, populate the smoothed ones
        if frame['keypoints_3d']:
            for kp_idx, original_kp in enumerate(frame['keypoints_3d']):
                new_frame["keypoints_3d"].append({
                    "name": original_kp['name'],
                    "x": smoothed_array[i, kp_idx, 0],
                    "y": smoothed_array[i, kp_idx, 1],
                    "z": smoothed_array[i, kp_idx, 2],
                    "visibility": original_kp['visibility']
                })
        new_frames.append(new_frame)
    
    return new_frames

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply temporal smoothing to 3D pose keypoints.")
    parser.add_argument('--input_path', type=str, required=True, help="Path to the input 3D keypoints JSON file.")
    parser.add_argument('--output_path', type=str, required=True, help="Full path for the output smoothed 3D keypoints JSON file.")
    parser.add_argument('--method', type=str, default="moving_average",
                        choices=["moving_average", "savgol", "one_euro", "none"], help="Smoothing method to apply.")
    parser.add_argument('--window_size', type=int, default=5, help="Window size for moving_average filter.")
    parser.add_argument('--window_length', type=int, default=11, help="Window length for savgol filter.")
    parser.add_argument('--polyorder', type=int, default=2, help="Polynomial order for savgol filter.")

    args = parser.parse_args()

    # Load the input JSON data
    with open(args.input_path, "r") as f:
        data = json.load(f)

    # Apply the selected filter
    smoothed_frames = apply_filter_to_frames(data["frames"], method=args.method,
                                             window_size=args.window_size,
                                             window_length=args.window_length,
                                             polyorder=args.polyorder)
    
    output_data = {
        "fps": data["fps"],
        "frames": smoothed_frames
    }

    # Save the smoothed data
    with open(args.output_path, 'w') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"3D keypoints smoothed using {args.method} method and saved to {args.output_path}")