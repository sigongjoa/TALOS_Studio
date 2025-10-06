# PRISM — AI 시네마 카툰 기획 모듈 (v2)

## 1. 새로운 정의
“프리즘은 서사를 시각화하는 기획 도구이며, 모든 작품은 여기서 ‘카툰 형태의 초안’으로 탄생한다.”

---

## 2. 목적 및 역할

| 구분 | 설명 |
|---|---|
| 🎯 **핵심 목표** | AI가 ‘콘셉트–스토리–씬 구상–프레임 단위 구성’을 자동으로 시각화하는 단계 |
| 🎨 **결과물 형태** | 만화(Storyboard Cartoon) 또는 카툰 스케치 수준의 ‘초기 시각화 시퀀스’ |
| 🧩 **후속 연결** | AXIS(원화)·FLUX(동화) 모듈로 자연스럽게 이어지는 데이터 설계도 역할 |
| 🧱 **작동 방식** | 텍스트 → 씬 구조화 → 컷별 설명 → 다중 레이어 기반 컷별 이미지 생성 |

---

## 3. 입력 (Input)
- **기본 텍스트:** 시나리오, 스토리, 핵심 감정 키워드
- **사용자 파라미터:** 원하는 스타일, 톤앤매너, 캐릭터 설명

---

## 4. 처리 (Processing)
1.  **서사 분석 (Narrative Analysis):** LLM이 입력된 텍스트를 분석하여 핵심 플롯, 캐릭터, 배경, 감정선을 추출합니다.
2.  **씬 구조화 (Scene Structuring):** 분석된 서사를 바탕으로 전체 스토리를 씬(Scene) 단위로 분할하고, 각 씬의 목적과 흐름을 정의합니다.
3.  **컷 분할 및 연출 (Cut Division & Direction):** 각 씬을 다시 컷(Cut) 단위로 나누고, 컷마다 카메라 워크(와이드, 클로즈업 등), 액션, 대사 등을 구체화합니다.
4.  **시각화 (Visualization):** ControlNet을 중심으로 다중 레이어 기술을 결합하여 ‘시네마 카툰’ 스타일의 이미지를 일관성 있게 생성합니다.

| 단계 | 기술 | 설명 |
|---|---|---|
| **Pose Layer** | OpenPose / DWpose | 캐릭터의 자세와 구도를 생성합니다. |
| **Depth Layer** | MiDaS / ZoeDepth | 공간의 깊이감과 카메라 방향성을 제어합니다. |
| **Style Layer** | LoRA / DreamBooth | 작품별 고유의 시각적 톤과 스타일을 조절합니다. |

5.  **데이터 패키징 (Data Packaging):** 생성된 모든 시각적/비시각적 정보를 후속 모듈이 읽을 수 있는 데이터 포맷으로 패키징합니다.

---

## 5. 출력 (Output): 시네마 카툰 패키지

### ① 프로젝트 구조 (Project Structure) - `project_structure.json`
전체 프로젝트를 포괄하는 계층화된 JSON 구조로, Orchestrator가 씬 단위 병렬 처리를 용이하게 합니다.
```json
{
  "project_name": "Project Talos",
  "scenes": [
    {
      "scene_id": "S01",
      "scene_name": "바다의 빛",
      "description": "노을지는 해변, 소녀가 파편을 손에 쥔다.",
      "emotion": "calm",
      "cuts": [
        {
          "cut_id": "S01_C1",
          "camera": "wide",
          "dialogue": "...",
          "image_path": "./visuals/S01_C1.png"
        },
        {
          "cut_id": "S01_C2",
          "camera": "close-up",
          "action": "손을 들어 빛을 본다",
          "image_path": "./visuals/S01_C2.png"
        }
      ]
    }
  ]
}
```

### ② AI 카툰 시퀀스 (Visual Draft Comic) - `visuals/`
- **포맷:** `.png` 또는 `.webp`
- **내용:** 생성된 컷 이미지를 시퀀스 순서대로 저장합니다. (e.g., `S01_C1.png`, `S01_C2.png`, ...)

### ③ 감정 곡선 (Emotion Curve) - `emotion_curve.csv`
씬과 컷에 대한 계층적 연결을 추가하여 CHROMA, CUTTURA, ECHO 모듈이 감정 변화를 직접 참조할 수 있도록 구조를 개선했습니다.
```csv
scene_id,cut_id,timestamp,emotion,intensity
S01,S01_C1,0.0,calm,0.8
S01,S01_C2,5.2,wonder,0.9
S02,S02_C1,10.5,tension,0.7
```

### ④ 구조화된 텍스트 로그 (Structured Log) - `narrative_log.md`
기획자 리뷰와 AI의 판단 근거(reasoning)를 병렬로 저장하여 디버깅 및 개선 과정을 용이하게 합니다.
```markdown
# Scene S01
**Narrative Summary:** 소녀가 바다의 빛을 발견한다.
**AI Notes:** 감정톤=calm, 배경=노을, 추천 카메라=pan left
**Reviewer Comment:** 컷2에서 캐릭터 감정 강조 필요
```

---

## 6. 워크플로우 내 위치

```
기획자 아이디어
   ↓
PRISM (스토리+감정→AI 콘티/카툰화)
   ↓
AXIS (라인 아트 및 키프레임)
   ↓
FLUX (보간 애니메이션)
```

---

## 7. 결론
PRISM은 단순한 “연출 설계”가 아니라, **“AI 기획 + 콘티 시각화 엔진”** 으로서, 후속 공정이 의존하는 **데이터 기반의 시네마틱 블루프린트**를 생성하는 핵심 모듈입니다.

**PRISM이 생성한 `project_structure.json`과 `visuals/`는 AXIS 모듈의 입력으로 직접 사용되며, 각 컷 단위 이미지는 라인아트 추출 및 포즈 리타겟팅의 기준 프레임으로 활용됩니다.**
