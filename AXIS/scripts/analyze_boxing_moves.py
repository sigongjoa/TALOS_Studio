
import json
import numpy as np
import argparse

# 펀치 감지를 위한 손의 속도 임계값 (m/s)
PUNCH_VELOCITY_THRESHOLD = 0.2
# 풋워크 감지를 위한 발의 이동 거리 임계값 (meters)
FOOTWORK_DISTANCE_THRESHOLD = 0.02
# MediaPipe Pose Landmark Indices
RIGHT_HAND_INDEX = 20
LEFT_HAND_INDEX = 19
RIGHT_FOOT_INDEX = 32
LEFT_FOOT_INDEX = 31


def load_3d_keypoints(filepath):
    """3D 키포인트 JSON 파일을 로드하여 numpy 배열과 fps를 반환"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    fps = data.get('fps', 30) # fps 정보가 없으면 30으로 가정
    
    all_frames_kps = []
    for frame_data in data['frames']:
        frame_kps = []
        if frame_data['keypoints_3d']: # Check if keypoints exist for the frame
            for kp in frame_data['keypoints_3d']:
                frame_kps.append([kp['x'], kp['y'], kp['z']])
        else:
            # If no keypoints, append a placeholder of zeros (33 keypoints, 3 coords each)
            frame_kps = np.zeros((33, 3)).tolist() # Assuming 33 keypoints
        all_frames_kps.append(frame_kps)

    return np.array(all_frames_kps), fps

def analyze_moves(keypoints_3d, fps=30):
    """키포인트 시계열 데이터를 분석하여 펀치와 풋워크 이벤트를 감지"""
    score = []
    
    for frame_idx in range(1, len(keypoints_3d)):
        prev_kps = keypoints_3d[frame_idx - 1]
        curr_kps = keypoints_3d[frame_idx]
        
        # --- 펀치 감지 (오른손) ---
        rh_prev = prev_kps[RIGHT_HAND_INDEX]
        rh_curr = curr_kps[RIGHT_HAND_INDEX]
        rh_disp = rh_curr - rh_prev
        rh_dist = np.linalg.norm(rh_disp)
        rh_velocity = rh_dist * fps
        
        if rh_velocity > PUNCH_VELOCITY_THRESHOLD:
            score.append({
                "frame": frame_idx,
                "time": frame_idx / fps,
                "move_type": "punch",
                "detail": "Right Punch",
                "velocity": round(rh_velocity, 2),
                "target_joint": "RightHand",
                "direction": classify_direction(rh_disp[0], rh_disp[1], rh_disp[2])
            })

        # --- 펀치 감지 (왼손) ---
        lh_prev = prev_kps[LEFT_HAND_INDEX]
        lh_curr = curr_kps[LEFT_HAND_INDEX]
        lh_disp = lh_curr - lh_prev
        lh_dist = np.linalg.norm(lh_disp)
        lh_velocity = lh_dist * fps

        if lh_velocity > PUNCH_VELOCITY_THRESHOLD:
            score.append({
                "frame": frame_idx,
                "time": frame_idx / fps,
                "move_type": "punch",
                "detail": "Left Punch",
                "velocity": round(lh_velocity, 2),
                "target_joint": "LeftHand",
                "direction": classify_direction(lh_disp[0], lh_disp[1], lh_disp[2])
            })

        # --- 풋워크 감지 (오른발) ---
        rf_prev = prev_kps[RIGHT_FOOT_INDEX]
        rf_curr = curr_kps[RIGHT_FOOT_INDEX]
        rf_disp = rf_curr - rf_prev
        rf_dist = np.linalg.norm(rf_disp)

        if rf_dist > FOOTWORK_DISTANCE_THRESHOLD:
            score.append({
                "frame": frame_idx,
                "time": frame_idx / fps,
                "move_type": "footwork",
                "detail": "Right Step",
                "distance": round(rf_dist, 2),
                "target_joint": "RightFoot",
                "direction": classify_direction(rf_disp[0], rf_disp[1], rf_disp[2])
            })
            
        # --- 풋워크 감지 (왼발) ---
        lf_prev = prev_kps[LEFT_FOOT_INDEX]
        lf_curr = curr_kps[LEFT_FOOT_INDEX]
        lf_disp = lf_curr - lf_prev
        lf_dist = np.linalg.norm(lf_disp)

        if lf_dist > FOOTWORK_DISTANCE_THRESHOLD:
            score.append({
                "frame": frame_idx,
                "time": frame_idx / fps,
                "move_type": "footwork",
                "detail": "Left Step",
                "distance": round(lf_dist, 2),
                "target_joint": "LeftFoot",
                "direction": classify_direction(lf_disp[0], lf_disp[1], lf_disp[2])
            })

    return score

def classify_direction(dx, dy, dz, threshold=0.02):
    """3D 변위 벡터를 기반으로 움직임 방향을 분류합니다.
    threshold는 움직임이 유의미하다고 판단하는 최소 거리(미터)입니다.
    """
    direction_parts = []

    # Y-axis (Up/Down)
    if dy > threshold: direction_parts.append("Up")
    elif dy < -threshold: direction_parts.append("Down")

    # X-axis (Left/Right - 상대적 방향이므로 카메라 기준)
    # MediaPipe의 X축은 일반적으로 오른쪽이 양수
    if dx > threshold: direction_parts.append("Right")
    elif dx < -threshold: direction_parts.append("Left")

    # Z-axis (Forward/Backward - 깊이)
    # MediaPipe의 Z축은 일반적으로 카메라에서 멀어지는 방향이 양수
    if dz > threshold: direction_parts.append("Backward")
    elif dz < -threshold: direction_parts.append("Forward")

    if not direction_parts:
        return "Static"
    return "-".join(direction_parts)

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Analyze boxing moves from 3D keypoints.")
    parser.add_argument("input_path", type=str, help="Path to the smoothed 3d keypoints JSON file.")
    parser.add_argument("output_path", type=str, help="Path to save the boxing score JSON file.")
    args = parser.parse_args()

    print(f"PUNCH_VELOCITY_THRESHOLD: {PUNCH_VELOCITY_THRESHOLD}")
    print(f"FOOTWORK_DISTANCE_THRESHOLD: {FOOTWORK_DISTANCE_THRESHOLD}")

    keypoints, fps = load_3d_keypoints(args.input_path)
    boxing_score = analyze_moves(keypoints, fps)

    with open(args.output_path, 'w') as f:
        json.dump(boxing_score, f, indent=2)
    print(f"Boxing score with {len(boxing_score)} events saved to {args.output_path}")

if __name__ == "__main__":
    main()
