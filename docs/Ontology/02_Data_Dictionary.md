# 2. Data Dictionary

This document provides a detailed specification for each data field used in the STUDIO TALOS ontology.

## Project Structure (`project_structure.json`)

| Field Path | Data Type | Description | Example | Required |
|---|---|---|---|---|
| `project_name` | String | The official name of the project. | "Project Talos" | Yes |
| `scenes` | Array[Scene] | An array containing all scenes in the project. | `[...]` | Yes |
| `scenes[].scene_id` | String | A unique identifier for the scene (e.g., S01, S02). | "S01" | Yes |
| `scenes[].scene_name` | String | A descriptive name for the scene. | "바다의 빛" | No |
| `scenes[].description` | String | A brief summary of the scene's content. | "노을지는 해변..." | No |
| `scenes[].emotion` | String | The dominant emotion of the scene. | "calm" | Yes |
| `scenes[].cuts` | Array[Cut] | An array containing all cuts within the scene. | `[...]` | Yes |
| `scenes[].cuts[].cut_id` | String | A unique identifier for the cut (e.g., S01_C1). | "S01_C1" | Yes |
| `scenes[].cuts[].camera` | String | Camera shot type or direction. | "close-up" | No |
| `scenes[].cuts[].dialogue`| String | Dialogue spoken in the cut. | "..." | No |
| `scenes[].cuts[].action` | String | A description of the primary action in the cut. | "손을 들어 빛을 본다" | No |
| `scenes[].cuts[].image_path`| String | The file path to the generated visual for the cut. | "./visuals/S01_C1.png" | Yes |

## Emotion Curve (`emotion_curve.csv`)

| Field Name | Data Type | Description | Example | Required |
|---|---|---|---|---|
| `scene_id` | String | The ID of the scene this data point belongs to. | "S01" | Yes |
| `cut_id` | String | The ID of the cut this data point belongs to. | "S01_C1" | Yes |
| `timestamp` | Float | The time in seconds from the start of the project. | 5.2 | Yes |
| `emotion` | String | The specific emotion at this timestamp. | "wonder" | Yes |
| `intensity` | Float | The intensity of the emotion (0.0 to 1.0). | 0.9 | Yes |
