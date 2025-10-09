# src/data_models.py

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import numpy as np

@dataclass(frozen=True)
class Point2D:
    """2D 공간상의 단일 점을 표현"""
    x: float
    y: float

@dataclass(frozen=True)
class Circle:
    """검출된 원을 표현"""
    center: Point2D
    radius: float

@dataclass(frozen=True)
class Triangle:
    """검출된 삼각형을 표현"""
    vertices: Tuple[Point2D, Point2D, Point2D]

@dataclass(frozen=True)
class Line3D:
    """3D 공간상의 단일 라인을 표현하는 데이터 클래스"""
    line_id: int
    layer: str
    points_3d: np.ndarray  # (N, 3) 형태의 3D 좌표 배열
    pressure: np.ndarray    # (N,) 형태의 압력 배열

@dataclass
class Line2D:
    """2D 이미지 공간상의 단일 라인을 표현하는 데이터 클래스"""
    points: np.ndarray  # (N, 2) 형태의 2D 좌표 배열

@dataclass
class Curve2D:
    """B-spline 피팅이 적용된 2D 곡선을 표현"""
    points: np.ndarray # (N, 2) 형태의 2D 좌표 배열

@dataclass(frozen=True)
class FrameContext:
    """한 프레임의 모든 처리 결과를 담는 불변 데이터 클래스"""
    frame_index: int
    original_frame: np.ndarray
    
    # 파이프라인 단계별 결과물
    edge_map: np.ndarray | None = None
    depth_map: np.ndarray | None = None
    flow_map: np.ndarray | None = None
    lines_2d: List[Line2D] | None = None # Vectorization 결과
    curves_2d: List[Curve2D] | None = None # Curve Fitting 결과
    lines: List[Line3D] | None = None
    circles: List[Circle] | None = None
    triangles: List[Triangle] | None = None
    
    # 기타 메타데이터 및 결과물
    grayscale_frame: np.ndarray | None = None # for Step 1 test
    metrics: Dict[str, float] | None = None
    extra_data: Dict[str, Any] | None = None # 유연한 데이터 저장을 위한 공간
