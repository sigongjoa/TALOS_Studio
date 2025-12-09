# AXIS 모듈 코드 명세서 (Code Specification)

## 1. 개요

이 문서는 AXIS 모듈의 3D 검증 파이프라인을 구현하기 위한 구체적인 코드 구조, 클래스, 인터페이스, 그리고 데이터 모델을 정의합니다. 이 명세서는 `AXIS_Implementation_Design_Patterns.md` 문서에서 제안된 디자인 패턴을 기반으로 작성되었습니다.

## 2. 디렉토리 구조 제안

AXIS 모듈의 소스 코드는 다음과 같은 구조로 구성합니다.

```
AXIS/
├── docs/                     # 모든 기획 및 설계 문서
├── src/                      # 소스 코드 루트
│   ├── __init__.py
│   ├── data_models.py      # 핵심 데이터 클래스 (FrameContext, Line3D 등)
│   ├── pipeline.py         # Pipeline, ProcessingStep(ABC), PipelineObserver(ABC)
│   ├── steps/                # 파이프라인의 각 단계를 구현한 클래스들
│   │   ├── __init__.py
│   │   ├── detection.py      # EdgeDetectionStep
│   │   ├── estimation.py     # DepthEstimationStep, FlowEstimationStep
│   │   ├── shape_detection.py # CircleDetectionStep, TriangleDetectionStep
│   │   └── tracking.py       # LineTrackingStep
│   └── strategies/             # 교체 가능한 알고리즘(전략)들
│       ├── __init__.py
│       ├── base.py           # 전략 인터페이스 (IEdgeDetector, IDepthEstimator)
│       ├── detectors.py      # HED, DexiNed 등 엣지 검출 전략 구현체
│       └── estimators.py     # MiDaS, RAFT 등 Depth/Flow 추정 전략 구현체
└── validation_script_3d.py   # 검증 파이프라인을 실행하는 메인 스크립트
```

## 3. 핵심 데이터 모델 (`src/data_models.py`)

파이프라인을 통해 전달되고 생성되는 핵심 데이터 구조를 정의합니다.

```python
from dataclasses import dataclass
from typing import List, Tuple, Dict
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
    line_id: str
    layer: str
    points_3d: np.ndarray  # (N, 3) 형태의 3D 좌표 배열
    pressure: np.ndarray    # (N,) 형태의 압력 배열

@dataclass(frozen=True)
class FrameContext:
    """한 프레임의 모든 처리 결과를 담는 불변 데이터 클래스"""
    frame_index: int
    original_frame: np.ndarray
    edge_map: np.ndarray | None = None
    depth_map: np.ndarray | None = None
    flow_map: np.ndarray | None = None
    lines: List[Line3D] | None = None
    circles: List[Circle] | None = None
    triangles: List[Triangle] | None = None
    metrics: Dict[str, float] | None = None
```

## 4. 전략 인터페이스 및 클래스 (`src/strategies/base.py`)

전략 패턴을 위한 추상 베이스 클래스(인터페이스)를 정의합니다.

```python
from abc import ABC, abstractmethod
import numpy as np

class IEdgeDetector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> np.ndarray:
        """프레임에서 엣지 맵을 반환합니다."""
        pass

class IDepthEstimator(ABC):
    @abstractmethod
    def estimate(self, frame: np.ndarray) -> np.ndarray:
        """프레임에서 뎁스 맵을 반환합니다."""
        pass

class IOpticalFlowEstimator(ABC):
    @abstractmethod
    def estimate(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """두 프레임 간의 Optical Flow를 반환합니다."""
        pass

# 실제 구현은 `src/strategies/detectors.py` 등에 위치합니다.
# 예: class HEDDetector(IEdgeDetector): ...
```

## 5. 파이프라인 API 및 클래스 (`src/pipeline.py`)

파이프라인 패턴의 핵심 클래스들을 정의합니다.

```python
from abc import ABC, abstractmethod
from typing import List
from .data_models import FrameContext

# --- Builder Pattern ---
class FrameContextBuilder:
    def __init__(self, frame_index: int, frame: np.ndarray):
        self._context = {"frame_index": frame_index, "original_frame": frame}

    def set_edge_map(self, edge_map: np.ndarray):
        self._context["edge_map"] = edge_map
        return self

    # ... set_depth_map, set_flow_map 등 다른 setter들 ...

    def build(self) -> FrameContext:
        return FrameContext(**self._context)

# --- Pipeline Pattern ---
class ProcessingStep(ABC):
    @abstractmethod
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        """빌더를 받아 컨텍스트를 업데이트하고 다시 빌더를 반환합니다."""
        pass

# --- Observer Pattern ---
class PipelineObserver(ABC):
    @abstractmethod
    def on_frame_processed(self, context: FrameContext):
        """프레임 처리가 완료될 때 호출됩니다."""
        pass

# --- Main Pipeline Class ---
class Pipeline:
    def __init__(self, steps: List[ProcessingStep]):
        self._steps = steps
        self._observers: List[PipelineObserver] = []

    def add_observer(self, observer: PipelineObserver):
        self._observers.append(observer)

    def run(self, initial_builder: FrameContextBuilder) -> FrameContext:
        builder = initial_builder
        for step in self._steps:
            builder = step.execute(builder)
        
        final_context = builder.build()
        self._notify(final_context)
        return final_context

    def _notify(self, context: FrameContext):
        for observer in self._observers:
            observer.on_frame_processed(context)
```

## 6. 파이프라인 단계 클래스 (예: `src/steps/detection.py`)

`ProcessingStep`의 구체적인 구현 예시입니다.

```python
from ..pipeline import ProcessingStep, FrameContextBuilder
from ..strategies.base import IEdgeDetector

class EdgeDetectionStep(ProcessingStep):
    def __init__(self, strategy: IEdgeDetector):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        frame = builder._context["original_frame"] # 실제로는 getter 사용 권장
        edge_map = self._strategy.detect(frame)
        builder.set_edge_map(edge_map)
        return builder
```

## 7. 산출물 정의 (Output Definition)

AXIS는 각 프레임에 대한 작화 정보를 두 가지 형태로 출력합니다.

### 7.1. 구조화된 데이터 (JSON)

- **파일**: `scene_data.json`
- **목적**: 프론트엔드 Dope Sheet와의 연동, 개별 객체 제어, 상호작용 등 동적인 처리를 위함.
- **내용**: 모든 프레임에 대한 라인, 원, 삼각형 등의 벡터 좌표 및 속성 정보를 포함합니다.

### 7.2. 렌더링된 이미지 (PNG)

- **경로**: `output_images/frame_{frame_index:04d}/`
- **목적**: 각 검출 단계의 결과를 시각적으로 즉시 디버깅하고 확인하기 위함.
- **파일 구성**:
    - `original.png`: 원본 프레임 이미지
    - `lines.png`: 투명 배경에 검출된 라인이 그려진 이미지
    - `circles.png`: 투명 배경에 검출된 원이 그려진 이미지
    - `triangles.png`: 투명 배경에 검출된 삼각형이 그려진 이미지

```python
from AXIS.src.pipeline import Pipeline, FrameContextBuilder
from AXIS.src.steps.detection import EdgeDetectionStep
from AXIS.src.steps.estimation import DepthEstimationStep # (구현 필요)
from AXIS.src.strategies.detectors import HEDDetector     # (구현 필요)
from AXIS.src.strategies.estimators import MiDaSEstimator   # (구현 필요)
# ... other imports

def main():
    # 1. 전략(알고리즘) 선택 및 생성
    edge_detector = HEDDetector()
    depth_estimator = MiDaSEstimator()

    # 2. 파이프라인 단계 구성
    pipeline_steps = [
        EdgeDetectionStep(strategy=edge_detector),
        DepthEstimationStep(strategy=depth_estimator),
        # ... FlowEstimationStep, CircleDetectionStep, LineTrackingStep 등 추가
    ]

    # 3. 파이프라인 생성
    pipeline = Pipeline(steps=pipeline_steps)

    # 4. 옵저버 등록 (선택 사항)
    # logger = MetricsLogger()
    # pipeline.add_observer(logger)

    # 5. 비디오 프레임에 대해 파이프라인 실행
    video_capture = cv2.VideoCapture("path/to/video.mp4")
    frame_idx = 0
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # 빌더 생성
        builder = FrameContextBuilder(frame_index=frame_idx, frame=frame)
        
        # 파이프라인 실행
        processed_context = pipeline.run(builder)
        
        print(f"Frame {frame_idx} processed. SSIM: {processed_context.metrics.get('ssim')}")
        frame_idx += 1

if __name__ == "__main__":
    main()
```