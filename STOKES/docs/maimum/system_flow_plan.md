# ⚙️ Effect Stokes + 마님 시스템 Flow

## 1. 전체 개요
이 시스템은 **수식 → 해설(마님) → 시뮬레이션(VFX) → 최종 영상**으로 이어지는 파이프라인입니다. 핵심은 **수학적 개념을 마님이 해설하고, 같은 수식을 기반으로 시뮬레이션과 렌더링을 실행**하여 시청자가 '이해+몰입'을 동시에 경험하게 만드는 것입니다.

---

## 2. 단계별 흐름

### 단계 1: 입력
- 사용자 입력: “무잔 회전 → 푸리에 변환 → 카운터 타이밍 표시”
- 입력 요소: 텍스트 설명, 특정 효과 이름, 선택적 수학식

### 단계 2: 파라미터 해석 (StyleAgent)
- 입력 텍스트를 분석하여 **시뮬레이션에 필요한 파라미터**와 **핵심 수식** 추출
- 예: 회전 속도, 각도, 반복 주기, 적용할 수학 공식(푸리에 변환)

### 단계 3: 해설 생성 (NarrationAgent, 마님)
- StyleAgent가 뽑은 수식을 기반으로 **내레이션 스크립트 생성**
- 톤: 지혜로운 해설자, 교육+밈 성격
- 출력: 음성 파일(mp3/wav), 자막 파일(srt)

### 단계 4: 시뮬레이션 (SimulationAgent)
- StyleAgent가 생성한 파라미터를 활용해 **Navier–Stokes 기반 유체 시뮬레이션** 실행
- 궤적, 파동, 입자 리본 등을 생성

### 단계 5: 렌더링 (RenderAgent)
- Blender, FFmpeg 등으로 VFX를 영상화
- 시뮬레이션 데이터 + 보조 그래프(FFT 등) 합성
- 최종 영상 클립 생성 (영상만)

### 단계 6: 합성 (Orchestrator)
- RenderAgent 결과(영상) + NarrationAgent 결과(오디오, 자막)를 동기화하여 하나의 쇼츠 완성
- 결과물: **VFX + 해설 + 자막**이 결합된 영상

---

## 3. 데이터 흐름 요약
```
사용자 입력 → StyleAgent → (수식/파라미터)
        ├─> NarrationAgent → (음성/자막)
        └─> SimulationAgent → RenderAgent → (VFX 영상)

최종 합성: (VFX 영상 + 음성 + 자막) → 완성 쇼츠
```

### 3.1 데이터 형식 명세

각 에이전트 간에 전달되는 주요 데이터 형식은 다음과 같습니다.

*   **StyleAgent 출력**:
    *   **`parameters.json`**: 시뮬레이션에 필요한 파라미터 (예: `{"rotation_speed": 10, "angle": 90, "frequency": "fourier_transform"}`).
    *   **`formulas.txt`**: 추출된 핵심 수식 (예: `f(t) = A * sin(wt + phi)`).
*   **NarrationAgent 입력**:
    *   **`parameters.json`**: StyleAgent의 출력과 동일.
    *   **`formulas.txt`**: StyleAgent의 출력과 동일.
*   **SimulationAgent 출력**:
    *   **`simulation_data.json` 또는 `simulation_data.h5`**: 시뮬레이션 결과 데이터 (예: 각 프레임별 입자 위치, 속도, 밀도 등). 구체적인 포맷은 시뮬레이션 종류에 따라 유동적.
*   **RenderAgent 입력**:
    *   **`simulation_data.json` 또는 `simulation_data.h5`**: SimulationAgent의 출력과 동일.
    *   **`graph_images/`**: 보조 그래프 이미지 파일들 (예: FFT 결과 이미지).
*   **NarrationAgent 출력**:
    *   **`narration.mp3` / `narration.wav`**: TTS 변환된 오디오 파일.
    *   **`subtitles.srt`**: 시간 정보가 포함된 자막 파일.
*   **Orchestrator 입력**:
    *   **`final_vfx_video.mp4`**: RenderAgent의 최종 영상.
    *   **`narration.mp3` / `narration.wav`**: NarrationAgent의 오디오 파일.
    *   **`subtitles.srt`**: NarrationAgent의 자막 파일.

---

## 4. 기대 효과
- **직관적 학습**: 수식이 실제 VFX로 변환되는 과정을 눈과 귀로 동시에 체험
- **콘텐츠 차별화**: 단순 “멋있는 효과”가 아니라, 그 효과의 수학적 본질까지 해설
- **시스템 확장성**: 다른 애니, 과학 개념에도 손쉽게 적용 가능

---

✅ 결론: 이 Flow는 **“수학적 개념을 이해시키기 위한 VFX+해설 결합 파이프라인”**이다.

