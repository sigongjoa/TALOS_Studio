# src/steps/estimation.py

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..strategies.base import IDepthEstimator, IOpticalFlowEstimator

class DepthEstimationStep(ProcessingStep):
    """뎁스 추정 전략을 실행하는 파이프라인 스텝"""
    def __init__(self, strategy: IDepthEstimator):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running DepthEstimationStep...")
        original_frame = builder.get("original_frame")
        
        # 주입된 전략을 사용하여 뎁스 맵 추정
        depth_map = self._strategy.estimate(original_frame)
        
        # 빌더에 결과 추가
        builder.set("depth_map", depth_map)
        
        return builder

class FlowEstimationStep(ProcessingStep):
    """옵티컬 플로우 추정 전략을 실행하는 파이프라인 스텝"""
    def __init__(self, strategy: IOpticalFlowEstimator):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        print("Running FlowEstimationStep...")
        prev_frame = builder.get("prev_frame")
        original_frame = builder.get("original_frame")

        if prev_frame is not None:
            # 주입된 전략을 사용하여 옵티컬 플로우 추정
            flow_map = self._strategy.estimate(prev_frame, original_frame)
            builder.set("flow_map", flow_map)
        else:
            print("Skipping FlowEstimationStep: prev_frame is not available.")
        
        return builder
