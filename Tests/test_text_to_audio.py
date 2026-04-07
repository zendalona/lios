#!/usr/bin/env python3
"""
Tests for lios/text_to_audio.py
Covers:
  - text_to_audio_converter.__init__() defaults
  - set_volume() – valid and invalid values
  - set_pitch()  – valid and invalid values
  - set_speed()  – valid and invalid values
  - get_volume/get_pitch/get_speed/get_voice/get_split_time
  - set_voice()  – mocked so we never call espeak
"""
import logging
from unittest.mock import patch

import pytest

logger = logging.getLogger(__name__)

# Patch list_voices for every test so no subprocess call hits espeak
FAKE_VOICES = ["english", "french", "german", "en-us", "en-gb"]
PATCH_VOICES = patch(
    "lios.text_to_audio.text_to_audio_converter.list_voices",
    staticmethod(lambda: FAKE_VOICES),
)


@PATCH_VOICES
class TestTextToAudioConverter:
    """All tests run with list_voices() mocked to FAKE_VOICES."""

    def _make(self, **kwargs):
        from lios.text_to_audio import text_to_audio_converter
        defaults = dict(text="hello", volume=100, voice="english",
                        split_time=5, pitch=50, speed=170)
        defaults.update(kwargs)
        return text_to_audio_converter(**defaults)

    # --- Defaults ---
    def test_default_volume(self):
        obj = self._make()
        assert obj.get_volume() == 100
        logger.info("default volume: %s", obj.get_volume())

    def test_default_pitch(self):
        assert self._make().get_pitch() == 50

    def test_default_speed(self):
        assert self._make().get_speed() == 170

    def test_default_voice(self):
        assert self._make().get_voice() == "english"

    def test_default_split_time(self):
        assert self._make().get_split_time() == 5

    # --- set_volume ---
    def test_volume_valid_min(self):
        obj = self._make(volume=0)
        assert obj.get_volume() == 0

    def test_volume_valid_max(self):
        obj = self._make(volume=200)
        assert obj.get_volume() == 200

    def test_volume_mid(self):
        obj = self._make(volume=100)
        assert obj.get_volume() == 100

    def test_volume_below_zero_uses_default(self):
        obj = self._make()
        result = obj.set_volume(-1)
        assert result is False
        assert obj.get_volume() == 100

    def test_volume_above_200_uses_default(self):
        obj = self._make()
        obj.set_volume(201)
        assert obj.get_volume() == 100

    def test_volume_valid_returns_none(self):
        obj = self._make()
        # Valid calls do not explicitly return False
        result = obj.set_volume(50)
        assert result is not False

    # --- set_pitch ---
    def test_pitch_valid_zero(self):
        obj = self._make()
        result = obj.set_pitch(0)
        assert result is True
        assert obj.get_pitch() == 0

    def test_pitch_valid_100(self):
        obj = self._make()
        assert obj.set_pitch(100) is True
        assert obj.get_pitch() == 100

    def test_pitch_below_zero_fallback(self):
        obj = self._make()
        result = obj.set_pitch(-1)
        assert result is False
        assert obj.get_pitch() == 50

    def test_pitch_above_100_fallback(self):
        obj = self._make()
        result = obj.set_pitch(101)
        assert result is False
        assert obj.get_pitch() == 50

    # --- set_speed ---
    def test_speed_valid_min(self):
        obj = self._make()
        result = obj.set_speed(100)
        assert result is True
        assert obj.get_speed() == 100

    def test_speed_valid_max(self):
        obj = self._make()
        result = obj.set_speed(450)
        assert result is True
        assert obj.get_speed() == 450

    def test_speed_below_min_fallback(self):
        obj = self._make()
        result = obj.set_speed(99)
        assert result is False
        assert obj.get_speed() == 170

    def test_speed_above_max_fallback(self):
        obj = self._make()
        result = obj.set_speed(451)
        assert result is False
        assert obj.get_speed() == 170

    # --- set_voice ---
    def test_valid_voice_accepted(self):
        obj = self._make()
        result = obj.set_voice("french")
        assert result is True
        assert obj.get_voice() == "french"
        logger.info("set_voice('french') → voice=%s", obj.get_voice())

    def test_invalid_voice_falls_back_to_english(self):
        obj = self._make()
        result = obj.set_voice("klingon")
        assert result is False
        assert obj.get_voice() == "english"
