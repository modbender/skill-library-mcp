"""Unit tests for device detection and info."""

import os
from unittest.mock import MagicMock, patch

import torch

from device import get_device, get_device_info


class TestGetDevice:
    def test_override_via_env(self):
        with patch.dict(os.environ, {"TORCH_DEVICE": "cpu"}):
            device = get_device()
            assert device == torch.device("cpu")

    def test_override_cuda_via_env(self):
        with patch.dict(os.environ, {"TORCH_DEVICE": "cuda:1"}):
            device = get_device()
            assert device == torch.device("cuda:1")

    @patch("device.torch")
    def test_falls_back_to_cpu_when_no_gpu(self, mock_torch):
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device = torch.device
        with patch.dict(os.environ, {}, clear=False):
            # Remove TORCH_DEVICE if set
            os.environ.pop("TORCH_DEVICE", None)
            device = get_device()
            assert device == torch.device("cpu")

    @patch("device.torch")
    def test_uses_cuda_when_available(self, mock_torch):
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3060"
        mock_torch.device = torch.device
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TORCH_DEVICE", None)
            device = get_device()
            assert device == torch.device("cuda")


class TestGetDeviceInfo:
    def test_cpu_device_info(self):
        device = torch.device("cpu")
        info = get_device_info(device)
        assert info["device"] == "cpu"
        assert info["device_name"] == "cpu"
        assert info["pytorch_version"] == torch.__version__
        assert "vram_total_mb" not in info
        assert "vram_used_mb" not in info

    @patch("device.torch")
    def test_cuda_device_info(self, mock_torch):
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3060"
        mock_torch.__version__ = "2.6.0"
        mock_torch.version.cuda = "12.4"

        # Mock device properties
        mock_props = MagicMock()
        mock_props.total_memory = 12 * 1024 * 1024 * 1024  # 12 GB
        mock_torch.cuda.get_device_properties.return_value = mock_props
        mock_torch.cuda.memory_allocated.return_value = 1 * 1024 * 1024 * 1024  # 1 GB

        device = torch.device("cuda")
        info = get_device_info(device)

        assert info["device"] == "cuda"
        assert info["device_name"] == "NVIDIA RTX 3060"
        assert info["pytorch_version"] == "2.6.0"
        assert info["cuda_version"] == "12.4"
        assert info["vram_total_mb"] == 12288
        assert info["vram_used_mb"] == 1024
