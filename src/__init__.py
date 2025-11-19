"""
TALOS Studio - AI-Powered Animation Production Platform

Main package for pipeline orchestration and utilities.
"""

__version__ = "0.1.0"
__author__ = "TALOS Team"

from .pipeline_executor import PipelineExecutor
from .device_manager import DeviceManager
from .error_handler import PipelineError, ValidationError

__all__ = [
    "PipelineExecutor",
    "DeviceManager",
    "PipelineError",
    "ValidationError",
]
