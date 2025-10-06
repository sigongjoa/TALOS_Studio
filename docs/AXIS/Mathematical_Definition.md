# Mathematical Definition of AI Stroke Generation
(확률적 곡선 생성의 수학적 정의)

---

## 1. Core Problem: From Pixels to Mathematical Functions

The fundamental challenge is to redefine image generation from a pixel-based problem to a vector-based, sequential curve generation problem. We are not generating a static grid of pixels, but rather modeling the **act of drawing** itself.

This can be mathematically defined as **Probabilistic Parametric Stroke Generation** or **Sequential Curve Generation in Continuous Space**.

---

## 2. Mathematical Formulation

Our goal is to learn a function, $f_{	heta}$, that, given a set of conditions $x$ (e.g., pose, emotion, layout), generates a sequence of strokes. Each stroke is a continuous curve parameterized by time $t$, defined by its coordinates $(x_t, y_t)$ and attributes like pressure $p_t$.

### 2.1. The Drawing Function

The overall drawing model can be expressed as a function that maps an input condition to a space of continuous curves:

$$ f_{	heta} : X \rightarrow S $$

Where:
- $X$: The input space, containing conditional information like pose keypoints, layout bounding boxes, and emotional cues.
- $S$: The output space, which is the space of all possible sets of continuous curves (strokes).
- $	heta$: The learnable parameters of our model.

### 2.2. The Stroke as a Continuous Function

A single stroke $s(t)$ is a continuous function parameterized by time $t \in [0, 1]$:

$$ s(t) = (x(t), y(t), p(t)) $$

- $(x(t), y(t))$: The coordinates of the point on the curve at time $t$.
- $p(t)$: The pressure (thickness) of the stroke at time $t$.

This curve can be represented using parametric forms like Bézier curves, B-Splines, or Catmull-Rom splines, which are the fundamental units of mathematical drawing:

$$ \mathbf{r}(t) = (x(t), y(t)) = \left( \sum_{i=0}^{n} a_i t^i, \sum_{i=0}^{n} b_i t^i \right) $$

---

## 3. Learning Perspective: A Sequential Prediction Problem

From a machine learning perspective, generating a stroke is a sequential prediction problem, analogous to language modeling. The model predicts the next point on the curve based on the previously drawn points and the initial conditions.

The probability of generating a sequence of points $s_{1:T}$ given an input $x$ is the product of conditional probabilities:

$$ P(s_{1:T} | x) = \prod_{t=1}^{T} P(s_t | s_{1:t-1}, x) $$

This formulation allows us to use architectures like Transformers, which excel at modeling sequential data, by treating the points on a curve as a sequence of tokens.

---

## 4. Positioning: A Probabilistic Vector Drawing System

Our approach can be formally defined as a **Probabilistic Vector Drawing System** or a **Generative Curve Model**. Its key characteristics are:

1.  **Conditional Generation:** It generates curves based on a set of input conditions $x$.
2.  **Sequential Optimization:** It optimizes the time-series properties of each curve (e.g., smoothness, curvature).
3.  **Structured Output:** The result is not a flat image but a structured, machine-readable data format (e.g., SVG, JSON Stroke Graph).

Mathematically, the core function is:

$$ \text{Draw}: X \xrightarrow{f_{\theta}} \{s_1(t), s_2(t), \dots, s_N(t)\} $$

Where $f_{	heta}$ is the conditional probabilistic generation function, and each $s_i(t)$ is a continuous stroke function (e.g., a Bézier curve).

---

## 5. Related Research and Keywords

This approach builds upon a rich history of research in computer graphics, vision, and machine learning.

| Keyword | Field | Representative Research / Reference |
|---|---|---|
| **Neural Sketch RNN** | Sequential Vector Curve Generation | Google Brain, “A Neural Representation of Sketch Drawings” (Ha & Eck, 2017) |
| **DiffVG** | Differentiable Vector Graphics | Li et al., 2020, SIGGRAPH |
| **DeepSVG** | SVG Vector Sequence Generation | Carlier et al., NeurIPS 2020 |
| **Im2Vec** | Image-to-Vector Conversion | Reddy et al., CVPR 2021 |
| **Stroke-based Rendering (SBR)** | Mathematical Foundations of AI Drawing | Haeberli, 1990; Hertzmann, 2001 |
| **VectorFlow / StrokeNet** | Continuous Stroke Generation | Jin et al., 2022 |
| **BezierGAN / BezierSketch** | Bézier Curve-based Generation | Liu et al., 2019 / Zou et al., 2021 |
