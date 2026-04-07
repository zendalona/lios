#!/usr/bin/env python3
"""
Tests for lios/ocr/__init__.py
───────────────────────────────
Covers:
  • get_available_engines() – return type, ordering, filtering by availability
  • All engine classes imported correctly
"""
import logging
from typing import Callable, List, Type
from unittest.mock import patch

import pytest

logger = logging.getLogger(__name__)

from lios.ocr.ocr_engine_base import OcrEngineBase


class TestGetAvailableEngines:
    """Test the package-level get_available_engines() function.

    NOTE: Other test modules may create incomplete OcrEngineBase subclasses
    (e.g. _Bad classes without a 'name' attribute). get_available_engines()
    iterates __subclasses__() and accesses .name, so we must guard against
    that pollution.  We patch the iteration to only include real engines.
    """
    get_available_engines: Callable[[], List[Type[OcrEngineBase]]]
    real_engines: List[Type[OcrEngineBase]]

    @pytest.fixture(autouse=True)
    def _import(self):
        from lios.ocr import get_available_engines
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract
        from lios.ocr.ocr_engine_cuneiform import OcrEngineCuneiform
        from lios.ocr.ocr_engine_gocr import OcrEngineGocr
        from lios.ocr.ocr_engine_ocrad import OcrEngineOcrad
        from lios.ocr.ocr_engine_abbyy_finereader11 import OcrEngineAbbyyFineReader11
        from lios.ocr.ocr_engine_abbyy_finereader9 import OcrEngineAbbyyFineReader9
        self.get_available_engines = get_available_engines
        self.real_engines = [
            OcrEngineTesseract, OcrEngineCuneiform, OcrEngineGocr,
            OcrEngineOcrad, OcrEngineAbbyyFineReader11, OcrEngineAbbyyFineReader9,
        ]

    def _safe_get_engines(self) -> List[Type[OcrEngineBase]]:
        """Call get_available_engines with __subclasses__ limited to real engines."""
        with patch.object(OcrEngineBase, "__subclasses__",
                          return_value=self.real_engines):
            return self.get_available_engines()

    def test_returns_list(self):
        result = self._safe_get_engines()
        assert isinstance(result, list)

    def test_all_items_are_subclasses_of_base(self):
        for engine_cls in self._safe_get_engines():
            assert issubclass(engine_cls, OcrEngineBase), \
                f"{engine_cls} is not a subclass of OcrEngineBase"

    def test_all_items_have_name(self):
        for engine_cls in self._safe_get_engines():
            assert hasattr(engine_cls, "name")
            assert isinstance(engine_cls.name, str)

    def test_all_items_report_available(self):
        """Every engine returned must have is_available() == True."""
        for engine_cls in self._safe_get_engines():
            assert engine_cls.is_available() is True, \
                f"{engine_cls.name} returned by get_available_engines but is_available() is False"
            logger.info("Available engine: %s", engine_cls.name)

    def test_unavailable_engines_excluded(self):
        """Patch all engines to unavailable → list should be empty."""
        patches = []
        for eng in self.real_engines:
            p = patch.object(eng, "is_available", staticmethod(lambda: False))
            patches.append(p)
            p.start()
        try:
            result = self._safe_get_engines()
            assert result == [], \
                f"Expected empty list when all unavailable, got {result}"
        finally:
            for p in patches:
                p.stop()


class TestImports:
    """Ensure all engine classes are importable from lios.ocr."""

    def test_import_tesseract(self):
        from lios.ocr import OcrEngineTesseract
        assert OcrEngineTesseract.name == "Tesseract"

    def test_import_cuneiform(self):
        from lios.ocr import OcrEngineCuneiform
        assert OcrEngineCuneiform.name == "Cuneiform"

    def test_import_gocr(self):
        from lios.ocr import OcrEngineGocr
        assert OcrEngineGocr.name == "Gocr"

    def test_import_ocrad(self):
        from lios.ocr import OcrEngineOcrad
        assert OcrEngineOcrad.name == "Ocrad"

    def test_import_abbyy11(self):
        from lios.ocr import OcrEngineAbbyyFineReader11
        assert OcrEngineAbbyyFineReader11.name == "ABBYY FineReader11"

    def test_import_abbyy9(self):
        from lios.ocr import OcrEngineAbbyyFineReader9
        assert OcrEngineAbbyyFineReader9.name == "ABBYY FineReader9"

    def test_import_base(self):
        from lios.ocr import OcrEngineBase
        assert OcrEngineBase is not None
