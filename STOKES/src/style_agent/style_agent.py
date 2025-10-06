import json
import sys
from src.llm_client import OllamaClient

class StyleAgent:
    def __init__(self, llm_client: OllamaClient = None):
        """
        Initializes the StyleAgent.

        Args:
            llm_client: An OllamaClient instance for parameter and formula extraction.
        """
        self.llm_client = llm_client

    def extract_parameters_and_formulas(self, user_input: str) -> tuple[dict, str]:
        """
        Extracts simulation parameters and a mathematical formula from user input.

        Args:
            user_input: The natural language description from the user.

        Returns:
            A tuple containing:
                - A dictionary of extracted parameters.
                - A string representing the extracted mathematical formula.
        """
        if not self.llm_client:
            sys.stdout.write("Warning: LLM client not provided for StyleAgent. Using placeholder extraction.\n")
            # Placeholder logic for demonstration
            if "회전" in user_input:
                parameters = {"type": "rotation", "speed": 10, "duration": 5}
                formula = "f(t) = A * cos(omega * t)"
            elif "푸리에" in user_input:
                parameters = {"type": "fourier_transform", "frequency_range": "low"}
                formula = "F(xi) = integral(f(x) * exp(-2*pi*i*x*xi), dx)"
            else:
                parameters = {"type": "default", "intensity": 1.0}
                formula = "y = x"
            return parameters, formula

        prompt = self._create_llm_prompt(user_input)
        response_text = self.llm_client.generate(prompt)
        
        # Assuming the LLM response is a JSON string with "parameters" and "formula" keys
        try:
            parsed_response = json.loads(response_text)
            parameters = parsed_response.get("parameters", {})
            formula = parsed_response.get("formula", "")
        except json.JSONDecodeError:
            sys.stderr.write(f"Error: LLM response was not a valid JSON: {response_text}. Using default values.\n")
            parameters = {"error": "invalid_llm_response"}
            formula = "error_formula"
        
        return parameters, formula

    def _create_llm_prompt(self, user_input: str) -> str:
        """
        Creates a prompt for the LLM to extract parameters and formulas.
        """
        prompt = (
            "Analyze the following user input to extract relevant simulation parameters "
            "and the core mathematical formula. Your response MUST be a JSON object "
            "containing two keys: 'parameters' (a dictionary of key-value pairs) and 'formula' (a string). "
            "DO NOT include any conversational text, explanations, or additional formatting outside the JSON.\n\n"
            "User Input: " + user_input + "\n\n"
            "Example Output:\n"
            "{\n"
            "  \"parameters\": {\"rotation_speed\": 10, \"angle\": 90, \"duration\": 5},\n"
            "  \"formula\": \"f(t) = A * sin(omega * t)\"\n"
            "}\n\n"
            "Please provide the JSON output only, with no other text."
        )
        return prompt
