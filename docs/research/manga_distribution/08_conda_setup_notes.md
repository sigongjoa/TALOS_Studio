# Conda 환경 설정 시 주의사항

## 문제: `conda activate` 오류
`conda activate <환경이름>` 명령 실행 시 `CondaError: Run 'conda init' before 'conda activate'` 오류가 발생하는 경우가 있습니다.

## 원인
이 오류는 conda가 셸 환경에 제대로 초기화되지 않았을 때 발생합니다. `conda init` 명령은 셸이 conda 환경을 활성화하고 비활성화할 수 있도록 셸의 구성 파일(예: `.bashrc`, `.zshrc`, `.profile`)을 수정합니다.

## 해결 방법
1. **`conda init` 실행:**
   ```bash
   conda init bash # 또는 사용 중인 셸에 따라 zsh, powershell 등
   ```
   이 명령은 셸 구성 파일을 수정합니다.

2. **셸 재시작 또는 구성 파일 소싱:**
   `conda init`을 실행한 후에는 변경 사항을 적용하기 위해 현재 셸을 닫고 새로 열거나, 다음 명령을 사용하여 구성 파일을 다시 로드해야 합니다.
   ```bash
   source ~/.bashrc # 또는 사용 중인 셸의 구성 파일 경로
   ```

3. **환경 활성화 재시도:**
   이제 `conda activate <환경이름>` 명령을 다시 실행하여 환경을 활성화할 수 있습니다.
   ```bash
   conda activate wonder3d
   ```

## Wonder3D 환경 설정 시 적용
Wonder3D 환경 설정 중 이 문제가 발생하면 위 단계를 따라 해결할 수 있습니다. 특히 CI/CD 환경에서는 셸 초기화가 자동으로 이루어지지 않을 수 있으므로, 스크립트 내에서 `conda init` 및 `source` 명령을 적절히 사용하는 것을 고려해야 합니다.
