# AXIS Pseudocode 구현 계획서

## 1. 개요

이 문서는 `AXIS_Code_Specification.md`에 정의된 클래스와 인터페이스를 실제 코드로 구현하기 위한 상세한 의사코드(Pseudocode)와 라이브러리 명세를 제공합니다. 개발자는 이 문서를 최종 청사진으로 삼아 실제 Python 코드 작성을 시작할 수 있습니다.

## 2. 핵심 라이브러리 및 버전

AXIS 모듈의 3D 검증 파이프라인은 다음 라이브러리를 기반으로 구현합니다.

```toml
# pyproject.toml 또는 requirements.txt

# 기본 및 수치 연산
python = "3.10"
numpy = "1.24.3"
opencv-python = "4.8.0"      # 비디오 I/O 및 기본 CV 연산
scikit-image = "0.21.0"     # SSIM 등 메트릭 계산용

# 딥러닝 모델 (PyTorch 기반)
torch = "2.0.1"
torchvision = "0.15.2"
timm = "0.9.7"               # MiDaS 모델 로딩 시 필요할 수 있음

# 벡터화 (선택 사항)
# pypotrace 또는 skan 등 비트맵 벡터화 라이브러리

# API 서버 (모듈 통합 시)
fastapi = "0.103.1"
uvicorn = "0.23.2"
```

## 3. 모듈 간 호환성 및 데이터 규약

- **참조 문서**: `TALOS_Inter-Module_Communication_Protocol.md`
- **입력 (Trigger)**: `Orchestrator`가 AXIS의 `POST /generate` 엔드포인트를 호출하며, Request Body에는 `job_id`, `cut_spec_url`, `video_source_url`이 포함됩니다.
- **출력 (Callback)**: 작업 완료 후, AXIS는 `Orchestrator`의 `POST /callbacks/job-completed` 엔드포인트를 호출하며, Body에는 `job_id`, `module_name`, `status`, `output_url`(`lines.json`의 위치)을 포함하여 전달합니다.

## 4. Pseudocode 구현

### 4.1. 전략 구현체 (`src/strategies/`)

**`estimators.py` - MiDaSEstimator**
```python
import torch
import numpy as np
from .base import IDepthEstimator

class MiDaSEstimator(IDepthEstimator):
    def __init__(self, model_type="MiDaS_small"):
        # 1. MiDaS 모델 로드 (torch.hub 사용)
        self.model = torch.hub.load("intel-isl/MiDaS", model_type)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        # 2. 모델에 맞는 Transform 로드
        transform = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = transform.small_transform if model_type == "MiDaS_small" else transform.dpt_transform

    def estimate(self, frame: np.ndarray) -> np.ndarray:
        # 1. 입력 프레임을 모델에 맞게 변환
        input_batch = self.transform(frame).to(self.device)

        # 2. 뎁스 추정 실행
        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        # 3. 결과를 numpy 배열로 변환하여 반환
        depth_map = prediction.cpu().numpy()
        return depth_map
```

**`detectors.py` - HEDDetector (예시)**
```python
import cv2
import numpy as np
from .base import IEdgeDetector

class HEDDetector(IEdgeDetector):
    def __init__(self, proto_path, model_path):
        # OpenCV의 DNN 모듈을 사용하여 Caffe 모델 로드
        self.net = cv2.dnn.readNetFromCaffe(proto_path, model_path)

    def detect(self, frame: np.ndarray) -> np.ndarray:
        # HED 모델에 맞는 전처리 및 추론 수행
        # ... (blob 생성, forward pass, 후처리)
        # 최종적으로 0-255 범위의 엣지 맵(grayscale) 반환
        pass
```

### 4.2. 파이프라인 단계 구현 (`src/steps/`)

**`estimation.py` - DepthEstimationStep**
```python
from ..pipeline import ProcessingStep, FrameContextBuilder
from ..strategies.base import IDepthEstimator

class DepthEstimationStep(ProcessingStep):
    def __init__(self, strategy: IDepthEstimator):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        # 빌더에서 현재 프레임 가져오기
        frame = builder.get_current_frame() # 빌더에 getter 필요

        # 전략을 사용하여 뎁스 맵 추정
        depth_map = self._strategy.estimate(frame)

        # 빌더에 결과 추가
        builder.set_depth_map(depth_map)
        return builder
```

**`tracking.py` - LineTrackingStep (핵심 로직)**
```python
class LineTrackingStep(ProcessingStep):
    def __init__(self):
        # 프레임 간 라인을 추적하기 위한 레지스트리
        self.line_registry = {}
        self.next_line_id = 0

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        # 1. 빌더에서 필요한 데이터 추출
        edge_map = builder.get_edge_map()
        depth_map = builder.get_depth_map()
        flow_map = builder.get_flow_map()
        camera_intrinsics = builder.get_camera_intrinsics()

        # 2. 엣지 맵을 벡터화하여 2D 라인 생성
        # `vectorize` 함수는 외부 라이브러리(pypotrace 등)를 사용한다고 가정
        current_2d_lines = vectorize(edge_map)

        # 3. 2D 라인을 3D로 변환 (Back-projection)
        current_3d_lines = []
        for line2d in current_2d_lines:
            points_3d = backproject_to_3d(line2d.points, depth_map, camera_intrinsics)
            current_3d_lines.append(points_3d)

        # 4. 라인 추적 (Temporal Matching)
        # - 이전 프레임의 라인들과 현재 프레임의 라인들을 비교
        # - (위치, 방향, flow vector 등을 기반으로 매칭)
        # - 매칭된 라인은 ID를 유지, 새로운 라인은 신규 ID 부여
        # - self.line_registry 업데이트
        tracked_lines = self.match_and_track(current_3d_lines, flow_map)

        # 5. 최종 Line3D 객체 리스트를 빌더에 추가
        builder.set_lines(tracked_lines)
        return builder
```

### 4.3. 메인 실행 스크립트 (`validation_script_3d.py`)

```python
import cv2
from AXIS.src.pipeline import Pipeline, FrameContextBuilder
from AXIS.src.steps.detection import EdgeDetectionStep
from AXIS.src.steps.estimation import DepthEstimationStep, FlowEstimationStep
from AXIS.src.steps.tracking import LineTrackingStep
from AXIS.src.strategies.detectors import HEDDetector
from AXIS.src.strategies.estimators import MiDaSEstimator, RAFTEstimator

def main():
    # --- 1. 의존성 및 전략 객체 생성 ---
    print("Loading strategies...")
    edge_strategy = HEDDetector("path/to/hed.prototxt", "path/to/hed.caffemodel")
    depth_strategy = MiDaSEstimator()
    flow_strategy = RAFTEstimator() # (구현 가정)

    # --- 2. 파이프라인 단계 구성 ---
    print("Configuring pipeline...")
    pipeline = Pipeline([
        EdgeDetectionStep(strategy=edge_strategy),
        DepthEstimationStep(strategy=depth_strategy),
        FlowEstimationStep(strategy=flow_strategy),
        LineTrackingStep(),
        # ... RenderStep, MetricsStep 등 추가 ...
    ])

    # --- 3. 비디오 처리 루프 ---
    print("Starting video processing...")
    video_capture = cv2.VideoCapture("path/to/video.mp4")
    frame_idx = 0
    prev_frame = None

    while True:
        ret, current_frame = video_capture.read()
        if not ret:
            break
        
        if prev_frame is not None:
            # 빌더 생성 (flow 계산을 위해 이전 프레임도 전달)
            builder = FrameContextBuilder(frame_index=frame_idx, frame=current_frame, prev_frame=prev_frame)
            
            # 파이프라인 실행
            processed_context = pipeline.run(builder)
            
            print(f"Frame {frame_idx} processed.")
            # print(f"  Metrics: {processed_context.metrics}")

        prev_frame = current_frame
        frame_idx += 1

    print("Processing finished.")
    video_capture.release()

if __name__ == "__main__":
    main()

```
