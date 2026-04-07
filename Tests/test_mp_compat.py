#!/usr/bin/env python3
"""
Tests for lios/mp_compat.py
Covers:
  - MultiprocessingCompatibility.get_python_version_info()
  - MultiprocessingCompatibility.needs_fork_workaround()
  - MultiprocessingCompatibility.get_status()
  - MultiprocessingCompatibility.initialize() (idempotency)
  - ensure_fork_context decorator
"""
import logging
import sys
import multiprocessing

import pytest

logger = logging.getLogger(__name__)

from lios.mp_compat import (
    MultiprocessingCompatibility,
    ensure_fork_context,
    mp_compat,
    init,
    status,
)


class TestGetPythonVersionInfo:
    """get_python_version_info() must match sys.version_info."""

    def test_returns_tuple_of_three(self):
        result = MultiprocessingCompatibility.get_python_version_info()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_matches_sys_version_info(self):
        major, minor, micro = MultiprocessingCompatibility.get_python_version_info()
        assert major == sys.version_info.major
        assert minor == sys.version_info.minor
        assert micro == sys.version_info.micro
        logger.info("Python version detected: %d.%d.%d", major, minor, micro)


class TestNeedsForkWorkaround:
    """needs_fork_workaround() → True only for Python ≥ 3.14."""

    def test_returns_bool(self):
        assert isinstance(MultiprocessingCompatibility.needs_fork_workaround(), bool)

    def test_consistent_with_version(self):
        major, minor, _ = MultiprocessingCompatibility.get_python_version_info()
        expected = (major == 3 and minor >= 14) or major > 3
        assert MultiprocessingCompatibility.needs_fork_workaround() == expected
        logger.info("needs_fork_workaround: %s (Python %d.%d)",
                    expected, major, minor)


class TestGetStatus:
    """get_status() must return a dict with all expected keys."""

    EXPECTED_KEYS = {
        "python_version",
        "python_version_tuple",
        "needs_workaround",
        "current_start_method",
        "initialized",
        "compatible",
    }

    def test_returns_dict(self):
        result = MultiprocessingCompatibility.get_status()
        assert isinstance(result, dict)

    def test_all_keys_present(self):
        result = MultiprocessingCompatibility.get_status()
        for key in self.EXPECTED_KEYS:
            assert key in result, f"Key '{key}' missing from get_status()"

    def test_python_version_string_format(self):
        result = MultiprocessingCompatibility.get_status()
        parts = result["python_version"].split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_python_version_tuple_matches_string(self):
        result = MultiprocessingCompatibility.get_status()
        t = result["python_version_tuple"]
        s = result["python_version"]
        assert s == f"{t[0]}.{t[1]}.{t[2]}"

    def test_needs_workaround_is_bool(self):
        assert isinstance(MultiprocessingCompatibility.get_status()["needs_workaround"], bool)

    def test_initialized_is_bool(self):
        assert isinstance(MultiprocessingCompatibility.get_status()["initialized"], bool)

    def test_compatible_is_bool(self):
        assert isinstance(MultiprocessingCompatibility.get_status()["compatible"], bool)

    def test_status_alias_works(self):
        """The module-level 'status' alias must return same data."""
        result = status()
        assert isinstance(result, dict)
        assert "python_version" in result


class TestInitialize:
    """initialize() must be idempotent."""

    def test_returns_true(self):
        result = MultiprocessingCompatibility.initialize()
        assert result is True

    def test_idempotent_multiple_calls(self):
        for _ in range(3):
            result = MultiprocessingCompatibility.initialize()
            assert result is True

    def test_initialized_flag_set(self):
        MultiprocessingCompatibility.initialize()
        assert MultiprocessingCompatibility._initialized is True

    def test_init_alias_works(self):
        assert init() is True


class TestEnsureForkContextDecorator:
    """@ensure_fork_context must call the wrapped function normally."""

    def test_decorated_function_runs(self):
        @ensure_fork_context
        def _fn(x, y):
            return x + y

        assert _fn(2, 3) == 5

    def test_decorated_function_preserves_name(self):
        @ensure_fork_context
        def _my_func():
            pass

        assert _my_func.__name__ == "_my_func"

    def test_decorator_does_not_suppress_exceptions(self):
        @ensure_fork_context
        def _bad():
            raise ValueError("intentional")

        with pytest.raises(ValueError, match="intentional"):
            _bad()


class TestConvenienceAliases:
    """Module-level aliases must point to the right objects."""

    def test_mp_compat_alias(self):
        assert mp_compat is MultiprocessingCompatibility

    def test_init_alias_callable(self):
        """init() must behave identically to MultiprocessingCompatibility.initialize()."""
        assert callable(init)
        assert init() is True

    def test_status_alias_callable(self):
        """status() must return the same dict as get_status()."""
        assert callable(status)
        result = status()
        assert isinstance(result, dict)
        assert "python_version" in result
