import requests
import json

class OllamaClient:
    def __init__(self, model: str = "llama2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.generate_url = f"{self.host}/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.generate_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Ollama server at {self.host}. Is Ollama running?")
            return "Error: Ollama server not reachable."
        except requests.exceptions.RequestException as e:
            print(f"Error during Ollama API call: {e}")
            return f"Error: Ollama API call failed - {e}"
