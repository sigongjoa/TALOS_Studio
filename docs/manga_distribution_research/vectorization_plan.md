# 계획: vtracer를 이용한 이미지 벡터화

## 1. 개요

본 문서는 흑백의 라인 아트(Line Art) 이미지를 `vtracer` 라이브러리를 사용하여 SVG 벡터 데이터로 변환하는 프로세스의 구현 및 배포 계획을 정의합니다.

최종 목표는 `vtracer`가 생성한 벡터 결과물을 시각적으로 확인할 수 있는 웹페이지를 배포하는 것입니다.

---

## 2. 구현 방식: `vtracer` 라이브러리 활용

복잡한 벡터화 알고리즘을 직접 구현하는 대신, 검증된 오픈소스 라이브러리인 `vtracer`의 Python 바인딩을 사용합니다. 이를 통해 전체 파이프라인을 아래와 같이 간소화합니다.

1.  **선 추출:** 원본 이미지에서 `MangaLineExtraction` 모델을 사용하여 벡터화에 적합한 Line Art 이미지를 생성합니다.
2.  **벡터화:** `vtracer.convert_image_to_svg_py()` 함수를 호출하여, Line Art 이미지를 입력으로 받아 최종 SVG 파일을 직접 생성합니다.
3.  **시각화:** 원본, Line Art, 최종 SVG 결과물을 나란히 비교할 수 있는 `index.html`을 생성합니다.

---

## 3. `vtracer` 상세 파라미터

`vtracer`의 Python 함수는 SVG 변환 시 아래와 같은 다양한 파라미터를 조절하는 기능을 제공합니다. 추후 `run_standalone_vectorizer.py` 스크립트에 이 파라미터들을 커맨드 라인 인자로 추가하여, 결과물의 품질을 세밀하게 튜닝할 수 있습니다.

*   `corner_threshold`: 코너를 얼마나 날카롭게 감지할지 (값이 클수록 둥글게 처리)
*   `length_threshold`: 얼마나 긴 경로를 유의미한 선으로 볼 것인지
*   `filter_speckle`: 지정된 크기보다 작은 노이즈(반점)를 얼마나 제거할지
*   `max_iterations`: 곡선 피팅의 정확도를 높이기 위해 얼마나 많이 반복 계산할지
*   `splice_threshold`: 여러 곡선 경로를 얼마나 부드럽게 연결할지
*   `path_precision`: SVG 경로의 소수점 이하 정밀도

---

## 4. 현재 상태

*   `vtracer` 라이브러리를 사용하는 파이프라인 구현이 완료되었습니다.
*   `run_standalone_vectorizer.py`를 실행하여 결과물을 생성하고, `git push`를 통해 배포할 수 있습니다.