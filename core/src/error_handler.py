"""
Error handling and custom exception classes for TALOS Studio.
"""

import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Base exception for all pipeline-related errors."""

    def __init__(self, message: str, details: Optional[str] = None, exit_code: int = 1):
        """
        Initialize pipeline error.

        Args:
            message: Main error message
            details: Additional details about the error
            exit_code: Exit code to use when exiting
        """
        self.message = message
        self.details = details
        self.exit_code = exit_code
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with details."""
        if self.details:
            return f"{self.message}\n\nDetails:\n{self.details}"
        return self.message

    def log_and_exit(self, logger_obj: logging.Logger = None) -> None:
        """Log error and exit with appropriate code."""
        log = logger_obj or logger
        log.error(f"{self.__class__.__name__}: {self.message}")
        if self.details:
            log.error(f"Details: {self.details}")
        log.exception("Full traceback:")
        sys.exit(self.exit_code)


class ValidationError(PipelineError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details, exit_code=2)


class FileNotFoundError_(PipelineError):
    """Raised when required file is not found."""

    def __init__(self, filepath: str, context: str = ""):
        message = f"File not found: {filepath}"
        if context:
            message += f" ({context})"
        super().__init__(message, exit_code=3)


class SubprocessError(PipelineError):
    """Raised when subprocess execution fails."""

    def __init__(self, command: str, return_code: int, stderr: str):
        message = f"Subprocess failed with return code {return_code}"
        details = f"Command: {command}\n\nStderr:\n{stderr}"
        super().__init__(message, details, exit_code=4)


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid."""

    def __init__(self, config_file: str, message: str):
        full_message = f"Configuration error in {config_file}: {message}"
        super().__init__(full_message, exit_code=5)


class DeviceError(PipelineError):
    """Raised when device selection fails."""

    def __init__(self, message: str):
        super().__init__(message, exit_code=6)


def setup_error_logging(log_file: str = "pipeline.log") -> logging.Logger:
    """
    Set up logging with file and console handlers.

    Args:
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    logger_obj = logging.getLogger("talos_studio")
    logger_obj.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)

    # Add handlers
    logger_obj.addHandler(file_handler)
    logger_obj.addHandler(console_handler)

    return logger_obj
