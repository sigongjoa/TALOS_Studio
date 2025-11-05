# CI/CD 및 테스트 전략 (수정판)

## 1. 개요 (Overview)

본 문서는 '만화 컷 → 3D 모델' PoC 파이프라인을 위한 **비-Docker 환경** 기반의 CI/CD 및 테스트 전략을 정의합니다. 모든 스펙은 코드로 관리되고 자동 검증되며, 실행 환경은 GitHub Actions Runner 위에 직접 구축됩니다.

## 2. 배포 결과물 구조 (수정)

`output_for_deployment` 디렉토리는 PoC의 핵심 비교 대상인 **다중 뷰 이미지를 포함**하도록 수정됩니다.

```
output_for_deployment/
├── index.html
├── original.png
├── track_a/
│   ├── view_01.png
│   ├── view_02.png
│   ├── ...
│   ├── model.glb
│   └── rendered.png
└── track_b/
    ├── view_01.png
    ├── view_02.png
    ├── ...
    ├── model.glb
    └── rendered.png
```

## 3. 기술 스택 (확정)

- **CI/CD 플랫폼**: **GitHub Actions**
- **3D 재구성**: **3D Gaussian Splatting**
- **3D 렌더링**: **Blender (스크립트 모드)**
- **Python 패키지 관리**: `requirements.txt`
- **테스트 프레임워크**: **Pytest**

## 4. CI/CD 파이프라인 전략: 역할 분리

CI와 CD의 역할을 명확히 분리하여 파이프라인의 효율성과 안정성을 확보합니다.

- **CI (Continuous Integration)**: **빠른 검증**을 목표로 합니다. 코드의 정합성, 단위 기능, 모듈 간의 인터페이스(계약)를 검증하지만, 시간이 오래 걸리는 3D 재구성 및 렌더링은 실행하지 않습니다.
- **CD (Continuous Deployment)**: **최종 결과물 생성 및 배포**를 목표로 합니다. `main` 브랜치에 병합될 때, 전체 파이프라인을 실행하여 최종 산출물을 만들고 GitHub Pages에 배포합니다.

## 5. CI 파이프라인 워크플로우 (`.github/workflows/ci.yml`)

- **트리거**: `develop` 브랜치 `push`, `main` 브랜치 `pull_request`
- **주요 단계**:
    1.  환경 설정 (Python, 시스템 라이브러리)
    2.  의존성 설치 (`requirements.txt`)
    3.  정적 코드 분석 (Linting)
    4.  **단위/통합 테스트 실행** (`pytest`): 모듈별 기능 및 모듈 간 데이터 규격(Schema) 준수 여부를 검증합니다.

## 6. CD 파이프라인 워크플로우 (`.github/workflows/deploy.yml`)

- **트리거**: `main` 브랜치에 `push`
- **주요 단계**:
    1.  환경 설정 (Python, Blender, 시스템 라이브러리)
    2.  의존성 설치
    3.  **(전체 파이프라인 실행)**: `run_pipeline.py`를 실행하여 `output_for_deployment` 디렉토리에 모든 산출물(다중 뷰 이미지, 3D 모델, 렌더링 이미지)을 생성합니다.
    4.  **(인수 테스트)**: `output_for_deployment` 디렉토리에 모든 파일이 정상적으로 생성되었는지 확인하여 최종 스펙(DoD) 달성 여부를 검증합니다.
    5.  **GitHub Pages 배포**: 검증 완료 후, 해당 디렉토리의 내용을 `gh-pages` 브랜치에 배포합니다.