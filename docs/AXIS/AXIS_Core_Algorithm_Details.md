# AXIS 핵심 알고리즘 상세 구현 가이드

## 1. 개요

이 문서는 `AXIS_Pseudocode_Implementation_Plan.md`에 기술된 의사코드 중, 구체적인 구현 방법 없이는 작성이 어려운 핵심 함수들(`vectorize`, `backproject_to_3d`, `match_and_track`)의 상세한 알고리즘과 구현 가이드를 제공합니다.

---

## 2. 2D 엣지 벡터화 (`vectorize` 함수)

**목표**: 0과 255로 이루어진 엣지 비트맵(grayscale image)을 입력받아, 파라메트릭 곡선(선)들의 리스트를 반환합니다.

**핵심 라이브러리**: `OpenCV`, `SciPy` (선택 사항)

### 2.1. 1단계: 외곽선 찾기 (Contour Finding)

엣지 맵에서 연결된 픽셀들의 집합, 즉 외곽선(Contour)을 찾습니다.

- **함수**: `cv2.findContours()`
- **로직**:
  ```python
  import cv2

  # 엣지 맵은 0이 아닌 값을 갖는 픽셀이 엣지를 의미해야 함
  # threshold를 거쳐 binary 이미지로 만드는 것이 안전
  _, binary_map = cv2.threshold(edge_map, 127, 255, cv2.THRESH_BINARY)

  # contours는 각 외곽선을 구성하는 점들의 리스트
  contours, _ = cv2.findContours(binary_map, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
  
  # 너무 짧은 컨투어는 노이즈일 가능성이 높으므로 필터링
  min_contour_length = 10
  valid_contours = [c for c in contours if len(c) > min_contour_length]
  ```

### 2.2. 2단계: 외곽선 근사화 (Contour Approximation)

외곽선을 구성하는 점이 너무 많으면 비효율적이므로, `cv2.approxPolyDP` (Douglas-Peucker 알고리즘)를 사용하여 점의 개수를 줄입니다.

- **함수**: `cv2.approxPolyDP()`
- **로직**:
  ```python
  simplified_contours = []
  # epsilon 값은 얼마나 디테일을 유지할지를 결정. 클수록 점의 수가 줄어듦.
  epsilon_ratio = 0.005 
  for contour in valid_contours:
      epsilon = epsilon_ratio * cv2.arcLength(contour, True)
      simplified = cv2.approxPolyDP(contour, epsilon, False) # False: open contour
      simplified_contours.append(simplified)
  ```

### 2.3. 3단계: 곡선 피팅 (Curve Fitting) - 선택 사항

더 부드러운 곡선을 원한다면, 근사화된 점들을 B-스플라인(B-spline)으로 피팅할 수 있습니다.

- **라이브러리**: `scipy.interpolate.splprep`
- **로직**:
  ```python
  from scipy.interpolate import splev, splprep

  smooth_lines = []
  for contour in simplified_contours:
      # splprep은 점들의 x, y 좌표를 분리해서 입력받음
      points = contour.reshape(-1, 2).T
      if points.shape[1] < 4: # B-spline은 최소 4개의 점이 필요
          continue

      # B-spline 곡선 모델 생성
      tck, u = splprep(points, s=2.0) # s: smoothing factor

      # 곡선을 따라 100개의 점을 샘플링
      new_points = splev(np.linspace(0, 1, 100), tck)
      smooth_lines.append(np.array(new_points).T)
  ```

---

## 3. 3D 역투영 (`backproject_to_3d` 함수)

**목표**: 2D 라인을 구성하는 픽셀 좌표 `(u, v)`들과 뎁스 맵, 카메라 내부 파라미터를 이용해 3D 공간 좌표 `(X, Y, Z)`를 계산합니다.

### 3.1. 입력 값 정의

- `points_2d`: `(N, 2)` 형태의 2D 픽셀 좌표 배열.
- `depth_map`: `(H, W)` 형태의 뎁스 맵. 각 픽셀은 카메라로부터의 거리(Z)를 의미.
- `camera_intrinsics`: 카메라 내부 파라미터 `K`.

### 3.2. 카메라 내부 파라미터 (Intrinsic Matrix, K)

`K`는 2D 픽셀 좌표와 3D 카메라 좌표계 사이의 변환을 정의하는 `3x3` 행렬입니다.

```
    [[fx, 0,  cx],
K =  [0,  fy, cy],
     [0,  0,  1 ]]
```
- `(fx, fy)`: 카메라의 초점 거리 (픽셀 단위)
- `(cx, cy)`: 이미지의 주점 (principal point), 보통 이미지의 중앙 좌표

### 3.3. 핵심 변환 수식 및 구현 로직

```python
import numpy as np

def backproject_to_3d(points_2d: np.ndarray, depth_map: np.ndarray, K: np.ndarray) -> np.ndarray:
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    points_3d = []
    for u, v in points_2d:
        # 픽셀 좌표는 정수이므로, 정수로 변환하여 뎁스 맵 조회
        u_int, v_int = int(round(u)), int(round(v))

        # 뎁스 맵 경계를 벗어나는지 확인
        if 0 <= v_int < depth_map.shape[0] and 0 <= u_int < depth_map.shape[1]:
            z = depth_map[v_int, u_int]

            # 0 또는 너무 큰 뎁스 값은 무시
            if z <= 0:
                continue

            # 역투영 공식 적용
            x = (u - cx) * z / fx
            y = (v - cy) * z / fy
            
            points_3d.append([x, y, z])

    return np.array(points_3d)
```

---

## 4. 시간적 라인 추적 (`match_and_track` 함수)

**목표**: 이전 프레임의 라인들과 현재 프레임의 라인들 간의 대응 관계를 찾아, 각 라인의 ID를 프레임 간에 일관되게 유지합니다.

### 4.1. 1단계: 위치 예측 (Prediction)

이전 프레임의 각 라인이 현재 프레임에서 어디에 나타날지 `Optical Flow`를 이용해 예측합니다.

- **로직**: 이전 라인의 2D 점들 위치에서 `flow_map` 값을 읽어와 새로운 2D 위치를 계산합니다.

### 4.2. 2단계: 비용 행렬 계산 (Cost Matrix Calculation)

현재 프레임의 각 라인(`current_line`)과, 예측된 이전 라인(`predicted_prev_line`)들 사이의 "거리"를 계산하여 비용 행렬을 만듭니다.

- **거리 측정 기법**: **`Directed Hausdorff Distance`** 를 사용하는 것이 효과적입니다. `A`의 모든 점에서 `B`의 점들까지의 최소 거리 중 최대값을 의미하며, 두 포인트 집합의 유사도를 측정합니다.
  - `scipy.spatial.distance.directed_hausdorff` 함수를 사용할 수 있습니다.

### 4.3. 3단계: 최적 매칭 (Optimal Matching)

비용 행렬을 바탕으로, 전체 비용이 최소화되는 최적의 라인 쌍을 찾습니다.

- **알고리즘**: **헝가리안 알고리즘 (Hungarian Algorithm)** 이 이 문제에 대한 최적의 해를 찾아줍니다.
- **라이브러리**: `scipy.optimize.linear_sum_assignment`
- **로직**:
  ```python
  from scipy.optimize import linear_sum_assignment
  from scipy.spatial.distance import directed_hausdorff

  # cost_matrix[i, j]는 current_line[i]와 predicted_prev_line[j] 간의 거리
  cost_matrix = np.zeros((len(current_lines), len(predicted_prev_lines)))
  for i, curr_line in enumerate(current_lines):
      for j, pred_line in enumerate(predicted_prev_lines):
          cost_matrix[i, j] = directed_hausdorff(curr_line.points_2d, pred_line.points_2d)[0]

  # 헝가리안 알고리즘으로 최적의 매칭 인덱스를 찾음
  row_ind, col_ind = linear_sum_assignment(cost_matrix)

  # 매칭 결과 (row_ind[k], col_ind[k])는 매칭된 쌍을 의미
  ```

### 4.4. 4단계: ID 관리 (ID Management)

매칭 결과를 바탕으로 라인 ID를 업데이트합니다.

- **로직**:
  1.  `linear_sum_assignment`로 얻은 `row_ind`, `col_ind`를 순회하며 매칭된 쌍을 찾습니다.
  2.  일정 거리(threshold) 이내에서 매칭된 경우, 현재 라인(`current_lines[row_ind]`)은 이전 라인(`predicted_prev_lines[col_ind]`)의 ID를 계승합니다.
  3.  매칭되지 않은 현재 라인들은 '새로운 라인'으로 간주하고, `next_line_id`를 새로 부여하고 1 증가시킵니다.
  4.  매칭되지 않은 이전 라인들은 '사라진 라인'으로 간주하고, `line_registry`에서 비활성화(inactive) 처리합니다.
