# AXIS 모듈 기획 및 문제 정의서

## 1. 모듈 이름

**AXIS (액시스)**

## 2. 한 줄 정의

**연출 의도(PRISM)를 해석하여, 3D 공간상에 제어 가능한 벡터 라인(vector line)으로 작화를 수행하는 시점인식(viewpoint-aware) 드로잉 엔진.**

## 3. 기획 의도 (Purpose & Goal)

기존의 AI 이미지 생성 방식(e.g., Diffusion)은 결과물이 픽셀의 집합(raster image)이므로, 통제 불가능하고 수정이 어려우며, 영상 제작 파이프라인에 통합하기 어렵다는 한계가 있습니다. 

AXIS 모듈의 핵심 기획 의도는 이러한 한계를 극복하고, **AI 창작을 '생성(Generation)'의 영역에서 '제어 가능한 계산(Controllable Computation)'의 영역으로 전환**하는 것입니다. AI가 그린 그림을 단순 결과물로 받는 것이 아니라, 그리는 '행위' 자체를 수학적(벡터)으로 표현하고, 이를 파라미터 단위로 제어함으로써 **완전한 통제권과 재현성을 확보**하는 것을 목표로 합니다.

## 4. 핵심 문제 정의 (Core Problem Definition)

AXIS 모듈은 다음의 세 가지 핵심 문제를 해결해야 합니다.

### 문제 1: 표현의 전환 (Representation Shift)
- **문제**: 픽셀 기반의 2D 이미지에서, 수학적으로 정의되고 제어 가능한 **벡터 기반의 파라메트릭 곡선(parametric curve)으로 표현 체계를 전환**해야 합니다.
- **해결 과제**: 이미지의 시각적 정보를 어떻게 손실 없이 선(line)들의 집합으로 변환할 것인가? 이 선들은 두께, 압력, 곡률 등의 속성을 가져야 합니다.

### 문제 2: 제어 가능성 확보 (Controllability)
- **문제**: 생성된 선들은 외부에서 **프로그래밍 방식으로 수정(edit), 추가(add), 삭제(delete)가 가능**해야 합니다.
- **해결 과제**: 각 선(stroke)에 고유 ID를 부여하고, 특정 선의 곡률, 위치, 두께 등을 변경할 수 있는 API를 어떻게 설계할 것인가?

### 문제 3: 시점 불변성 및 시간적 일관성 (Viewpoint Invariance & Temporal Consistency)
- **문제**: 2D 이미지 평면에서만 라인을 추출할 경우, 카메라의 회전, 이동 등 **시점 변화가 발생하면 라인의 연속성이 붕괴**됩니다. (e.g., 라인 떨림, 끊김, 왜곡 현상)
- **해결 과제**: 라인을 2D가 아닌 **3D 공간상에 존재하는 'Line Field'로 정의**해야 합니다. 이를 위해 영상의 각 프레임에서 **Depth(깊이)와 Optical Flow(광학 흐름) 정보를 추출 및 융합**하여, 카메라가 움직여도 동일한 객체의 라인은 3D 공간상에서 일관성을 유지하도록 추적해야 합니다.

## 5. 주요 기능 및 역할 (Key Features & Roles)

- **PRISM 연출 해석**: PRISM 모듈로부터 전달받은 컷(cut)의 연출 정보(카메라 워크, 포즈, 감정 등)를 파싱합니다.
- **3D 구조 분석**: 입력 영상으로부터 캐릭터의 3D 포즈, 씬의 Depth Map, 객체의 Optical Flow를 계산합니다.
- **3D 라인 필드 생성**: 분석된 3D 구조 정보를 바탕으로, 3D 공간상에 파라메트릭 곡선(라인)들의 집합을 생성합니다.
- **레이어 관리**: 생성된 라인들을 의미 단위(인물, 배경, 소품 등)로 레이어화하여 관리합니다.
- **2D 투영 렌더링**: 주어진 프레임의 카메라 매트릭스(Projection Matrix)에 따라 3D 라인들을 2D 이미지 평면에 투영(projection)하여 최종 작화를 렌더링합니다.
- **수정 API 제공**: 외부(Orchestrator 또는 사용자)에서 특정 라인을 제어할 수 있는 API를 제공합니다.

## 6. 핵심 기술 스택 (Core Technology Concepts)

- **Computer Vision**: Edge Detection(HED, DexiNed), Depth Estimation(MiDaS), Optical Flow(RAFT) 등
- **Geometric Computing**: 3D 역투영(Back-projection), 카메라 행렬 연산, 3D 기하학
- **Vector Graphics**: Parametric Curve(Bézier, Spline) 생성 및 처리, SVG/JSON 포맷 출력
- **Generative AI (향후)**: 생성된 라인의 스타일을 변환하거나(Style Transfer), 디테일을 추가하는(Refinement) 역할

## 7. 산출물 정의 (Output Definition)

AXIS는 각 프레임에 대한 작화 정보를 담은 **구조화된 JSON 파일**을 출력합니다. 이 파일은 3D 공간 좌표를 포함한 라인 데이터, 레이어 정보, 스타일 프로필 등을 포함합니다.

```json
{
  "cut_id": "S01_C02",
  "frame_index": 101,
  "camera_projection_matrix": [[...]],
  "lines": [
    {
      "line_id": "char01_outline_001",
      "layer": "character_main",
      "points_3d": [[-1.5, 2.1, -5.0], [-1.4, 2.2, -5.1], ...],
      "pressure": [0.8, 0.7, 0.5]
    }
  ],
  "layers": ["background", "character_main", ...]
}
```

## 8. 검증 및 성공 기준 (Validation & Success Criteria)

- **정량적 기준**: 원본 영상과, AXIS가 생성한 3D 라인을 다시 렌더링한 영상 간의 **SSIM(Structural Similarity Index) 값이 평균 0.85 이상**을 유지해야 합니다. 프레임 간 라인의 **곡률 변화량(Δκ)이 설정된 임계값 이하**로 유지되어야 합니다.
- **정성적 기준**: 카메라가 역동적으로 움직이는 씬에서도 **라인의 떨림이나 끊김 현상 없이 안정적으로 형태가 유지**되어야 합니다. 렌더링된 결과물이 시각적으로 원본의 구조를 명확하게 표현해야 합니다.
