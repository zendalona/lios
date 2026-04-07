#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/drawing_area.py (DrawingArea)
────────────────────────────────────────────────────
Covers: instantiation, rectangle list management, drawing rectangle,
        event connections, redraw, get_width/get_height with a pixbuf.
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


@pytest.fixture
def drawing_area(gtk_init):
    from lios.ui.gtk.drawing_area import DrawingArea
    return DrawingArea()


# ═══════════════════════════════════════════════════════════════════════════
class TestDrawingAreaBasic:
    def test_instantiation(self, drawing_area):
        assert drawing_area is not None

    def test_default_rectangles_empty(self, drawing_area):
        assert drawing_area.rectangles == []

    def test_default_drawing_rectangle_none(self, drawing_area):
        assert drawing_area.drawing_rectangle is None


# ═══════════════════════════════════════════════════════════════════════════
class TestDrawingAreaRectangles:
    def test_set_rectangle_list(self, drawing_area):
        rects = [(True, 10, 20, 50, 60), (False, 30, 40, 70, 80)]
        drawing_area.set_rectangle_list(rects)
        assert len(drawing_area.rectangles) == 2
        assert drawing_area.rectangles[0][0] is True  # Selected

    def test_set_rectangle_list_empty(self, drawing_area):
        drawing_area.set_rectangle_list([(True, 1, 2, 3, 4)])
        drawing_area.set_rectangle_list([])
        assert drawing_area.rectangles == []

    def test_set_drawing_rectangle(self, drawing_area):
        drawing_area.set_drawing_rectangle((10, 20, 100, 50))
        assert drawing_area.drawing_rectangle == (10, 20, 100, 50)

    def test_clear_drawing_rectangle(self, drawing_area):
        drawing_area.set_drawing_rectangle((10, 20, 100, 50))
        drawing_area.set_drawing_rectangle(None)
        assert drawing_area.drawing_rectangle is None


# ═══════════════════════════════════════════════════════════════════════════
class TestDrawingAreaEvents:
    def test_connect_button_press_no_crash(self, drawing_area):
        drawing_area.connect_button_press_event(lambda coords, btn: None)

    def test_connect_button_release_no_crash(self, drawing_area):
        drawing_area.connect_button_release_event(lambda coords, btn: None)

    def test_connect_motion_notify_no_crash(self, drawing_area):
        drawing_area.connect_motion_notify_event(lambda coords: None)


# ═══════════════════════════════════════════════════════════════════════════
class TestDrawingAreaRedraw:
    def test_redraw_no_crash(self, drawing_area):
        drawing_area.redraw()  # Calls queue_draw()


# ═══════════════════════════════════════════════════════════════════════════
class TestDrawingAreaWithPixbuf:
    def test_width_height_after_load(self, gtk_init, tmp_path):
        """Create a small test image and load it into the DrawingArea."""
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GdkPixbuf
        from lios.ui.gtk.drawing_area import DrawingArea

        # Create a 100x50 test image
        img_path = str(tmp_path / "test.png")
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 100, 50)
        pixbuf.fill(0xFF0000FF)
        pixbuf.savev(img_path, "png", [], [])

        da = DrawingArea()
        da.load_image(img_path, [], 1)
        assert da.get_width() == 100
        assert da.get_height() == 50

    def test_original_height(self, gtk_init, tmp_path):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GdkPixbuf
        from lios.ui.gtk.drawing_area import DrawingArea

        img_path = str(tmp_path / "test2.png")
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 80, 120)
        pixbuf.fill(0x00FF00FF)
        pixbuf.savev(img_path, "png", [], [])

        da = DrawingArea()
        da.load_image(img_path, [], 1)
        assert da.get_original_height() == 120

    def test_load_image_with_scale(self, gtk_init, tmp_path):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GdkPixbuf
        from lios.ui.gtk.drawing_area import DrawingArea

        img_path = str(tmp_path / "test3.png")
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 100, 100)
        pixbuf.fill(0x0000FFFF)
        pixbuf.savev(img_path, "png", [], [])

        da = DrawingArea()
        da.load_image(img_path, [], 2)  # 2x scale
        assert da.get_width() == 200
        assert da.get_height() == 200

    def test_save_image_rectangle(self, gtk_init, tmp_path):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GdkPixbuf
        from lios.ui.gtk.drawing_area import DrawingArea
        import os

        img_path = str(tmp_path / "source.png")
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 200, 200)
        pixbuf.fill(0xFF00FFFF)
        pixbuf.savev(img_path, "png", [], [])

        da = DrawingArea()
        da.load_image(img_path, [], 1)

        out_path = str(tmp_path / "cropped.png")
        da.save_image_rectangle(out_path, 10, 10, 50, 50)
        assert os.path.exists(out_path)
