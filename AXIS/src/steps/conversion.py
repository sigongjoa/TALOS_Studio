# src/steps/conversion.py

import cv2
from pipeline import ProcessingStep, FrameContextBuilder

class GrayscaleConversionStep(ProcessingStep):
    """(테스트용) 원본 프레임을 흑백으로 변환하는 간단한 스텝"""
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running GrayscaleConversionStep...")
        original_frame = builder.get("original_frame")
        
        # OpenCV를 사용하여 흑백으로 변환
        grayscale_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
        
        # 빌더에 결과 추가
        builder.set("grayscale_frame", grayscale_frame)
        
        return builder
