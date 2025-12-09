# 전체 프로세스 및 워크플로우 (Process & Workflow)

현재 CI/CD 계획은 성공적인 흐름(Happy Path)만을 다루고 있습니다. 실제 프로젝트에서는 개발 및 운영을 위한 구체적인 프로세스가 필요합니다.

## 데이터 흐름도 (Text-based Data Flow)

1.  **입력 (Input)**:
    -   사용자가 `input/original.png` 제공

2.  **1단계: 다중 뷰 생성 (Multi-view Generation)**
    -   **Input**: `input/original.png`
    -   **Process**: `run_view_synthesis.py` (A-Track, B-Track 각각 실행)
    -   **Output**: `temp/track_a/` 와 `temp/track_b/` 디렉토리에 다음 파일 생성:
        -   `view_01.png`, `view_02.png`, ...
        -   `camera_poses.json` (`schemas/step1_output_schema.json` 규격 준수)

3.  **2단계: 3D 재구성 (3D Reconstruction)**
    -   **Input**: `temp/track_a/` 와 `temp/track_b/` 의 이미지 및 `camera_poses.json`
    -   **Process**: `run_3d_reconstruction.py` (A-Track, B-Track 각각 실행)
    -   **Output**: `temp/track_a/model.glb` 와 `temp/track_b/model.glb` 생성

4.  **3단계: 2D 렌더링 (2D Rendering)**
    -   **Input**: `temp/track_a/model.glb` 와 `temp/track_b/model.glb`
    -   **Process**: `run_rendering.py` (A-Track, B-Track 각각 실행)
    -   **Output**: `temp/track_a/rendered.png` 와 `temp/track_b/rendered.png` 생성

5.  **4단계: 패키징 (Packaging)**
    -   **Input**: `temp/` 디렉토리의 모든 결과물
    -   **Process**: `package_results.py`
    -   **Output**: `output_for_deployment/` 디렉토리에 최종 결과물 복사 및 `index.html` 생성

6.  **출력 (Output)**:
    -   `output_for_deployment/` 디렉토리의 모든 파일이 GitHub Pages에 배포됨

## 예외 처리 (Error Handling) 정책

**예:** "A-Track 실행은 성공했으나 B-Track이 실패할 경우, CI/CD 파이프라인은 실패로 간주하고 배포하지 않는다." 또는 "A-Track의 결과물만이라도 배포한다."

## 테스트 전략 (Test Strategy)

**예:** "NeRF 모델은 CI/CD에서 실행하기 너무 무거우므로, 로컬에서 test_3d_reconstruction.py 스크립트로 사전 검증한다."

## 로컬 개발 환경 설정 (비-Docker 가이드)

모든 개발자는 CI/CD 환경과의 일관성을 유지하기 위해 다음 절차에 따라 로컬 환경을 설정합니다.

**1. 시스템 의존성 설치**

`detailed_specifications.md`의 '환경 명세'에 명시된 시스템 라이브러리를 설치합니다.

```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libxi6 libxrender1 git wget
```

**2. Python 가상 환경 설정**

프로젝트 루트 디렉토리에서 Python 3.10을 사용하여 가상 환경을 생성하고 활성화합니다.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

**3. Python 의존성 설치**

활성화된 가상 환경에서 `requirements.txt` 파일에 명시된 모든 라이브러리를 설치합니다.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Blender 설치**

`detailed_specifications.md`에 명시된 버전의 Blender를 다운로드하고, 터미널에서 바로 실행할 수 있도록 경로를 설정합니다.

```bash
wget https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-x86_64.tar.xz
tar -xf blender-4.1.1-linux-x86_64.tar.xz
# 터미널 세션에 Blender 경로 추가 (영구적으로 추가하려면 .bashrc 또는 .zshrc에 추가)
export PATH="$PWD/blender-4.1.1-linux-x86_64:$PATH"
```

**5. 환경 변수 설정**

필요한 API 키나 설정 값들을 `.env` 파일로 생성하고, `python-dotenv` 라이브러리를 사용하여 스크립트에서 로드합니다.
