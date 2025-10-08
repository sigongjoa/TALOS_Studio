# 3. Data Specification: `scene_data.json`

## 3.1. Overview
The `scene_data.json` file is the data contract between the Python backend and the JavaScript frontend. It contains all the necessary information to visualize the tracked lines for every frame of the video. The backend's primary role is to generate a file that strictly adheres to this specification.

## 3.2. File Location
The file must be generated at `axis-interactive-timing-editor/public/scene_data.json`. Placing it in the `public` directory makes it directly accessible to the frontend application without requiring special configuration.

## 3.3. Data Schema

### Root Type
The root of the JSON file is an **Array** of `FrameData` objects.

```
[
  {...FrameData for frame 0...},
  {...FrameData for frame 1...},
  {...FrameData for frame 2...},
  ...
]
```

### `FrameData` Object
Each object in the root array represents a single frame in the video and has the following structure:

| Field         | Type            | Description                                       |
|---------------|-----------------|---------------------------------------------------|
| `frame_index` | `number`        | The 0-based index of the frame.                   |
| `lines`       | `Array<LineData>` | An array of all lines tracked and visible in this frame. |

**Example:**
```json
{
  "frame_index": 5,
  "lines": [
    {...LineData...},
    {...LineData...}
  ]
}
```

### `LineData` Object
Each object in the `lines` array represents a single, tracked line and has the following structure:

| Field    | Type                      | Description                                                              |
|----------|---------------------------|--------------------------------------------------------------------------|
| `id`     | `number`                  | The persistent, unique integer ID for the line, assigned by the tracking step. |
| `points` | `Array<[number, number]>` | An array of `[x, y]` coordinate pairs representing the vertices of the 2D line. |

**Example:**
```json
{
  "id": 15,
  "points": [
    [101.3, 210.0],
    [105.1, 215.5],
    [110.0, 220.1]
  ]
}
```
