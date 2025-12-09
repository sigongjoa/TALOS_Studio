"""
Unit tests for pipeline_executor module.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pipeline_executor import PipelineExecutor
from src.error_handler import ValidationError, ConfigurationError


class TestPipelineExecutor:
    """Test PipelineExecutor class."""

    def test_initialization_with_missing_config(self):
        """Test initialization fails with missing config file."""
        with pytest.raises(ConfigurationError):
            PipelineExecutor(config_path="nonexistent_config.yml")

    def test_initialization_with_valid_config(self):
        """Test initialization with valid config."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("pipeline_temp_dir: temp\n")
            f.write("output_deployment_dir: output\n")
            config_path = f.name

        try:
            executor = PipelineExecutor(config_path=config_path)
            assert executor.config is not None
            assert executor.device_manager is not None
        finally:
            os.unlink(config_path)

    def test_validate_inputs_success(self):
        """Test input validation with valid file."""
        # Create a temporary config and image file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.yml")
            image_file = os.path.join(tmpdir, "image.png")

            # Create config
            with open(config_file, 'w') as f:
                f.write("pipeline_temp_dir: temp\noutput_deployment_dir: output\n")

            # Create dummy image
            with open(image_file, 'w') as f:
                f.write("dummy image data")

            executor = PipelineExecutor(config_path=config_file)
            # Should not raise
            executor.validate_inputs(image_file)

    def test_validate_inputs_missing_file(self):
        """Test input validation fails with missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.yml")

            with open(config_file, 'w') as f:
                f.write("pipeline_temp_dir: temp\noutput_deployment_dir: output\n")

            executor = PipelineExecutor(config_path=config_file)

            with pytest.raises(ValidationError):
                executor.validate_inputs("/nonexistent/image.png")

    def test_validate_inputs_invalid_type(self):
        """Test input validation fails with invalid type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.yml")

            with open(config_file, 'w') as f:
                f.write("pipeline_temp_dir: temp\noutput_deployment_dir: output\n")

            executor = PipelineExecutor(config_path=config_file)

            with pytest.raises(ValidationError):
                executor.validate_inputs(123)  # Invalid: not a string

    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.yml")

            with open(config_file, 'w') as f:
                f.write("pipeline_temp_dir: temp\noutput_deployment_dir: output\n")

            executor = PipelineExecutor(config_path=config_file)
            test_dir = os.path.join(tmpdir, "test_dir")

            result = executor.ensure_directory(test_dir)
            assert os.path.exists(result)
            assert os.path.isdir(result)

    def test_configuration_loading_with_invalid_yaml(self):
        """Test config loading fails with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML
            config_path = f.name

        try:
            with pytest.raises(ConfigurationError):
                PipelineExecutor(config_path=config_path)
        finally:
            os.unlink(config_path)
