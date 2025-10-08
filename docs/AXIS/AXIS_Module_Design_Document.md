# AXIS Module Design Document

## 1. Overview

**AXIS** is the core animation and keyframe generation engine in the TALOS pipeline. It serves as the bridge between the directorial decisions made by **PRISM** and the final visual output. Its primary function is not to generate raster images, but to **calculate, generate, and manage line information** as a system of vector-based strokes.

AXIS embodies the principle of "Controllable Art" by treating drawing as a computational process, transforming the abstract concept of "a drawing" into a structured set of mathematical data.

## 2. Architecture and Roles

AXIS operates through a sequential pipeline of specialized sub-modules:

| Step | Component | Description |
| :--- | :--- | :--- |
| 1 | **Cut Spec Parser** | Ingests and interprets the `cut.json` specification from PRISM, including camera parameters, character poses, and emotional context. |
| 2 | **Pose/Structure Extractor** | Estimates the 3D structure or 2D keypoints of characters and objects within the scene (e.g., using OpenPose, SMPL, or ControlNet). |
| 3 | **Line Generator (Stroke AI)** | The core AI component that generates parametric curves ($s(t)$) representing the actual lines of the drawing, based on the extracted structural data. |
| 4 | **Composition Assembler** | Organizes the generated lines into distinct layers (e.g., foreground, mid-ground, background, characters, effects) for independent processing. |
| 5 | **Vector Renderer** | Assembles the final output into a vector format (e.g., `.svg`, `.json`) rather than a flat pixel image. This preserves editability. |
| 6 | **Review & Correction API** | Exposes functions to allow for programmatic, stroke-level modifications, such as `edit_stroke(stroke_id, delta_curvature, delta_pressure)`. |

## 3. Technical & Mathematical Definition

The fundamental output of AXIS is a set of parametric curves, where each curve represents a single stroke.

A stroke $s_i$ is defined as:

$$ s_i(t) = (x_i(t), y_i(t), p_i(t)), \quad t \in [0, 1] $$

Where:
- **$(x_i(t), y_i(t))$**: The 2D coordinates of the point on the curve at parameter $t$.
- **$p_i(t)$**: The pressure or thickness of the stroke at that point.

An important property of each stroke is its **curvature**, $\kappa_i$, which defines its bend:

$$ \kappa_i(t) = \frac{|x\'(t)y\''(t) - y\'(t)x\''(t)|}{(x\'(t)^2 + y\'(t)^2)^{3/2}} $$

The goal of the AXIS AI is not to "draw an image" but to **generate a set of curves {s_1, s_2, ..., s_n}**. This structured data is crucial for downstream modules like CHROMA (coloring) and RAYGEN (effects), as it allows them to precisely identify and manipulate each line.

## 4. Pipeline and Data Flow

```
PRISM (cut.json)
       │
       ▼
AXIS: Cut Parser
       │
       ▼
AXIS: Pose Generator → keypoints.json
       │
       ▼
AXIS: Stroke AI (e.g., VectorNet) → lines.json (List of parametric curves)
       │
       ▼
AXIS: Layer Composer → scene.svg / scene.json
       │
       ▼
   To CHROMA
```

## 5. AI Model Composition

AXIS is a composite system of several specialized AI models:

| Component | Role | Example Models / Techniques |
| :--- | :--- | :--- |
| **PoseNet / SMPL-X** | Extracts character skeletons and 3D poses. | OpenPose, SMPLify-X, ControlNet for Pose |
| **LineNet (Stroke Gen)** | Converts keypoints into vector strokes. | DiffVG, DeepSVG, EdgeLineNet |
| **SegNet** | Generates segmentation masks for coloring. | Segment Anything Model (SAM), CLIPSeg |
| **RefineNet** | Smooths, connects, and cleans up lines. | Transformer-based spline smoother |
| **Stylizer** | Adapts the drawing to a specific art style. | LoRA + Custom Diffusion Line Adapter |

## 6. Output Data Specification (Example)

The primary output of AXIS is a structured JSON file that describes the entire scene in terms of its constituent lines and layers.

```json
{
  "cut_id": "S01_C02",
  "frame_size": [1920, 1080],
  "lines": [
    {
      "stroke_id": "char01_outline_001",
      "layer": "character_main",
      "points": [[101.3, 210.0], [105.1, 215.5], [110.0, 220.1]],
      "pressure": [0.8, 0.7, 0.5],
      "style_class": "outline"
    },
    {
      "stroke_id": "char01_hair_001",
      "layer": "hair",
      "points": [[150.0, 160.2], [160.5, 165.3], [170.2, 170.0]],
      "pressure": [0.4, 0.5, 0.6],
      "style_class": "detail"
    }
  ],
  "layers": [
    "background",
    "character_main",
    "hair",
    "effects_foreground"
  ],
  "style_profile": {
    "name": "ghibli_style_01",
    "line_width_base": 2.0,
    "curve_tolerance": 0.05,
    "pressure_sensitivity": 0.8
  }
}
```
This format provides a rich, machine-readable representation that allows the CHROMA module to perform layered coloring and enables precise post-processing.

## 7. Summary

AXIS is the cornerstone of the generative pipeline, translating directorial intent into concrete, editable forms.

| Module | Role | Output |
| :--- | :--- | :--- |
| **PRISM** | **Director** - Creates the shot composition, emotion, and camera work. | `cut.json` |
| **AXIS** | **Animator/Artist** - Generates the lines and forms. | `lines.json` / `scene.svg` |
| **CHROMA** | **Colorist** - Handles color, tone, and material properties. | `colored_layers.png` |
| **RAYGEN** | **Lighting/VFX** - Adds cinematic lighting and effects. | `final_frame.png` |
```