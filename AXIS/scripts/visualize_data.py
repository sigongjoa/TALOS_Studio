import json
import os
import argparse
import cv2
import numpy as np

# YOLOv8 17-keypoint definition
# 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear,
# 5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow,
# 9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip,
# 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle

SKELETON_EDGES = np.array([
    [0, 1],   # nose to left_eye
    [0, 2],   # nose to right_eye
    [1, 3],   # left_eye to left_ear
    [2, 4],   # right_eye to right_ear
    [5, 6],   # left_shoulder to right_shoulder (torso)
    [5, 7],   # left_shoulder to left_elbow
    [7, 9],   # left_elbow to left_wrist
    [6, 8],   # right_shoulder to right_elbow
    [8, 10],  # right_elbow to right_wrist
    [5, 11],  # left_shoulder to left_hip (torso)
    [6, 12],  # right_shoulder to right_hip (torso)
    [11, 12], # left_hip to right_hip (pelvis)
    [11, 13], # left_hip to left_knee
    [13, 15], # left_knee to left_ankle
    [12, 14], # right_hip to right_knee
    [14, 16]  # right_knee to right_ankle
])

def project_3d_to_2d(poses_3d, R, t, fx):
    """Projects 3D points to 2D image coordinates."""
    poses_2d_projected = []
    for pose_3d in poses_3d:
        # Apply camera extrinsics
        pose_3d_cam = np.dot(R, pose_3d.T - t).T
        
        # Project to 2D
        x_2d = (pose_3d_cam[:, 0] / pose_3d_cam[:, 2]) * fx + (1280 / 2) # Adjust for a 1280x720 canvas
        y_2d = (pose_3d_cam[:, 1] / pose_3d_cam[:, 2]) * fx + (720 / 2)
        
        poses_2d_projected.append(np.vstack((x_2d, y_2d)).T)
    return poses_2d_projected

def draw_skeleton(frame, keypoints, edges, color=(0, 255, 0)):
    """Draws a skeleton on a given frame."""
    for edge in edges:
        p1 = tuple(keypoints[edge[0]].astype(int))
        p2 = tuple(keypoints[edge[1]].astype(int))
        
        # Check if points are valid (not -1)
        if p1[0] == -1 or p1[1] == -1 or p2[0] == -1 or p2[1] == -1:
            continue
        
        cv2.line(frame, p1, p2, color, 2, cv2.LINE_AA)
    
    for i, kp in enumerate(keypoints):
        pt = tuple(kp.astype(int))
        if pt[0] == -1 or pt[1] == -1:
            continue
        cv2.circle(frame, pt, 3, color, -1)

def main():
    parser = argparse.ArgumentParser(description="Create 2D and 3D keypoint overlay videos and logs.")
    parser.add_argument('--video', type=str, required=True, help="Path to the original video file.")
    parser.add_argument('--json', type=str, required=True, help="Path to the JSON file with 2D and 3D keypoints.")
    parser.add_argument('--extrinsics', type=str, default='models/lightweight-human-pose-estimation-3d-demo/data/extrinsics.json', help="Path to camera extrinsics file.")
    parser.add_argument('--fx', type=np.float32, default=1000.0, help='Camera focal length.') # A more reasonable default
    parser.add_argument('--output_dir', type=str, default='output_data', help="Directory to save the output files.")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # --- Load Data ---
    with open(args.json, 'r') as f:
        all_frames_data = json.load(f)
    
    with open(args.extrinsics, 'r') as f:
        extrinsics = json.load(f)
    R = np.array(extrinsics['R'], dtype=np.float32)
    t = np.array(extrinsics['t'], dtype=np.float32).reshape((3, 1))

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file {args.video}")

    # --- Setup Outputs ---
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video_2d_out = cv2.VideoWriter(os.path.join(args.output_dir, 'video_2d_overlay.mp4'), fourcc, fps, (width, height))
    video_3d_out = cv2.VideoWriter(os.path.join(args.output_dir, 'video_3d_overlay.mp4'), fourcc, fps, (width, height))

    log_2d = open(os.path.join(args.output_dir, '2d_keypoints.txt'), 'w')
    log_3d = open(os.path.join(args.output_dir, '3d_keypoints.txt'), 'w')

    # --- Main Loop ---
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx >= len(all_frames_data):
            print(f"Warning: Video has more frames ({frame_idx}) than JSON data ({len(all_frames_data)}). Stopping.")
            break

        frame_data = all_frames_data[frame_idx]
        poses_2d = np.array(frame_data['keypoints_2d'])
        poses_3d = np.array(frame_data['keypoints_3d'])

        frame_2d_overlay = frame.copy()
        frame_3d_overlay = frame.copy()

        # --- 2D Visualization and Logging ---
        log_2d.write(f'--- Frame {frame_idx} ---\n')
        for i, person_2d in enumerate(poses_2d):
            log_2d.write(f'Person {i}:\n{np.array2string(person_2d)}\n')
            # The 2D pose array has a confidence score at the end, so we slice it off.
            keypoints_data_2d = person_2d[:17*3]
            keypoints_2d = keypoints_data_2d.reshape((17, 3))[:, :2] # Take only x, y
            draw_skeleton(frame_2d_overlay, keypoints_2d, SKELETON_EDGES, color=(0, 255, 0))

        # --- 3D Visualization and Logging ---
        log_3d.write(f'--- Frame {frame_idx} ---\n')
        if poses_3d.size > 0:
            # The 3D pose array from the JSON is flat (51 elements), reshape to (17, 3).
            poses_3d_reshaped = [p.reshape(17, 4)[:, :3] for p in poses_3d]
            log_3d.write(f'{np.array2string(np.array(poses_3d_reshaped))}\n')
            
            # Project 3D points to 2D for overlay
            projected_poses_2d = project_3d_to_2d(poses_3d_reshaped, R, t, args.fx)
            for person_projected_2d in projected_poses_2d:
                draw_skeleton(frame_3d_overlay, person_projected_2d, SKELETON_EDGES, color=(0, 0, 255))

        video_2d_out.write(frame_2d_overlay)
        video_3d_out.write(frame_3d_overlay)

        print(f'Processed frame {frame_idx}', end='\r')
        frame_idx += 1

    # --- Cleanup ---
    print("\nDone. Releasing resources.")
    cap.release()
    video_2d_out.release()
    video_3d_out.release()
    log_2d.close()
    log_3d.close()

if __name__ == "__main__":
    main()