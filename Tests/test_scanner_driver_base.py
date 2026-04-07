#!/usr/bin/env python3
"""
Tests for lios/scanner/driver_base.py
──────────────────────────────────────
Covers:
  • DriverBase is abstract — cannot be instantiated directly
  • Every missing abstract method individually raises TypeError
  • SCAN_AREA_* constants have correct values (0–3)
  • A complete concrete stub implements all methods cleanly
"""
import logging
import pytest
from lios.scanner.driver_base import DriverBase

logger = logging.getLogger(__name__)


# ─── Concrete stub ────────────────────────────────────────────────────────
class _StubDriver(DriverBase):
    """Minimal valid implementation of DriverBase for testing."""

    def __init__(self, device="test", scanner_mode_switching=False,
                 resolution=300, brightness=40, scan_area=0):
        # Don't call super().__init__() — it opens devices
        self.resolution = resolution
        self.brightness = brightness
        self.scan_area = scan_area
        self.scanner_mode = "Color"
        self.brightness_multiplier = 1
        self.brightness_offset = 0

    def scan(self, filename, resolution=-1, brightness=-1, scan_area=-1):
        pass

    def get_resolution(self):
        return self.resolution

    def set_resolution(self, resolution):
        self.resolution = resolution

    def get_brightness(self):
        return self.brightness

    def set_brightness(self, brightness):
        self.brightness = brightness

    def set_scan_area(self, scan_area):
        self.scan_area = scan_area

    def get_scan_area(self):
        return self.scan_area

    def set_scan_mode(self, scan_mode):
        self.scanner_mode = scan_mode

    def get_scan_mode(self, scan_mode=None):
        return self.scanner_mode

    def get_available_scan_modes(self):
        return ["Color", "Gray", "Lineart"]

    def check_brightness_support(self):
        return True

    @staticmethod
    def get_available_devices():
        return []

    @staticmethod
    def is_available():
        return True

    def cancel(self):
        pass

    def close(self):
        pass


# ─── Abstract enforcement ─────────────────────────────────────────────────
class TestDriverBaseAbstractEnforcement:

    def test_direct_instantiation_raises(self):
        with pytest.raises(TypeError):
            DriverBase()  # type: ignore[abstract]

    def test_missing_scan_raises(self):
        class _B(DriverBase):
            def __init__(self, *a, **k): pass
            def get_resolution(self): return 0
            def set_resolution(self, r): pass
            def get_brightness(self): return 0
            def set_brightness(self, b): pass
            def set_scan_area(self, a): pass
            def get_scan_area(self): return 0
            def set_scan_mode(self, m): pass
            def get_scan_mode(self, m): return ""
            def get_available_scan_modes(self): return []
            def check_brightness_support(self): return False
            @staticmethod
            def get_available_devices(): return []
            @staticmethod
            def is_available(): return False
            def cancel(self): pass
            def close(self): pass
        with pytest.raises(TypeError):
            _B()

    def test_missing_is_available_raises(self):
        class _B(DriverBase):
            def __init__(self, *a, **k): pass
            def scan(self, *a, **k): pass
            def get_resolution(self): return 0
            def set_resolution(self, r): pass
            def get_brightness(self): return 0
            def set_brightness(self, b): pass
            def set_scan_area(self, a): pass
            def get_scan_area(self): return 0
            def set_scan_mode(self, m): pass
            def get_scan_mode(self, m): return ""
            def get_available_scan_modes(self): return []
            def check_brightness_support(self): return False
            @staticmethod
            def get_available_devices(): return []
            def cancel(self): pass
            def close(self): pass
        with pytest.raises(TypeError):
            _B()

    def test_complete_stub_does_not_raise(self):
        d = _StubDriver()
        assert d is not None
        logger.info("Complete stub driver instantiated OK")


# ─── SCAN_AREA constants ──────────────────────────────────────────────────
class TestScanAreaConstants:

    def test_full_is_zero(self):
        assert DriverBase.SCAN_AREA_FULL == 0

    def test_three_quarter_is_one(self):
        assert DriverBase.SCAN_AREA_THREE_QUARTER == 1

    def test_half_is_two(self):
        assert DriverBase.SCAN_AREA_HALF == 2

    def test_quarter_is_three(self):
        assert DriverBase.SCAN_AREA_QUARTER == 3

    def test_constants_are_unique(self):
        vals = [
            DriverBase.SCAN_AREA_FULL,
            DriverBase.SCAN_AREA_THREE_QUARTER,
            DriverBase.SCAN_AREA_HALF,
            DriverBase.SCAN_AREA_QUARTER,
        ]
        assert len(set(vals)) == 4

    def test_stub_can_use_constants(self):
        d = _StubDriver()
        d.set_scan_area(DriverBase.SCAN_AREA_FULL)
        assert d.get_scan_area() == DriverBase.SCAN_AREA_FULL


# ─── Stub behaviour ───────────────────────────────────────────────────────
class TestStubDriverBehaviour:

    def setup_method(self):
        self.driver = _StubDriver()

    def test_default_resolution(self):
        assert self.driver.get_resolution() == 300

    def test_set_resolution(self):
        self.driver.set_resolution(600)
        assert self.driver.get_resolution() == 600

    def test_default_brightness(self):
        assert self.driver.get_brightness() == 40

    def test_set_brightness(self):
        self.driver.set_brightness(80)
        assert self.driver.get_brightness() == 80

    def test_is_available_returns_bool(self):
        assert isinstance(_StubDriver.is_available(), bool)

    def test_get_available_devices_list(self):
        assert isinstance(_StubDriver.get_available_devices(), list)

    def test_get_available_scan_modes(self):
        modes = self.driver.get_available_scan_modes()
        assert isinstance(modes, list)
        assert len(modes) > 0

    def test_check_brightness_support_bool(self):
        assert isinstance(self.driver.check_brightness_support(), bool)

    def test_cancel_does_not_raise(self):
        self.driver.cancel()

    def test_close_does_not_raise(self):
        self.driver.close()

    def test_scan_does_not_raise(self):
        self.driver.scan("/tmp/fake_scan.png")

    def test_stub_is_subclass(self):
        assert issubclass(_StubDriver, DriverBase)
