# 완료의 정의 (Definition of Done - DoD)

PoC(Proof of Concept)는 "개념 증명"이 목적이므로, 언제 "증명"이 완료되었는지 판단할 기준이 명확해야 합니다.

## 기능적 DoD
"사용자가 original.png를 제출했을 때, index.html에서 A트랙과 B트랙의 model.glb 파일이 렌더링되고, rendered.png 이미지가 나란히 비교되어 보이면 완료로 간주한다."

## 비기능적 DoD (성능/품질)

### 성능
"전체 파이프라인(로컬 실행 또는 CD 배포 기준)은 15분 이내에 완료되어야 한다."

### 품질
"B-Track의 결과물이 기하학적으로 깨지더라도, 3D 모델 파일(model.glb) 생성이 성공적으로 완료되어야 한다."
