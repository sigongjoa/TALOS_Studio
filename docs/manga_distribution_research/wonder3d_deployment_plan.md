# Wonder3D 배포 워크플로우 계획

## 목표
단일 2D 이미지로부터 3D 모델(메쉬)을 생성하고, 이를 웹 페이지를 통해 시각적으로 보여주는 쇼케이스를 배포합니다.

## 제안 워크플로우

### 1. 환경 설정
*   **Conda 환경 및 Pip 종속성 설치:**
    *   Wonder3D 프로젝트에 필요한 Python 패키지 및 라이브러리를 위한 격리된 Conda 환경을 생성하고 활성화합니다.
    *   `requirements.txt`에 명시된 모든 종속성을 `pip`을 사용하여 설치합니다.
    *   `git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch`와 같은 특별한 종속성도 설치합니다.
*   **모델 체크포인트 다운로드 (수동/캐싱 필요):**
    *   Wonder3D 및 SAM(Segment Anything Model)에 필요한 대용량 모델 체크포인트(가중치 파일)를 다운로드합니다.
    *   CI/CD 환경에서는 이 단계가 병목 현상이 될 수 있으므로, 캐싱 전략을 고려하거나 사전에 다운로드된 모델을 사용하는 방안을 모색합니다.

### 2. 3D 에셋 생성 스크립트 (`run_wonder3d_pipeline.py`)
*   **기능:** 입력 2D 이미지로부터 3D 모델(메쉬)을 생성하는 전체 파이프라인을 자동화하는 Python 스크립트입니다.
*   **세부 단계:**
    *   **입력 처리:** 지정된 디렉토리에서 입력 2D 이미지를 가져옵니다.
    *   **Wonder3D 추론:** Wonder3D의 `test_mvdiffusion_seq.py` 스크립트를 실행하여 입력 이미지로부터 다중 뷰 노멀 맵(normal map) 및 컬러 이미지(color image)를 생성합니다.
    *   **메쉬 추출:** 생성된 다중 뷰 이미지를 기반으로 Instant-NSR (`./instant-nsr-pl/launch.py`) 또는 NeuS (`./NeuS/run.sh`)와 같은 메쉬 추출 도구를 사용하여 3D 메쉬(예: `.obj`, `.glb` 형식)를 생성합니다.
    *   **선택적 렌더링:** 생성된 3D 메쉬의 다양한 뷰를 2D 이미지 또는 비디오로 렌더링하여 시각적 자료를 추가합니다.
    *   **출력 정리:** 생성된 다중 뷰 이미지, 3D 메쉬, 렌더링된 뷰 등의 모든 결과물을 구조화된 출력 디렉토리(예: `wonder3d_outputs/<timestamp>/<image_name>/`)에 저장합니다.

### 3. 배포 패키징 스크립트 (`package_wonder3d_results.py`)
*   **기능:** `run_wonder3d_pipeline.py`에 의해 생성된 3D 에셋을 웹 쇼케이스 형태로 패키징하는 Python 스크립트입니다.
*   **세부 단계:**
    *   **출력 디렉토리 스캔:** `run_wonder3d_pipeline.py`가 결과를 저장한 출력 디렉토리를 스캔하여 각 3D 에셋 세트(입력 이미지, 다중 뷰 이미지, 메쉬)를 식별합니다.
    *   **개별 웹 페이지 생성:** 각 3D 에셋 세트에 대해 `output_for_deployment/` 디렉토리 내부에 전용 HTML 웹 페이지를 생성합니다.
        *   이 웹 페이지는 원본 입력 2D 이미지, Wonder3D가 생성한 다중 뷰 이미지, 그리고 메쉬를 위한 간단한 인터랙티브 3D 뷰어(예: Three.js 또는 Google Model Viewer JavaScript 라이브러리 활용)를 포함합니다.
        *   3D 뷰어는 사용자가 마우스로 모델을 회전하거나 확대/축소할 수 있도록 구현합니다.
    *   **메인 쇼케이스 업데이트:** `output_for_deployment/pages.json` 파일을 업데이트하여 새로 생성된 각 개별 웹 페이지에 대한 링크와 설명을 추가합니다. 이 `pages.json` 파일은 메인 인덱스 페이지에서 모든 쇼케이스 항목을 나열하는 데 사용됩니다.

### 4. CI/CD 통합 (GitHub Actions)
*   **`.github/workflows/deploy.yml` 수정:**
    *   **환경 설정 단계 추가:** Wonder3D 환경 설정(Conda 환경 생성, 종속성 설치) 단계를 GitHub Actions 워크플로우에 포함합니다.
    *   **파이프라인 실행:** 예제 입력 이미지 세트에 대해 `run_wonder3d_pipeline.py` 스크립트를 실행합니다.
    *   **패키징 실행:** `package_wonder3d_results.py` 스크립트를 실행하여 배포를 위한 웹 페이지 및 에셋을 준비합니다.
    *   **GitHub Pages 배포:** `output_for_deployment/` 디렉토리의 내용을 GitHub Pages에 배포하여 웹 쇼케이스를 공개적으로 접근 가능하게 만듭니다.

## 주요 고려사항 및 과제
*   **GPU 요구사항:** Wonder3D 추론 및 메쉬 추출 과정은 상당한 GPU 자원을 필요로 합니다. GitHub Actions 러너에서 GPU 사용 가능 여부 및 성능을 사전에 확인하고, 필요한 경우 GPU 지원 러너를 사용하도록 설정해야 합니다.
*   **모델 체크포인트 관리:** 대용량 모델 체크포인트의 다운로드 및 관리는 CI/CD 파이프라인의 실행 시간을 늘리고 제한에 도달할 수 있습니다. GitHub Actions 캐싱 기능을 활용하거나, Docker 이미지에 모델을 미리 포함시키는 등의 효율적인 전략이 필요합니다.
*   **3D 뷰어 통합:** 웹 페이지에 3D 모델을 효과적으로 표시하기 위한 JavaScript 기반의 3D 뷰어 라이브러리(예: Three.js, Model Viewer)를 선택하고 통합하는 작업이 필요합니다. 이는 웹 개발 지식을 요구합니다.
*   **오류 처리 및 로깅:** 파이프라인의 각 단계에서 발생할 수 있는 오류를 적절히 처리하고, 디버깅을 위한 상세한 로깅 시스템을 구축해야 합니다.
*   **확장성:** 향후 더 많은 입력 이미지 또는 다양한 모델을 처리할 수 있도록 파이프라인의 확장성을 고려하여 설계합니다.
