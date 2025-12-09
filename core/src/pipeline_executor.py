"""
Main pipeline orchestrator for TALOS Studio.

Coordinates the execution of reconstruction, rendering, and packaging stages.
"""

import os
import sys
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Any

from .error_handler import (
    PipelineError,
    ValidationError,
    SubprocessError,
    ConfigurationError,
)
from .device_manager import DeviceManager

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Execute the TALOS Studio animation generation pipeline."""

    def __init__(self, config_path: str = "config.yml"):
        """
        Initialize pipeline executor.

        Args:
            config_path: Path to YAML configuration file

        Raises:
            ConfigurationError: If config file is invalid
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.device_manager = DeviceManager()
        self.temp_dir = self.config.get("pipeline_temp_dir", "temp")
        self.output_dir = self.config.get("output_deployment_dir", "output_for_deployment")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration file.

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If config is invalid
        """
        if not os.path.exists(self.config_path):
            raise ConfigurationError(
                self.config_path,
                f"File not found"
            )

        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ConfigurationError(
                    self.config_path,
                    "Configuration must be a valid YAML dictionary"
                )

            logger.info(f"✓ Configuration loaded from {self.config_path}")
            return config

        except yaml.YAMLError as e:
            raise ConfigurationError(
                self.config_path,
                f"Invalid YAML syntax: {e}"
            ) from e

    def validate_inputs(self, input_image: str) -> None:
        """
        Validate input image file.

        Args:
            input_image: Path to input image

        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(input_image, str):
            raise ValidationError(
                f"Input image path must be string, got {type(input_image).__name__}"
            )

        if not os.path.exists(input_image):
            raise ValidationError(
                f"Input image not found: {input_image}",
                "Please provide a valid image file path"
            )

        if not os.path.isfile(input_image):
            raise ValidationError(
                f"Input path is not a file: {input_image}"
            )

        logger.info(f"✓ Input validation passed: {input_image}")

    def run_subprocess(
        self,
        command: list,
        description: str,
        timeout: int = 3600
    ) -> str:
        """
        Run external subprocess with error handling.

        Args:
            command: Command list (as for subprocess.run)
            description: Description of what's running (for logging)
            timeout: Timeout in seconds

        Returns:
            Stdout from subprocess

        Raises:
            SubprocessError: If subprocess fails
        """
        logger.info(f"Running: {description}")
        logger.debug(f"Command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(command[0]) if command else None
            )
            logger.info(f"✓ {description} completed successfully")
            logger.debug(f"Stdout: {result.stdout[:500]}")  # First 500 chars
            return result.stdout

        except subprocess.TimeoutExpired as e:
            raise SubprocessError(
                ' '.join(command),
                -1,
                f"Process timed out after {timeout} seconds"
            ) from e

        except subprocess.CalledProcessError as e:
            raise SubprocessError(
                ' '.join(command),
                e.returncode,
                e.stderr or e.stdout
            ) from e

    def ensure_directory(self, path: str) -> str:
        """
        Ensure directory exists.

        Args:
            path: Directory path

        Returns:
            Normalized path

        Raises:
            ValidationError: If directory cannot be created
        """
        try:
            os.makedirs(path, exist_ok=True)
            logger.debug(f"✓ Directory ensured: {path}")
            return path
        except OSError as e:
            raise ValidationError(
                f"Cannot create directory: {path}",
                str(e)
            ) from e

    def execute(self, input_image: str, output_dir: Optional[str] = None) -> str:
        """
        Execute the full pipeline.

        Args:
            input_image: Path to input image
            output_dir: Optional override for output directory

        Returns:
            Path to output directory

        Raises:
            PipelineError: If pipeline execution fails
        """
        try:
            # Validate inputs
            self.validate_inputs(input_image)

            # Set output directory
            if output_dir:
                self.output_dir = output_dir

            # Create directories
            self.ensure_directory(self.temp_dir)
            self.ensure_directory(self.output_dir)

            # Log device info
            self.device_manager.print_device_info()

            logger.info("=" * 60)
            logger.info("STARTING PIPELINE EXECUTION")
            logger.info("=" * 60)
            logger.info(f"Input image: {input_image}")
            logger.info(f"Output directory: {self.output_dir}")
            logger.info(f"Temp directory: {self.temp_dir}")

            # TODO: Implement actual pipeline stages
            # Stage 1: 3D Reconstruction (TripoSR)
            # Stage 2: 2D Rendering (Blender)
            # Stage 3: Packaging Results

            logger.info("=" * 60)
            logger.info("✓ PIPELINE EXECUTION COMPLETED")
            logger.info("=" * 60)

            return self.output_dir

        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError(
                f"Unexpected error during pipeline execution: {e}",
                str(e)
            ) from e
