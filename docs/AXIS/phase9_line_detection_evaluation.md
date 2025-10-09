# Phase 9: AI-based Line Detection Model Evaluation

**Document Status:** Draft
**Date:** 2025-10-09

## 1. Evaluation Goal

To select the most suitable AI-based line/curve detection model for integration into the AXIS pipeline. The chosen model must be able to extract structurally and semantically meaningful lines from video frames, moving beyond traditional edge detection methods.

## 2. Methodology

1.  **Setup:** Each candidate model was installed in a separate, isolated virtual environment to prevent dependency conflicts.
2.  **Test Image:** A representative sample image (`input/test_image.png`) was used as a common input for all models.
3.  **Execution:** A master script (`run_comparison.py`) was used to execute the inference script for each model.
4.  **Output Generation:** For each model, two types of images were generated:
    *   **Detection:** The raw detected lines/curves on a black background.
    *   **Overlay:** The detected lines/curves overlaid on the original image.
5.  **Montage Creation:** All generated images were compiled into a single comparison grid (`comparison_grid.png`) for side-by-side analysis.

## 3. Candidate Libraries

The following libraries were evaluated:

-   **Deep Hough Transform (DHT)**
-   **HAWP (Holistically-Attracted Wireframe Parser)**
-   **L-CNN (Line Segment Detector CNN)**
-   **Wireframe Transformer**
-   **LineArt / Sketch Simplification Models**

### 3.1. Line Art Extraction & Simplification Models

These models are specialized in extracting clean line art from images, often with a focus on anime/manga styles or general sketch simplification.

| Model Name | Main Task | Model Architecture | Framework | Pre-trained Models | GitHub Stars | Animation Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MangaLineExtraction_PyTorch** | Structural Line Art Extraction | FCN | PyTorch | Provided (erika.pth) | 178 | High |
| **Anime2Sketch** | Multi-purpose Sketch Extraction | GAN (Domain Adaptation) | PyTorch | Provided (Google Drive) | 2.1k | Very High |
| **ArtLine** | Human Line Art | U-Net + Perceptual Loss | PyTorch (fast.ai) | Provided (Colab/RunwayML) | 3.6k | High (Human-centric) |
| **sketch_simplification** | Rough Sketch Refinement | FCN / GAN | PyTorch | Provided (model_gan.t7 etc.) | 743 | High (for preprocessing) |
| **ControlNet (lineart_anime)** | High-fidelity Line Art Generation | Diffusion + ControlNet | PyTorch (Diffusers/UI) | Provided (Hugging Face) | N/A | Very High (State-of-the-art) |

### 3.2. Recent & Promising Line Detection Models

These models represent recent advancements in general line and line segment detection, often combining deep learning with traditional computer vision techniques.

| Model Name | Paper Year / Status | Implementation | Feature Summary | GitHub / arXiv |
| :--- | :--- | :--- | :--- | :--- |
| **DeepLSD** | CVPR 2023 | ✅ Implemented (GitHub) | Deep learning + traditional method combination. Predicts line distance field, angle field, then applies refinement. | [GitHub](https://github.com/cherubicXN/DeepLSD) |
| **ScaleLSD** | 2025 (Recent) | ✅ Implemented (Code in paper link) | Robust line detector operating domain-independently. "Code and Models are available" specified. | [arXiv](https://arxiv.org/abs/2308.09000) |
| **Deep-Hough-Transform-Line-Priors** | ECCV 2020 | ✅ Implemented | Integrates traditional Hough Transform line knowledge (prior) into a neural network. | [GitHub](https://github.com/PeterWang512/Deep-Hough-Transform-Line-Priors) |
| **SOLD2** | 2021 | ✅ Implemented | Provides a module for self-supervised line detection and descriptor merging. | [arXiv](https://arxiv.org/abs/2106.05606) |
| **LineSegmentsDetection (Collection)** | — | ✅ Implemented (Collection) | Collection of various line segment detection algorithms + code. References DeepLSD, LETR, etc. | [GitHub](https://github.com/cherubicXN/LineSegmentsDetection) |

## 4. Comparison Results

*(This section will be filled in once the `comparison_grid.png` is generated.)*

**[Placeholder for `comparison_grid.png`]**

## 5. Analysis and Evaluation

*(This section will be filled in after analyzing the results.)*

| Model | Strengths | Weaknesses | Suitability for AXIS |
| :--- | :--- | :--- | :--- |
| **DHT** | - | - | - |
| **HAWP** | - | - | - |
| **L-CNN** | - | - | - |
| **Wireframe Transformer** | - | - | - |
| **LineArt Models** | - | - | - |

### 5.1. Qualitative Analysis

-   **DHT:** (e.g., Good at finding straight, structural lines but misses fine curves...)
-   **HAWP:** (e.g., Excellent at capturing character outlines as a connected graph...)
-   **L-CNN:** (e.g., Provides clean vector output but can be noisy...)
-   ...

## 6. Final Recommendation

*(This section will contain the final decision.)*

Based on the analysis, the recommended model for initial integration into the AXIS pipeline is **[Model Name]**.

**Reasoning:**
-   (e.g., It provides the best balance of performance and quality for our specific use case of character motion analysis.)
-   (e.g., Its output format (wireframe graph) is highly compatible with the planned data structure for the timing editor.)

## 7. Next Steps

-   Proceed with Phase 1 (Technical Implementation) to generate the comparison results.
-   Update this document with the generated results and complete the analysis.
-   Begin integration of the chosen model into the main AXIS pipeline as per `AXIS_Development_Roadmap_and_Improvements.md`.

## 8. Limitations and Considerations

These models are primarily designed around line segments, and their ability to handle **smooth curves** perfectly is often limited. Most implementations approximate curves using straight line segments or combinations of segments. Directly outputting curve structures in a vector format is still largely an area of active research and experimentation, with fully stable implementations being rare.