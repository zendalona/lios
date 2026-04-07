#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/tree_view.py
──────────────────────────────────
Covers: CellRendererSpin, CellRendererText, CellRendererToggle,
        TreeView (append, remove, get_list, set_list, clear,
        on_edited callbacks, column visibility, signal connections)
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


def _make_tree_view(callback=None):
    from lios.ui.gtk.tree_view import TreeView
    cb = callback or (lambda row: None)
    # Note: bool columns must have editable=False because
    # CellRendererToggle doesn't support the 'editable' property
    tv = TreeView([
        ("Name", str, True),
        ("Value", float, True),
        ("Active", bool, False),
    ], cb)
    return tv


# ═══════════════════════════════════════════════════════════════════════════
class TestCellRenderers:
    def test_cell_renderer_spin(self, gtk_init):
        from lios.ui.gtk.tree_view import CellRendererSpin
        cr = CellRendererSpin(0)
        assert cr.pos == 0

    def test_cell_renderer_text(self, gtk_init):
        from lios.ui.gtk.tree_view import CellRendererText
        cr = CellRendererText(2)
        assert cr.pos == 2

    def test_cell_renderer_toggle(self, gtk_init):
        from lios.ui.gtk.tree_view import CellRendererToggle
        cr = CellRendererToggle(1)
        assert cr.pos == 1


# ═══════════════════════════════════════════════════════════════════════════
class TestTreeViewBasic:
    def test_instantiation(self, gtk_init):
        tv = _make_tree_view()
        assert tv is not None

    def test_append_and_get_list(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["Alpha", 1.0, False])
        tv.append(["Beta", 2.5, True])
        result = tv.get_list()
        assert len(result) == 2
        assert result[0][0] == "Alpha"
        assert result[1][0] == "Beta"

    def test_append_values_preserved(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["Test", 3.14, False])
        result = tv.get_list()
        assert abs(result[0][1] - 3.14) < 0.01
        assert result[0][2] is False

    def test_clear(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["A", 1.0, False])
        tv.append(["B", 2.0, True])
        tv.clear()
        assert tv.get_list() == []

    def test_remove_by_index(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["A", 1.0, False])
        tv.append(["B", 2.0, True])
        tv.append(["C", 3.0, False])
        tv.remove(1)  # Remove "B"
        result = tv.get_list()
        assert len(result) == 2
        assert result[0][0] == "A"
        assert result[1][0] == "C"


# ═══════════════════════════════════════════════════════════════════════════
class TestTreeViewSetList:
    def test_set_list_replaces(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["Old", 0.0, False])
        tv.set_list([("New1", 1.0, True), ("New2", 2.0, False)])
        result = tv.get_list()
        assert len(result) == 2
        assert result[0][0] == "New1"

    def test_set_list_empty(self, gtk_init):
        tv = _make_tree_view()
        tv.append(["A", 1.0, False])
        tv.set_list([])
        assert tv.get_list() == []


# ═══════════════════════════════════════════════════════════════════════════
class TestTreeViewEditing:
    def test_on_edited_callback(self, gtk_init):
        called_with = []
        tv = _make_tree_view(callback=lambda row: called_with.append(row))
        tv.append(["A", 1.0, False])
        # Simulate cell edit
        from lios.ui.gtk.tree_view import CellRendererText
        cell = CellRendererText(0)
        tv.on_edited(cell, "0", "Changed")
        result = tv.get_list()
        assert result[0][0] == "Changed"
        assert 0 in called_with

    def test_on_float_edited_callback(self, gtk_init):
        called_with = []
        tv = _make_tree_view(callback=lambda row: called_with.append(row))
        tv.append(["A", 1.0, False])
        from lios.ui.gtk.tree_view import CellRendererSpin
        cell = CellRendererSpin(1)
        tv.on_float_edited(cell, "0", "9.99")
        result = tv.get_list()
        assert abs(result[0][1] - 9.99) < 0.01
        assert 0 in called_with

    def test_on_bool_edited_callback(self, gtk_init):
        called_with = []
        tv = _make_tree_view(callback=lambda row: called_with.append(row))
        tv.append(["A", 1.0, False])
        from lios.ui.gtk.tree_view import CellRendererToggle
        cell = CellRendererToggle(2)
        tv.on_bool_edited(cell, "0")
        result = tv.get_list()
        assert result[0][2] is True
        assert 0 in called_with


# ═══════════════════════════════════════════════════════════════════════════
class TestTreeViewColumns:
    def test_column_count(self, gtk_init):
        tv = _make_tree_view()
        assert tv.get_n_columns() == 3

    def test_set_column_visible(self, gtk_init):
        tv = _make_tree_view()
        tv.set_column_visible(0, False)
        col = tv.get_column(0)
        assert col.get_visible() is False

    def test_set_column_visible_true(self, gtk_init):
        tv = _make_tree_view()
        tv.set_column_visible(0, False)
        tv.set_column_visible(0, True)
        col = tv.get_column(0)
        assert col.get_visible() is True


# ═══════════════════════════════════════════════════════════════════════════
class TestTreeViewSignals:
    def test_connect_update_callback(self, gtk_init):
        tv = _make_tree_view()
        tv.connect_update_callback(lambda row: None)

    def test_connect_cursor_change_function(self, gtk_init):
        tv = _make_tree_view()
        tv.connect_cursor_change_function(lambda: None)
        assert tv.cursor_change_handler_id is not None

    def test_block_unblock_cursor_change(self, gtk_init):
        tv = _make_tree_view()
        tv.connect_cursor_change_function(lambda: None)
        tv.block_cursor_change_signal()  # Should not crash
        tv.unblock_cursor_change_signal()  # Should not crash

    def test_block_without_handler_no_crash(self, gtk_init):
        tv = _make_tree_view()
        tv.block_cursor_change_signal()  # No handler yet, should not crash

    def test_is_reorderable(self, gtk_init):
        tv = _make_tree_view()
        assert tv.get_reorderable() is True
