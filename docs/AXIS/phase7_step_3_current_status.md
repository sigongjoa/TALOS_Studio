# Phase 7, Step 3: 현재 진행 상황 문서화

## 1. 단계 목표

Step 1에서 구축한 파이프라인 골격 위에, 딥러닝 기반 뎁스 추정 모델(MiDaS)을 `Strategy`로 사용하는 `DepthEstimationStep`을 구현하고, 파이프라인에 통합하여 정상 작동하는지 검증하는 것을 목표로 한다.

## 2. 현재까지의 진행 상황

-   **`MiDaSEstimator` 구현 완료**: `AXIS/src/strategies/estimators.py` 파일에 `MiDaSEstimator` 클래스를 구현했다. 이 클래스는 `torch.hub.load`를 사용하여 MiDaS 모델을 로드하고 뎁스 맵을 추정한다.
-   **`DepthEstimationStep` 구현 완료**: `AXIS/src/steps/estimation.py` 파일에 `DepthEstimationStep` 클래스를 구현했다. 이 스텝은 `MiDaSEstimator` 전략을 받아 뎁스 추정을 수행한다.
-   **`AXIS/src/main.py` 업데이트**: `main.py` 스크립트를 수정하여 `EdgeDetectionStep`과 `DepthEstimationStep`을 파이프라인에 추가하고, 엣지 맵과 뎁스 맵 결과를 `tests/data/` 폴더에 저장하도록 변경했다.
-   **`import os` 누락 수정**: `main.py`에서 `os` 모듈이 임포트되지 않아 발생한 `NameError`를 수정했다.

## 3. 현재 당면한 문제: `NameError: name 'Pipeline' is not defined`

`AXIS/src/main.py` 스크립트를 실행하는 과정에서 `NameError: name 'Pipeline' is not defined` 오류가 발생하고 있다. 이는 `main.py`에서 `Pipeline` 클래스를 임포트했음에도 불구하고, 파이썬 런타임이 이를 찾지 못하는 문제이다.

-   **오류 발생 위치**: `AXIS/src/main.py`의 `pipeline = Pipeline(steps=[...])` 라인.
-   **원인 분석**: `from .pipeline import Pipeline, FrameContextBuilder`와 같이 상대 경로로 임포트했음에도 불구하고, `Pipeline` 클래스가 정의되지 않았다는 오류가 발생하는 것은 파이썬의 패키지 로딩 메커니즘과 관련된 미묘한 문제일 가능성이 높다. 이는 `pipeline` 모듈이 완전히 로드되기 전에 `main` 모듈이 `Pipeline` 클래스를 참조하려 할 때 발생할 수 있다.

## 4. 해결 방안 및 다음 단계

`NameError`를 해결하기 위해 `AXIS/src/main.py` 파일의 임포트 방식을 변경하여 `Pipeline` 클래스를 명시적으로 참조하도록 수정하겠습니다.

-   **수정 내용**: `from .pipeline import Pipeline, FrameContextBuilder` 구문을 `import .pipeline as pipeline_module`로 변경하고, `Pipeline`과 `FrameContextBuilder`를 사용할 때 `pipeline_module.Pipeline`, `pipeline_module.FrameContextBuilder`와 같이 모듈 이름을 통해 접근하도록 합니다. 이 방식은 임포트 시점을 명확히 하여 문제를 해결할 수 있습니다.

이 수정 작업을 먼저 진행한 후, 다시 `AXIS/src/main` 모듈을 실행하여 Step 3의 성공적인 완료를 검증하겠습니다.
