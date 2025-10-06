
"""
prompt_builder.py

This module is responsible for constructing the detailed natural language prompts
that are sent to the Large Language Model (LLM). It translates user requests
into a structured format that guides the LLM to generate specific JSON outputs
required for OpenSim simulations.
"""

def build_llm_prompt(user_input_text: str) -> str:
    """
    Constructs a detailed prompt string for the LLM based on user input,
    guiding the LLM to generate structured JSON output for OpenSim.

    Args:
        user_input_text (str): The natural language description of the desired motion from the user.

    Returns:
        str: A formatted prompt string ready to be sent to the LLM API.
    """
    print(f"Building LLM prompt for: {user_input_text}")
    # Placeholder for actual prompt template
    return f"""
    오직 JSON 객체만 출력해야 해. 어떤 추가적인 설명이나 대화도 없이, 오직 JSON 객체만 출력해야 해.
    너는 OpenSim 시뮬레이션을 위한 동작 데이터를 생성하는 AI 에이전트야.
    사용자의 요청을 분석해서, OpenSim이 이해할 수 있는 정확한 JSON 형식의 데이터를 출력해야 해.
    JSON은 다음 필드를 포함해야 해:
    - 'action': (문자열) 동작에 대한 설명적인 이름.
    - 'duration': (실수) 동작의 예상 지속 시간(초).
    - 'parameters': (객체 배열) 각 객체는 관절 또는 신체 부위와 목표 상태를 나타내.
        - 'joint': (문자열) 관절의 이름 (예: 'pelvis_tilt', 'hip_flexion_l', 'knee_angle_r').
        - 'target_angle_x': (실수, 선택 사항) X축 회전의 목표 각도(도).
        - 'target_angle_y': (실수, 선택 사항) Y축 회전의 목표 각도(도).
        - 'target_angle_z': (실수, 선택 사항) Z축 회전의 목표 각도(도).
        - 'muscle_activation': (실수, 선택 사항) 근육 활성화 수준 (0.0 ~ 1.0).
        - 'target_position_x': (실수, 선택 사항) X축의 목표 위치(미터).
        - 'target_position_y': (실수, 선택 사항) Y축의 목표 위치(미터).
        - 'target_position_z': (실수, 선택 사항) Z축의 목표 위치(미터).
    동작과 관련된 매개변수만 포함하고, 지정되지 않은 매개변수는 생략해.
    관절 이름은 OpenSim 모델의 실제 관절 이름을 사용해야 해. 예를 들어, '왼쪽 엉덩이'는 'hip_flexion_l'이 될 수 있어.

    예시 JSON 형식:
    ```json
    {{
        "action": "wave_hand",
        "duration": 2.0,
        "parameters": [
            {{
                "joint": "elbow_L",
                "target_angle_x": 90.0
            }},
            {{
                "joint": "shoulder_R",
                "muscle_activation": 0.8
            }}
        ]
    }}
    ```

    사용자 요청: '{user_input_text}'
    오직 JSON 객체만 출력해야 해. 어떤 추가적인 설명이나 대화도 없이, 오직 JSON 객체만 출력해야 해."""

if __name__ == '__main__':
    test_input = "왼쪽 팔을 90도 들어올리는 동작"
    prompt = build_llm_prompt(test_input)
    print("\n--- Generated Prompt ---\n")
    print(prompt)
