# src/strategies/estimators.py

import torch
import numpy as np
import cv2
from .base import IDepthEstimator, IOpticalFlowEstimator

class MiDaSEstimator(IDepthEstimator):
    """MiDaS 모델을 사용하여 뎁스를 추정하는 전략 클래스"""
    def __init__(self, model_type="MiDaS_small"):
        print(f"Loading MiDaS model ({model_type})...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # PyTorch Hub에서 MiDaS 모델 로드
        # trust_repo=True로 설정하여 비대화형 환경에서 모델 다운로드 허용
        self.model = torch.hub.load("intel-isl/MiDaS", model_type, pretrained=True, trust_repo=True).to(self.device)
        self.model.eval()
        print("MiDaS model loaded.")

        # 모델에 맞는 Transform 로드
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        self.transform = midas_transforms.small_transform if model_type == "MiDaS_small" else midas_transforms.dpt_transform

    def estimate(self, frame: np.ndarray) -> np.ndarray:
        print("Running MiDaSEstimator...")
        # 입력 프레임을 모델에 맞게 변환
        # MiDaS는 RGB 이미지를 기대하므로 BGR -> RGB 변환
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img_rgb).to(self.device)

        # 뎁스 추정 실행
        with torch.no_grad():
            prediction = self.model(input_batch)

            # 원본 이미지 크기로 스케일 조정
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        # 결과를 numpy 배열로 변환하여 반환
        depth_map = prediction.cpu().numpy()
        
        # 뎁스 맵 정규화 (시각화를 위해 0-255 범위로)
        depth_map = cv2.normalize(depth_map, None, 255,0, cv2.NORM_MINMAX, cv2.CV_8U)
        
        return depth_map

# RAFTEstimator는 Step 4에서 구현 예정
import torchvision.models.optical_flow as optical_flow

# ... (MiDaSEstimator code remains the same) ...

class RAFTEstimator(IOpticalFlowEstimator):
    def __init__(self, model_name="raft_large"):
        print(f"Loading RAFT model ({model_name}) from torchvision...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # torchvision에서 RAFT 모델 로드 (더 안정적인 방법)
        if model_name == "raft_large":
            self.model = optical_flow.raft_large(weights='DEFAULT').to(self.device)
        else:
            # raft_small도 동일한 방식으로 로드 가능
            self.model = optical_flow.raft_small(weights='DEFAULT').to(self.device)
        
        self.model.eval()
        print("RAFT model loaded.")

    def _preprocess(self, frame: np.ndarray) -> torch.Tensor:
        # RAFT는 BGR 이미지를 RGB로 변환하고 [0, 255] 범위의 Tensor를 기대함
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float()
        return tensor.to(self.device)

    def estimate(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        print("Running RAFTEstimator...")
        
        # 프레임 전처리
        img1 = self._preprocess(frame1).unsqueeze(0)
        img2 = self._preprocess(frame2).unsqueeze(0)

        # Optical Flow 추정 실행
        with torch.no_grad():
            # torchvision의 RAFT 모델은 이미지 2개만 인자로 받습니다.
            # 출력은 flow 예측값의 리스트이며, 마지막 요소가 최종 결과입니다.
            list_of_flows = self.model(img1, img2)
            flow_up = list_of_flows[-1]

        # 결과를 numpy 배열로 변환
        flow_map = flow_up[0].permute(1, 2, 0).cpu().numpy()
        return flow_map
