# AXIS 3D Line Field Extension: Achieving Viewpoint Invariance

## 1. The Fundamental Limitation of 2D Line Representation

The previously discussed validation pipeline, based on 2D Computer Vision (CV) techniques, operates on a critical assumption: that the structure between consecutive frames is roughly similar, representable by simple 2D translations.

$$ I_t(x, y) \approx I_{t+1}(x + \Delta x, y + \Delta y) $$

This assumption holds for simple camera pans but breaks down under more complex cinematography, leading to significant failures:

- **Problem**: Rapid camera rotations, perspective shifts (parallax), and object rotations cause the 2D projection of lines to change non-linearly.
- **Consequence**: This results in `edge misalignment`, `curvature drift`, `topological tears` (lines breaking apart), and ultimately, `reconstruction failure`.

The root cause is that the line representation is confined to the 2D image plane, lacking any understanding of the 3D space it is projected from.

## 2. The Solution: A 3D-Aware Line Space

To overcome this, we must elevate the line representation from a 2D space to a **"3D-aware Line Space"** or **"Line Field in 3D Space."** In this paradigm, lines are treated as curves existing in a 3D world, and what we see in any given frame is merely a 2D projection of these curves.

## 3. Methodologies for 3D Line Tracking

### 3.1. Method 1: Depth Map Fusion

By incorporating depth information, we can back-project 2D edges into the 3D space.

1.  **Estimate Depth**: For each frame $I_t$, compute a depth map $D_t(x, y) = \text{depth\_estimator}(I_t)$.
2.  **Lift to 3D**: Each point $(x_i, y_i)$ on a 2D edge is lifted to a 3D point $P_i$ using the camera intrinsic matrix $K$.
    $$ P_i = K^{-1} [x_i, y_i, 1]^T D_t(x_i, y_i) $$
3.  **3D Curve**: The AXIS line is now a 3D parametric curve: $s_i(t) = (X(t), Y(t), Z(t))$.

This 3D representation is invariant to camera motion. A change in viewpoint, represented by a camera transformation matrix $T_{cam}$, is simply applied to the 3D curve: $s_i'(t) = T_{cam} \cdot s_i(t)$.

### 3.2. Method 2: Optical Flow & Epipolar Constraint

This method tracks pixel correspondence between frames to maintain line continuity.

1.  **Calculate Flow**: Compute the optical flow field $F(x, y)$ between frames $I_t$ and $I_{t+1}$.
2.  **Track Lines**: The position of a line in the next frame is predicted by interpolating along the flow field.
3.  **Constraint**: The epipolar constraint, $(x', y', 1)^T F (x, y, 1) = 0$, can be used to validate the matches.

This approach is effective for tracking but is vulnerable to fast rotations and occlusions.

### 3.3. Method 3: Hybrid Depth-Flow Tracking (Recommended)

This approach offers the most robust solution by combining the strengths of both depth and flow.

1.  **Unified Data Generation**: For each frame, calculate both the depth map and the optical flow to the next frame.
2.  **Temporal Line Identification**: Assign a unique ID to each detected edge. This ID is tracked across frames.
3.  **State Update**: For each edge, create and update a state that includes its 3D position (from depth) and its motion vector (from flow).

**Implementation Pseudocode:**

```python
# Assume existence of these functions
from .cv_utils import detect_edges, estimate_depth, calc_optical_flow
from .geo_utils import backproject_to_3d

# Data structure to hold line information across frames
line_registry = {}

# --- In the main processing loop ---

# 1. Extract fundamental data from the current frame
edges = detect_edges(frame)
depth_map = estimate_depth(frame)
flow_map = calc_optical_flow(frame, next_frame)

# 2. Update the state of each line
for edge in edges:
    # Find the 3D position of the edge point
    point_3d = backproject_to_3d(edge.xy, depth_map, camera_intrinsics)
    
    # Predict the edge's position in the next frame
    next_xy_prediction = edge.xy + flow_map[edge.xy]
    
    # Update a persistent registry of lines
    # (Matching logic to associate edge with a line_id is required)
    line_id = find_or_create_line_id(edge)
    update_line_registry(line_id, frame_index, point_3d, next_xy_prediction)

```
This hybrid method ensures **Temporal Line Consistency**, allowing the system to track the same object line even as the camera moves dramatically.

## 4. Extended AXIS Renderer: Projection from 3D

With a 3D line representation, the AXIS renderer must be extended to function as a virtual camera.

The rendering of a frame $I_t$ is now a projection $\Pi_t$ of the 3D line set $S_t$:

$$ I_t(x, y) = \Pi_t(S_t) $$

Where $\Pi_t$ is the complete camera projection matrix for that frame, combining intrinsics ($K$) and extrinsics (Rotation $R_t$, Translation $T_t$):

$$ \Pi_t = K[R_t | T_t] $$

This correctly models the physical process of cinematography: the lines exist in 3D, and the final image is a projection determined by the camera's properties at that instant.

## 5. Summary and Path Forward

The 2D-only approach is insufficient for a robust system. By elevating AXIS to a 3D-aware framework, we solve the critical problem of viewpoint invariance.

| Approach | Pros | Cons |
| :--- | :--- | :--- |
| 2D CV-only | Simple, fast | Fails on viewpoint changes |
| + Depth Map | Maintains perspective | Sensitive to depth noise |
| + Optical Flow | Strong object tracking | Higher computational cost |
| **Hybrid (Recommended)** | **Achieves overall consistency** | **Higher implementation complexity** |

**Conclusion**: The identified limitation—line collapse under viewpoint transformation—is a consequence of the framework being confined to 2D. The solution is to represent lines in 3D and track them using a hybrid of depth and optical flow. This ensures that a character's lines, for example, remain continuous and stable even as the virtual camera moves and rotates.
