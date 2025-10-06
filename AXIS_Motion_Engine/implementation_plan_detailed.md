### 실제 구현 및 시각화, 테스트 계획

**목표:** LLM 기반 근육 움직임 모델링 워크플로우의 각 목업 단계를 실제 구현으로 전환하고, 시각화 및 자동화된 테스트를 통해 완성도를 높입니다.

**현재 목업 상태:**
*   **LLM Agent:** 더미 응답을 반환합니다.
*   **OpenSim Agent:** 더미 모델을 로드하고, 일부 파라미터 적용에 경고가 있었습니다.
*   **Data Conversion:** `.sto`를 `.bvh`로 변환하는 로직은 존재하지만, 입력 데이터가 목업 기반입니다.
*   **Blender Automation:** 더미 비디오 파일을 생성합니다.

---

**Phase 1: 실제 LLM 연동 (Real LLM Integration)**

*   **목표:** LLM Agent가 실제 LLM API를 호출하여 유의미한 동작 데이터를 생성하도록 합니다.
*   **세부 계획:**
    1.  **LLM 선택:** 사용할 LLM 서비스(예: OpenAI GPT, Google Gemini, Hugging Face 모델 등)를 결정합니다.
    2.  **API 키 설정:** 선택한 LLM 서비스의 API 키를 안전하게 관리하고 `src/llm_agent/llm_connector.py`에서 사용할 수 있도록 환경 변수 등으로 설정합니다.
    3.  **`llm_connector.py` 수정:** `src/llm_agent/llm_connector.py` 파일 내의 `simulate_llm_api_call` 함수를 실제 LLM API 호출 로직으로 대체합니다. API 요청 및 응답 파싱 로직을 구현합니다.
    4.  **프롬프트 최적화:** `src/llm_agent/prompt_builder.py`의 프롬프트를 실제 LLM이 OpenSim 시뮬레이션에 필요한 정확하고 상세한 JSON 데이터를 생성하도록 최적화합니다.

---

**Phase 2: 견고한 OpenSim 모델 및 실제 시뮬레이션 (Robust OpenSim Model & Real Simulation)**

*   **목표:** 더미 OpenSim 모델을 실제적이고 완전한 인체 모델로 교체하고, LLM이 생성한 데이터를 기반으로 정확한 시뮬레이션을 수행합니다.
*   **세부 계획:**
    1.  **실제 OpenSim 모델 교체:** `models/dummy_human_model.osim` 파일을 실제적이고 완전한 인체 OpenSim 모델 파일로 교체합니다. (예: OpenSim에서 제공하는 `gait2392_simbody.osim` 또는 `full_body.osim` 같은 모델)
    2.  **`simulate_motion.py` 개선:**
        *   이전 경고(`Could not apply parameter for joint shoulder_L`)를 해결합니다. 이는 새 모델의 관절 명칭 및 구조에 맞게 스크립트의 파라미터 적용 로직을 수정하거나, LLM이 생성하는 데이터 형식을 모델에 맞게 조정해야 할 수 있습니다.
        *   LLM이 생성한 JSON 데이터를 OpenSim 모델에 정확히 매핑하고 적용하는 로직을 강화합니다.
    3.  **시뮬레이션 파라미터 조정:** OpenSim 시뮬레이션의 정확도를 높이기 위해 필요한 물리적 파라미터(예: 시간 스텝, 솔버 설정 등)를 조정합니다.
    4.  **`.sto` 파일 유효성 검증:** 시뮬레이션 결과로 생성되는 `.sto` 파일이 유의미하고 완전한 모션 데이터를 포함하는지 확인합니다.

---

**Phase 3: 실제 Blender 렌더링 (Real Blender Rendering)**

*   **목표:** OpenSim에서 변환된 `.bvh` 모션 데이터를 사용하여 Blender에서 실제 애니메이션을 렌더링하고 비디오 파일을 생성합니다.
*   **세부 계획:**
    1.  **Blender 환경 설정:**
    2.  **`apply_motion_and_render.py` 수정:** `src/blender_automation/apply_motion_and_render.py` 파일 내의 더미 비디오 생성 로직을 실제 Blender Python API를 사용하여 렌더링하는 코드로 대체합니다.
        *   `.bvh` 파일 로드 및 캐릭터에 모션 적용.
        *   카메라, 조명, 재질 설정.
        *   렌더링 설정(해상도, 프레임 레이트, 렌더 엔진 등).
        *   애니메이션 렌더링 및 비디오 파일로 저장.
    3.  **Blender 모델 준비:** `models/dummy_character.blend` 파일을 실제 렌더링에 사용할 캐릭터 모델로 교체하거나, 기존 모델을 개선합니다.

---

**Phase 4: 시각화 및 테스트 (Visualization & Testing)**

*   **목표:** 생성된 모션 및 비디오의 품질을 시각적으로 검증하고, 워크플로우의 각 단계 및 전체 시스템에 대한 자동화된 테스트를 구현합니다.
*   **세부 계획:**
    1.  **시각적 검증:**
        *   생성된 `.bvh` 파일을 Blender와 같은 3D 뷰어에서 로드하여 모션이 올바르게 적용되었는지 확인합니다.
        *   최종 렌더링된 비디오 파일(`rendered_animation.mp4`)을 재생하여 시각적 품질과 애니메이션의 정확성을 검토합니다.
    2.  **단위/통합 테스트:**
        *   `src/llm_agent`, `src/opensim_agent`, `src/data_conversion` 모듈에 대한 Python 단위 테스트를 작성합니다. (예: LLM 응답 파싱, OpenSim 모델 로드, 데이터 변환 등)
        *   각 단계의 출력이 다음 단계의 입력으로 올바르게 전달되는지 확인하는 통합 테스트를 구현합니다.
    3.  **종단 간(End-to-End) 테스트:**
        *   전체 워크플로우를 실행하고 최종 비디오 파일의 존재 여부, 크기, 또는 특정 프레임의 내용 등을 검증하는 자동화된 종단 간 테스트를 개발합니다. (예: 비디오 파일의 해시값 비교, 특정 키프레임 이미지 추출 및 비교 등)
