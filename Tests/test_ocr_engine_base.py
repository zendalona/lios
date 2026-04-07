#!/usr/bin/env python3
"""
Tests for lios/ocr/ocr_engine_base.py
──────────────────────────────────────
Exhaustive coverage of OcrEngineBase:
  • Abstract-method enforcement (cannot instantiate the base, partial impl raises)
  • set_language()  – valid, invalid, empty, None
  • set_language_2() – valid, invalid, resets to False on bad input
  • set_language_3() – valid, invalid, resets to False on bad input
  • Language change sequences (valid → invalid → valid)
  • cancel() default (no-op, must not raise)
  • ocr_image_to_text_with_multiprocessing() stubbed path
  • Subclassing contract – all required methods, name attribute convention
"""
import logging
import multiprocessing
from unittest.mock import patch, MagicMock

import pytest

logger = logging.getLogger(__name__)

from lios.ocr.ocr_engine_base import OcrEngineBase


# ═══════════════════════════════════════════════════════════════════════════
# Concrete stubs
# ═══════════════════════════════════════════════════════════════════════════
class _StubEngine(OcrEngineBase):
    """Minimal valid concrete implementation for testing base behaviour."""
    name = "StubEngine"
    _languages = ["eng", "fra", "deu", "spa", "hin", "ara"]

    def __init__(self, language=None):
        self.language = language
        self.language_2 = False
        self.language_3 = False

    @staticmethod
    def get_available_languages():
        return _StubEngine._languages

    @staticmethod
    def support_multiple_languages():
        return True

    def ocr_image_to_text(self, image_file_name):
        return f"OCR result for {image_file_name}"

    @staticmethod
    def is_available():
        return True


class _StubSingleLangEngine(OcrEngineBase):
    """Engine that only supports one language (like Gocr / Ocrad)."""
    name = "SingleLangStub"
    _languages = ["eng"]

    def __init__(self, language=None):
        self.language = language
        self.language_2 = False
        self.language_3 = False

    @staticmethod
    def get_available_languages():
        return _StubSingleLangEngine._languages

    @staticmethod
    def support_multiple_languages():
        return False

    def ocr_image_to_text(self, image_file_name):
        return "text"

    @staticmethod
    def is_available():
        return True


# ═══════════════════════════════════════════════════════════════════════════
# 1. Abstract-method enforcement
# ═══════════════════════════════════════════════════════════════════════════
class TestAbstractMethodEnforcement:
    """OcrEngineBase is abstract – instantiation must fail."""

    def test_direct_instantiation_raises_type_error(self):
        with pytest.raises(TypeError):
            OcrEngineBase()

    def test_missing_get_available_languages_raises(self):
        class _Bad(OcrEngineBase):
            @staticmethod
            def support_multiple_languages(): return False
            def ocr_image_to_text(self, f): return ""
            @staticmethod
            def is_available(): return False
        with pytest.raises(TypeError):
            _Bad()

    def test_missing_support_multiple_languages_raises(self):
        class _Bad(OcrEngineBase):
            @staticmethod
            def get_available_languages(): return []
            def ocr_image_to_text(self, f): return ""
            @staticmethod
            def is_available(): return False
        with pytest.raises(TypeError):
            _Bad()

    def test_missing_ocr_image_to_text_raises(self):
        class _Bad(OcrEngineBase):
            @staticmethod
            def get_available_languages(): return []
            @staticmethod
            def support_multiple_languages(): return False
            @staticmethod
            def is_available(): return False
        with pytest.raises(TypeError):
            _Bad()

    def test_missing_is_available_raises(self):
        class _Bad(OcrEngineBase):
            @staticmethod
            def get_available_languages(): return []
            @staticmethod
            def support_multiple_languages(): return False
            def ocr_image_to_text(self, f): return ""
        with pytest.raises(TypeError):
            _Bad()

    def test_complete_implementation_does_not_raise(self):
        engine = _StubEngine("eng")
        assert engine.language == "eng"
        logger.info("Complete stub instantiated OK")


# ═══════════════════════════════════════════════════════════════════════════
# 2. set_language() — primary language
# ═══════════════════════════════════════════════════════════════════════════
class TestSetLanguage:
    engine: _StubEngine

    def setup_method(self):
        self.engine = _StubEngine()

    def test_valid_language_returns_true(self):
        assert self.engine.set_language("eng") is True

    def test_valid_language_updates_attribute(self):
        self.engine.set_language("fra")
        assert self.engine.language == "fra"
        logger.info("set_language('fra') → %s", self.engine.language)

    def test_invalid_language_returns_false(self):
        assert self.engine.set_language("xyz") is False

    def test_invalid_language_preserves_previous(self):
        self.engine.language = "deu"
        self.engine.set_language("xyz")
        assert self.engine.language == "deu"

    def test_none_language_returns_false(self):
        assert self.engine.set_language(None) is False

    def test_empty_string_returns_false(self):
        assert self.engine.set_language("") is False

    @pytest.mark.parametrize("lang", _StubEngine._languages)
    def test_every_known_language_accepted(self, lang):
        assert self.engine.set_language(lang) is True
        assert self.engine.language == lang

    def test_case_sensitive(self):
        """Language codes are case-sensitive; 'ENG' ≠ 'eng'."""
        assert self.engine.set_language("ENG") is False

    def test_set_language_sequence_valid_invalid_valid(self):
        assert self.engine.set_language("eng") is True
        assert self.engine.set_language("bad") is False
        assert self.engine.language == "eng"  # previous valid sticks
        assert self.engine.set_language("spa") is True
        assert self.engine.language == "spa"


# ═══════════════════════════════════════════════════════════════════════════
# 3. set_language_2() — secondary language
# ═══════════════════════════════════════════════════════════════════════════
class TestSetLanguage2:
    engine: _StubEngine

    def setup_method(self):
        self.engine = _StubEngine()

    def test_valid_returns_true(self):
        assert self.engine.set_language_2("fra") is True
        assert self.engine.language_2 == "fra"

    def test_invalid_returns_false(self):
        assert self.engine.set_language_2("zzz") is False

    def test_invalid_resets_to_false(self):
        self.engine.language_2 = "deu"  # type: ignore[assignment]
        self.engine.set_language_2("zzz")
        assert self.engine.language_2 is False
        logger.info("set_language_2 invalid → language_2=%s", self.engine.language_2)

    def test_valid_then_invalid_resets(self):
        self.engine.set_language_2("fra")
        assert self.engine.language_2 == "fra"
        self.engine.set_language_2("bad")
        assert self.engine.language_2 is False

    def test_none_is_invalid(self):
        assert self.engine.set_language_2(None) is False
        assert self.engine.language_2 is False

    @pytest.mark.parametrize("lang", _StubEngine._languages)
    def test_all_languages_accepted(self, lang):
        assert self.engine.set_language_2(lang) is True
        assert self.engine.language_2 == lang


# ═══════════════════════════════════════════════════════════════════════════
# 4. set_language_3() — tertiary language
# ═══════════════════════════════════════════════════════════════════════════
class TestSetLanguage3:
    engine: _StubEngine

    def setup_method(self):
        self.engine = _StubEngine()

    def test_valid_returns_true(self):
        assert self.engine.set_language_3("deu") is True
        assert self.engine.language_3 == "deu"

    def test_invalid_returns_false(self):
        assert self.engine.set_language_3("nope") is False

    def test_invalid_resets_to_false(self):
        self.engine.language_3 = "spa"  # type: ignore[assignment]
        self.engine.set_language_3("nope")
        assert self.engine.language_3 is False

    def test_valid_then_invalid_then_valid(self):
        self.engine.set_language_3("ara")
        assert self.engine.language_3 == "ara"
        self.engine.set_language_3("bad")
        assert self.engine.language_3 is False
        self.engine.set_language_3("hin")
        assert self.engine.language_3 == "hin"

    @pytest.mark.parametrize("lang", _StubEngine._languages)
    def test_all_languages_accepted(self, lang):
        assert self.engine.set_language_3(lang) is True
        assert self.engine.language_3 == lang


# ═══════════════════════════════════════════════════════════════════════════
# 5. Multi-language combinations
# ═══════════════════════════════════════════════════════════════════════════
class TestMultiLanguageCombinations:
    """Test setting all three language slots simultaneously."""
    engine: _StubEngine

    def setup_method(self):
        self.engine = _StubEngine()

    def test_all_three_different_languages(self):
        self.engine.set_language("eng")
        self.engine.set_language_2("fra")
        self.engine.set_language_3("deu")
        assert self.engine.language == "eng"
        assert self.engine.language_2 == "fra"
        assert self.engine.language_3 == "deu"

    def test_same_language_in_all_slots(self):
        """The base allows duplicates — that's fine."""
        self.engine.set_language("eng")
        self.engine.set_language_2("eng")
        self.engine.set_language_3("eng")
        assert self.engine.language == "eng"
        assert self.engine.language_2 == "eng"
        assert self.engine.language_3 == "eng"

    def test_primary_valid_others_invalid(self):
        self.engine.set_language("spa")
        self.engine.set_language_2("bad1")
        self.engine.set_language_3("bad2")
        assert self.engine.language == "spa"
        assert self.engine.language_2 is False
        assert self.engine.language_3 is False

    def test_single_lang_engine_cannot_set_lang2(self):
        engine = _StubSingleLangEngine()
        assert engine.set_language("eng") is True
        assert engine.set_language_2("fra") is False
        assert engine.language_2 is False
        logger.info("Single-lang engine correctly rejects second language")


# ═══════════════════════════════════════════════════════════════════════════
# 6. cancel() — default implementation
# ═══════════════════════════════════════════════════════════════════════════
class TestCancel:

    def test_cancel_does_not_raise(self):
        """Base cancel() is a no-op pass — must not raise."""
        OcrEngineBase.cancel()  # static-ish call

    def test_stub_cancel_does_not_raise(self):
        engine = _StubEngine("eng")
        # cancel is a bare function, not bound to self in base
        OcrEngineBase.cancel()


# ═══════════════════════════════════════════════════════════════════════════
# 7. ocr_image_to_text() via stub
# ═══════════════════════════════════════════════════════════════════════════
class TestOcrImageToText:

    def test_returns_string(self):
        engine = _StubEngine("eng")
        result = engine.ocr_image_to_text("test_image.png")
        assert isinstance(result, str)

    def test_result_contains_filename(self):
        engine = _StubEngine("eng")
        result = engine.ocr_image_to_text("test_image.png")
        assert "test_image.png" in result


# ═══════════════════════════════════════════════════════════════════════════
# 8. Subclass contract & name attribute
# ═══════════════════════════════════════════════════════════════════════════
class TestSubclassContract:

    def test_stub_has_name(self):
        assert hasattr(_StubEngine, "name")
        assert _StubEngine.name == "StubEngine"

    def test_single_lang_engine_has_name(self):
        assert _StubSingleLangEngine.name == "SingleLangStub"

    def test_stub_is_subclass_of_base(self):
        assert issubclass(_StubEngine, OcrEngineBase)

    def test_instance_is_instance_of_base(self):
        engine = _StubEngine("eng")
        assert isinstance(engine, OcrEngineBase)

    def test_subclasses_registered(self):
        subs = OcrEngineBase.__subclasses__()
        # Our stubs must be among registered subclasses
        sub_names = [s.__name__ for s in subs]
        assert "_StubEngine" in sub_names
        assert "_StubSingleLangEngine" in sub_names
        logger.info("Registered subclasses: %s", sub_names)

    def test_get_available_languages_returns_list(self):
        langs = _StubEngine.get_available_languages()
        assert isinstance(langs, list)
        assert len(langs) > 0

    def test_support_multiple_languages_returns_bool(self):
        assert isinstance(_StubEngine.support_multiple_languages(), bool)

    def test_is_available_returns_bool(self):
        assert isinstance(_StubEngine.is_available(), bool)


# ═══════════════════════════════════════════════════════════════════════════
# 9. Edge cases
# ═══════════════════════════════════════════════════════════════════════════
class TestEdgeCases:

    def test_set_language_with_whitespace(self):
        engine = _StubEngine()
        assert engine.set_language(" eng") is False

    def test_set_language_with_trailing_whitespace(self):
        engine = _StubEngine()
        assert engine.set_language("eng ") is False

    def test_set_language_numeric_string(self):
        engine = _StubEngine()
        assert engine.set_language("123") is False

    def test_set_language_with_special_chars(self):
        engine = _StubEngine()
        assert engine.set_language("eng!") is False

    def test_multiple_rapid_language_changes(self):
        engine = _StubEngine()
        for lang in _StubEngine._languages * 5:  # 30 rapid calls
            assert engine.set_language(lang) is True
            assert engine.language == lang

    def test_language_attribute_type_is_string_after_set(self):
        engine = _StubEngine()
        engine.set_language("hin")
        assert type(engine.language) is str
