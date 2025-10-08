# AXIS Framework Validation Pipeline

## 1. Objective: Pre-Training Framework Validation

Before training any generative AI models, it is critical to validate that the core framework of AXIS is fundamentally sound. This validation process aims to answer a single question:

**"Can the AXIS framework reliably extract line-level information from a standard video source, and subsequently render that information back into a visually and temporally consistent sequence?"**

Success in this stage proves that our chosen data representation—the **Line Function Space**—is a stable and viable foundation for subsequent AI model training.

## 2. Conceptual Workflow

The validation is performed through a multi-stage pipeline that uses established Computer Vision (CV) techniques to bootstrap the process without relying on a pre-trained model.

| Step | Action | Description | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | **Input Source** | Use a standard animation or live-action video clip (e.g., a combat scene). | To secure a realistic test case with complex motion and transformations. |
| 2 | **Frame Sampling** | Extract frames from the video at a consistent rate (e.g., 12-24 fps). | To ensure temporal continuity for analysis. |
| 3 | **Line Detection (CV)** | Apply a robust edge detection algorithm to each frame. | To extract a foundational stroke map from pixels. (Examples: HED, DexiNed, DiffEdgeNet). |
| 4 | **Vectorization** | Convert the pixel-based edge maps into vector strokes (parametric curves). | To functionalize the visual data into the AXIS format. (Examples: Potrace, DeepSVG, DiffVG). |
| 5 | **AXIS Renderer** | Render the vector strokes back into a raster image (e.g., by rasterizing the SVG). | To create a visual output that can be compared with the original frame. |
| 6 | **Temporal Stability Check** | Quantitatively measure the consistency between frames. | To verify that the line representation maintains structural integrity during motion. (Metrics: SSIM, Optical Flow, Δκ). |

## 3. Mathematical Formulation and Metrics

We can define the process and its evaluation criteria mathematically:

- Let the original video frame at time $t$ be **$I_t(x, y)$**.
- The set of detected and vectorized line functions is **$S_t = \{s_i(t) \mid s_i(t) = (x_i(t), y_i(t), p_i(t))\}$**.
- The frame rendered back from the line functions is **$\\hat{I}_t(x, y) = R(S_t)$**, where $R$ is the AXIS renderer.

We evaluate the success of this loop using two primary metrics:

1.  **Structural Similarity (Intra-frame):** How well does the rendered frame match the original?
    $$ \text{Error}(t) = 1 - \text{SSIM}(I_t, \hat{I}_t) $$

2.  **Curvature Stability (Inter-frame):** How much does the shape of a corresponding line change between frames?
    $$ \Delta\kappa_i = |\kappa_i(t+1) - \kappa_i(t)| $$

**Validation Success Criteria:**
- **Average SSIM $\\geq 0.85$**: The rendered output is structurally very similar to the original.
- **Average $\\Delta\kappa \\leq 0.05$**: The lines are stable and do not jitter or deform unnaturally over time.

Passing these criteria confirms that **"the AXIS line representation maintains the structural stability of the original video source."**

## 4. Implementation Pseudocode (Python)

The validation loop can be implemented with the following structure:

```python
import cv2

# Assume the existence of these functions
from .cv_utils import edge_detector # e.g., HED or DexiNed
from .vector_utils import vectorize_edges # e.g., Potrace or DiffVG
from .render_utils import render_strokes # Renders vectors to a numpy array
from .metrics import calc_ssim, calc_curvature_change

video_path = "path/to/your/video.mp4"
cap = cv2.VideoCapture(video_path)

previous_strokes = None
metrics_log = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Detect edges from the source frame
    edge_map = edge_detector(frame)

    # 2. Vectorize pixel edges into stroke functions
    current_strokes = vectorize_edges(edge_map)

    # 3. Render the strokes back to a raster image
    rendered_frame = render_strokes(current_strokes, frame.shape)

    # 4. Calculate metrics
    ssim_value = calc_ssim(frame, rendered_frame)
    
    curvature_diff = 0
    if previous_strokes:
        curvature_diff = calc_curvature_change(previous_strokes, current_strokes)
    
    metrics_log.append({"ssim": ssim_value, "curvature_diff": curvature_diff})
    
    previous_strokes = current_strokes

# Analyze metrics_log to check if it meets the success criteria
print(f"Validation finished. Average SSIM: {sum(m['ssim'] for m in metrics_log) / len(metrics_log)}")
```

## 5. Core Rationale

This validation-first approach is built on several key insights:

| Insight | Implication |
| :--- | :--- |
| **Representation Before Training** | AI model training is only meaningful if the target data representation is proven to be stable and expressive. This validation is that proof. |
| **CV as a Foundation** | We can leverage existing, non-trained CV algorithms to create the foundational data (the "base matrix") for the AXIS framework. |
| **Closed-Loop Verification** | Successfully rendering the vectorized data back into a high-fidelity image proves that our Line Function Space is a "closed" space, which is critical for ensuring model convergence during training. |
| **Training as Refinement** | This process establishes a controllable structure *first*. AI training then becomes a more focused task of *refining* this structure (e.g., adding style, emotion, and nuance) rather than creating it from scratch. |

## 6. Conclusion

This validation pipeline is not about testing *how an AI draws*, but about scientifically proving that the *space in which the AI will learn to draw* is mathematically and structurally sound. Successfully completing this stage de-risks the entire project and confirms that the AXIS framework provides a solid foundation for building a truly controllable and stable AI animation system.
