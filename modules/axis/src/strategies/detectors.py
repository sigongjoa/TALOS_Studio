# src/strategies/detectors.py

import torch
import numpy as np
import cv2
from .base import IEdgeDetector

# PiDiNet 유틸리티 함수 (모델 저장소에서 가져옴)
def pidinet_bsd_val(image, mean, std):
    image = image.astype(np.float32)
    image -= mean
    image /= std
    return image

# class PiDiNetDetector(IEdgeDetector):
#     """PiDiNet 모델을 사용하여 엣지를 검출하는 전략 클래스"""
#     def __init__(self):
#         print("Loading PiDiNet model...")
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         # PyTorch Hub에서 모델 로드
#         self.model = torch.hub.load("hello-world-bytes/pidinet-pytorch", "pidinet_bsds", pretrained=True).to(self.device)
#         self.model.eval()
#         print("PiDiNet model loaded.")

#     def detect(self, frame: np.ndarray) -> np.ndarray:
#         # 모델 입력에 맞게 이미지 전처리
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image_pidi = pidinet_bsd_val(image, [103.939, 116.779, 123.68], [1., 1., 1.])
#         image_pidi = torch.from_numpy(image_pidi).permute(2, 0, 1).unsqueeze(0).to(self.device)

#         # 모델 추론
#         with torch.no_grad():
#             edge_map = self.model(image_pidi)[-1]
        
#         # 결과를 0-255 범위의 numpy 배열로 변환
#         edge_map = edge_map.cpu().numpy().squeeze()
#         edge_map = (edge_map * 255).astype(np.uint8)
        
#         return edge_map

class CannyDetector(IEdgeDetector):
    """OpenCV Canny 엣지 검출기를 사용하는 전략 클래스"""
    def __init__(self, threshold1: int = 100, threshold2: int = 200):
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        print(f"CannyDetector initialized with thresholds: {threshold1}, {threshold2}")

    def detect(self, frame: np.ndarray) -> np.ndarray:
        print("Running CannyDetector...")
        # Canny는 그레이스케일 이미지를 입력으로 받음
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge_map = cv2.Canny(gray_frame, self.threshold1, self.threshold2)
        return edge_map