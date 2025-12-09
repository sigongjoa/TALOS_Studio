# 연구 노트: 만화 이미지의 분포 수식화

## 1. 연구 목표

본 연구의 목표는 만화 스타일의 이미지가 갖는 독특한 시각적 특징을 분석하고, 이를 수식화하여 통계적인 분포 모델로 표현하는 것입니다. 이를 통해 만화 이미지의 생성, 변환, 분석 등 다양한 분야에 응용할 수 있는 기반을 마련하고자 합니다.

## 2. 실험 기록 (Version History)

(아래 표는 CI/CD에 의해 `[publish]` 커밋 시 자동으로 업데이트됩니다.)

| 버전 (Version) | 주요 변경사항 (Description) | 소스 코드 (Commit) | 결과물 (Deployment) |
| :--- | :--- | :--- | :--- |
| v0.2.0 | 5개 참조 이미지에 대한 전체 벡터화 파이프라인 실행 및 배포 | [`094eda9`](https://github.com/sigongjoa/TALOS_Studio/commit/094eda9) | [결과 보기](https://sigongjoa.github.io/TALOS_Studio/094eda9/) |
| v0.1.0 | - | - | - |
| | | | |

---

## 3. 배포 및 이력 관리 방법 (How to Deploy and Manage History)

이 프로젝트의 테스트 결과물은 GitHub Actions를 통해 자동으로 웹사이트에 배포되고 이력이 관리됩니다. **핵심은 `output_visualizations` 디렉토리와 `[publish]` 커밋 메시지 키워드입니다.**

### 신규 테스트 결과 배포 절차

1.  **테스트 실행 및 결과물 생성:**
    *   로컬 환경에서 새로운 테스트를 실행합니다.
    *   테스트 결과로 생성된 모든 시각화 파일(이미지, HTML 등)을 **`output_visualizations` 디렉토리 안에 저장**합니다. 이 디렉토리의 내용을 완전히 새로운 결과물로 채웁니다.

2.  **코드 및 결과물 커밋:**
    *   변경된 소스 코드와 함께, 새로운 결과물이 담긴 `output_visualizations` 디렉토리의 내용을 커밋합니다.
    *   이 결과를 웹사이트 이력에 남기고 싶다면 **커밋 메시지 마지막에 `[publish]` 키워드를 반드시 포함**해야 합니다.

    **커밋 예시:**
    ```bash
    # 1. 변경된 모든 파일을 스테이징
    git add .

    # 2. [publish] 키워드를 포함하여 커밋
    git commit -m "Feat: Add new blur effect analysis [publish]"
    ```

3.  **`main` 브랜치에 푸시:**
    *   해당 커밋을 `main` (또는 `master`) 브랜치로 푸시합니다.
    ```bash
    git push origin main
    ```

### 푸시 이후 자동화 프로세스

`main` 브랜치에 `[publish]` 키워드가 포함된 커밋이 푸시되면, CI/CD 워크플로우가 자동으로 실행되어 다음 과정을 수행합니다.

1.  **결과물 아카이빙:** `output_visualizations` 디렉토리의 내용이 고유한 커밋 ID 폴더에 저장됩니다.
2.  **이력 업데이트:** 배포 이력(`deployment_history.json`)에 새 커밋 정보가 추가되고, 이 정보를 바탕으로 모든 배포 이력을 보여주는 목차 페이지(`index.html`)가 새로 생성됩니다.
3.  **웹사이트 배포:** 최종 결과물이 [결과 확인 웹사이트](https://sigongjoa.github.io/TALOS_Studio/)에 배포됩니다.

이 과정을 통해, '실험 기록' 표를 수동으로 업데이트할 필요 없이 모든 배포 기록이 웹사이트에 자동으로 누적됩니다.