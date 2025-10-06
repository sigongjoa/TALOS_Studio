
from flask import Flask, jsonify, send_from_directory, abort
import json
import os

# 비디오 파일명 (하드코딩, 추후 확장 가능)
VIDEO_FILENAME = "boxing.mp4"
# NOTE: This assumes the output directory structure from the mediapipe script is consistent.
# e.g., output_data/boxing/boxing_smoothed_3d_keypoints.json
BASE_NAME = os.path.splitext(VIDEO_FILENAME)[0]
OUTPUT_DIR = f"output_data/{BASE_NAME}"

# 생성될 데이터 파일 경로
KEYPOINTS_FILE = f"{OUTPUT_DIR}/{BASE_NAME}_smoothed_3d_keypoints.json"
SCORE_FILE = f"{OUTPUT_DIR}/boxing_score.json"

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def index():
    """메인 index.html 페이지를 제공"""
    return send_from_directory('.', 'index.html')

@app.route('/video')
def video_file():
    """비디오 파일을 제공"""
    try:
        return send_from_directory('input_videos', VIDEO_FILENAME, as_attachment=False)
    except FileNotFoundError:
        abort(404, description=f"Video file '{VIDEO_FILENAME}' not found in 'input_videos'.")

@app.route('/api/boxing-data')
def get_boxing_data():
    """3D 키포인트와 복싱 악보 데이터를 JSON으로 제공"""
    if not os.path.exists(KEYPOINTS_FILE) or not os.path.exists(SCORE_FILE):
         abort(404, description="Data files not found. Please run the analysis pipeline first on 'boxing.mp4'.")
    
    with open(KEYPOINTS_FILE, 'r') as f:
        keypoints_data = json.load(f)
    with open(SCORE_FILE, 'r') as f:
        score_data = json.load(f)

    response_data = {
        "keypoints": keypoints_data,
        "score": score_data
    }
    return jsonify(response_data)

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Serving data for video: {VIDEO_FILENAME}")
    print(f"Keypoints file: {KEYPOINTS_FILE}")
    print(f"Score file: {SCORE_FILE}")
    app.run(host='0.0.0.0', port=5001)
