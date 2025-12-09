"""
Unit tests for device_manager module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.device_manager import DeviceManager


class TestDeviceManager:
    """Test DeviceManager class."""

    def test_initialization(self):
        """Test DeviceManager initialization."""
        manager = DeviceManager()
        assert manager.available_devices is not None
        assert "cpu" in manager.available_devices
        assert "cuda" in manager.available_devices
        assert manager.default_device is not None

    def test_available_devices_structure(self):
        """Test available devices have correct structure."""
        manager = DeviceManager()

        # CPU should always be available
        assert manager.available_devices["cpu"]["available"] is True

        # CUDA info should be present
        assert "available" in manager.available_devices["cuda"]
        assert "count" in manager.available_devices["cuda"]
        assert isinstance(manager.available_devices["cuda"]["devices"], list)

    def test_default_device_is_string(self):
        """Test default device is a valid string."""
        manager = DeviceManager()
        assert isinstance(manager.default_device, str)
        assert manager.default_device in ["cpu", "cuda:0"] or "cuda:" in manager.default_device

    def test_get_device_without_specification(self):
        """Test get_device returns default device."""
        manager = DeviceManager()
        device = manager.get_device()
        assert device == manager.default_device

    def test_get_device_cpu(self):
        """Test requesting CPU device."""
        manager = DeviceManager()
        device = manager.get_device("cpu")
        assert device == "cpu"

    def test_get_device_invalid_spec(self):
        """Test invalid device specification falls back to default."""
        manager = DeviceManager()
        # Invalid specs should fall back to default device
        device = manager.get_device("invalid_device:99")
        assert device == manager.default_device

    def test_get_device_info(self):
        """Test getting device info."""
        manager = DeviceManager()
        info = manager.get_device_info()
        assert info == manager.available_devices

    def test_cuda_fallback_on_unavailable(self):
        """Test CUDA request falls back to CPU if unavailable."""
        manager = DeviceManager()

        # If CUDA is not available
        if not manager.available_devices["cuda"]["available"]:
            device = manager.get_device("cuda:0")
            assert device == "cpu"
        else:
            # If CUDA is available, should return cuda:0
            device = manager.get_device("cuda:0")
            assert "cuda:" in device
