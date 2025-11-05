# 상세 명세 파일 (Detailed Specifications)

현재 문서는 "NeRF 또는 3DGS를 사용한다", "Blender 또는 Pyrender를 사용한다"와 같이 여러 옵션을 제시하거나 고수준의 기술 스택을 나열하고 있습니다. 실제 구현을 위해서는 다음 사항이 명확하게 정의된 '명세서'가 필요합니다.

## 데이터 명세
각 파이프라인 단계(모듈)가 주고받는 데이터의 정확한 포맷은 `schemas/` 디렉토리에 있는 JSON 스키마 파일로 정의합니다.

**예:** 1단계(다중 뷰 생성)의 결과물은 `schemas/step1_output_schema.json` 파일에 정의된 구조를 따라야 합니다. 이 스키마는 생성된 이미지 파일 목록과 각 이미지에 해당하는 4x4 카메라 변환 행렬 목록을 포함하도록 강제합니다.

## 컴포넌트 명세
사용할 기술의 버전을 포함하여 최종 결정을 내려야 합니다.

**예:** "B-Track은 Stable Diffusion v1.5 모델과 ControlNet v1.1의 Depth 모델을 사용한다."

## API 명세 (선택적)
만약 각 단계를 별도의 마이크로서비스로 구성한다면, 각 서비스 간의 API 엔드포인트, 요청(Request), 응답(Response) 형식을 정의해야 합니다.

## 환경 명세 (Environment Specification)

이 PoC 파이프라인은 비-Docker 환경에서 실행되는 것을 전제로 하며, 모든 개발자와 CI/CD 환경은 다음 명세를 따라야 합니다.

- **운영체제 (Operating System)**: `Ubuntu 22.04`
- **Python 버전**: `3.10.12`
- **CUDA Toolkit**: `11.8`
- **cuDNN**: `8.6` (CUDA 11.8 호환 버전)
- **Blender**: `4.1.1`
- **Python 패키지**: `requirements.txt` 에 명시된 모든 라이브러리 및 해당 버전
- **시스템 라이브러리 (apt-get)**:
    - `libgl1-mesa-glx`
    - `libxi6`
    - `libxrender1`
    - `git`
    - `wget`
