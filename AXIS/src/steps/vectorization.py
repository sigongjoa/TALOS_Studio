# src/steps/vectorization.py

import cv2
import numpy as np
from typing import List

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Line2D

class LineVectorizationStep(ProcessingStep):
    """엣지 맵을 벡터 라인(Line2D)의 리스트로 변환하는 파이프라인 스텝"""
    def __init__(self, min_contour_length: int = 10, epsilon_ratio: float = 0.005):
        """
        Args:
            min_contour_length: 최소 길이 이하의 컨투어는 노이즈로 간주하고 무시합니다.
            epsilon_ratio: 컨투어 근사화(단순화)에 사용될 epsilon 값의 비율입니다.
        """
        self.min_contour_length = min_contour_length
        self.epsilon_ratio = epsilon_ratio

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running LineVectorizationStep...")
        edge_map = builder.get("edge_map")

        if edge_map is None:
            print("Skipping LineVectorizationStep: edge_map is not available.")
            return builder

        # 1. 외곽선 찾기 (Contour Finding)
        contours, _ = cv2.findContours(edge_map, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        vectorized_lines: List[Line2D] = []
        for contour in contours:
            # 2. 너무 짧은 컨투어는 노이즈로 간주하여 필터링
            if len(contour) < self.min_contour_length:
                continue

            # 3. 외곽선 근사화 (Contour Approximation) - Douglas-Peucker 알고리즘
            epsilon = self.epsilon_ratio * cv2.arcLength(contour, True)
            simplified_contour = cv2.approxPolyDP(contour, epsilon, False) # False: open contour
            
            # OpenCV의 (1, N, 2) 형태를 (N, 2) 형태로 변경
            points = simplified_contour.squeeze(axis=1)
            
            vectorized_lines.append(Line2D(points=points))
        
        print(f"Vectorized {len(vectorized_lines)} lines.")
        builder.set("lines_2d", vectorized_lines)
        
        return builder
