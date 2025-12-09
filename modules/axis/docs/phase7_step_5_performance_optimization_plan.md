# Phase 7, Step 5: Performance Optimization Plan

## 1. Problem Definition

The current implementation of the video processing pipeline is unacceptably slow. Processing a 1-minute video clip takes approximately 1 hour, which is not viable for production use. The user has requested an analysis of the bottleneck and a plan for optimization.

## 2. Performance Analysis

The primary bottleneck is not the GPU-bound deep learning models (MiDaS, RAFT), but rather the CPU-bound logic within the `LineTrackingStep`.

- **Current Inefficient Logic**: The current implementation compares every new line in the current frame against every predicted line from the previous frame. With ~200 lines per frame, this results in approximately `200 * 200 = 40,000` computationally expensive Hausdorff distance calculations for every single frame.
- **Root Cause**: This brute-force, all-pairs comparison approach has a time complexity of O(N*M), where N and M are the number of lines in consecutive frames. This does not scale.

## 3. Proposed Solution: Algorithm-level Optimization

As correctly identified by the user, reducing the amount of computation via a pre-processing or filtering step is the most effective solution.

### Plan A: Search Space Optimization via Spatial Partitioning (Immediate Priority)

This plan aims to drastically reduce the number of distance calculations by implementing a spatial filter.

1.  **Grid Creation**: Before matching, the screen space of the current frame is divided into a virtual grid (e.g., 10x10 cells).
2.  **Line Indexing (Pre-processing)**: Each new line in the current frame is indexed based on which grid cells it occupies. A dictionary can be used to map each cell to a list of lines that pass through it.
3.  **Localized Search**: When tracking a line from the previous frame, its predicted new position is calculated using the optical flow map. Instead of comparing it against all new lines, we now only compare it against the lines present in the grid cell(s) corresponding to its predicted position (and perhaps neighboring cells).

#### Expected Outcome

This will reduce the number of comparisons from `N * M` to `N * k`, where `k` is the small average number of lines in a grid cell. This is expected to reduce the number of expensive calculations by 95-99%, leading to a massive performance improvement (from hours to minutes) using only the CPU.

## 4. Future Considerations (Long-Term Plan)

If the performance after implementing Plan A is still insufficient, the following steps can be considered:

-   **Plan B (GPU Acceleration)**: The optimized distance calculation logic could be ported to the GPU using libraries like `CuPy` to further accelerate the process.
-   **Plan C (Parallel Processing with Overlap)**: The video can be processed in overlapping chunks using Python's `multiprocessing` module. Each process would "warm up" its tracking state on the overlapping frames before producing its final output, ensuring seamless tracking across chunk boundaries.

## 5. Next Step

Proceed with implementing **Plan A**: Refactor the `LineTrackingStep` to include the spatial grid optimization.
