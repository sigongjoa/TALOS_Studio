"""
Device detection and management for TALOS Studio.

Handles GPU/CPU selection with intelligent fallback.
"""

import logging
from typing import Optional

try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manage device selection for deep learning models."""

    def __init__(self):
        """Initialize device manager."""
        self.available_devices = self._detect_available_devices()
        self.default_device = self._get_default_device()

    @staticmethod
    def _detect_available_devices() -> dict:
        """
        Detect available devices on the system.

        Returns:
            Dictionary with device information
        """
        devices = {
            "cpu": {"available": True, "name": "CPU"},
            "cuda": {"available": False, "count": 0, "devices": []},
        }

        if torch is not None and torch.cuda.is_available():
            devices["cuda"]["available"] = True
            devices["cuda"]["count"] = torch.cuda.device_count()
            devices["cuda"]["devices"] = [
                torch.cuda.get_device_name(i) for i in range(devices["cuda"]["count"])
            ]

        return devices

    @staticmethod
    def _get_default_device() -> str:
        """
        Get default device based on availability.

        Returns:
            Device string ("cuda:0", "cpu", etc.)
        """
        if torch is not None and torch.cuda.is_available():
            device = "cuda:0"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✅ CUDA available. Using GPU: {gpu_name}")
            return device
        else:
            logger.warning(
                "⚠️  CUDA not available. Using CPU for inference. "
                "This will be very slow. Consider installing CUDA drivers."
            )
            return "cpu"

    def get_device(self, specified_device: Optional[str] = None) -> str:
        """
        Get device to use for inference.

        Args:
            specified_device: User-specified device string

        Returns:
            Device string to use

        Raises:
            ValueError: If specified device is invalid or unavailable
        """
        if specified_device is not None:
            return self._validate_and_select_device(specified_device)

        return self.default_device

    def _validate_and_select_device(self, device_spec: str) -> str:
        """
        Validate user-specified device.

        Args:
            device_spec: Device specification string

        Returns:
            Validated device string

        Raises:
            ValueError: If device is invalid
        """
        if device_spec == "cpu":
            logger.info("Using CPU (as requested)")
            return "cpu"

        if "cuda" in device_spec:
            if not self.available_devices["cuda"]["available"]:
                logger.warning(
                    f"CUDA not available, but '{device_spec}' was requested. "
                    "Falling back to CPU."
                )
                return "cpu"

            # Parse device ID
            try:
                device_id = int(device_spec.split(":")[-1])
                if device_id >= self.available_devices["cuda"]["count"]:
                    logger.warning(
                        f"Requested CUDA device {device_id} not available. "
                        f"System has {self.available_devices['cuda']['count']} CUDA device(s). "
                        "Falling back to cuda:0"
                    )
                    return "cuda:0"
                device_name = self.available_devices["cuda"]["devices"][device_id]
                logger.info(f"Using GPU {device_id}: {device_name}")
                return device_spec
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid device specification: {device_spec}")
                raise ValueError(f"Invalid CUDA device spec: {device_spec}") from e

        # Default fallback
        logger.warning(f"Unknown device: {device_spec}. Using default ({self.default_device})")
        return self.default_device

    def get_device_info(self) -> dict:
        """
        Get information about available devices.

        Returns:
            Dictionary with device information
        """
        return self.available_devices

    def print_device_info(self) -> None:
        """Print device information to logger."""
        logger.info("=" * 60)
        logger.info("DEVICE INFORMATION")
        logger.info("=" * 60)

        if self.available_devices["cpu"]["available"]:
            logger.info("✓ CPU: Available")

        if self.available_devices["cuda"]["available"]:
            logger.info(f"✓ CUDA: Available ({self.available_devices['cuda']['count']} device(s))")
            for i, device_name in enumerate(self.available_devices["cuda"]["devices"]):
                logger.info(f"  • cuda:{i} - {device_name}")
        else:
            logger.info("✗ CUDA: Not available")

        logger.info(f"\nDefault device: {self.default_device}")
        logger.info("=" * 60)
