# PoC 파이프라인: 기술적 타당성 평가 및 워크플로우

“단일 만화 컷에서 다중 시점 이미지를 합성하고 → NeRF로 3D화 → 리깅/애니메이션화” 파이프라인 전체의 기술적 실현 가능성 평가입니다.

---

## 🧩 전체 파이프라인 기술적 타당성 평가

### 1️⃣ 단일 컷 → 다중 시점 이미지 생성

*   **핵심 목표:** 한 장의 만화 컷을 기반으로, “좌/우/후/상/하 시점” 같은 다른 각도 이미지를 생성합니다.
*   **기술적 가능성:** ✅ **가능**

*   **모델 후보:**
    *   **Zero-1-to-3 / Zero123-XL:** 단일 이미지에서 여러 시점 이미지를 추론 (canonical → rotated view)
    *   **Stable Diffusion + ControlNet (depth / normal / pose):** 원본 컷을 컨트롤맵으로 두고 다른 각도 prompt와 함께 제어 가능
    *   **LLM 보조 (Gemini / GPT-4o / Phi-4 / Claude):** “해당 컷의 반대편 시점은 어떤 구도일까?” 프롬프트 자동 생성

*   **⚠️ 한계:**
    *   Zero123 계열 모델은 만화/애니메이션 스타일에 특화된 데이터가 부족하여, 사실적인 이미지에 비해 2D 셀룩(cel-look) 스타일에서는 아티팩트(artifact)가 발생할 수 있습니다.
    *   **해결책:** Fine-tuning 또는 **LoRA (만화체 보정)**를 적용하여 실용성을 높일 수 있습니다.

*   **💡 결론:**
    *   **"가능함"**. 특히 `Zero123 + 만화체 LoRA + LLM 프롬프트 오케스트레이션` 구조를 활용하면 PoC 수준에서 유의미한 결과를 얻을 수 있습니다.

---

### 2️⃣ 다중 시점 이미지 → 3D 모델 복원 (NeRF/3DGS 계열)

*   **핵심 목표:** 생성된 다중 시점 이미지를 입력으로 NeRF 기반의 3D 재구성(reconstruction)을 수행합니다.
*   **기술적 가능성:** ✅ **가능**

*   **도구 후보:**
    *   **Instant-NGP (NVIDIA)**
    *   **NeRFStudio**
    *   **3D Gaussian Splatting (GSplat)**

*   **입력 요구사항:**
    *   여러 각도의 이미지가 동일한 객체로 인식될 수 있어야 합니다.
    *   카메라 포즈(pose)가 정확하거나, 근사치라도 제공되어야 합니다. (**COLMAP** 등으로 추정 가능)

*   **⚠️ 한계:**
    *   LLM/T2I로 생성한 다중 시점 이미지는 **정확한 기하학적 일관성(geometry consistency)이 부족**하여 NeRF 학습을 불안정하게 만들 수 있습니다.
    *   **해결책:**
        *   (a) Depth map consistency loss 추가
        *   (b) Image registration 후 pseudo-pose 추정
        *   (c) DreamGaussian, StableDreamFusion처럼 “latent NeRF fine-tuning” 방식 사용

*   **💡 결론:**
    *   **"기술적으로 가능하지만, 정합성 확보 필요"**. 즉, 각 이미지의 depth map 정렬(alignment)을 잘 수행하면 학습 성공률을 높일 수 있습니다.

---

### 3️⃣ 3D 모델 → 리깅/애니메이션

*   **핵심 목표:** 복원된 3D 모델을 애니메이션 가능한 형태(스켈레톤 + 스킨 웨이팅)로 전환합니다.
*   **기술적 가능성:** ✅ **가능**

*   **도구 후보:**
    *   Blender **Auto-Rig Pro**, **Mixamo** Auto-Rigging, **SMPLify-X**, **Deep Rigging Networks** 등
    *   최근에는 **OpenPose + Mesh Deformation** 조합으로 자동 본(bone) 생성도 가능합니다.

*   **⚠️ 한계:**
    *   만화체 모델은 기하학적 구조가 단순하지 않고(과장된 비율, 큰 머리/손 등), 이로 인해 자동 리깅 시 오류가 발생할 수 있습니다.
    *   **해결책:** “Stylized rigging helper”를 커스텀 스크립트로 작성하여 해결 가능합니다.

*   **💡 결론:**
    *   **"애니메이션용 리깅은 가능"**. 다만, 만화체에 특화된 본 구조 커스터마이징이 필요합니다.

---

### 🧠 종합 기술 평가

| 단계 | 기술 가능성 | 주요 기술 스택 | 난이도 | 리스크 |
| :--- | :--- | :--- | :--- | :--- |
| ① 단일 컷 → 다중 시점 생성 | ✅ 높음 | Zero123, ControlNet, LLM | ★★★ | 스타일 일관성 |
| ② 다중 시점 → 3D 복원 | ⚠️ 중간 | NeRF, Gaussian Splatting, COLMAP | ★★★★ | 기하 정합성 |
| ③ 3D 모델 → 리깅/애니메이션 | ✅ 높음 | Blender Auto-Rig, Mixamo | ★★★ | 만화체 스켈레톤 맞춤 |
| ④ 전과정 자동화 (파이프라인화) | ⚠️ 낮음 | Python + Blender API + SD/NeRF 통합 | ★★★★★ | 도구 간 인터페이스 |

---

### 🔧 요약 결론

*   **Proof of Concept (PoC) 수준에서는 충분히 실현 가능합니다.**
*   상용화 수준으로 발전시키기 위해서는 다음 사항들이 필요합니다:
    1.  Multi-view 이미지 생성 시 **geometry constraint 강화**
    2.  NeRF 학습 시 **depth supervision 추가**
    3.  스타일 일관성 유지를 위한 **LoRA fine-tuning**
