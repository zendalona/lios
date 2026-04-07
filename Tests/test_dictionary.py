#!/usr/bin/env python3
"""
Tests for lios/dictionary.py
Covers:
  - dictionary_language_dict: key/value types, required language codes
  - Mapping correctness for commonly-used Tesseract → enchant language codes
"""
import logging
import pytest

logger = logging.getLogger(__name__)

from lios.dictionary import dictionary_language_dict


class TestDictionaryLanguageDict:
    """Verify the Tesseract-to-enchant code mapping table."""

    def test_is_dict(self):
        assert isinstance(dictionary_language_dict, dict)

    def test_non_empty(self):
        assert len(dictionary_language_dict) > 0
        logger.info("dictionary_language_dict size: %d", len(dictionary_language_dict))

    def test_all_keys_are_strings(self):
        for k in dictionary_language_dict:
            assert isinstance(k, str), f"Key {k!r} is not a string"

    def test_all_values_are_strings(self):
        for v in dictionary_language_dict.values():
            assert isinstance(v, str), f"Value {v!r} is not a string"

    def test_all_values_non_empty(self):
        for k, v in dictionary_language_dict.items():
            assert len(v) > 0, f"Empty value for key '{k}'"

    # --- Spot-check well-known language codes ---
    @pytest.mark.parametrize("tess_code,enchant_code", [
        ("eng", "en"),
        ("fra", "fr"),
        ("deu", "de"),
        ("ita", "it"),
        ("spa", "es"),
        ("por", "pt"),
        ("rus", "ru"),
        ("pol", "pl"),
        ("hun", "hu"),
        ("swe", "sv"),
        ("tur", "tr"),
        ("ara", "ar"),
        ("hin", "hi"),
    ])
    def test_known_mapping(self, tess_code, enchant_code):
        assert tess_code in dictionary_language_dict, \
            f"'{tess_code}' not found in dictionary_language_dict"
        assert dictionary_language_dict[tess_code] == enchant_code, \
            (f"Expected '{tess_code}' → '{enchant_code}', "
             f"got '{dictionary_language_dict[tess_code]}'")
        logger.info("mapping OK: %s → %s", tess_code, enchant_code)

    def test_english_mapping(self):
        assert dictionary_language_dict.get("eng") == "en"

    def test_no_key_maps_to_empty_string(self):
        for k, v in dictionary_language_dict.items():
            assert v.strip() != "", f"Key '{k}' maps to a blank/whitespace value"
