# Line Detection Model Comparison: Implementation Status

**Date:** 2025-10-09

This document summarizes the current implementation status of the line detection models for the AXIS project evaluation.

| Model | Status | Notes |
| :--- | :--- | :--- |
| **HAWP** | ✅ Implemented | Basic detection is working. Overlay generation is pending. |
| **L-CNN** | ✅ Implemented | Basic detection is working. Overlay generation is pending. |
| **DeepLSD** | ❌ Failed | Installation failed due to C++ extension build errors (pytlsd -> pybind11 -> CMake compatibility). |
| **Deep Hough Transform** | ⏸️ Postponed | Requires CUDA for compilation. Will be revisited later. |
| **Wireframe Transformer** | ✅ Implemented | Inference script working. Generates detection image. |
| **LineArt / Sketch Models (MangaLineExtraction_PyTorch)** | ✅ Implemented | Inference script working. Generates detection image. |
| **ScaleLSD** | ✅ Implemented | Inference script working. Generates detection image. |
| **SOLD2** | ✅ Implemented | Inference script working. Generates detection and overlay images. |
| **LineSegmentsDetection** | 📋 To-Do | Not yet implemented. |

## Next Steps

1.  Investigate and implement the next model from the "To-Do" list (e.g., SOLD2 or Wireframe Transformer).
2.  Implement the remaining models from the "To-Do" list.
3.  Implement overlay image generation for all models.
4.  Update the main evaluation document (`docs/AXIS/phase9_line_detection_evaluation.md`) with the final results.
