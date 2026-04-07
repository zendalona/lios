#!/usr/bin/env python3
"""
Tests for lios/scanner/scanimage_driver.py (DriverScanimage)
─────────────────────────────────────────────────────────────
All subprocess.getoutput and os.system calls are mocked.

Covers:
  • name, is_subclass
  • is_available() – true/false paths
  • get_available_devices()
    - filters out escl:, airscan:, v4l devices
    - returns only valid scanner lines
  • Resolution getter/setter
  • Brightness getter/setter
  • Scan mode getter/setter
  • Scan area constants (FULL / THREE_QUARTER / HALF / QUARTER)
  • check_brightness_support()
  • cancel() calls pkill scanimage
  • close() is a no-op
  • scan() builds correct command with resolution/mode/device
  • scan() appends brightness if supported
"""
import logging
import os
from unittest.mock import patch, MagicMock, call

import pytest

logger = logging.getLogger(__name__)

from lios.scanner.driver_base import DriverBase


# ─── Helper: minimal DriverScanimage without calling __init__ ──────────────
def _make_driver(*, resolution=300, brightness=40, scanner_mode="Color",
                 device="test_scanner", max_x="216", max_y="297",
                 brightness_support=True) -> "DriverScanimage":
    from lios.scanner.scanimage_driver import DriverScanimage
    d = DriverScanimage.__new__(DriverScanimage)
    d.device = device
    d.device_name = device
    d.resolution = resolution
    d.brightness = brightness
    d.scanner_mode = scanner_mode
    d.max_x = max_x
    d.max_y = max_y
    d.y = int(max_y)
    d.light_parameter_state = brightness_support
    d.light_parameter = "brightness"
    d.brightness_multiplier = 2
    d.brightness_offset = -100
    d.available_modes = ["Color", "Gray", "Lineart"]
    return d


# ═══════════════════════════════════════════════════════════════════════════
class TestDriverScanimageContract:

    def test_name(self):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert DriverScanimage.name == "Scanimage"

    def test_is_subclass_of_driver_base(self):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert issubclass(DriverScanimage, DriverBase)

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value="whereis scanimage\nscanimage: /bin/scanimage")
    def test_is_available_true(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert DriverScanimage.is_available() is True

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value="whereis scanimage\nscanimage:")
    def test_is_available_false(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert DriverScanimage.is_available() is False


# ═══════════════════════════════════════════════════════════════════════════
class TestGetAvailableDevices:

    _VALID_OUTPUT = (
        "device `hp:net1' is a Hewlett-Packard hp scanner\n"
        "device `canon:usb2' is a Canon scanner\n"
        "device `escl:http://192.168.1.1' is AirScan scanner\n"
        "device `airscan:e0:Printer' is AirScan\n"
        "device `v4l:/dev/video0' is a webcam\n"
    )

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value=_VALID_OUTPUT)
    def test_filters_escl(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        result = DriverScanimage.get_available_devices()
        assert not any("escl:" in d for d in result)

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value=_VALID_OUTPUT)
    def test_filters_airscan(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        result = DriverScanimage.get_available_devices()
        assert not any("airscan:" in d for d in result)

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value=_VALID_OUTPUT)
    def test_filters_v4l(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        result = DriverScanimage.get_available_devices()
        assert not any("v4l" in d for d in result)

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value=_VALID_OUTPUT)
    def test_includes_real_scanners(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        result = DriverScanimage.get_available_devices()
        assert len(result) == 2
        assert any("hp:net1" in d for d in result)
        assert any("canon:usb2" in d for d in result)
        logger.info("Valid scanner devices: %s", result)

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value="No scanners found")
    def test_empty_when_no_device_lines(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert DriverScanimage.get_available_devices() == []

    @patch("lios.scanner.scanimage_driver.subprocess.getoutput",
           return_value="")
    def test_empty_on_blank_output(self, _):
        from lios.scanner.scanimage_driver import DriverScanimage
        assert DriverScanimage.get_available_devices() == []


# ═══════════════════════════════════════════════════════════════════════════
class TestResolutionBrightnessMode:

    def test_get_resolution(self):
        d = _make_driver(resolution=600)
        assert d.get_resolution() == 600

    def test_set_resolution(self):
        d = _make_driver()
        d.set_resolution(1200)
        assert d.get_resolution() == 1200

    def test_get_brightness(self):
        d = _make_driver(brightness=75)
        assert d.get_brightness() == 75

    def test_set_brightness(self):
        d = _make_driver()
        d.set_brightness(50)
        assert d.get_brightness() == 50

    def test_get_scan_mode(self):
        d = _make_driver(scanner_mode="Gray")
        assert d.get_scan_mode(None) == "Gray"

    def test_set_scan_mode(self):
        d = _make_driver()
        d.set_scan_mode("Lineart")
        assert d.get_scan_mode(None) == "Lineart"

    def test_get_available_scan_modes(self):
        d = _make_driver()
        modes = d.get_available_scan_modes()
        assert "Color" in modes
        assert "Gray" in modes

    def test_check_brightness_support_true(self):
        d = _make_driver(brightness_support=True)
        assert d.check_brightness_support() is True

    def test_check_brightness_support_false(self):
        d = _make_driver(brightness_support=False)
        assert d.check_brightness_support() is False


# ═══════════════════════════════════════════════════════════════════════════
class TestScanAreaScanimage:

    def test_set_scan_area_full(self):
        d = _make_driver(max_y="200")
        d.set_scan_area(DriverBase.SCAN_AREA_FULL)
        assert d.y == 200

    def test_set_scan_area_three_quarter(self):
        d = _make_driver(max_y="200")
        d.set_scan_area(DriverBase.SCAN_AREA_THREE_QUARTER)
        assert d.y == 150

    def test_set_scan_area_half(self):
        d = _make_driver(max_y="200")
        d.set_scan_area(DriverBase.SCAN_AREA_HALF)
        assert d.y == 100

    def test_set_scan_area_quarter(self):
        d = _make_driver(max_y="200")
        d.set_scan_area(DriverBase.SCAN_AREA_QUARTER)
        assert d.y == 50


# ═══════════════════════════════════════════════════════════════════════════
class TestScanCommand:

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_calls_os_system(self, mock_sys):
        d = _make_driver(brightness_support=False)
        d.scan("/tmp/out.pnm")
        assert mock_sys.called

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_command_contains_device(self, mock_sys):
        d = _make_driver(device="hp:net1", brightness_support=False)
        d.scan("/tmp/out.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "hp:net1" in cmd

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_command_contains_resolution(self, mock_sys):
        d = _make_driver(resolution=600, brightness_support=False)
        d.scan("/tmp/out.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "600" in cmd

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_command_contains_mode(self, mock_sys):
        d = _make_driver(scanner_mode="Gray", brightness_support=False)
        d.scan("/tmp/out.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "Gray" in cmd

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_command_contains_brightness_when_supported(self, mock_sys):
        d = _make_driver(brightness=60, brightness_support=True)
        d.scan("/tmp/out.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "--brightness=60" in cmd
        logger.info("Scan command: %s", cmd)

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_command_no_brightness_when_unsupported(self, mock_sys):
        d = _make_driver(brightness_support=False)
        d.scan("/tmp/out.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "--brightness" not in cmd

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_runs_convert_strip(self, mock_sys):
        d = _make_driver(brightness_support=False)
        d.scan("/tmp/out.pnm")
        all_cmds = [c[0][0] for c in mock_sys.call_args_list]
        assert any("convert" in c and "-strip" in c for c in all_cmds)

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_scan_output_redirected_to_filename(self, mock_sys):
        d = _make_driver(brightness_support=False)
        d.scan("/tmp/my_scan.pnm")
        cmd = mock_sys.call_args_list[0][0][0]
        assert "/tmp/my_scan.pnm" in cmd


# ═══════════════════════════════════════════════════════════════════════════
class TestCancelClose:

    @patch("lios.scanner.scanimage_driver.os.system")
    def test_cancel_kills_scanimage(self, mock_sys):
        d = _make_driver()
        d.cancel()
        mock_sys.assert_called_once_with("pkill scanimage")

    def test_close_is_noop(self):
        d = _make_driver()
        result = d.close()
        assert result is None
