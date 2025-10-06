
import cv2
import mediapipe as mp
import json
import os
import argparse

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def run_pose_estimation_mediapipe(video_path, output_dir, output_annotated_frames_dir=None):
    """
    Runs MediaPipe Pose on a video to extract 3D world keypoints and saves them to a JSON file.
    Also overlays the pose estimation on video frames and saves them.
    Focuses on single person tracking with MediaPipe's built-in smoothing.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        print("Warning: Could not get FPS from video. Assuming 30.")
        fps = 30

    output_data = {
        "fps": fps,
        "frames": []
    }
    frame_idx = 0

    print(f"Processing video with MediaPipe: {video_path}")

    if output_annotated_frames_dir:
        os.makedirs(output_annotated_frames_dir, exist_ok=True)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"End of video or failed to read frame at index {frame_idx}")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            frame_keypoints_3d = []
            if results.pose_world_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                for i, landmark in enumerate(results.pose_world_landmarks.landmark):
                    frame_keypoints_3d.append({
                        "name": mp_pose.PoseLandmark(i).name,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })

            output_data["frames"].append({
                "frame_index": frame_idx,
                "keypoints_3d": frame_keypoints_3d
            })
            
            if output_annotated_frames_dir:
                frame_filename = os.path.join(output_annotated_frames_dir, f'frame_{frame_idx:05d}.png')
                cv2.imwrite(frame_filename, image)

            frame_idx += 1

    cap.release()

    # The output filename is now directly specified
    with open(output_dir, 'w') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"\nMediaPipe 3D world keypoints extracted and saved to {output_dir}")
    print(f"Annotated frames saved to {output_annotated_frames_dir}")
    print(f"Total frames processed: {frame_idx}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract 3D world pose keypoints from a video using MediaPipe Pose.")
    parser.add_argument('--video_path', type=str, required=True, help="Path to the input video file.")
    parser.add_argument('--output_path', type=str, required=True, help="Full path for the output JSON file.")
    parser.add_argument('--output_annotated_frames_dir', type=str, default=None, help="Optional: Directory to save annotated image frames.")

    args = parser.parse_args()

    if args.output_annotated_frames_dir:
        os.makedirs(args.output_annotated_frames_dir, exist_ok=True)
    
    output_dir_path = os.path.dirname(args.output_path)
    if output_dir_path:
        os.makedirs(output_dir_path, exist_ok=True)

    run_pose_estimation_mediapipe(args.video_path, args.output_path, args.output_annotated_frames_dir)
