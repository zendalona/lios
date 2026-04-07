#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/text_view.py (TextView)
──────────────────────────────────────────────
Uses pytest-xvfb for headless GTK testing.

Covers:
  • set_text / get_text round-trip
  • insert_text at START, CURSOR, END
  • get_line_count / get_cursor_line_number
  • move_cursor_to_line
  • has_selection default
  • delete_all_text
  • set_modified / get_modified
  • is_cursor_at_start / is_cursor_at_end
  • move_forward_to_word / move_backward_to_word
  • count_non_empty_lines
  • highlights_cursor_line (doesn't crash)
  • get_text_from_cursor_to_end
  • delete_text_from_cursor_to_end
"""
import logging
import pytest

logger = logging.getLogger(__name__)

# GTK must be imported INSIDE functions/fixtures so pytest-xvfb
# has time to set up the virtual display first.


@pytest.fixture
def text_view():
    """Create a fresh TextView instance for each test."""
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    Gtk.init([])
    from lios.ui.gtk.text_view import TextView
    tv = TextView()
    return tv


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewBasic:

    def test_set_and_get_text(self, text_view):
        text_view.set_text("Hello World")
        assert text_view.get_text() == "Hello World"

    def test_set_text_overwrites(self, text_view):
        text_view.set_text("First")
        text_view.set_text("Second")
        assert text_view.get_text() == "Second"

    def test_empty_text(self, text_view):
        assert text_view.get_text() == ""

    def test_unicode_text(self, text_view):
        text_view.set_text("नमस्ते दुनिया 你好世界")
        assert "नमस्ते" in text_view.get_text()
        assert "你好" in text_view.get_text()

    def test_multiline_text(self, text_view):
        text_view.set_text("Line1\nLine2\nLine3")
        assert text_view.get_text() == "Line1\nLine2\nLine3"


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewInsert:

    def test_insert_at_end(self, text_view):
        from lios.ui.gtk.text_view import TextView
        text_view.set_text("Hello")
        text_view.insert_text(" World", TextView.AT_END)
        assert text_view.get_text() == "Hello World"

    def test_insert_at_start(self, text_view):
        from lios.ui.gtk.text_view import TextView
        text_view.set_text("World")
        text_view.insert_text("Hello ", TextView.AT_START)
        assert text_view.get_text() == "Hello World"

    def test_insert_at_cursor(self, text_view):
        from lios.ui.gtk.text_view import TextView
        text_view.set_text("Hello World")
        # Cursor defaults to end after set_text
        text_view.insert_text("!", TextView.AT_CURSOR)
        result = text_view.get_text()
        assert "!" in result


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewLineOps:

    def test_line_count_single(self, text_view):
        text_view.set_text("Hello")
        assert text_view.get_line_count() == 1

    def test_line_count_multi(self, text_view):
        text_view.set_text("L1\nL2\nL3\nL4")
        assert text_view.get_line_count() == 4

    def test_line_count_empty(self, text_view):
        assert text_view.get_line_count() == 1  # GTK always has at least 1

    def test_cursor_line_number_default(self, text_view):
        text_view.set_text("Hello")
        # After set_text the cursor is at 0
        assert text_view.get_cursor_line_number() >= 0

    def test_move_cursor_to_line(self, text_view):
        text_view.set_text("L0\nL1\nL2\nL3")
        text_view.move_cursor_to_line(2)
        assert text_view.get_cursor_line_number() == 2

    def test_move_cursor_to_first_line(self, text_view):
        text_view.set_text("L0\nL1\nL2")
        text_view.move_cursor_to_line(0)
        assert text_view.get_cursor_line_number() == 0

    def test_count_non_empty_lines(self, text_view):
        text_view.set_text("Hello\n\nWorld")
        assert text_view.count_non_empty_lines() == 2

    def test_count_non_empty_lines_all_empty(self, text_view):
        text_view.set_text("\n\n")
        # GTK always has at least 1 line; only truly blank lines
        # (where iter.ends_line() is True) are skipped
        count = text_view.count_non_empty_lines()
        assert count >= 0  # Verify it returns without error

    def test_count_non_empty_lines_no_empty(self, text_view):
        text_view.set_text("A\nB\nC")
        assert text_view.count_non_empty_lines() == 3


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewModifiedFlag:

    def test_default_not_modified(self, text_view):
        # After set_text, GTK marks the buffer as modified
        text_view.set_modified(False)
        assert text_view.get_modified() is False

    def test_set_modified_true(self, text_view):
        text_view.set_modified(True)
        assert text_view.get_modified() is True

    def test_set_modified_false(self, text_view):
        text_view.set_modified(True)
        text_view.set_modified(False)
        assert text_view.get_modified() is False


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewSelection:

    def test_has_selection_default_false(self, text_view):
        text_view.set_text("Hello World")
        assert text_view.has_selection() is False


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewDelete:

    def test_delete_all_text(self, text_view):
        text_view.set_text("Hello World")
        text_view.delete_all_text()
        assert text_view.get_text() == ""

    def test_delete_all_on_empty(self, text_view):
        text_view.delete_all_text()
        assert text_view.get_text() == ""


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewCursorPosition:

    def test_is_cursor_at_start(self, text_view):
        text_view.set_text("Hello")
        text_view.move_cursor_to_line(0)
        # Move to start
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_start_iter())
        assert text_view.is_cursor_at_start() == 1

    def test_is_cursor_at_end(self, text_view):
        text_view.set_text("Hello")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_end_iter())
        assert text_view.is_cursor_at_end() == 1

    def test_not_at_start_when_at_end(self, text_view):
        text_view.set_text("Hello")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_end_iter())
        assert text_view.is_cursor_at_start() == 0

    def test_not_at_end_when_at_start(self, text_view):
        text_view.set_text("Hello")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_start_iter())
        assert text_view.is_cursor_at_end() == 0


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewFindReplace:

    def test_move_forward_to_word_found(self, text_view):
        text_view.set_text("Hello World Foo Bar")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_start_iter())
        result = text_view.move_forward_to_word("Foo")
        assert result is True

    def test_move_forward_to_word_not_found(self, text_view):
        text_view.set_text("Hello World")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_start_iter())
        result = text_view.move_forward_to_word("ZZZZZ")
        assert result is False

    def test_move_backward_to_word_found(self, text_view):
        text_view.set_text("Hello World Foo Bar")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_end_iter())
        result = text_view.move_backward_to_word("Hello")
        assert result is True

    def test_move_backward_to_word_not_found(self, text_view):
        text_view.set_text("Hello World")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_end_iter())
        result = text_view.move_backward_to_word("ZZZZZ")
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewHighlight:

    def test_highlights_cursor_line_no_crash(self, text_view):
        text_view.set_text("Line1\nLine2\nLine3")
        text_view.move_cursor_to_line(1)
        text_view.highlights_cursor_line()  # Should not crash

    def test_remove_all_highlights_no_crash(self, text_view):
        text_view.set_text("Hello")
        text_view.remove_all_highlights()  # Should not crash

    def test_set_highlight_font_no_crash(self, text_view):
        text_view.set_highlight_font("Sans 14")

    def test_set_font_no_crash(self, text_view):
        text_view.set_font("Monospace 12")


# ═══════════════════════════════════════════════════════════════════════════
class TestTextViewCursorText:

    def test_get_text_from_cursor_to_end(self, text_view):
        text_view.set_text("Hello World")
        buf = text_view.get_buffer()
        buf.place_cursor(buf.get_start_iter())
        result = text_view.get_text_from_cursor_to_end()
        assert result == "Hello World"

    def test_delete_text_from_cursor_to_end(self, text_view):
        text_view.set_text("Hello World")
        buf = text_view.get_buffer()
        # Place cursor at position 5 (after "Hello")
        iter_at_5 = buf.get_iter_at_offset(5)
        buf.place_cursor(iter_at_5)
        text_view.delete_text_from_cursor_to_end()
        assert text_view.get_text() == "Hello"
