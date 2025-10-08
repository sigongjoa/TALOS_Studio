# src/strategies/base.py

from abc import ABC, abstractmethod
import numpy as np

class IEdgeDetector(ABC):
    """엣지 검출 전략에 대한 인터페이스"""
    @abstractmethod
    def detect(self, frame: np.ndarray) -> np.ndarray:
        """프레임에서 엣지 맵을 반환합니다."""
        pass

class IDepthEstimator(ABC):
    """뎁스 추정 전략에 대한 인터페이스"""
    @abstractmethod
    def estimate(self, frame: np.ndarray) -> np.ndarray:
        """프레임에서 뎁스 맵을 반환합니다."""
        pass

class IOpticalFlowEstimator(ABC):
    """옵티컬 플로우 추정 전략에 대한 인터페이스"""
    @abstractmethod
    def estimate(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """두 프레임 간의 옵티컬 플로우를 반환합니다."""
        pass
