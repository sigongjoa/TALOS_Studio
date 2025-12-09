# src/validation.py
"""
Input validation utilities for the AXIS pipeline.

This module provides validation functions for common input types to catch
invalid data at module boundaries early.
"""

import numpy as np
from typing import Any, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Custom exception for validation failures."""
    pass


def validate_frame(frame: Any, frame_index: Optional[int] = None) -> np.ndarray:
    """
    Validate and normalize a video frame.

    Args:
        frame: Input frame (should be ndarray)
        frame_index: Optional frame index for error reporting

    Returns:
        Validated numpy array

    Raises:
        ValidationError: If frame is invalid
    """
    if frame is None:
        raise ValidationError("Frame cannot be None")

    if not isinstance(frame, np.ndarray):
        raise ValidationError(
            f"Frame must be numpy array, got {type(frame).__name__}"
        )

    if frame.size == 0:
        raise ValidationError("Frame cannot be empty")

    if len(frame.shape) not in (2, 3):
        raise ValidationError(
            f"Frame must be 2D (grayscale) or 3D (color), got shape {frame.shape}"
        )

    if len(frame.shape) == 3:
        if frame.shape[2] not in (1, 3, 4):
            raise ValidationError(
                f"Color frame must have 1, 3, or 4 channels, got {frame.shape[2]}"
            )

    # Check reasonable image dimensions (not too small or too large)
    if frame.shape[0] < 10 or frame.shape[1] < 10:
        raise ValidationError(
            f"Frame dimensions too small: {frame.shape}. Minimum 10x10."
        )

    if frame.shape[0] > 10000 or frame.shape[1] > 10000:
        logger.warning(f"Frame dimensions unusually large: {frame.shape}")

    # Check data type is numeric
    if not np.issubdtype(frame.dtype, np.number):
        raise ValidationError(
            f"Frame data type must be numeric, got {frame.dtype}"
        )

    logger.debug(f"Frame {frame_index or 'N/A'} validated: shape={frame.shape}, dtype={frame.dtype}")
    return frame


def validate_keypoints(keypoints: Any, num_keypoints: int) -> np.ndarray:
    """
    Validate 2D/3D keypoint data.

    Args:
        keypoints: Array of keypoints (N, 2) for 2D or (N, 3) for 3D
        num_keypoints: Expected number of keypoints

    Returns:
        Validated keypoints array

    Raises:
        ValidationError: If keypoints invalid
    """
    if keypoints is None:
        raise ValidationError("Keypoints cannot be None")

    if not isinstance(keypoints, np.ndarray):
        raise ValidationError(
            f"Keypoints must be numpy array, got {type(keypoints).__name__}"
        )

    if keypoints.ndim != 2:
        raise ValidationError(
            f"Keypoints must be 2D array, got shape {keypoints.shape}"
        )

    if keypoints.shape[0] != num_keypoints:
        raise ValidationError(
            f"Expected {num_keypoints} keypoints, got {keypoints.shape[0]}"
        )

    if keypoints.shape[1] not in (2, 3):
        raise ValidationError(
            f"Keypoints must have 2D (x,y) or 3D (x,y,z) coords, got {keypoints.shape[1]} dims"
        )

    # Check for NaN or Inf values
    if np.any(np.isnan(keypoints)) or np.any(np.isinf(keypoints)):
        raise ValidationError(
            "Keypoints contain NaN or Inf values"
        )

    # Check coordinates are in reasonable range
    if np.any(np.abs(keypoints) > 1e6):
        logger.warning(f"Keypoints have unusually large values: max={np.max(np.abs(keypoints))}")

    logger.debug(f"Keypoints validated: shape={keypoints.shape}")
    return keypoints


def validate_confidence(confidence: Any, expected_length: int) -> np.ndarray:
    """
    Validate confidence scores.

    Args:
        confidence: Array of confidence scores (N,) with values in [0, 1]
        expected_length: Expected array length

    Returns:
        Validated confidence array

    Raises:
        ValidationError: If confidence invalid
    """
    if confidence is None:
        raise ValidationError("Confidence cannot be None")

    if not isinstance(confidence, np.ndarray):
        raise ValidationError(
            f"Confidence must be numpy array, got {type(confidence).__name__}"
        )

    if confidence.ndim != 1:
        raise ValidationError(
            f"Confidence must be 1D array, got shape {confidence.shape}"
        )

    if confidence.shape[0] != expected_length:
        raise ValidationError(
            f"Expected {expected_length} confidence scores, got {confidence.shape[0]}"
        )

    if np.any(confidence < 0) or np.any(confidence > 1):
        raise ValidationError(
            f"Confidence scores must be in [0, 1], got range [{np.min(confidence)}, {np.max(confidence)}]"
        )

    logger.debug(f"Confidence validated: shape={confidence.shape}, mean={np.mean(confidence):.3f}")
    return confidence


def validate_image_path(path: Any) -> str:
    """
    Validate image file path.

    Args:
        path: Path to image file

    Returns:
        Normalized path string

    Raises:
        ValidationError: If path invalid or file not found
    """
    if not isinstance(path, (str, bytes)):
        raise ValidationError(
            f"Image path must be string, got {type(path).__name__}"
        )

    import os
    if not os.path.exists(path):
        raise ValidationError(f"Image file not found: {path}")

    if not os.path.isfile(path):
        raise ValidationError(f"Path is not a file: {path}")

    # Check file extension
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.mp4', '.avi', '.mov')
    if not path.lower().endswith(valid_extensions):
        logger.warning(f"Unusual image file extension: {path}")

    logger.debug(f"Image path validated: {path}")
    return str(path)


def validate_output_path(path: Any, create: bool = True) -> str:
    """
    Validate output directory path.

    Args:
        path: Directory path for output
        create: If True, create directory if it doesn't exist

    Returns:
        Normalized directory path

    Raises:
        ValidationError: If path invalid
    """
    if not isinstance(path, (str, bytes)):
        raise ValidationError(
            f"Output path must be string, got {type(path).__name__}"
        )

    import os
    path = str(path)

    if create:
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            raise ValidationError(f"Cannot create output directory: {e}")
    else:
        # Just check it's a valid path
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            raise ValidationError(f"Parent directory does not exist: {parent}")

    logger.debug(f"Output path validated: {path}")
    return path


def validate_config(config: Any, required_keys: Optional[list] = None) -> dict:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Returns:
        Validated configuration

    Raises:
        ValidationError: If config invalid
    """
    if config is None:
        raise ValidationError("Configuration cannot be None")

    if not isinstance(config, dict):
        raise ValidationError(
            f"Configuration must be dict, got {type(config).__name__}"
        )

    if required_keys:
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise ValidationError(f"Missing required config keys: {missing}")

    logger.debug(f"Configuration validated: {len(config)} keys")
    return config
