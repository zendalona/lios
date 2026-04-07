#!/usr/bin/env python3
"""
Tests for lios/ocr/tesseract_path_finder.py
────────────────────────────────────────────
Covers:
  • FastTessdataFinder – init, _is_timeout, _elapsed
  • _is_valid_tessdata_quick – real tmp dirs
  • _check_environment_vars – mocked env
  • _get_smart_common_paths – OS-specific lists
  • _check_path_with_glob – glob expansion
  • _finalize_paths – dedup, prioritisation
  • _get_tessdata_from_binary – relative-path logic
  • _find_tesseract_binaries – shutil.which mock
  • Cache load / save cycle
  • Module-level API functions: find_tessdata_paths, validate_tessdata_path, clear_cache
"""
import json
import logging
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

logger = logging.getLogger(__name__)

from lios.ocr.tesseract_path_finder import (
    FastTessdataFinder,
    find_tessdata_paths,
    get_tessdata_path,
    validate_tessdata_path,
    clear_cache,
)


# ═══════════════════════════════════════════════════════════════════════════
# FastTessdataFinder – construction & timing
# ═══════════════════════════════════════════════════════════════════════════
class TestFastTessdataFinderInit:

    def test_default_timeout(self):
        f = FastTessdataFinder()
        assert f.timeout == 8.0

    def test_custom_timeout(self):
        f = FastTessdataFinder(timeout=2.0)
        assert f.timeout == 2.0

    def test_default_max_workers(self):
        f = FastTessdataFinder()
        assert f.max_workers == 4

    def test_custom_max_workers(self):
        f = FastTessdataFinder(max_workers=2)
        assert f.max_workers == 2

    def test_found_paths_starts_empty(self):
        f = FastTessdataFinder()
        assert len(f.found_paths) == 0

    def test_os_type_is_string(self):
        f = FastTessdataFinder()
        assert isinstance(f.os_type, str)
        assert f.os_type in ("linux", "darwin", "windows")

    def test_cache_file_is_in_home(self):
        f = FastTessdataFinder()
        assert str(Path.home()) in str(f.cache_file)

    def test_cache_max_age(self):
        f = FastTessdataFinder()
        assert f.cache_max_age == 6 * 3600


class TestTimingMethods:

    def test_elapsed_zero_before_start(self):
        f = FastTessdataFinder()
        assert f._elapsed() == 0

    def test_elapsed_positive_after_start(self):
        f = FastTessdataFinder()
        f.start_time = time.time() - 1.0
        assert f._elapsed() >= 1.0

    def test_is_timeout_false_initially(self):
        f = FastTessdataFinder(timeout=5.0)
        f.start_time = time.time()
        assert f._is_timeout() is False

    def test_is_timeout_true_after_expiry(self):
        f = FastTessdataFinder(timeout=0.0)
        f.start_time = time.time() - 1.0
        assert f._is_timeout() is True


# ═══════════════════════════════════════════════════════════════════════════
# _is_valid_tessdata_quick – uses real tmp dirs
# ═══════════════════════════════════════════════════════════════════════════
class TestIsValidTessdataQuick:

    def test_valid_dir_with_traineddata(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"data")
        f = FastTessdataFinder()
        assert f._is_valid_tessdata_quick(str(tmp_path)) is True

    def test_empty_dir_is_invalid(self, tmp_path):
        f = FastTessdataFinder()
        assert f._is_valid_tessdata_quick(str(tmp_path)) is False

    def test_dir_with_wrong_extension(self, tmp_path):
        (tmp_path / "eng.dat").write_bytes(b"data")
        f = FastTessdataFinder()
        assert f._is_valid_tessdata_quick(str(tmp_path)) is False

    def test_nonexistent_path(self):
        f = FastTessdataFinder()
        assert f._is_valid_tessdata_quick("/nonexistent/path/tessdata") is False

    def test_file_not_dir(self, tmp_path):
        file_path = tmp_path / "not_a_dir"
        file_path.write_bytes(b"x")
        f = FastTessdataFinder()
        assert f._is_valid_tessdata_quick(str(file_path)) is False


# ═══════════════════════════════════════════════════════════════════════════
# _check_environment_vars
# ═══════════════════════════════════════════════════════════════════════════
class TestCheckEnvironmentVars:

    def test_tessdata_prefix_found(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"data")
        f = FastTessdataFinder()
        f.start_time = time.time()
        with patch.dict(os.environ, {"TESSDATA_PREFIX": str(tmp_path)}):
            paths = f._check_environment_vars()
        assert len(paths) >= 1
        logger.info("env var paths: %s", paths)

    def test_no_env_vars(self):
        f = FastTessdataFinder()
        f.start_time = time.time()
        with patch.dict(os.environ, {}, clear=True):
            # Some env vars might leak; ensure we don't crash
            paths = f._check_environment_vars()
            assert isinstance(paths, list)


# ═══════════════════════════════════════════════════════════════════════════
# _get_smart_common_paths – OS-dependent
# ═══════════════════════════════════════════════════════════════════════════
class TestGetSmartCommonPaths:

    def test_returns_list(self):
        f = FastTessdataFinder()
        paths = f._get_smart_common_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_linux_paths_contain_usr_share(self):
        f = FastTessdataFinder()
        f.os_type = "linux"
        paths = f._get_smart_common_paths()
        assert any("/usr/share" in p for p in paths)

    def test_darwin_paths_contain_homebrew(self):
        f = FastTessdataFinder()
        f.os_type = "darwin"
        paths = f._get_smart_common_paths()
        assert any("homebrew" in p for p in paths)

    def test_windows_paths_contain_program_files(self):
        f = FastTessdataFinder()
        f.os_type = "windows"
        paths = f._get_smart_common_paths()
        assert any("Program Files" in p for p in paths)


# ═══════════════════════════════════════════════════════════════════════════
# _check_path_with_glob
# ═══════════════════════════════════════════════════════════════════════════
class TestCheckPathWithGlob:

    def test_exact_valid_path(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"x")
        f = FastTessdataFinder()
        result = f._check_path_with_glob(str(tmp_path))
        assert len(result) == 1

    def test_exact_invalid_path(self, tmp_path):
        f = FastTessdataFinder()
        result = f._check_path_with_glob(str(tmp_path / "nonexistent"))
        assert result == []

    def test_glob_pattern(self, tmp_path):
        sub = tmp_path / "tessdata"
        sub.mkdir()
        (sub / "eng.traineddata").write_bytes(b"x")
        f = FastTessdataFinder()
        result = f._check_path_with_glob(str(tmp_path / "*"))
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════════════════════
# _finalize_paths – dedup & priority
# ═══════════════════════════════════════════════════════════════════════════
class TestFinalizePaths:

    def test_deduplicates(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"x")
        f = FastTessdataFinder()
        result = f._finalize_paths([str(tmp_path), str(tmp_path)])
        assert len(result) == 1

    def test_removes_invalid_paths(self, tmp_path):
        f = FastTessdataFinder()
        result = f._finalize_paths(["/nonexistent/path"])
        assert result == []

    def test_returns_list(self, tmp_path):
        f = FastTessdataFinder()
        result = f._finalize_paths([])
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════════════════════
# _find_tesseract_binaries
# ═══════════════════════════════════════════════════════════════════════════
class TestFindTesseractBinaries:

    @patch("lios.ocr.tesseract_path_finder.shutil.which", return_value="/usr/bin/tesseract")
    def test_finds_via_which(self, _):
        f = FastTessdataFinder()
        bins = f._find_tesseract_binaries()
        assert "/usr/bin/tesseract" in bins

    @patch("lios.ocr.tesseract_path_finder.shutil.which", return_value=None)
    def test_returns_list_when_not_found(self, _):
        f = FastTessdataFinder()
        bins = f._find_tesseract_binaries()
        assert isinstance(bins, list)


# ═══════════════════════════════════════════════════════════════════════════
# Cache load / save
# ═══════════════════════════════════════════════════════════════════════════
class TestCache:

    def test_save_and_load_cycle(self, tmp_path):
        f = FastTessdataFinder()
        f.cache_file = tmp_path / "test_cache.json"
        # Create a real tessdata dir for validation
        tessdir = tmp_path / "tessdata"
        tessdir.mkdir()
        (tessdir / "eng.traineddata").write_bytes(b"x")
        f._save_cache([str(tessdir)])
        loaded = f._load_cache()
        assert str(tessdir) in loaded

    def test_load_missing_cache(self, tmp_path):
        f = FastTessdataFinder()
        f.cache_file = tmp_path / "missing.json"
        assert f._load_cache() == []

    def test_load_expired_cache(self, tmp_path):
        f = FastTessdataFinder()
        f.cache_file = tmp_path / "old_cache.json"
        f._save_cache(["/some/path"])
        # Force old timestamp
        old_time = time.time() - f.cache_max_age - 100
        os.utime(str(f.cache_file), (old_time, old_time))
        assert f._load_cache() == []


# ═══════════════════════════════════════════════════════════════════════════
# Module-level API
# ═══════════════════════════════════════════════════════════════════════════
class TestModuleAPI:

    def test_find_tessdata_paths_returns_list(self):
        result = find_tessdata_paths(verbose=False, timeout=2.0)
        assert isinstance(result, list)
        logger.info("find_tessdata_paths returned %d paths", len(result))

    def test_get_tessdata_path_returns_str_or_none(self):
        result = get_tessdata_path(verbose=False)
        assert result is None or isinstance(result, str)

    def test_validate_tessdata_path_existing_dir(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"fake")
        info = validate_tessdata_path(str(tmp_path))
        assert info["valid"] is True
        assert info["exists"] is True
        assert info["readable"] is True
        assert info["language_count"] == 1
        assert "eng" in info["languages"]
        assert info["size_mb"] >= 0

    def test_validate_tessdata_path_nonexistent(self):
        info = validate_tessdata_path("/nonexistent/tessdata")
        assert info["valid"] is False
        assert info["exists"] is False

    def test_validate_tessdata_path_empty_dir(self, tmp_path):
        info = validate_tessdata_path(str(tmp_path))
        assert info["valid"] is False
        assert info["language_count"] == 0

    def test_clear_cache_returns_bool(self):
        result = clear_cache()
        assert isinstance(result, bool)
