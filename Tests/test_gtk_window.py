#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/window.py and lios/ui/gtk/dialog.py
──────────────────────────────────────────────────────────
"""
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def gtk_init():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    Gtk.init([])


# ═══════════════════════════════════════════════════════════════════════════
class TestWindow:
    def test_title_set(self, gtk_init):
        from lios.ui.gtk.window import Window
        w = Window("LIOS Test")
        assert w.get_title() == "LIOS Test"

    def test_connect_close_function(self, gtk_init):
        from lios.ui.gtk.window import Window
        w = Window("Test")
        w.connect_close_function(lambda *a: None)

    def test_connect_configure_event_handler(self, gtk_init):
        from lios.ui.gtk.window import Window
        w = Window("Test")
        w.connect_configure_event_handler(lambda *a: None)

    def test_is_gtk_window(self, gtk_init):
        from lios.ui.gtk.window import Window
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        w = Window("Sub")
        assert isinstance(w, Gtk.Window)


# ═══════════════════════════════════════════════════════════════════════════
class TestDialog:
    def test_button_id_constants(self, gtk_init):
        from lios.ui.gtk.dialog import Dialog
        assert Dialog.BUTTON_ID_1 == 1
        assert Dialog.BUTTON_ID_2 == 2
        assert Dialog.BUTTON_ID_3 == 3

    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.dialog import Dialog
        d = Dialog("Test Dialog", ("OK", 1))
        assert d.get_title() == "Test Dialog"

    def test_add_widget(self, gtk_init):
        from lios.ui.gtk.dialog import Dialog
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        d = Dialog("Test", ("OK", 1))
        lbl = Gtk.Label("Inside")
        d.add_widget(lbl)
        content = d.get_content_area()
        children = content.get_children()
        assert len(children) > 0

    def test_add_widget_with_label(self, gtk_init):
        from lios.ui.gtk.dialog import Dialog
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        d = Dialog("Test", ("OK", 1))
        entry = Gtk.Entry()
        d.add_widget_with_label(entry, "Name:")
        content = d.get_content_area()
        children = content.get_children()
        assert len(children) > 0

    def test_is_gtk_dialog(self, gtk_init):
        from lios.ui.gtk.dialog import Dialog
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        d = Dialog("Sub", ("OK", 1))
        assert isinstance(d, Gtk.Dialog)
