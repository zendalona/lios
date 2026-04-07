#!/usr/bin/env python3
"""
Tests for lios/scanner/sane_driver.py (DriverSane)
───────────────────────────────────────────────────
The sane Python binding is mocked entirely so tests run on any machine
regardless of whether python-sane is installed.

Strategy:
  • Inject a fake `sane` module into sys.modules BEFORE importing sane_driver
  • Use importlib.reload() to get a fresh module with available=True
  • For lifecycle tests, build instances bypassing __init__

Covers:
  • is_available() reflects module-level `available` flag
  • name == "Sane"
  • is_subclass of DriverBase
  • get_scanner_option() search and miss
  • get_available_scan_modes() with mocked options
  • get_available_devices() filters device list correctly
  • scan() calls scanner.scan() and writes to /tmp then converts
  • get/set resolution, brightness, scan_mode
  • cancel() delegates to scanner.cancel()
  • close() delegates to scanner.close()
  • check_brightness_support() reflects state
"""
import importlib
import logging
import sys
import types
from unittest.mock import MagicMock, patch, call

import pytest

logger = logging.getLogger(__name__)

from lios.scanner.driver_base import DriverBase


# ─── Inject the fake sane module and reload sane_driver with it ────────────
def _build_fake_sane(devices=None):
    fake = types.ModuleType("sane")
    fake.init = MagicMock(return_value=(1, 0, 3))
    fake.open = MagicMock()
    fake.get_devices = MagicMock(return_value=devices or [])
    return fake


def _reload_driver_with_sane(fake_sane):
    """Force a fresh import of sane_driver with the given sane module."""
    sys.modules["sane"] = fake_sane
    import lios.scanner.sane_driver as mod
    importlib.reload(mod)
    return mod


def _make_driver(*, brightness_param="brightness", min_val=-100, max_val=100,
                 brightness_support=True, scanner_mode="Color"):
    """Build a DriverSane instance without calling __init__."""
    from lios.scanner.sane_driver import DriverSane
    d = DriverSane.__new__(DriverSane)
    scanner = MagicMock()
    scanner.resolution = 300
    scanner.brightness = 40
    scanner.threshold = 128
    scanner.mode = scanner_mode
    d.scanner = scanner
    d.light_parameter_state = brightness_support
    d.light_parameter = brightness_param
    d.min = min_val
    d.max = max_val
    d.brightness_multiplier = 1
    d.brightness_offset = 0
    d.resolution = 300
    d.brightness = 40
    d.device_name = "test_scanner"
    return d


# ═══════════════════════════════════════════════════════════════════════════
class TestDriverSaneContract:

    def test_name(self):
        from lios.scanner.sane_driver import DriverSane
        assert DriverSane.name == "Sane"

    def test_is_subclass_of_driver_base(self):
        from lios.scanner.sane_driver import DriverSane
        assert issubclass(DriverSane, DriverBase)

    def test_is_available_true_when_sane_imported(self):
        """Reload sane_driver with a working fake sane → available must be True."""
        fake = _build_fake_sane()
        mod = _reload_driver_with_sane(fake)
        assert mod.available is True
        assert mod.DriverSane.is_available() is True

    def test_is_available_false_when_sane_missing(self):
        """Remove sane from sys.modules → available must be False."""
        sys.modules.pop("sane", None)
        import lios.scanner.sane_driver as mod
        importlib.reload(mod)
        assert mod.available is False
        assert mod.DriverSane.is_available() is False
        # Restore a fake for subsequent tests
        sys.modules["sane"] = _build_fake_sane()
        importlib.reload(mod)


# ═══════════════════════════════════════════════════════════════════════════
class TestGetScannerOption:

    def test_returns_option_when_found(self):
        d = _make_driver()
        fake_opts = [
            (1, "brightness", None, None, None, None, None, None, (-100, 100)),
            (2, "threshold", None, None, None, None, None, None, (0, 255)),
        ]
        d.scanner.get_options = MagicMock(return_value=fake_opts)
        result = d.get_scanner_option("brightness")
        assert result[1] == "brightness"

    def test_returns_false_when_not_found(self):
        d = _make_driver()
        d.scanner.get_options = MagicMock(return_value=[
            (1, "mode", None, None, None, None, None, None, ["Color"])
        ])
        assert d.get_scanner_option("brightness") is False

    def test_returns_false_on_empty_options(self):
        d = _make_driver()
        d.scanner.get_options = MagicMock(return_value=[])
        assert d.get_scanner_option("anything") is False


# ═══════════════════════════════════════════════════════════════════════════
class TestResolutionBrightnessSane:

    def test_get_resolution(self):
        d = _make_driver()
        d.scanner.resolution = 600
        assert d.get_resolution() == 600

    def test_set_resolution(self):
        d = _make_driver()
        d.set_resolution(150)
        assert d.scanner.resolution == 150

    def test_get_brightness_via_brightness_param(self):
        d = _make_driver(brightness_param="brightness")
        d.scanner.brightness = 55
        assert d.get_brightness() == 55

    def test_get_brightness_via_threshold_param(self):
        d = _make_driver(brightness_param="threshold")
        d.scanner.threshold = 200
        assert d.get_brightness() == 200

    def test_get_brightness_no_support_returns_negative(self):
        d = _make_driver(brightness_support=False)
        assert d.get_brightness() == -1

    def test_set_brightness_updates_scanner_brightness(self):
        d = _make_driver(brightness_param="brightness")
        d.set_brightness(70)
        assert d.scanner.brightness == 70

    def test_set_brightness_updates_scanner_threshold(self):
        d = _make_driver(brightness_param="threshold")
        d.set_brightness(180)
        assert d.scanner.threshold == 180

    def test_set_brightness_no_support_does_not_set(self):
        d = _make_driver(brightness_support=False)
        original = d.scanner.brightness
        d.set_brightness(99)
        assert d.scanner.brightness == original


# ═══════════════════════════════════════════════════════════════════════════
class TestScanModeSane:

    def test_get_scan_mode(self):
        d = _make_driver(scanner_mode="Gray")
        assert d.get_scan_mode(None) == "Gray"

    def test_set_scan_mode(self):
        d = _make_driver()
        d.set_scan_mode("Lineart")
        assert d.scanner.mode == "Lineart"

    def test_get_available_scan_modes_with_option(self):
        d = _make_driver()
        fake_opts = [
            (3, "mode", None, None, None, None, None, None, ["Color", "Gray", "Lineart"])
        ]
        d.scanner.get_options = MagicMock(return_value=fake_opts)
        modes = d.get_available_scan_modes()
        assert isinstance(modes, list)

    def test_get_available_scan_modes_without_option(self):
        d = _make_driver()
        d.scanner.get_options = MagicMock(return_value=[])
        assert d.get_available_scan_modes() == []


# ═══════════════════════════════════════════════════════════════════════════
class TestScanAreaSane:

    def test_set_scan_area_full(self):
        d = _make_driver()
        brx_opt = (1, "br-x", *[None]*6, (0, 216))
        bry_opt = (2, "br-y", *[None]*6, (0, 297))
        d.scanner.get_options = MagicMock(return_value=[brx_opt, bry_opt])
        d.set_scan_area(DriverBase.SCAN_AREA_FULL)
        assert d.scanner.br_y == 297

    def test_set_scan_area_half(self):
        d = _make_driver()
        brx_opt = (1, "br-x", *[None]*6, (0, 216))
        bry_opt = (2, "br-y", *[None]*6, (0, 200))
        d.scanner.get_options = MagicMock(return_value=[brx_opt, bry_opt])
        d.set_scan_area(DriverBase.SCAN_AREA_HALF)
        assert d.scanner.br_y == 100

    def test_set_scan_area_returns_false_when_no_bry(self):
        d = _make_driver()
        d.scanner.get_options = MagicMock(return_value=[])
        result = d.set_scan_area(DriverBase.SCAN_AREA_FULL)
        assert result is False

    def test_get_scan_area(self):
        d = _make_driver()
        d.scanner.br_y = 150
        assert d.get_scan_area() == 150


# ═══════════════════════════════════════════════════════════════════════════
class TestScanAndLifecycleSane:

    @patch("lios.scanner.sane_driver.os.system")
    def test_scan_invokes_scanner_scan(self, mock_sys):
        d = _make_driver()
        pil_img = MagicMock()
        d.scanner.scan = MagicMock(return_value=pil_img)
        d.scan("/tmp/test_out.png")
        d.scanner.scan.assert_called_once()
        pil_img.save.assert_called_once_with("/tmp/sane_temp.png")
        assert mock_sys.called

    def test_cancel_calls_scanner_cancel(self):
        d = _make_driver()
        d.cancel()
        d.scanner.cancel.assert_called_once()

    def test_close_calls_scanner_close(self):
        d = _make_driver()
        d.close()
        d.scanner.close.assert_called_once()

    def test_check_brightness_support_true(self):
        d = _make_driver(brightness_support=True)
        assert d.check_brightness_support() is True

    def test_check_brightness_support_false(self):
        d = _make_driver(brightness_support=False)
        assert d.check_brightness_support() is False


# ═══════════════════════════════════════════════════════════════════════════
class TestGetAvailableDevicesSane:

    def test_returns_only_scanner_devices(self):
        fake_devices = [
            ("net:host:hp_laserjet", "HP", "LaserJet", "scanner"),
            ("usb:0x03f0:0x1b17", "Canon", "Pixma", "printer"),
        ]
        fake = _build_fake_sane(devices=fake_devices)
        mod = _reload_driver_with_sane(fake)
        devices = mod.DriverSane.get_available_devices()
        assert len(devices) == 1
        assert devices[0][0] == "net:host:hp_laserjet"

    def test_returns_empty_when_no_scanners(self):
        fake_devices = [("usb:001", "Acme", "Printer", "printer")]
        fake = _build_fake_sane(devices=fake_devices)
        mod = _reload_driver_with_sane(fake)
        assert mod.DriverSane.get_available_devices() == []

    def test_returns_empty_on_empty_list(self):
        fake = _build_fake_sane(devices=[])
        mod = _reload_driver_with_sane(fake)
        assert mod.DriverSane.get_available_devices() == []
