# AXIS 모듈 구현을 위한 디자인 패턴 가이드

이 문서는 AXIS 모듈, 특히 3D 검증 파이프라인(`validation_script_3d.py`)을 구현할 때 적용할 핵심 디자인 패턴을 정의합니다. 올바른 디자인 패턴을 적용하면 모듈성, 확장성, 테스트 용이성이 높은 견고하고 유연한 시스템을 구축할 수 있습니다.

## 1. 파이프라인 패턴 (Pipeline Pattern) / 책임 연쇄 패턴 (Chain of Responsibility)

- **적용 이유**: AXIS의 검증 프로세스는 `(영상 읽기) → (엣지 검출) → (Depth 추정) → (Flow 계산) → (3D 변환/추적) → (렌더링/평가)` 와 같이 명확한 단계별 데이터 처리 흐름을 가집니다. 파이프라인 패턴은 각 단계를 독립적인 컴포넌트로 분리하여 결합도를 낮추고, 각 단계의 재사용성과 교체 용이성을 높입니다.

- **구현 방식**:
    - 각 처리 단계를 `ProcessingStep`이라는 공통 인터페이스를 상속받는 클래스로 정의합니다. (예: `EdgeDetectionStep`, `DepthEstimationStep`, `LineTrackingStep`).
    - 각 `Step`은 이전 단계의 결과물이 담긴 데이터 컨텍스트(Context)를 입력으로 받아 자신의 작업을 수행하고, 컨텍스트를 업데이트하여 다음 `Step`으로 전달합니다.
    - 전체 파이프라인의 실행을 관리하는 `Pipeline` 클래스가 이 `Step`들을 순서대로 호출합니다.

## 2. 전략 패턴 (Strategy Pattern)

- **적용 이유**: 특정 처리 단계에서 여러 다른 알고리즘을 실험하고 교체해야 할 필요성이 높습니다. 예를 들어, '엣지 검출'에는 `HED`, `DexiNed`, `Canny` 등 다양한 전략이 있을 수 있고, 'Depth 추정'에는 `MiDaS`, `ZoeDepth` 등 다른 모델을 사용할 수 있습니다. 전략 패턴을 사용하면 런타임에 이 알고리즘들을 동적으로 쉽게 교체할 수 있습니다.

- **구현 방식**:
    - `IEdgeDetector`, `IDepthEstimator` 와 같은 추상 인터페이스(또는 추상 기본 클래스)를 정의합니다.
    - `HEDDetector`, `DexiNedDetector` 처럼 각 알고리즘을 인터페이스를 구현한 구체적인 '전략(Strategy)' 클래스로 작성합니다.
    - `EdgeDetectionStep`과 같은 파이프라인 단계 클래스는 구체적인 알고리즘 클래스가 아닌, `IEdgeDetector` 인터페이스에만 의존합니다. 실제 사용할 알고리즘(전략 객체)은 외부에서 생성하여 주입(Dependency Injection)해 줍니다.

## 3. 빌더 패턴 (Builder Pattern)

- **적용 이유**: 파이프라인의 각 단계를 거치면서 처리해야 할 데이터의 종류가 계속 늘어납니다. (원본 프레임 이미지, 엣지맵, 뎁스맵, 3D 라인 리스트, 평가 메트릭 등). 빌더 패턴을 사용하면 이 복잡한 데이터 객체의 생성 과정을 단계별로 분리하여, 생성 로직의 복잡도를 낮추고 객체 생성의 일관성을 유지할 수 있습니다.

- **구현 방식**:
    - 파이프라인을 통해 전달될 데이터 묶음을 `FrameDataContext`라고 정의합니다.
    - `FrameDataBuilder` 클래스를 만들어, 파이프라인의 각 `Step`이 자신의 결과물을 빌더에 추가하도록 설계합니다. (예: `builder.set_depth_map(depth_data)`)
    - 파이프라인의 마지막에서 `builder.build()`를 호출하여, 모든 데이터가 포함된 완전하고 불변(immutable)한 `FrameDataContext` 객체를 생성합니다.

## 4. 옵저버 패턴 (Observer Pattern)

- **적용 이유**: 파이프라인의 각 프레임 처리가 끝날 때마다, 그 결과를 다른 부분(예: 메트릭 로깅, 실시간 시각화, UI 업데이트 등)에 알려야 할 수 있습니다. 옵저버 패턴은 핵심 처리 로직과 결과 통보/활용 로직을 분리하여, 시스템의 결합도를 낮추고 유연성을 높입니다.

- **구현 방식**:
    - `Pipeline` 클래스를 'Subject(주체)'로 만듭니다. 이 클래스는 관찰자(Observer)를 등록/해제하는 메소드를 가집니다.
    - `MetricsLogger`, `RealtimeVisualizer` 등을 'Observer(관찰자)' 인터페이스를 구현한 클래스로 만듭니다.
    - 각 프레임 처리가 완료되면, `Pipeline`은 등록된 모든 `Observer`에게 `notify(frame_data_context)` 메소드를 호출하여 처리 결과가 담긴 데이터 객체를 전달합니다.

## 종합적인 아키텍처 예시 (의사코드)

```python
# 1. 전략 패턴 (Strategy Pattern)
class IEdgeDetector:
    def detect(self, frame: np.array) -> np.array: pass

class HEDDetector(IEdgeDetector): ...
class CannyDetector(IEdgeDetector): ...

# 2. 파이프라인 패턴 (Pipeline Pattern)
class ProcessingStep:
    def execute(self, context_builder: 'FrameDataBuilder'): pass

class EdgeDetectionStep(ProcessingStep):
    def __init__(self, strategy: IEdgeDetector):
        self.strategy = strategy
    
    def execute(self, context_builder):
        frame = context_builder.get_current_frame()
        edges = self.strategy.detect(frame)
        context_builder.set_edges(edges)
        # 다음 스텝으로 빌더를 넘겨줌
        return context_builder

# 3. 빌더 패턴 (Builder Pattern)
class FrameDataBuilder:
    def __init__(self, frame):
        self._frame_data = {"frame": frame}

    def set_edges(self, edges):
        self._frame_data["edges"] = edges
        return self
    
    def build(self):
        return self._frame_data # In reality, an immutable data class

# 4. 옵저버 패턴 (Observer Pattern)
class PipelineObserver:
    def on_frame_processed(self, context): pass

class MetricsLogger(PipelineObserver): ...

# 전체 파이프라인 구성 및 실행
class Pipeline:
    def __init__(self, steps: list[ProcessingStep]):
        self.steps = steps
        self.observers = []

    def add_observer(self, observer: PipelineObserver):
        self.observers.append(observer)

    def run(self, initial_builder):
        builder = initial_builder
        for step in self.steps:
            builder = step.execute(builder)
        
        final_context = builder.build()
        for observer in self.observers:
            observer.on_frame_processed(final_context)
        return final_context

# --- Main Execution ---
# 전략 주입
edge_detector_strategy = HEDDetector()

# 파이프라인 구성
pipeline = Pipeline([
    EdgeDetectionStep(strategy=edge_detector_strategy),
    DepthEstimationStep(strategy=MiDaSEstimator()),
    # ... other steps
])

# 옵저버 등록
logger = MetricsLogger()
pipeline.add_observer(logger)

# 실행
for frame in video_frames:
    builder = FrameDataBuilder(frame)
    pipeline.run(builder)
```

### 결론

**파이프라인 패턴**으로 전체 구조의 뼈대를 잡고, 각 파이프라인 단계를 **전략 패턴**으로 유연하고 교체 가능하게 만들며, 복잡한 데이터 객체는 **빌더 패턴**으로 안전하게 생성하고, 처리 결과는 **옵저버 패턴**으로 다른 모듈에 전파하는 방식이 가장 이상적입니다. 이 패턴들의 조합은 복잡한 AXIS 검증 시스템을 체계적이고 견고하게 만들어 줄 것입니다.
