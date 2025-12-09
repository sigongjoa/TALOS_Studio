# Phase 7, Step 2: EdgeDetectionStep 구현 및 테스트

## 1. 단계 목표

Step 1에서 구축한 파이프라인 골격 위에, 딥러닝 기반 엣지 검출 전략(PiDiNet -> Canny로 변경)을 사용하는 `EdgeDetectionStep`을 구현하고, 파이프라인에 통합하여 정상 작동하는지 검증하는 것을 목표로 한다.

## 2. 구현 상세

Step 2는 다음 하위 작업으로 진행되었다.

### 2.1. 가상 환경 설정 및 라이브러리 설치

- **가상 환경 생성**: `python3 -m venv AXIS/venv` 명령어로 가상 환경을 생성했다.
- **`.gitignore` 업데이트**: `/AXIS/venv/`를 `.gitignore`에 추가하여 가상 환경 폴더가 Git에 포함되지 않도록 했다.
- **기본 라이브러리 설치**: `AXIS/venv/bin/python -m pip install numpy opencv-python-headless` 명령어로 `numpy`와 `opencv-python-headless`를 설치했다.
- **딥러닝 라이브러리 설치**: `AXIS/venv/bin/python -m pip install torch torchvision timm` 명령어로 PyTorch 관련 라이브러리를 설치했다.

### 2.2. 전략 인터페이스 정의 (`src/strategies/base.py`)

`IEdgeDetector`, `IDepthEstimator`, `IOpticalFlowEstimator`와 같은 전략 인터페이스(추상 베이스 클래스)를 정의했다.

### 2.3. 엣지 검출 전략 구현 (`src/strategies/detectors.py`)

- **PiDiNet 시도 및 변경**: 초기 계획은 `PiDiNetDetector`를 구현하는 것이었으나, `torch.hub.load`를 통한 모델 로딩이 `HTTP Error 404`로 실패했다. `PiDiNet`의 복잡한 수동 설치 과정을 피하기 위해, **`CannyDetector`**로 전략을 변경했다.
- **`CannyDetector` 구현**: `OpenCV`의 `cv2.Canny` 함수를 사용하는 `CannyDetector` 클래스를 구현하여 `IEdgeDetector` 인터페이스를 만족시켰다.

```python
# AXIS/src/strategies/detectors.py (CannyDetector 부분)
import cv2
import numpy as np
from .base import IEdgeDetector

class CannyDetector(IEdgeDetector):
    def __init__(self, threshold1: int = 100, threshold2: int = 200):
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def detect(self, frame: np.ndarray) -> np.ndarray:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge_map = cv2.Canny(gray_frame, self.threshold1, self.threshold2)
        return edge_map
```

### 2.4. 엣지 검출 스텝 구현 (`src/steps/detection.py`)

주입된 `IEdgeDetector` 전략을 사용하여 엣지 맵을 검출하고 `FrameContextBuilder`에 추가하는 `EdgeDetectionStep` 클래스를 구현했다.

```python
# AXIS/src/steps/detection.py
from ..pipeline import ProcessingStep, FrameContextBuilder
from ..strategies.base import IEdgeDetector

class EdgeDetectionStep(ProcessingStep):
    def __init__(self, strategy: IEdgeDetector):
        self._strategy = strategy

    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        original_frame = builder.get("original_frame")
        edge_map = self._strategy.detect(original_frame)
        builder.set("edge_map", edge_map)
        return builder
```

### 2.5. 메인 실행 스크립트 수정 (`AXIS/src/main.py`)

`AXIS/src/main.py` 스크립트를 수정하여 `CannyDetector`를 사용하는 `EdgeDetectionStep`을 파이프라인에 추가하고, 엣지 맵 결과를 `tests/data/edge_map_output.png` 파일로 저장하도록 변경했다.

```python
# AXIS/src/main.py (주요 변경 사항)
# ...
from .steps.detection import EdgeDetectionStep
from .strategies.detectors import CannyDetector

def main():
    # ...
    pipeline = Pipeline(steps=[
        EdgeDetectionStep(strategy=CannyDetector())
    ])
    # ...
    edge_map_result = processed_context.edge_map
    cv2.imwrite(output_image_path, edge_map_result)
    # ...
```

## 3. 테스트 상세

### 3.1. 테스트 시나리오

1.  `AXIS/tests/data/sample_image.png` 파일을 로드한다.
2.  `CannyDetector` 전략을 사용하는 `EdgeDetectionStep` 하나만 포함된 `Pipeline`을 생성한다.
3.  파이프라인을 실행하여 엣지 맵을 검출한다.
4.  결과로 나온 엣지 맵을 `AXIS/tests/data/edge_map_output.png` 파일로 저장한다.

### 3.2. 테스트 실행 및 결과

- **실행 명령어**: `AXIS/venv/bin/python -m AXIS.src.main`
- **실행 결과**: 스크립트가 성공적으로 실행되었으며, 콘솔에 "Success!" 메시지가 출력되었다.
- **검증**: `AXIS/tests/data/` 디렉토리에 원본 이미지의 엣지 정보가 추출된 `edge_map_output.png` 파일이 정상적으로 생성되었음을 시각적으로 확인했다.

## 4. 완료의 정의 (Definition of Done) 충족

- **[X] 코드 구현**: Step 2에 계획된 모든 코드(전략 인터페이스, 엣지 검출 전략, 엣지 검출 스텝)가 작성되었다.
- **[X] 단위/통합 테스트**: `AXIS/src/main.py` 스크립트가 `EdgeDetectionStep`의 통합 테스트 역할을 수행하여, 엣지 검출 기능이 정상 작동함을 증명했다.
- **[X] 문서 업데이트**: 현재 이 `phase7_step_2.md` 문서를 작성함으로써 모든 과정이 문서화되었다.

## 5. 결론

Step 2를 통해, AXIS 모듈의 파이프라인에 엣지 검출 기능이 성공적으로 통합되었으며, `CannyDetector`를 통해 엣지 맵을 추출하는 것이 검증되었다. 이제 이 기반 위에 다음 단계인 뎁스 추정 기능을 추가할 준비가 완료되었다.
