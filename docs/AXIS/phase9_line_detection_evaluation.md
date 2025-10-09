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
