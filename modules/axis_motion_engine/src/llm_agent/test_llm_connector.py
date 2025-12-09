import unittest
from unittest.mock import patch, MagicMock
import json
import os
import requests

from src.llm_agent.llm_connector import call_llm_api

class TestLlmConnector(unittest.TestCase):

    def setUp(self):
        # Ensure environment variables are clean for each test
        if "OLLAMA_API_URL" in os.environ:
            del os.environ["OLLAMA_API_URL"]
        if "OLLAMA_MODEL_NAME" in os.environ:
            del os.environ["OLLAMA_MODEL_NAME"]

    @patch('requests.post')
    def test_call_llm_api_success(self, mock_post):
        # Mock a successful Ollama response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2",
            "created_at": "2025-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": '{"action": "test", "duration": 1.0, "parameters": []}'},
            "done": True
        }
        mock_post.return_value = mock_response

        # Expected parsed JSON
        expected_data = {"action": "test", "duration": 1.0, "parameters": []}

        # Call the function
        result = call_llm_api("test prompt")

        # Assertions
        self.assertEqual(result, expected_data)
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama2",
                "messages": [{"role": "user", "content": "test prompt"}],
                "stream": False
            }
        )

    @patch('requests.post')
    def test_call_llm_api_http_error(self, mock_post):
        # Mock an HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        # Assert that RequestException is raised
        with self.assertRaises(requests.exceptions.RequestException):
            call_llm_api("test prompt")

    @patch('requests.post')
    def test_call_llm_api_invalid_json_content(self, mock_post):
        # Mock a response where message.content is not valid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2",
            "message": {"role": "assistant", "content": "this is not json"},
            "done": True
        }
        mock_post.return_value = mock_response

        # Assert that ValueError is raised due to invalid JSON content
        with self.assertRaises(ValueError) as cm:
            call_llm_api("test prompt")
        self.assertIn("LLM returned non-JSON content within its message.", str(cm.exception))

    @patch('requests.post')
    def test_call_llm_api_unexpected_format(self, mock_post):
        # Mock a response with unexpected format (missing 'message')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2",
            "done": True
        }
        mock_post.return_value = mock_response

        # Assert that ValueError is raised due to unexpected format
        with self.assertRaises(ValueError) as cm:
            call_llm_api("test prompt")
        self.assertIn("Unexpected LLM response format: 'message' or 'content' not found.", str(cm.exception))

    @patch('requests.post')
    def test_call_llm_api_custom_ollama_url_and_model(self, mock_post):
        # Set custom environment variables
        os.environ["OLLAMA_API_URL"] = "http://my-ollama-server:8080/api/chat"
        os.environ["OLLAMA_MODEL_NAME"] = "my-custom-model"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "my-custom-model",
            "message": {"role": "assistant", "content": '{"action": "custom", "duration": 3.0, "parameters": []}'},
            "done": True
        }
        mock_post.return_value = mock_response

        call_llm_api("another prompt")

        mock_post.assert_called_once_with(
            "http://my-ollama-server:8080/api/chat",
            json={
                "model": "my-custom-model",
                "messages": [{"role": "user", "content": "another prompt"}],
                "stream": False
            }
        )

if __name__ == '__main__':
    unittest.main()
