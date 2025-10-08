# AXIS 모듈 코딩 컨벤션

## 1. 개요

이 문서는 AXIS 모듈의 Python 코드 작성 시 일관성을 유지하고, 잠재적인 오류를 줄이며, 가독성을 높이기 위한 코딩 스타일 가이드를 정의합니다. 모든 코드는 이 컨벤션을 따르는 것을 원칙으로 합니다.

---

## 2. 명명 규칙 (Naming Conventions)

-   **클래스 (Classes)**: `PascalCase`를 사용합니다.
    -   *예시*: `FrameContext`, `EdgeDetectionStep`, `MiDaSEstimator`

-   **함수 및 메소드 (Functions & Methods)**: `snake_case`를 사용합니다.
    -   *예시*: `run_pipeline`, `estimate`, `_preprocess`

-   **변수 (Variables)**: `snake_case`를 사용합니다.
    -   *예시*: `original_frame`, `flow_map`, `prev_frame`

-   **상수 (Constants)**: `UPPER_SNAKE_CASE`를 사용합니다. 모듈 최상단에 정의합니다.
    -   *예시*: `DEFAULT_THRESHOLD = 100`, `VIDEO_INPUT_PATH = "..."`

-   **내부용(Internal) 멤버**: 외부 사용을 권장하지 않는 내부 변수나 메소드는 앞에 밑줄(`_`) 하나를 붙입니다.
    -   *예시*: `_context_data`, `_notify`

---

## 3. 임포트 스타일 (Import Style)

임포트 관련 오류는 가장 흔하게 발생하는 문제 중 하나이므로, 다음 규칙을 반드시 준수합니다.

### 3.1. 임포트 순서

PEP 8 가이드라인에 따라 다음 순서로 그룹화하고, 그룹 사이에는 한 줄을 띄웁니다.

1.  **표준 라이브러리**: `os`, `sys`, `argparse` 등
2.  **서드파티 라이브러리**: `cv2`, `numpy`, `torch` 등
3.  **로컬 애플리케이션(우리 프로젝트) 라이브러리**: `from .pipeline import ...` 등

```python
# 좋은 예시
import os
import argparse

import cv2
import numpy as np

from .pipeline import Pipeline, FrameContextBuilder
from .strategies.estimators import MiDaSEstimator
```

### 3.2. 로컬 임포트 규칙 (가장 중요)

`src` 패키지 내의 모듈 간 임포트는 **항상 상대 경로(relative path)를 사용**합니다.

-   **같은 디렉토리**: `from . import my_module`
-   **상위 디렉토리**: `from .. import parent_module`
-   **하위 디렉토리**: `from .sub_package import my_module`

```python
# src/steps/estimation.py 에서의 올바른 임포트 예시
from ..pipeline import ProcessingStep, FrameContextBuilder  # 상위 디렉토리의 pipeline 모듈
from ..strategies.base import IDepthEstimator             # 상위 디렉토리의 strategies 패키지
```

### 3.3. 스크립트 실행 방법

상대 경로 임포트를 사용한 코드는 일반적인 `python a_script.py` 방식으로 실행하면 `ImportError`가 발생합니다. 프로젝트의 루트 디렉토리(`AXIS/`)에서 **`-m` (모듈) 옵션을 사용하여 실행해야 합니다.**

-   **올바른 실행 방식**:
    ```bash
    # AXIS/ 디렉토리에서 실행
    python -m src.main
    ```
-   **잘못된 실행 방식**:
    ```bash
    # AXIS/src/ 디렉토리에서 실행
    python main.py  # (X) ImportError 발생
    ```

---

## 4. 타입 힌트 (Type Hinting)

모든 함수와 메소드의 시그니처에는 **반드시 타입 힌트를 명시**합니다. 이는 코드의 명확성을 높이고, 정적 분석 도구(IDE, mypy 등)의 도움을 받아 버그를 사전에 찾는 데 큰 도움이 됩니다.

-   *예시*:
    ```python
    def estimate(self, frame: np.ndarray, threshold: int = 100) -> np.ndarray:
        # ...
        pass
    ```

---

## 5. 문서화 (Documentation)

-   **Docstrings**: 모든 공개(public) 클래스, 함수, 메소드에는 **반드시 Docstring을 작성**하여 그 역할, 인자, 반환 값에 대해 설명합니다.
-   **주석 (Comments)**: 복잡한 로직이나, 특정 결정의 배경(왜 이렇게 코드를 작성했는지)을 설명해야 할 때만 주석을 사용합니다. '무엇을' 하는지에 대한 주석은 지양하고, '왜' 그렇게 하는지에 대한 주석을 지향합니다.

---
## 6. 향후 도입 제안

코드 컨벤션의 자동화를 위해 다음 도구들의 도입을 고려합니다.

-   **Formatter**: `black` (코드 형식을 통일하여 스타일에 대한 논쟁을 없앰)
-   **Linter**: `ruff` (매우 빠른 속도로 코드의 잠재적 오류, 버그, 스타일 문제를 검사)
