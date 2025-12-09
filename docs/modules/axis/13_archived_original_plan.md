# AXIS — Stroke-based AI 원화 생성 모듈 설계서 (Line-by-Line Architecture)

## 1. 철학: “행위 생성” AI

> “AI는 그림을 완성하는 존재가 아니라, 선을 그려주는 동료 작화가로 진화한다.”

AXIS는 픽셀(Raster) 결과물을 생성하는 기존의 이미지 생성 모델과 근본적으로 다릅니다. AI가 ‘그림을 그리는 행위’ 자체를 학습하고, 수정 가능한 ‘선(Stroke)’의 연속으로 결과물을 만들어내는 **벡터 기반 원화 생성 엔진**입니다.

---

## 2. 개념: 픽셀 생성 vs. 스트로크 생성

| 구분 | 기존 Diffusion / Image Generator | **AXIS (Stroke-based AI)** |
|---|---|---|
| **출력 형태** | 픽셀 (Raster) 이미지 | **벡터 (Stroke Graph)** |
| **해상도 의존성** | 높음 (업스케일 필요) | **없음 (해상도 독립적)** |
| **편집 가능성** | 낮음 (픽셀 단위 수정) | **높음 (선 단위 수정, 추가, 삭제)** |
| **학습 데이터** | 이미지-텍스트 쌍 | **선화 데이터 (SVG, 포즈, 제어점)** |
| **핵심 목표** | 최종 결과물 생성 | **수정 가능한 작화 파이프라인 데이터 생성** |
| **자원 효율성** | 높음 (전체 이미지 재연산) | **낮음 (선 단위 부분 연산 가능)** |

---

## 3. 입력 (Input)

AXIS는 PRISM 모듈의 출력물을 직접 입력으로 받습니다.

1.  **프로젝트 구조 (`project_structure.json`):** 씬, 컷, 카메라, 캐릭터 레이아웃 등 구조화된 정보
2.  **시각적 콘티 (`visuals/`):** 각 컷의 구도와 분위기를 참조하기 위한 레퍼런스 이미지
3.  **포즈 데이터 (Pose Data):** ControlNet 등을 통해 PRISM 단계에서 추출된 캐릭터의 포즈 키포인트 (e.g., DWpose keypoints)

---

## 4. 처리 (Processing): Stroke Prediction Pipeline

### 4.1. 데이터 표현: Stroke Sequence
AI는 이미지를 ‘선들의 집합’으로 인식하고, 그리는 순서와 속성을 학습합니다. 모든 원화는 아래와 같은 Stroke Sequence 데이터로 표현됩니다.

```json
{
  "frame_id": "S01_C01",
  "strokes": [
    {
      "stroke_id": "strk_001",
      "start_point": [10, 20],
      "control_points": [[35, 25], [55, 35]],
      "end_point": [80, 45],
      "pressure": 0.7,
      "color": "black",
      "order": 1
    },
    {
      "stroke_id": "strk_002",
      "start_point": [15, 30],
      "control_points": [[40, 40], [60, 50]],
      "end_point": [75, 60],
      "pressure": 0.5,
      "color": "black",
      "order": 2
    }
  ],
  "layer": "character_outline"
}
```

### 4.2. 모델 아키텍처: Transformer 기반 Sequence-to-Sequence

-   **Encoder:** 입력된 포즈, 레이아웃, 감정 정보를 인코딩합니다.
-   **Transformer Decoder:** 인코딩된 컨텍스트를 바탕으로, 다음에 그려질 선(Stroke)의 속성(좌표, 압력 등)을 순차적으로 예측합니다.

```
[Input: Pose + Layout] ==> Encoder ==> [Context Vector] ==> Transformer Decoder ==> [Output: Stroke Sequence]
```

### 4.3. 학습 데이터 파이프라인
1.  **원화 수집:** 스튜디오 내부 자료 또는 공개된 원화(Genga) 프레임을 수집합니다.
2.  **Stroke 추출:** OpenCV, Potrace, DeepSVG 등의 CV 파이프라인을 통해 래스터 이미지를 벡터 선 데이터로 변환합니다.
3.  **Stroke 정렬:** 그래프 기반 정렬 알고리즘(DFS/BFS)을 사용하여 선들의 그리기 순서를 예측하고 부여합니다.
4.  **데이터 변환:** 추출된 선들을 모델이 학습할 수 있는 Stroke Sequence JSON 형태로 변환합니다.

---

## 5. 출력 (Output)

-   **Stroke Graph (`.json`):** 위 4.1.에서 정의한 Stroke Sequence가 포함된 JSON 파일. 후속 모듈과의 데이터 교환을 위한 핵심 결과물입니다.
-   **시각적 표현 (`.svg`):** 생성된 Stroke Graph를 렌더링한 벡터 이미지 파일. 해상도에 관계없이 선명한 결과물을 보장합니다.

---

## 6. 제어 가능성 (Controllability)

AXIS는 ‘선’ 단위로 결정을 내리므로, 인간 아티스트가 개입할 수 있는 제어 포인트가 극대화됩니다.

| 제어 포인트 | 설명 | 컨트롤 방법 |
|---|---|---|
| **🎨 Stroke 영역** | 어디에 선을 추가/제거할지 결정 | Region Mask, Prompt Tag |
| **✏️ Stroke 속성** | 선의 굵기, 색상, 압력 조절 | Numeric Control (0.0–1.0) |
| **🕒 Stroke 순서** | 먼저 그릴 부분과 나중에 그릴 부분 제어 | Sequence Scheduling |
| **🧭 방향성** | 브러시의 방향과 흐름 제어 | Angle Control, Symmetry Flag |

---

## 7. 파이프라인 통합 (Pipeline Integration)

-   **PRISM → AXIS:** PRISM의 콘티(`project_structure.json`)와 포즈 데이터를 입력받아, AXIS가 `Stroke Graph`를 생성합니다.
-   **AXIS → FLUX:** 생성된 `Stroke Graph` 간의 보간(Interpolation)을 통해 벡터 모핑(Vector Morphing) 기반의 부드러운 동화를 구현합니다.
-   **AXIS → CHROMA:** `Stroke Graph`의 레이어 정보를 기반으로, 각 영역(e.g., `character_outline`)에 정확한 채색을 적용합니다.