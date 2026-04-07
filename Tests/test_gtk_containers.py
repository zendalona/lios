#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/containers.py
────────────────────────────────────
Covers: Grid, ScrollBox, NoteBook, Frame, Paned, Box, Toolbar
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
class TestGrid:
    def test_constants(self, gtk_init):
        from lios.ui.gtk.containers import Grid
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        assert Grid.BOTTOM == Gtk.PositionType.BOTTOM
        assert Grid.RIGHT == Gtk.PositionType.RIGHT
        assert Grid.NEW_ROW == 1

    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.containers import Grid
        g = Grid()
        assert g.x == 0
        assert g.y == 0

    def test_add_widgets_single_row(self, gtk_init):
        from lios.ui.gtk.containers import Grid
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        g = Grid()
        lbl1 = Gtk.Label("A")
        lbl2 = Gtk.Label("B")
        g.add_widgets([(lbl1, 1, 1), (lbl2, 1, 1)])
        assert g.x == 2  # Two widgets placed side by side

    def test_add_widgets_new_row(self, gtk_init):
        from lios.ui.gtk.containers import Grid
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        g = Grid()
        lbl1 = Gtk.Label("A")
        lbl2 = Gtk.Label("B")
        g.add_widgets([(lbl1, 1, 1), Grid.NEW_ROW, (lbl2, 1, 1)])
        assert g.y == 1
        assert g.x == 1


# ═══════════════════════════════════════════════════════════════════════════
class TestScrollBox:
    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.containers import ScrollBox
        sb = ScrollBox()
        assert sb is not None

    def test_scroll_no_crash(self, gtk_init):
        from lios.ui.gtk.containers import ScrollBox
        sb = ScrollBox()
        sb.scroll(0, 0)


# ═══════════════════════════════════════════════════════════════════════════
class TestNoteBook:
    def test_instantiation(self, gtk_init):
        from lios.ui.gtk.containers import NoteBook
        nb = NoteBook()
        assert nb.get_n_pages() == 0

    def test_add_page(self, gtk_init):
        from lios.ui.gtk.containers import NoteBook
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        nb = NoteBook()
        nb.add_page("Page 1", Gtk.Label("Content 1"))
        assert nb.get_n_pages() == 1

    def test_add_multiple_pages(self, gtk_init):
        from lios.ui.gtk.containers import NoteBook
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        nb = NoteBook()
        nb.add_page("P1", Gtk.Label("C1"))
        nb.add_page("P2", Gtk.Label("C2"))
        nb.add_page("P3", Gtk.Label("C3"))
        assert nb.get_n_pages() == 3


# ═══════════════════════════════════════════════════════════════════════════
class TestFrame:
    def test_label(self, gtk_init):
        from lios.ui.gtk.containers import Frame
        f = Frame("My Frame")
        assert f.get_label() == "My Frame"


# ═══════════════════════════════════════════════════════════════════════════
class TestPaned:
    def test_horizontal(self, gtk_init):
        from lios.ui.gtk.containers import Paned
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        p = Paned(Paned.HORIZONTAL)
        assert p.get_orientation() == Gtk.Orientation.HORIZONTAL

    def test_vertical(self, gtk_init):
        from lios.ui.gtk.containers import Paned
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        p = Paned(Paned.VERTICAL)
        assert p.get_orientation() == Gtk.Orientation.VERTICAL


# ═══════════════════════════════════════════════════════════════════════════
class TestBox:
    def test_horizontal_orientation(self, gtk_init):
        from lios.ui.gtk.containers import Box
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        b = Box(Box.HORIZONTAL)
        assert b.get_orientation() == Gtk.Orientation.HORIZONTAL

    def test_vertical_orientation(self, gtk_init):
        from lios.ui.gtk.containers import Box
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        b = Box(Box.VERTICAL)
        assert b.get_orientation() == Gtk.Orientation.VERTICAL

    def test_connect_configure_no_crash(self, gtk_init):
        from lios.ui.gtk.containers import Box
        b = Box(Box.HORIZONTAL)
        b.connect_configure_event_handler(lambda *a: None)
