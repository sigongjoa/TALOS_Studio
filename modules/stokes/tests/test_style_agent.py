import os
import json
import pytest
from src.style_agent.style_agent import StyleAgent

class MockLLMClient:
    def generate(self, prompt: str):
        class MockResponse:
            def __init__(self, text):
                self.text = text
        if "회전하는 효과" in prompt:
            return MockResponse(json.dumps({"parameters": {"type": "llm_rotation", "speed": 15}, "formula": "R(theta)"}))
        elif "푸리에 변환을 사용한 효과" in prompt:
            return MockResponse(json.dumps({"parameters": {"type": "llm_fourier", "precision": "high"}, "formula": "FFT(signal)"}))
        return MockResponse(json.dumps({"parameters": {"type": "llm_default"}, "formula": "LLM_formula"}))

@pytest.fixture
def style_agent_with_llm():
    return StyleAgent(llm_client=MockLLMClient())

@pytest.fixture
def style_agent_no_llm():
    return StyleAgent()

def test_extract_parameters_and_formulas_no_llm_rotation(style_agent_no_llm, capsys):
    user_input = "무잔 회전 공격"
    parameters, formula = style_agent_no_llm.extract_parameters_and_formulas(user_input)
    assert "Warning: LLM client not provided for StyleAgent." in capsys.readouterr().out
    assert parameters == {"type": "rotation", "speed": 10, "duration": 5}
    assert formula == "f(t) = A * cos(omega * t)"

def test_extract_parameters_and_formulas_no_llm_fourier(style_agent_no_llm, capsys):
    user_input = "푸리에 변환 효과"
    parameters, formula = style_agent_no_llm.extract_parameters_and_formulas(user_input)
    assert "Warning: LLM client not provided for StyleAgent." in capsys.readouterr().out
    assert parameters == {"type": "fourier_transform", "frequency_range": "low"}
    assert formula == "F(xi) = integral(f(x) * exp(-2*pi*i*x*xi), dx)"

def test_extract_parameters_and_formulas_no_llm_default(style_agent_no_llm, capsys):
    user_input = "그냥 기본 효과"
    parameters, formula = style_agent_no_llm.extract_parameters_and_formulas(user_input)
    assert "Warning: LLM client not provided for StyleAgent." in capsys.readouterr().out
    assert parameters == {"type": "default", "intensity": 1.0}
    assert formula == "y = x"

def test_extract_parameters_and_formulas_with_llm_rotation(style_agent_with_llm):
    user_input = "회전하는 효과를 보여줘"
    parameters, formula = style_agent_with_llm.extract_parameters_and_formulas(user_input)
    assert parameters == {"type": "llm_rotation", "speed": 15}
    assert formula == "R(theta)"

def test_extract_parameters_and_formulas_with_llm_fourier(style_agent_with_llm):
    user_input = "푸리에 변환을 사용한 효과"
    parameters, formula = style_agent_with_llm.extract_parameters_and_formulas(user_input)
    assert parameters == {"type": "llm_fourier", "precision": "high"}
    assert formula == "FFT(signal)"

def test_extract_parameters_and_formulas_with_llm_invalid_json(style_agent_with_llm, capsys):
    # Simulate LLM returning invalid JSON
    class InvalidJsonMockLLMClient(MockLLMClient):
        def generate(self, prompt: str):
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            return MockResponse("this is not json")
    
    invalid_json_agent = StyleAgent(llm_client=InvalidJsonMockLLMClient())
    user_input = "some input"
    parameters, formula = invalid_json_agent.extract_parameters_and_formulas(user_input)
    assert "Error: LLM response was not a valid JSON. Using default values." in capsys.readouterr().err
    assert parameters == {"error": "invalid_llm_response"}
    assert formula == "error_formula"
