# 라인 감지 모델 배포 워크플로우 (Line Detection Model Deployment Workflow)

## 개요

이 문서는 라인 감지 모델의 테스트 결과를 웹 페이지로 배포하는 전체 워크플로우를 설명합니다. 모델 실행은 로컬에서 수동으로 이루어지며, 그 결과물은 별도의 스크립트를 통해 웹 배포용으로 패키징됩니다. 최종적으로 GitHub Actions CI/CD 파이프라인을 통해 GitHub Pages에 배포됩니다.

## 1. 모델 테스트 및 결과 생성

라인 감지 모델의 테스트는 개발자가 로컬 환경에서 수동으로 실행합니다. 각 모델은 특정 입력 이미지에 대해 감지 결과를 생성합니다.

*   **모델 실행 스크립트 예시**: `line_detection_comparison/run_comparison.py`
    *   이 스크립트는 `line_detection_comparison/input/` 디렉토리에 있는 단일 이미지(`test_image.jpg` 등)에 대해 HAWP, L-CNN, DSINE 등 여러 라인 감지 모델을 실행합니다.
    *   각 모델의 감지 결과는 `line_detection_comparison/output/` 디렉토리에 `[모델명]_detection.png` 형식으로 저장됩니다 (예: `hawp_detection.png`, `sold2_detection.png`).
    *   일부 모델은 이미지 외에 `[모델명]_detection.json`과 같은 메타데이터 JSON 파일을 생성할 수 있습니다. 이 파일들은 `output/` 디렉토리에 함께 저장됩니다.

**개발자 역할**: 원하는 테스트 이미지를 `input/` 디렉토리에 배치하고, `run_comparison.py`와 같은 모델 실행 스크립트를 실행하여 `output/` 디렉토리에 최신 결과물이 준비되었는지 확인합니다.

## 2. 배포용 패키징

`output/` 디렉토리에 준비된 모델 테스트 결과물은 `package_for_deployment.py` 스크립트를 통해 웹 배포에 적합한 형태로 변환됩니다.

*   **스크립트**: `line_detection_comparison/package_for_deployment.py`
*   **실행 방법**: `python line_detection_comparison/package_for_deployment.py`

**주요 기능**: 
1.  **결과물 스캔**: `line_detection_comparison/output/` 디렉토리에서 `*_detection.png` 패턴을 가진 모든 감지 결과 이미지 파일을 찾습니다.
2.  **원본 이미지 식별**: `line_detection_comparison/input/` 디렉토리에서 소스 이미지(예: `test_image.jpg`)를 식별합니다.
3.  **모델별 페이지 디렉토리 생성**: 각 감지 결과(`*_detection.png`)에 대해 `output_for_deployment/` 디렉토리 내부에 `[모델명]-[타임스탬프]` 형식의 고유한 디렉토리(예: `sold2-20251020103345/`)를 생성합니다.
4.  **파일 복사**: 
    *   원본 이미지를 각 모델 페이지 디렉토리 내 `original.png`로 복사합니다.
    *   해당 모델의 감지 결과 이미지를 각 모델 페이지 디렉토리 내 `detection.png`로 복사합니다.
    *   **메타데이터 JSON 처리**: `output/` 디렉토리에서 `[모델명]_detection.json`과 같은 메타데이터 JSON 파일이 존재하면, 이를 각 모델 페이지 디렉토리 내 `metadata.json`으로 복사하고, 해당 페이지의 `index.html`에 다운로드 링크를 추가합니다.
5.  **동적 `index.html` 생성**: 
    *   각 모델 페이지 디렉토리 내에 `index.html` 파일을 생성합니다.
    *   이 HTML 파일은 하드코딩된 제목과 설명 대신, JavaScript를 포함하여 `output_for_deployment/pages.json` 파일을 동적으로 읽어와 자신의 제목(`<h1>`)과 설명(`p`)을 채웁니다.
6.  **`pages.json` 업데이트**: `output_for_deployment/pages.json` 파일을 업데이트하여 새로 생성된 각 모델 페이지에 대한 항목을 추가합니다. 이 `pages.json`은 메인 쇼케이스 페이지에서 각 모델 페이지로의 링크를 제공하는 메타데이터 역할을 합니다.

**개발자 역할**: 모델 테스트 후, 이 스크립트를 실행하여 최신 결과물이 웹 배포용으로 패키징되도록 합니다.

## 3. CI/CD를 통한 배포

배포용으로 패키징된 파일들은 GitHub Actions CI/CD 파이프라인을 통해 GitHub Pages에 자동으로 배포됩니다.

*   **CI/CD 설정**: `.github/workflows/deploy.yml`
*   **트리거**: `main` 또는 `master` 브랜치에 코드가 푸시될 때 워크플로우가 자동으로 시작됩니다.
*   **배포 대상**: `output_for_deployment/` 디렉토리의 모든 콘텐츠가 GitHub Pages로 배포됩니다.

**개발자 역할**: `package_for_deployment.py` 스크립트 실행 후, `output_for_deployment/` 디렉토리 내의 변경 사항(새로 생성된 페이지 디렉토리, 업데이트된 `pages.json` 등)을 `git add .`, `git commit`, `git push` 명령어를 통해 원격 저장소에 푸시합니다. 푸시가 완료되면 GitHub Actions가 자동으로 배포를 진행합니다.

## 4. 웹사이트 구조

배포된 웹사이트는 다음과 같은 구조를 가집니다:

*   **메인 쇼케이스 페이지**: `[GitHub Pages URL]/index.html`
    *   `output_for_deployment/pages.json`에 정의된 모든 모델 페이지 목록을 보여줍니다. 각 항목은 해당 모델 페이지로의 링크를 포함합니다.
*   **각 모델별 결과 페이지**: `[GitHub Pages URL]/[모델명]-[타임스탬프]/index.html`
    *   해당 모델의 원본 이미지와 감지 결과 이미지를 나란히 보여줍니다.
    *   페이지의 제목과 설명은 `pages.json`에서 동적으로 가져와 표시됩니다.
    *   메타데이터 JSON 파일이 존재할 경우, 해당 파일을 다운로드할 수 있는 링크가 제공됩니다.

## 결론

이 워크플로우는 모델 테스트와 웹 배포 과정을 분리하여 효율성을 높입니다. 개발자는 로컬에서 모델 결과를 유연하게 생성하고, `package_for_deployment.py`를 통해 이를 쉽게 웹에 공유할 수 있습니다. CI/CD는 배포의 자동화와 일관성을 보장합니다.