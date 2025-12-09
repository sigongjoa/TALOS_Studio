"""
Unit tests for error_handler module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.error_handler import (
    PipelineError,
    ValidationError,
    FileNotFoundError_,
    SubprocessError,
    ConfigurationError,
    DeviceError,
)


class TestPipelineError:
    """Test PipelineError class."""

    def test_creation_with_message_only(self):
        """Test creating error with just message."""
        error = PipelineError("Test error")
        assert error.message == "Test error"
        assert error.exit_code == 1

    def test_creation_with_details(self):
        """Test creating error with message and details."""
        error = PipelineError("Test error", details="Error details")
        assert error.message == "Test error"
        assert "Error details" in str(error)
        assert error.exit_code == 1

    def test_custom_exit_code(self):
        """Test custom exit code."""
        error = PipelineError("Test", exit_code=42)
        assert error.exit_code == 42


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_exit_code(self):
        """Test ValidationError has exit code 2."""
        error = ValidationError("Invalid input")
        assert error.exit_code == 2


class TestFileNotFoundError:
    """Test FileNotFoundError_ class."""

    def test_file_not_found_error(self):
        """Test FileNotFoundError_ format."""
        error = FileNotFoundError_("/path/to/file.txt", context="config file")
        assert "/path/to/file.txt" in str(error)
        assert "config file" in str(error)
        assert error.exit_code == 3


class TestSubprocessError:
    """Test SubprocessError class."""

    def test_subprocess_error_format(self):
        """Test SubprocessError includes command and stderr."""
        error = SubprocessError("python script.py", 1, "Error output")
        assert "python script.py" in str(error)
        assert "Error output" in str(error)
        assert error.exit_code == 4


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_configuration_error_format(self):
        """Test ConfigurationError format."""
        error = ConfigurationError("config.yml", "Invalid YAML")
        assert "config.yml" in str(error)
        assert "Invalid YAML" in str(error)
        assert error.exit_code == 5


class TestDeviceError:
    """Test DeviceError class."""

    def test_device_error_exit_code(self):
        """Test DeviceError has exit code 6."""
        error = DeviceError("CUDA not available")
        assert error.exit_code == 6
