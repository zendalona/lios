#!/usr/bin/env python3
"""
Tests for every concrete OCR engine class
──────────────────────────────────────────
Engines tested (each mocked so no real binary is called):
  • OcrEngineTesseract  – multi-language, file processing, cancel, dirs
  • OcrEngineCuneiform  – single-language, regex parsing
  • OcrEngineGocr       – single language list, PNM handling
  • OcrEngineOcrad      – single language list, iso-8859-9 encoding
  • OcrEngineAbbyyFineReader9  – large language list
  • OcrEngineAbbyyFineReader11 – large language list

All subprocess / os.system calls are patched so tests never exec real binaries.
"""
import logging
import os
import re
from typing import Type, cast
from unittest.mock import patch, MagicMock

import pytest

logger = logging.getLogger(__name__)

from lios.ocr.ocr_engine_base import OcrEngineBase


# ─── Tesseract ────────────────────────────────────────────────────────────
class TestOcrEngineTesseract:
    """Tests for OcrEngineTesseract – mocked to avoid real shell calls."""
    cls: Type[OcrEngineBase]
    ext: str

    @pytest.fixture(autouse=True)
    def _import_tesseract(self):
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract, TESSDATA_EXTENSION
        self.cls = OcrEngineTesseract
        self.ext = TESSDATA_EXTENSION

    # --- class attributes ---
    def test_name_attribute(self):
        assert self.cls.name == "Tesseract"

    def test_is_subclass_of_base(self):
        assert issubclass(self.cls, OcrEngineBase)

    def test_tessdata_extension_value(self):
        assert self.ext == ".traineddata"

    # --- is_available ---
    @patch("lios.ocr.ocr_engine_tesseract.subprocess.getoutput",
           return_value="tesseract: /usr/bin/tesseract /usr/share/tesseract")
    def test_is_available_true(self, mock_getoutput):
        assert self.cls.is_available() is True
        logger.info("is_available with /usr/bin/tesseract → True")

    @patch("lios.ocr.ocr_engine_tesseract.subprocess.getoutput",
           return_value="tesseract:")
    def test_is_available_false(self, mock_getoutput):
        assert self.cls.is_available() is False

    # --- support_multiple_languages ---
    def test_support_multiple_languages(self):
        assert self.cls.support_multiple_languages() is True

    # --- get_available_languages_in_dirpath ---
    def test_get_available_languages_in_dirpath_empty_dir(self, tmp_path):
        assert self.cls.get_available_languages_in_dirpath(str(tmp_path)) == []

    def test_get_available_languages_in_dirpath_with_files(self, tmp_path):
        (tmp_path / "eng.traineddata").write_bytes(b"x")
        (tmp_path / "fra.traineddata").write_bytes(b"x")
        (tmp_path / "unrelated.txt").write_bytes(b"x")
        langs = self.cls.get_available_languages_in_dirpath(str(tmp_path))
        assert "eng" in langs
        assert "fra" in langs
        assert "unrelated" not in langs

    def test_get_available_languages_in_dirpath_case_insensitive_ext(self, tmp_path):
        (tmp_path / "deu.TRAINEDDATA").write_bytes(b"x")
        langs = self.cls.get_available_languages_in_dirpath(str(tmp_path))
        assert "deu" in langs

    def test_get_available_languages_in_dirpath_bad_path(self):
        langs = self.cls.get_available_languages_in_dirpath("/nonexistent/path")
        assert langs == []

    # --- get_available_dirs ---
    def test_get_available_dirs_returns_list(self):
        result = self.cls.get_available_dirs()
        assert isinstance(result, list)

    # --- ocr_image_to_text (mocked) ---
    @patch("lios.ocr.ocr_engine_tesseract.os.system")
    @patch("lios.ocr.ocr_engine_tesseract.os.remove")
    def test_ocr_image_to_text_returns_string_on_missing_output(self, mock_remove, mock_sys):
        """When output file doesn't exist, should return empty string."""
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        engine.language_2 = False  # type: ignore[assignment]
        engine.language_3 = False  # type: ignore[assignment]
        result = engine.ocr_image_to_text("/fake/input.png")
        assert isinstance(result, str)

    @patch("lios.ocr.ocr_engine_tesseract.os.system")
    @patch("lios.ocr.ocr_engine_tesseract.os.remove")
    def test_ocr_multi_language_command(self, mock_remove, mock_sys):
        """When language_2/3 set, languages string should contain '+'."""
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        engine.language_2 = "fra"  # type: ignore[assignment]
        engine.language_3 = "deu"  # type: ignore[assignment]
        engine.ocr_image_to_text("/fake/input.png")
        calls = mock_sys.call_args_list
        assert len(calls) >= 2
        tess_cmd = calls[1][0][0]
        assert "eng+fra+deu" in tess_cmd
        logger.info("Tesseract multi-lang cmd: %s", tess_cmd)

    @patch("lios.ocr.ocr_engine_tesseract.os.system")
    @patch("lios.ocr.ocr_engine_tesseract.os.remove")
    def test_ocr_single_language_no_plus(self, mock_remove, mock_sys):
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        engine.language_2 = False  # type: ignore[assignment]
        engine.language_3 = False  # type: ignore[assignment]
        engine.ocr_image_to_text("/fake/input.png")
        calls = mock_sys.call_args_list
        tess_cmd = calls[1][0][0]
        assert "+" not in tess_cmd

    @patch("lios.ocr.ocr_engine_tesseract.os.system")
    @patch("lios.ocr.ocr_engine_tesseract.os.remove")
    def test_ocr_with_only_language_2(self, mock_remove, mock_sys):
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        engine.language_2 = "fra"  # type: ignore[assignment]
        engine.language_3 = False  # type: ignore[assignment]
        engine.ocr_image_to_text("/fake/input.png")
        tess_cmd = mock_sys.call_args_list[1][0][0]
        assert "eng+fra" in tess_cmd
        assert tess_cmd.count("+") == 1

    # --- cancel ---
    @patch("lios.ocr.ocr_engine_tesseract.os.system")
    def test_cancel_kills_processes(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill convert" in c for c in calls)
        assert any("pkill tesseract" in c for c in calls)


# ─── Cuneiform ────────────────────────────────────────────────────────────
class TestOcrEngineCuneiform:
    cls: Type[OcrEngineBase]
    prefix: str
    split_re: re.Pattern  # type: ignore[type-arg]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr.ocr_engine_cuneiform import (
            OcrEngineCuneiform, LANGUAGES_LINE_PREFIX, LANGUAGES_SPLIT_RE,
        )
        self.cls = OcrEngineCuneiform
        self.prefix = LANGUAGES_LINE_PREFIX
        self.split_re = LANGUAGES_SPLIT_RE

    def test_name(self):
        assert self.cls.name == "Cuneiform"

    def test_is_subclass(self):
        assert issubclass(self.cls, OcrEngineBase)

    def test_support_multiple_languages_false(self):
        assert self.cls.support_multiple_languages() is False

    @patch("lios.ocr.ocr_engine_cuneiform.subprocess.getoutput",
           return_value="cuneiform: /usr/bin/cuneiform")
    def test_is_available_true(self, _):
        assert self.cls.is_available() is True

    @patch("lios.ocr.ocr_engine_cuneiform.subprocess.getoutput",
           return_value="cuneiform:")
    def test_is_available_false(self, _):
        assert self.cls.is_available() is False

    @patch("lios.ocr.ocr_engine_cuneiform.subprocess.getoutput",
           return_value="Supported languages: eng ger fra rus swe spa ita")
    def test_get_available_languages_parses(self, _):
        langs = self.cls.get_available_languages()
        assert "eng" in langs
        assert "ger" in langs
        assert "fra" in langs
        logger.info("Cuneiform parsed langs: %s", langs)

    @patch("lios.ocr.ocr_engine_cuneiform.subprocess.getoutput",
           return_value="No output")
    def test_get_available_languages_empty(self, _):
        langs = self.cls.get_available_languages()
        assert langs == []

    def test_languages_split_regex(self):
        """The regex [^a-z] should split on any non-lowercase char."""
        result = self.split_re.split("eng ger.fra")
        assert "eng" in result
        assert "ger" in result
        assert "fra" in result

    @patch("lios.ocr.ocr_engine_cuneiform.os.system")
    def test_cancel_kills(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill cuneiform" in c for c in calls)

    @patch("lios.ocr.ocr_engine_cuneiform.os.system")
    @patch("lios.ocr.ocr_engine_cuneiform.os.remove")
    def test_ocr_returns_string_on_failure(self, mock_rm, mock_sys):
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        result = engine.ocr_image_to_text("/fake/img.png")
        assert isinstance(result, str)


# ─── Gocr ─────────────────────────────────────────────────────────────────
class TestOcrEngineGocr:
    cls: Type[OcrEngineBase]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr.ocr_engine_gocr import OcrEngineGocr
        self.cls = OcrEngineGocr

    def test_name(self):
        assert self.cls.name == "Gocr"

    def test_support_multiple_languages_false(self):
        assert self.cls.support_multiple_languages() is False

    def test_get_available_languages_only_eng(self):
        langs = self.cls.get_available_languages()
        assert langs == ["eng"]

    @patch("lios.ocr.ocr_engine_gocr.subprocess.getoutput",
           return_value="gocr: /usr/bin/gocr")
    def test_is_available_true(self, _):
        assert self.cls.is_available() is True

    @patch("lios.ocr.ocr_engine_gocr.subprocess.getoutput",
           return_value="gocr:")
    def test_is_available_false(self, _):
        assert self.cls.is_available() is False

    @patch("lios.ocr.ocr_engine_gocr.os.system")
    def test_cancel_kills(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill gocr" in c for c in calls)

    @patch("lios.ocr.ocr_engine_gocr.os.system")
    @patch("lios.ocr.ocr_engine_gocr.os.remove")
    def test_ocr_returns_empty_on_failure(self, mock_rm, mock_sys):
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        result = engine.ocr_image_to_text("/fake/img.png")
        assert result == ""


# ─── Ocrad ────────────────────────────────────────────────────────────────
class TestOcrEngineOcrad:
    cls: Type[OcrEngineBase]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr.ocr_engine_ocrad import OcrEngineOcrad
        self.cls = OcrEngineOcrad

    def test_name(self):
        assert self.cls.name == "Ocrad"

    def test_support_multiple_languages_false(self):
        assert self.cls.support_multiple_languages() is False

    def test_get_available_languages_only_eng(self):
        assert self.cls.get_available_languages() == ["eng"]

    @patch("lios.ocr.ocr_engine_ocrad.subprocess.getoutput",
           return_value="ocrad: /usr/bin/ocrad")
    def test_is_available_true(self, _):
        assert self.cls.is_available() is True

    @patch("lios.ocr.ocr_engine_ocrad.subprocess.getoutput",
           return_value="ocrad:")
    def test_is_available_false(self, _):
        assert self.cls.is_available() is False

    @patch("lios.ocr.ocr_engine_ocrad.os.system")
    def test_cancel_kills(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill ocrad" in c for c in calls)

    @patch("lios.ocr.ocr_engine_ocrad.os.system")
    @patch("lios.ocr.ocr_engine_ocrad.os.remove")
    def test_ocr_returns_empty_on_failure(self, mock_rm, mock_sys):
        engine = cast(OcrEngineBase, self.cls.__new__(self.cls))
        engine.language = "eng"
        result = engine.ocr_image_to_text("/fake/img.png")
        assert result == ""


# ─── ABBYY FineReader 11 ─────────────────────────────────────────────────
class TestOcrEngineAbbyyFineReader11:
    cls: Type[OcrEngineBase]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr.ocr_engine_abbyy_finereader11 import OcrEngineAbbyyFineReader11
        self.cls = OcrEngineAbbyyFineReader11

    def test_name(self):
        assert self.cls.name == "ABBYY FineReader11"

    def test_support_multiple_languages_false(self):
        assert self.cls.support_multiple_languages() is False

    def test_get_available_languages_is_long_list(self):
        langs = self.cls.get_available_languages()
        assert isinstance(langs, list)
        assert len(langs) > 100
        assert "English" in langs
        assert "French" in langs
        assert "Spanish" in langs
        logger.info("ABBYY11 languages count: %d", len(langs))

    def test_get_available_languages_all_strings(self):
        for lang in self.cls.get_available_languages():
            assert isinstance(lang, str) and len(lang) > 0

    @patch("lios.ocr.ocr_engine_abbyy_finereader11.subprocess.getoutput",
           return_value="abbyyocr11: /usr/bin/abbyyocr11")
    def test_is_available_true(self, _):
        assert self.cls.is_available() is True

    @patch("lios.ocr.ocr_engine_abbyy_finereader11.subprocess.getoutput",
           return_value="abbyyocr11:")
    def test_is_available_false(self, _):
        assert self.cls.is_available() is False

    @patch("lios.ocr.ocr_engine_abbyy_finereader11.os.system")
    def test_cancel_kills(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill abbyyocr11" in c for c in calls)


# ─── ABBYY FineReader 9 ──────────────────────────────────────────────────
class TestOcrEngineAbbyyFineReader9:
    cls: Type[OcrEngineBase]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr.ocr_engine_abbyy_finereader9 import OcrEngineAbbyyFineReader9
        self.cls = OcrEngineAbbyyFineReader9

    def test_name(self):
        assert self.cls.name == "ABBYY FineReader9"

    def test_support_multiple_languages_false(self):
        assert self.cls.support_multiple_languages() is False

    def test_get_available_languages_is_long_list(self):
        langs = self.cls.get_available_languages()
        assert len(langs) > 100
        assert "English" in langs

    @patch("lios.ocr.ocr_engine_abbyy_finereader9.subprocess.getoutput",
           return_value="abbyyocr9: /usr/bin/abbyyocr9")
    def test_is_available_true(self, _):
        assert self.cls.is_available() is True

    @patch("lios.ocr.ocr_engine_abbyy_finereader9.subprocess.getoutput",
           return_value="abbyyocr9:")
    def test_is_available_false(self, _):
        assert self.cls.is_available() is False

    @patch("lios.ocr.ocr_engine_abbyy_finereader9.os.system")
    def test_cancel_kills(self, mock_sys):
        self.cls.cancel()
        calls = [c[0][0] for c in mock_sys.call_args_list]
        assert any("pkill abbyyocr9" in c for c in calls)

    def test_abbyy9_and_11_languages_match(self):
        from lios.ocr.ocr_engine_abbyy_finereader11 import OcrEngineAbbyyFineReader11
        l9 = self.cls.get_available_languages()
        l11 = OcrEngineAbbyyFineReader11.get_available_languages()
        assert l9 == l11, "FineReader 9 and 11 should share the same language list"
