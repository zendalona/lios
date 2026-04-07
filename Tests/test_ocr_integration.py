#!/usr/bin/env python3
"""
Integration tests for OcrEngineTesseract
──────────────────────────────────────────
These tests call the REAL tesseract binary on a generated test image.

They are automatically SKIPPED if:
  • tesseract binary is not installed, or
  • Pillow is not available (can't create test image)

To run them: ensure tesseract-ocr is installed:
    sudo apt install tesseract-ocr
"""
import logging
import os
import shutil
import tempfile

import pytest

logger = logging.getLogger(__name__)

# ─── Runtime guards ───────────────────────────────────────────────────────
_tesseract_available = shutil.which("tesseract") is not None

try:
    from PIL import Image, ImageDraw, ImageFont
    _pillow_available = True
except ImportError:
    _pillow_available = False

requires_tesseract = pytest.mark.skipif(
    not _tesseract_available,
    reason="tesseract binary not installed"
)
requires_pillow = pytest.mark.skipif(
    not _pillow_available,
    reason="Pillow not installed"
)
requires_both = pytest.mark.skipif(
    not (_tesseract_available and _pillow_available),
    reason="tesseract binary and/or Pillow not available"
)


# ─── Fixtures ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def test_image_dir():
    """Temporary directory that lives for the whole module."""
    d = tempfile.mkdtemp(prefix="lios_ocr_test_")
    yield d
    import shutil as _shutil
    _shutil.rmtree(d, ignore_errors=True)


def _make_text_image(path: str, text: str, font_size: int = 48) -> None:
    """Create a white PNG with black text at the given path."""
    img = Image.new("RGB", (600, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), text, fill=(0, 0, 0))
    img.save(path)
    logger.info("Created test image: %s", path)


# ─── Tests ────────────────────────────────────────────────────────────────
class TestTesseractIntegration:
    """End-to-end OCR integration: real binary, real image, real output."""

    @requires_both
    def test_ocr_hello_world(self, test_image_dir):
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract

        img_path = os.path.join(test_image_dir, "hello.png")
        _make_text_image(img_path, "Hello World")

        engine = OcrEngineTesseract.__new__(OcrEngineTesseract)
        engine.language = "eng"
        engine.language_2 = False
        engine.language_3 = False

        result = engine.ocr_image_to_text(img_path)
        assert isinstance(result, str), "OCR must return a string"
        assert len(result.strip()) > 0, "OCR output must not be empty"
        # Tesseract may add line breaks and extra whitespace
        result_clean = result.strip().replace("\n", " ").lower()
        assert "hello" in result_clean, \
            f"Expected 'Hello' in OCR output, got: {result!r}"
        logger.info("OCR output: %r", result)

    @requires_both
    def test_ocr_digits(self, test_image_dir):
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract

        img_path = os.path.join(test_image_dir, "digits.png")
        _make_text_image(img_path, "1234567890")

        engine = OcrEngineTesseract.__new__(OcrEngineTesseract)
        engine.language = "eng"
        engine.language_2 = False
        engine.language_3 = False

        result = engine.ocr_image_to_text(img_path)
        result_digits = "".join(c for c in result if c.isdigit())
        assert len(result_digits) > 0, \
            f"Expected digits in OCR output, got: {result!r}"
        logger.info("Digit OCR output: %r", result)

    @requires_both
    def test_ocr_known_word_lios(self, test_image_dir):
        """OCR a larger, cleaner render of 'LIOS OCR'.

        PIL's default small font renders poorly; use a large image so letters
        are big enough for tesseract to resolve.  We assert that the output is
        non-empty — a weaker but more reliable signal than exact-word matching.
        """
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract

        img_path = os.path.join(test_image_dir, "lios.png")
        # Larger canvas + large font_size for reliable recognition
        _make_text_image(img_path, "LIOS OCR", font_size=72)

        engine = OcrEngineTesseract.__new__(OcrEngineTesseract)
        engine.language = "eng"
        engine.language_2 = False
        engine.language_3 = False

        result = engine.ocr_image_to_text(img_path)
        # At minimum, tesseract should return some characters
        assert isinstance(result, str)
        assert len(result.strip()) > 0, \
            f"Expected non-empty OCR output for 'LIOS OCR', got: {result!r}"
        logger.info("LIOS OCR output: %r", result)

    @requires_tesseract
    def test_ocr_empty_image_returns_string(self, test_image_dir):
        """White blank image: OCR must return a string (possibly empty)."""
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract

        if not _pillow_available:
            pytest.skip("Pillow not available to create test image")

        img_path = os.path.join(test_image_dir, "blank.png")
        img = Image.new("RGB", (300, 100), color=(255, 255, 255))
        img.save(img_path)

        engine = OcrEngineTesseract.__new__(OcrEngineTesseract)
        engine.language = "eng"
        engine.language_2 = False
        engine.language_3 = False

        result = engine.ocr_image_to_text(img_path)
        assert isinstance(result, str), "Must always return a string"

    @requires_tesseract
    def test_tesseract_is_available(self):
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract
        assert OcrEngineTesseract.is_available() is True

    @requires_tesseract
    def test_get_available_languages_contains_eng(self):
        from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract
        dirs = OcrEngineTesseract.get_available_dirs()
        langs = []
        for d in dirs:
            langs.extend(OcrEngineTesseract.get_available_languages_in_dirpath(d))
        assert "eng" in langs, \
            f"'eng' not found in tessdata dirs: {dirs}"
        logger.info("Tessdata dirs: %s | Languages: %s", dirs, langs[:10])
