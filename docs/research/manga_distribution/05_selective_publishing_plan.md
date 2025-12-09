# 계획: 선택적 목차 업데이트 기능 구현

## 1. 목표

현재 배포 시스템은 모든 `push`에 대해 목차 페이지(`index.html`)를 업데이트합니다. 이로 인해 사소한 테스트 배포가 모두 목차에 기록되어 목록이 지저분해질 수 있습니다.

본 계획의 목표는, 사용자가 **원하는 배포만 목차에 추가**할 수 있도록 선택적 업데이트 기능을 구현하는 것입니다.

---

## 2. 구현 방식

커밋 메시지에 포함된 특정 꼬리표(flag), **`[publish]`**를 기준으로 목차 업데이트 여부를 결정합니다.

*   **일반 커밋:** `git commit -m "A minor fix"`
    *   결과물은 버전 폴더(`/<commit-hash>/`)에 정상적으로 저장됩니다.
    *   **목차 페이지는 변경되지 않습니다.**
*   **특별 커밋:** `git commit -m "Add new feature [publish]"`
    *   결과물이 버전 폴더에 저장됩니다.
    *   **목차 페이지가 재성성되어, 이 버전이 새로운 항목으로 추가됩니다.**

이 로직은 `.github/scripts/generate_history.sh` 스크립트 파일을 수정하여 구현합니다.

---

## 3. 스크립트 수정 상세 계획

`generate_history.sh` 스크립트의 로직을 아래와 같이 변경합니다.

### 3.1. 플래그 확인 단계 추가

스크립트 상단부에서, 현재 워크플로우를 실행시킨 커밋의 메시지를 확인합니다. 메시지에 `[publish]` 문자열이 포함되어 있는지 여부를 변수(`PUBLISH_TOC`)에 저장합니다.

```bash
# .github/scripts/generate_history.sh

PUBLISH_TOC=false
if [[ "${{ github.event.head_commit.message }}" == *"[publish]"* ]]; then
  PUBLISH_TOC=true
fi
```

### 3.2. 조건부 목차 생성

기존의 목차 페이지(`index.html`) 생성 로직 전체를 `if` 조건문으로 감쌉니다.

```bash
# .github/scripts/generate_history.sh

# ... (상단 생략) ...

# Generate index.html ONLY IF the flag is present
if [ "$PUBLISH_TOC" = true ]; then
  echo "[publish] flag detected. Regenerating index.html..."

  # --- 이 안에 기존의 index.html 생성 코드 전체가 들어감 ---
  # 1. Write top part of the HTML
  # 2. Generate the <ul> list dynamically
  # 3. Write middle part of HTML
  # 4. Add the iframe for the latest result
  # 5. Write the final part of the HTML

else
  echo "No [publish] flag. Skipping index.html regeneration."
fi
```

### 3.3. 결과

*   `[publish]`가 **있으면:** `if`문이 참이 되어, 스크립트는 모든 버전 폴더를 스캔하여 새로운 목차 페이지를 생성합니다.
*   `[publish]`가 **없으면:** `if`문을 건너뛰므로, 기존에 있던 `index.html`이 그대로 유지됩니다. 단, 현재 커밋의 결과물 폴더(`/<commit-hash>/`)는 정상적으로 추가되므로, 고유 주소로의 접근은 가능합니다.

---

## 4. 첫 번째 단계

위 계획에 따라, `.github/scripts/generate_history.sh` 스크립트 파일 수정을 시작합니다.
