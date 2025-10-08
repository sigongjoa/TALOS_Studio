# TALOS 모듈 간 통신 프로토콜 정의서

## 1. 개요

### 1.1. 목적

이 문서는 TALOS 프로젝트를 구성하는 핵심 모듈들(`Orchestrator`, `PRISM`, `AXIS`, `CHROMA` 등)이 상호작용하는 방식, API 명세, 그리고 데이터 흐름에 대한 표준 통신 규약을 정의합니다. 이 문서를 통해 각 모듈 개발자는 다른 모듈과의 연동 방식을 명확히 이해하고, 일관된 방식으로 시스템을 통합할 수 있습니다.

### 1.2. 통신 방식 원칙

- **제어 및 명령 (Control & Command)**: 모듈 간의 작업 시작, 상태 확인 등의 통신은 **RESTful API**를 통해 이루어집니다. 작업 지시는 비동기(asynchronous) 방식을 기본으로 합니다.
- **대용량 데이터 전달 (Large Data Transfer)**: 비디오, 3D 모델, 프레임 데이터, 복잡한 JSON 등 크기가 큰 데이터는 API 요청/응답 본문에 직접 포함하지 않습니다. 대신, 공유 가능한 스토리지(예: AWS S3, Google Cloud Storage)에 데이터를 저장하고, 해당 데이터에 접근할 수 있는 **URL**을 API를 통해 전달합니다.

## 2. 전체 통신 흐름 (Overall Communication Flow)

전체 애니메이션 생성 작업은 `Orchestrator`에 의해 총괄되며, 다음과 같은 순서로 진행됩니다.

1.  **사용자/클라이언트**가 `Orchestrator`에게 새로운 작업 생성을 요청합니다 (`POST /jobs`).
2.  **Orchestrator**는 `PRISM` 모듈에게 연출 생성을 요청합니다.
3.  **PRISM**은 작업 완료 후, 결과물(`cut_spec.json`)의 URL을 `Orchestrator`에게 콜백(callback)으로 알립니다.
4.  **Orchestrator**는 `PRISM`의 결과물 URL을 포함하여 `AXIS` 모듈에게 작화 생성을 요청합니다 (`POST /generate`).
5.  **AXIS**는 작업 완료 후, 결과물(`lines.json`)의 URL을 `Orchestrator`에게 콜백으로 알립니다.
6.  **Orchestrator**는 `AXIS`의 결과물 URL을 포함하여 `CHROMA` 모듈에게 채색 작업을 요청합니다 (`POST /colorize`).
7.  **CHROMA**는 작업 완료 후, 최종 결과물의 URL을 `Orchestrator`에게 콜백으로 알립니다.
8.  **Orchestrator**는 전체 작업 상태를 '완료'로 업데이트하고, 사용자는 최종 결과물을 확인할 수 있습니다.

## 3. API 엔드포인트 명세

### 3.1. Orchestrator API

- **`POST /jobs`**: 새로운 애니메이션 생성 작업을 시작합니다.
  - **Request Body**: `{ "prompt": "...", "style": "..." }`
  - **Response**: `{ "job_id": "job-xyz-123", "status": "pending" }`

- **`GET /jobs/{job_id}`**: 특정 작업의 전체 진행 상태를 조회합니다.
  - **Response**: `{ "job_id": "...", "status": "processing", "current_module": "AXIS", "details": "..." }`

- **`POST /callbacks/job-completed`**: (내부용) 각 모듈이 비동기 작업 완료를 알리기 위해 호출하는 콜백 엔드포인트입니다. (세부사항은 4장 참고)

### 3.2. AXIS API

- **`POST /generate`**: `PRISM`의 결과물을 기반으로 3D 라인 필드 작화 작업을 비동기적으로 시작합니다.
  - **Request Body**:
    ```json
    {
      "job_id": "job-xyz-123",
      "cut_spec_url": "s3://talos-data/job-xyz-123/prism/cut_S01_C02.json",
      "video_source_url": "s3://talos-data/inputs/source_video.mp4"
    }
    ```
  - **Response** (202 Accepted):
    ```json
    {
      "status": "accepted",
      "message": "Line generation task started for job job-xyz-123."
    }
    ```

### 3.3. CHROMA API

- **`POST /colorize`**: `AXIS`의 결과물을 기반으로 채색 작업을 비동기적으로 시작합니다.
  - **Request Body**:
    ```json
    {
      "job_id": "job-xyz-123",
      "lines_data_url": "s3://talos-data/job-xyz-123/axis/scene_S01_C02.json",
      "style_profile_url": "s3://talos-data/styles/ghibli.json"
    }
    ```
  - **Response** (202 Accepted):
    ```json
    {
      "status": "accepted",
      "message": "Colorization task started for job job-xyz-123."
    }
    ```

## 4. 비동기 작업 완료 통보 (Asynchronous Callback Protocol)

시간이 오래 걸리는 작업을 수행하는 모듈(`PRISM`, `AXIS`, `CHROMA`)은 작업이 완료되거나 실패했을 때, 반드시 `Orchestrator`의 콜백 API를 호출하여 상태를 알려야 합니다.

- **콜백 수신 엔드포인트 (on Orchestrator)**: `POST /callbacks/job-completed`
- **Request Body**:
  ```json
  {
    "job_id": "job-xyz-123",
    "module_name": "AXIS",
    "status": "completed", // "completed" or "failed"
    "output_url": "s3://talos-data/job-xyz-123/axis/scene_S01_C02.json", // 성공 시 결과물 위치
    "error_message": null // 실패 시 에러 메시지
  }
  ```

## 5. 핵심 데이터 페이로드 형식

모듈 간에 URL로 전달될 핵심 데이터 파일의 JSON 구조는 각 모듈의 설계 문서에 정의된 바를 따릅니다.

- **`cut_spec.json` (PRISM → AXIS)**: 카메라 정보, 캐릭터 포즈, 감정 곡선 등을 포함합니다.
- **`lines.json` (AXIS → CHROMA)**: 3D 공간 좌표를 포함한 라인 데이터, 레이어 정보, 스타일 프로필 등을 포함합니다. (상세: `AXIS_Code_Specification.md` 참고)
