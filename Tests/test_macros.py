#!/usr/bin/env python3
"""
Tests for lios/macros.py
Covers:
  - get_list_of_mixed_case_combinations()
  - Constant type/value sanity checks
  - set_datadir() path assignment behaviour
  - version format
"""
import logging
import os
import pytest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level import (import macros fresh to get baseline state)
# ---------------------------------------------------------------------------
import lios.macros as macros


class TestMixedCaseCombinations:
    """get_list_of_mixed_case_combinations() – pure function, no I/O."""

    def test_single_lowercase_word(self):
        result = macros.get_list_of_mixed_case_combinations(["ab"])
        # 'ab' → 2^2 = 4 combinations
        assert len(result) == 4
        expected = {"ab", "Ab", "aB", "AB"}
        assert set(result) == expected
        logger.info("single_lowercase_word: %s", result)

    def test_multiple_words(self):
        result = macros.get_list_of_mixed_case_combinations(["a", "b"])
        # each single-char word → 2 combos, total 4
        assert len(result) == 4

    def test_returns_list(self):
        result = macros.get_list_of_mixed_case_combinations(["png"])
        assert isinstance(result, list)

    def test_empty_list_input(self):
        result = macros.get_list_of_mixed_case_combinations([])
        assert result == []

    def test_all_image_formats_present(self):
        """supported_image_formats must contain the canonical lowercase forms."""
        base_formats = ["png", "pnm", "jpg", "jpeg", "tif", "tiff", "bmp", "pbm", "ppm"]
        for fmt in base_formats:
            assert fmt in macros.supported_image_formats, \
                f"Expected '{fmt}' in supported_image_formats"
        for fmt in base_formats:
            assert fmt.upper() in macros.supported_image_formats, \
                f"Expected '{fmt.upper()}' in supported_image_formats"
        logger.info("supported_image_formats count: %d", len(macros.supported_image_formats))

    def test_all_text_formats_present(self):
        assert "txt" in macros.supported_text_formats
        assert "TXT" in macros.supported_text_formats

    def test_all_pdf_formats_present(self):
        assert "pdf" in macros.supported_pdf_formats
        assert "PDF" in macros.supported_pdf_formats


class TestConstants:
    """Sanity-check public constants exposed by macros.py."""

    def test_version_is_string(self):
        assert isinstance(macros.version, str)

    def test_version_has_dot(self):
        assert "." in macros.version
        logger.info("LIOS version: %s", macros.version)

    def test_app_name_is_string(self):
        assert isinstance(macros.app_name, str)
        assert len(macros.app_name) > 0

    def test_config_dir_under_home(self):
        home = os.environ["HOME"]
        assert macros.config_dir.startswith(home), \
            "config_dir must be under the user's HOME directory"

    def test_tmp_dir_value(self):
        assert macros.tmp_dir == "/tmp/Lios/"

    def test_preferences_file_under_config_dir(self):
        assert macros.preferences_file_path.startswith(macros.config_dir)

    def test_bookmarks_dir_under_config_dir(self):
        assert macros.bookmarks_dir.startswith(macros.config_dir)

    def test_major_character_encodings_non_empty(self):
        assert len(macros.major_character_encodings_list) > 0
        assert "utf-8" in macros.major_character_encodings_list

    def test_links_are_https(self):
        assert macros.source_link.startswith("https://")
        assert macros.home_page_link.startswith("https://")


class TestSetDatadir:
    """set_datadir() must update all derived paths without double-prefixing."""

    def test_set_datadir_updates_logo(self):
        macros.set_datadir("/tmp/fake_lios_data")
        assert macros.logo_file.startswith("/tmp/fake_lios_data")
        logger.info("logo_file after set_datadir: %s", macros.logo_file)

    def test_set_datadir_updates_icon_dir(self):
        macros.set_datadir("/tmp/fake_lios_data")
        assert macros.icon_dir.startswith("/tmp/fake_lios_data")

    def test_set_datadir_updates_readme(self):
        macros.set_datadir("/tmp/fake_lios_data")
        assert macros.readme_file.startswith("/tmp/fake_lios_data")

    def test_set_datadir_no_double_prefix(self):
        macros.set_datadir("/tmp/fake_lios_data")
        # Calling again must not produce double prefix
        macros.set_datadir("/tmp/fake_lios_data")
        count = macros.logo_file.count("/tmp/fake_lios_data")
        assert count == 1, f"Double-prefix detected: {macros.logo_file}"
