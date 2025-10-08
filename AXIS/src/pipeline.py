# src/pipeline.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np
from .data_models import FrameContext

import dataclasses

# --- Builder Pattern ---
class FrameContextBuilder:
    """FrameContext 객체의 생성을 단계별로 처리하는 빌더 클래스"""
    def __init__(self, frame_index: int, original_frame: np.ndarray, prev_frame: np.ndarray | None = None):
        self._context_data: Dict[str, Any] = {
            "frame_index": frame_index,
            "original_frame": original_frame,
            "prev_frame": prev_frame
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._context_data.get(key, default)

    def set(self, key: str, value: Any):
        self._context_data[key] = value
        return self

    def build(self) -> FrameContext:
        """최종적으로 불변의 FrameContext 객체를 생성합니다."""
        # FrameContext 데이터클래스에 정의된 필드 이름만 가져옵니다.
        valid_field_names = {f.name for f in dataclasses.fields(FrameContext)}

        # 빌더의 데이터 중, FrameContext에 실제 존재하는 필드만 필터링합니다.
        filtered_data = {
            key: value
            for key, value in self._context_data.items()
            if key in valid_field_names
        }

        return FrameContext(**filtered_data)

# --- Pipeline Pattern ---
class ProcessingStep(ABC):
    """파이프라인의 각 단계를 나타내는 추상 베이스 클래스"""
    @abstractmethod
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        """빌더를 받아 컨텍스트를 업데이트하고 다시 빌더를 반환합니다."""
        pass

# --- Observer Pattern ---
class PipelineObserver(ABC):
    """파이프라인의 이벤트를 수신하는 옵저버의 추상 베이스 클래스"""
    @abstractmethod
    def on_frame_processed(self, context: FrameContext):
        """프레임 처리가 완료될 때 호출됩니다."""
        pass

# --- Main Pipeline Class ---
class Pipeline:
    """ProcessingStep들을 순차적으로 실행하는 파이프라인 실행기"""
    def __init__(self, steps: List[ProcessingStep]):
        self._steps = steps
        self._observers: List[PipelineObserver] = []

    def add_observer(self, observer: PipelineObserver):
        self._observers.append(observer)

    def run(self, initial_builder: FrameContextBuilder) -> FrameContext:
        """주어진 빌더로 파이프라인의 모든 단계를 실행합니다."""
        builder = initial_builder
        for step in self._steps:
            builder = step.execute(builder)
        
        final_context = builder.build()
        self._notify(final_context)
        return final_context

    def _notify(self, context: FrameContext):
        for observer in self._observers:
            observer.on_frame_processed(context)
