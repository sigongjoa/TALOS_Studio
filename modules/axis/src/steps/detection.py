# src/steps/detection.py

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..strategies.base import IEdgeDetector

class EdgeDetectionStep(ProcessingStep):
    """엣지 검출 전략을 실행하는 파이프라인 스텝"""
    def __init__(self, strategy: IEdgeDetector):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running EdgeDetectionStep...")
        original_frame = builder.get("original_frame")
        
        # 주입된 전략을 사용하여 엣지 맵 검출
        edge_map = self._strategy.detect(original_frame)
        
        # 빌더에 결과 추가
        builder.set("edge_map", edge_map)
        
        return builder
