# 4. Backend Implementation Plan

## 4.1. File to Modify
`AXIS/src/main.py`

## 4.2. Objective
Refactor the script from a multi-purpose testing file into a dedicated command-line tool for generating the `scene_data.json` file required by the frontend viewer.

## 4.3. Command-Line Interface
The script will be executed as a module and accept two required arguments:
```bash
python -m AXIS.src.main --video [path_to_video.mp4] --output [path_to_output.json]
```
- `--video`: The absolute or relative path to the input video file.
- `--output`: The absolute or relative path where the final `scene_data.json` will be saved.

## 4.4. Core Logic Refactoring

The `main()` function will be restructured to perform the following sequence:

1.  **Initialization:**
    - Parse command-line arguments.
    - Instantiate all necessary pipeline steps, including a single, stateful instance of `LineTrackingStep`.
    - Assemble the full pipeline in the correct execution order.

2.  **Data Collection Loop:**
    - Initialize an empty list: `all_frames_data = []`.
    - Open the video file using `cv2.VideoCapture`.
    - Loop through every frame of the video until `cap.read()` returns false.
    - **Inside the loop for each frame:**
        a. Perform frame resizing to manage memory usage.
        b. Create the `FrameContextBuilder` with the current and previous frames.
        c. Execute `pipeline.run(builder)` to get the `processed_context`.
        d. Check if `processed_context.lines` contains valid tracked `Line3D` objects.
        e. **Transform Data:** Call a helper function, `_project_and_format_lines(processed_context)`, to convert the pipeline's output into the required JSON structure.
        f. Append the result of the transformation to the `all_frames_data` list.
        g. Update `prev_frame` for the next iteration.

3.  **Final Serialization:**
    - After the loop completes, use the `json` module to dump the `all_frames_data` list into the file path specified by the `--output` argument.
    - `json.dump(all_frames_data, f)`

## 4.5. Helper Function: `_project_and_format_lines`

A new helper function will be created within `main.py` to handle the data transformation.

- **Input:** `processed_context: FrameContext`, `frame_height: int`, `frame_width: int`
- **Output:** A dictionary conforming to the `FrameData` specification.
- **Pseudocode:**
    ```python
    def _project_and_format_lines(context, h, w):
        # 1. Project 3D lines to 2D
        # Re-uses the projection logic from the tracking step
        projected_points_list = _project_3d_to_2d(context.lines, h, w)

        # 2. Format data for JSON
        line_data_list = []
        for line_3d, points_2d in zip(context.lines, projected_points_list):
            line_data = {
                "id": line_3d.line_id,
                "points": points_2d.tolist() # Convert numpy array to list
            }
            line_data_list.append(line_data)

        # 3. Assemble final frame data object
        frame_data = {
            "frame_index": context.frame_index,
            "lines": line_data_list
        }
        return frame_data
    ```
This ensures a clean separation between the pipeline execution and the final data formatting logic.
