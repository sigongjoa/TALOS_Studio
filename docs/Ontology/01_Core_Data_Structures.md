# 1. Core Data Structures

## 1.1. Project Structure (`project_structure.json`)

This is the master file for a project, containing a hierarchical structure of scenes and cuts.

```json
{
  "project_name": "Project Talos",
  "scenes": [
    {
      "scene_id": "S01",
      "scene_name": "바다의 빛",
      "description": "노을지는 해변, 소녀가 파편을 손에 쥔다.",
      "emotion": "calm",
      "cuts": [
        {
          "cut_id": "S01_C1",
          "camera": "wide",
          "dialogue": "...",
          "image_path": "./visuals/S01_C1.png"
        },
        {
          "cut_id": "S01_C2",
          "camera": "close-up",
          "action": "손을 들어 빛을 본다",
          "image_path": "./visuals/S01_C2.png"
        }
      ]
    }
  ]
}
```

## 1.2. Emotion Curve (`emotion_curve.csv`)

This file tracks the emotional arc of the project over time, linked to specific scenes and cuts.

```csv
scene_id,cut_id,timestamp,emotion,intensity
S01,S01_C1,0.0,calm,0.8
S01,S01_C2,5.2,wonder,0.9
S02,S02_C1,10.5,tension,0.7
```
