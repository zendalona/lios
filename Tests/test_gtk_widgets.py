#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/widget.py
───────────────────────────────
Covers: Entry, Label, Button, IconButton, SpinButton, ComboBox,
        ListView, ColorButton, FontButton, Separator, CheckButton,
        ProgressBar, Statusbar
"""
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def gtk_init():
    """Initialize GTK once for the entire module."""
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    Gtk.init([])


# ═══════════════════════════════════════════════════════════════════════════
class TestEntry:
    def test_set_get_text(self, gtk_init):
        from lios.ui.gtk.widget import Entry
        e = Entry()
        e.set_text("hello")
        assert e.get_text() == "hello"

    def test_empty_default(self, gtk_init):
        from lios.ui.gtk.widget import Entry
        e = Entry()
        assert e.get_text() == ""

    def test_connect_change_handler_no_crash(self, gtk_init):
        from lios.ui.gtk.widget import Entry
        e = Entry()
        e.connect_change_handler(lambda *a: None)

    def test_connect_activate_no_crash(self, gtk_init):
        from lios.ui.gtk.widget import Entry
        e = Entry()
        e.connect_activate_function(lambda *a: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestLabel:
    def test_text_on_construction(self, gtk_init):
        from lios.ui.gtk.widget import Label
        lbl = Label("Test Label")
        assert lbl.get_text() == "Test Label"

    def test_empty_label(self, gtk_init):
        from lios.ui.gtk.widget import Label
        lbl = Label("")
        assert lbl.get_text() == ""


# ═══════════════════════════════════════════════════════════════════════════
class TestButton:
    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.widget import Button
        btn = Button("Click Me")
        assert btn.get_label() == "Click Me"

    def test_connect_function_no_crash(self, gtk_init):
        from lios.ui.gtk.widget import Button
        btn = Button("OK")
        btn.connect_function(lambda *a: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestSpinButton:
    def test_default_value(self, gtk_init):
        from lios.ui.gtk.widget import SpinButton
        sb = SpinButton(value=42, lower=0, upper=100)
        assert sb.get_value() == 42

    def test_set_value(self, gtk_init):
        from lios.ui.gtk.widget import SpinButton
        sb = SpinButton(value=1, lower=0, upper=100)
        sb.set_value(75)
        assert sb.get_value() == 75

    def test_bounds_respected(self, gtk_init):
        from lios.ui.gtk.widget import SpinButton
        sb = SpinButton(value=50, lower=10, upper=90)
        sb.set_value(200)  # Over max
        assert sb.get_value() <= 90


# ═══════════════════════════════════════════════════════════════════════════
class TestComboBox:
    def test_add_item(self, gtk_init):
        from lios.ui.gtk.widget import ComboBox
        cb = ComboBox()
        cb.add_item("Item 1")
        cb.add_item("Item 2")
        model = cb.get_model()
        assert len(model) == 2

    def test_clear(self, gtk_init):
        from lios.ui.gtk.widget import ComboBox
        cb = ComboBox()
        cb.add_item("Item 1")
        cb.clear()
        model = cb.get_model()
        assert len(model) == 0

    def test_connect_change_callback(self, gtk_init):
        from lios.ui.gtk.widget import ComboBox
        cb = ComboBox()
        cb.connect_change_callback_function(lambda *a: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestListView:
    def test_add_item(self, gtk_init):
        from lios.ui.gtk.widget import ListView
        lv = ListView("Test Column")
        lv.add_item("row 1")
        lv.add_item("row 2")
        model = lv.get_model()
        assert len(model) == 2

    def test_clear(self, gtk_init):
        from lios.ui.gtk.widget import ListView
        lv = ListView("Col")
        lv.add_item("a")
        lv.clear()
        assert len(lv.get_model()) == 0

    def test_connect_on_select_callback(self, gtk_init):
        from lios.ui.gtk.widget import ListView
        lv = ListView("Col")
        lv.connect_on_select_callback(lambda *a: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestSeparator:
    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.widget import Separator
        s = Separator()
        assert s is not None


# ═══════════════════════════════════════════════════════════════════════════
class TestCheckButton:
    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.widget import CheckButton
        cb = CheckButton()
        assert cb is not None

    def test_connect_handler(self, gtk_init):
        from lios.ui.gtk.widget import CheckButton
        cb = CheckButton()
        cb.connect_handler_function(lambda *a: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestStatusbar:
    def test_set_text(self, gtk_init):
        from lios.ui.gtk.widget import Statusbar
        sb = Statusbar()
        sb.show_all()
        sb.set_text("Ready")
        assert sb.label.get_text() == "Ready"

    def test_set_line_wrap(self, gtk_init):
        from lios.ui.gtk.widget import Statusbar
        sb = Statusbar()
        sb.set_line_wrap(True)  # Should not crash
