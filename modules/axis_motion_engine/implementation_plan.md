### **프로젝트명: AI 기반 물리 엔진 활용 캐릭터 모션 자동화 시스템 (MotionEq)**

**최종 목표:** 자연어 프롬프트(LLM)를 통해 OpenSim 물리 엔진으로 캐릭터 모션을 생성하고, 이를 Blender에서 렌더링하여 애니메이션 비디오를 자동 생성하는 시스템 구축.

---

### **Phase 0: 프로젝트 설정 및 환경 구성**

1.  **프로젝트 디렉토리 구조 생성:**
    *   `motion_eq/` (프로젝트 루트 디렉토리)
        *   `src/` (모든 Python 스크립트)
            *   `llm_agent/` (LLM 관련 스크립트)
            *   `opensim_agent/` (OpenSim 관련 스크립트)
            *   `blender_automation/` (Blender 자동화 스크립트)
            *   `data_conversion/` (데이터 변환 스크립트)
            *   `main.py` (전체 워크플로우 오케스트레이션 스크립트)
        *   `models/` (OpenSim `.osim` 파일, Blender `.blend` 파일)
        *   `output/` (생성된 모션 파일, 렌더링된 비디오)
        *   `config/` (API 키, 설정 파일 등)
        *   `docs/` (문서)
        *   `docker/` (Docker 관련 파일: Dockerfile, docker-compose.yml 등)
        *   `requirements.txt` (Python 의존성 목록)
        *   `README.md` (프로젝트 설명)
2.  **Python 가상 환경 설정 (로컬 개발용, Docker 사용 시 선택 사항):**
    *   터미널에서 `motion_eq/` 디렉토리로 이동합니다.
    *   `python -m venv venv` 명령으로 가상 환경을 생성합니다.
    *   `source venv/bin/activate` (Linux/macOS) 또는 `venv\Scripts\activate` (Windows) 명령으로 가상 환경을 활성화합니다.
3.  **핵심 Python 라이브러리 설치 (로컬 개발용, Docker 사용 시 `requirements.txt`에 명시):**
    *   `pip install requests` (LLM API 호출용)
    *   `pip install opensim` (OpenSim Python API)
    *   `pip install numpy scipy` (데이터 처리 및 과학 계산용, 필요시)
    *   `pip freeze > requirements.txt` (설치된 라이브러리 목록 저장)
4.  **LLM API 키 확보:**
    *   사용할 LLM (예: Google Gemini API, OpenAI GPT API 등)의 API 키를 발급받습니다.
    *   보안을 위해 `config/config.py` 파일에 저장하거나 환경 변수로 설정합니다. (예: `os.environ.get("LLM_API_KEY")`)
5.  **OpenSim 모델 준비:**
    *   적절한 인체 근골격계 모델(`.osim` 파일)을 확보하거나 생성합니다. 이 파일을 `models/` 디렉토리에 저장합니다. (예: `models/human_model.osim`)

---

### **Phase 1: LLM 에이전트 개발 (자연어 → 구조화된 데이터)**

**목표:** 사용자의 자연어 프롬프트를 OpenSim이 이해할 수 있는 JSON 형식의 구조화된 데이터로 변환합니다.

1.  **LLM 입력 프롬프트 구조 정의:**
    *   `src/llm_agent/prompt_builder.py` 파일을 생성합니다.
    *   `def build_llm_prompt(user_input_text: str) -> str:` 함수를 구현하여 LLM에 보낼 상세 프롬프트를 구성합니다. 이 프롬프트는 LLM이 특정 JSON 형식으로 응답하도록 유도해야 합니다.
    *   **예시 프롬프트 템플릿:** (기존과 동일)
2.  **LLM API 호출 구현:**
    *   `src/llm_agent/llm_connector.py` 파일을 생성합니다.
    *   `def call_llm_api(prompt: str) -> dict:` 함수를 구현하여 구성된 프롬프트를 LLM API에 전송하고 JSON 응답을 받습니다.
    *   API 인증 (환경 변수 `LLM_API_KEY` 사용), 요청 형식 지정, 응답 파싱 로직을 포함합니다.
    *   API 호출 실패 또는 잘못된 형식의 응답에 대한 오류 처리 로직을 구현합니다.
3.  **JSON 데이터 유효성 검사:**
    *   `src/llm_agent/json_validator.py` 파일을 생성합니다.
    *   `def validate_opensim_json(json_data: dict) -> bool:` 함수를 구현하여 LLM의 출력 JSON이 예상되는 구조와 데이터 유형을 준수하는지 확인합니다.

---

### **Phase 2: OpenSim 에이전트 개발 (구조화된 데이터 → 모션 파일)**

**목표:** LLM으로부터 받은 구조화된 JSON 데이터를 기반으로 OpenSim에서 실제 모션 데이터를 시뮬레이션하고 파일로 저장합니다.

1.  **OpenSim 모델 로딩:**
    *   `src/opensim_agent/simulate_motion.py` 파일을 생성합니다.
    *   `def load_opensim_model(model_path: str) -> opensim.Model:` 함수를 구현하여 `.osim` 모델 파일을 로드합니다. (Docker 컨테이너 내부의 `/app/models` 경로 사용)
2.  **목표 자세/모션 적용:** (기존과 동일)
3.  **역동역학(Inverse Dynamics) 또는 최적화 구현:** (기존과 동일)
4.  **모션 파일 생성:**
    *   `run_simulation` 함수 내에서 시뮬레이션 결과를 OpenSim 호환 `.sto` (kinematics) 또는 `.trc` (marker trajectories) 파일로 `output/` 디렉토리에 저장합니다. (Docker 컨테이너 내부의 `/app/output` 경로 사용)

---

### **Phase 3: 데이터 변환 및 Blender 자동화**

**목표:** OpenSim에서 생성된 모션 파일을 Blender에서 읽을 수 있는 형식으로 변환하고, Blender API를 사용하여 캐릭터에 모션을 적용하고 렌더링합니다.

1.  **OpenSim → Blender 형식 변환기:**
    *   `src/data_conversion/convert_motion.py` 파일을 생성합니다.
    *   `def convert_opensim_to_bvh(opensim_motion_file_path: str, output_bvh_path: str, joint_mapping: dict) -> str:` 함수를 구현합니다.
    *   이 스크립트는 `opensim_agent` 컨테이너 또는 별도의 `data_converter` 컨테이너에서 실행될 수 있습니다.
2.  **Blender 자동화 스크립트:**
    *   `src/blender_automation/apply_motion_and_render.py` 파일을 생성합니다. 이 스크립트는 **`blender_renderer` Docker 컨테이너 내부의 Blender Python 환경에서 실행**될 것입니다.
    *   `def automate_blender(blender_file_path: str, bvh_file_path: str, output_video_path: str) -> None:` 함수를 구현합니다.
    *   이 함수는 다음을 수행합니다:
        *   `models/` 디렉토리에 있는 미리 리깅된 Blender 캐릭터 모델 (`.blend` 파일)을 로드합니다. (컨테이너 내부의 `/app/models` 경로 사용)
        *   변환된 `BVH` (또는 `FBX`) 모션 파일을 임포트합니다. (컨테이너 내부의 `/app/output` 경로 사용)
        *   임포트된 모션 데이터를 캐릭터의 아머쳐(Armature)에 적용합니다.
        *   카메라, 조명, 렌더링 설정 (예: 해상도, 프레임 속도, 출력 형식)을 구성합니다.
        *   애니메이션을 `output/` 디렉토리에 비디오 파일 (예: `.mp4`)로 렌더링합니다. (컨테이너 내부의 `/app/output` 경로 사용)
    *   **Blender Python API (bpy):** Blender의 `bpy` 모듈 사용법을 숙지해야 합니다.

---

### **Phase 4: 통합 및 워크플로우 오케스트레이션**

**목표:** 모든 개별 구성 요소를 연결하여 전체 시스템 워크플로우를 자동화합니다.

1.  **메인 오케스트레이션 스크립트 (`src/main.py`):**
    *   사용자로부터 자연어 입력을 받습니다.
    *   Phase 1의 LLM 에이전트를 호출하여 구조화된 JSON을 얻습니다.
    *   Phase 2의 OpenSim 에이전트를 호출하여 `.sto` 또는 `.trc` 모션 파일을 생성합니다.
    *   Phase 3의 데이터 변환 스크립트를 호출하여 `BVH` 또는 `FBX` 파일로 변환합니다.
    *   **Blender 렌더링 트리거:** `blender_renderer` 컨테이너에 Blender 렌더링 작업을 지시합니다. 이는 `docker-compose exec blender_renderer blender --background --python /app/src/blender_automation/apply_motion_and_render.py`와 같은 명령을 `subprocess` 모듈을 통해 실행하거나, 더 견고한 방법으로는 두 컨테이너 간의 메시지 큐 (예: RabbitMQ, Redis)를 사용하여 작업을 전달하는 방식을 고려할 수 있습니다.
2.  **사용자 인터페이스 (선택 사항):**
    *   `argparse` 모듈을 사용하여 간단한 명령줄 인터페이스 (CLI)를 구현하거나, Flask 또는 Streamlit을 사용하여 기본적인 웹 인터페이스를 구축하여 시스템 사용 편의성을 높일 수 있습니다. 이 UI는 `opensim_agent` 컨테이너 내에서 실행되거나 별도의 `ui` 서비스로 Docker Compose에 추가될 수 있습니다.

---

### **Phase 5: 테스트 및 개선**

**목표:** 시스템의 각 구성 요소와 전체 워크플로우를 테스트하고, 물리적 정확성과 시각적 품질을 개선합니다.

1.  **단위 테스트:**
    *   각 함수/모듈 (LLM 프롬프트 생성, JSON 유효성 검사, OpenSim 모델 로딩, 데이터 변환 로직 등)에 대한 단위 테스트를 작성합니다. (예: `pytest` 사용)
    *   테스트는 해당 컨테이너 내에서 실행됩니다. (예: `docker-compose run opensim_agent pytest src/llm_agent/`)
2.  **통합 테스트:**
    *   다양한 자연어 입력을 사용하여 전체 파이프라인을 테스트합니다.
    *   `docker-compose up`으로 전체 시스템을 실행하고 `src/main.py`를 통해 테스트합니다.
3.  **시각적 검사:**
    *   렌더링된 애니메이션을 물리적 정확성과 시각적 품질 측면에서 비판적으로 평가합니다.
4.  **반복적 개선:**
    *   테스트 결과를 바탕으로 LLM 프롬프트, OpenSim 시뮬레이션 매개변수, Blender 자동화 스크립트를 지속적으로 개선합니다.