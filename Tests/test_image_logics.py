#!/usr/bin/env python3
"""
Tests for lios/image_logics.py
Covers:
  - detect_overlap()
  - detect_out_of_range()
  - order_rectangle()
  - is_overlapping()
  - find_index_for_new_box()
"""
import logging
import pytest

logger = logging.getLogger(__name__)

from lios.image_logics import (
    detect_overlap,
    detect_out_of_range,
    order_rectangle,
    is_overlapping,
    find_index_for_new_box,
)

# ---------------------------------------------------------------------------
# detect_overlap
# ---------------------------------------------------------------------------
class TestDetectOverlap:
    """detect_overlap(list, new_start_x, new_start_y, new_end_x, new_end_y)
    Each item in list is (start_x, start_y, width, height).
    """

    def _boxes(self):
        # A single box: top-left (10,10), width 50, height 50 → spans to (60,60)
        return [(10, 10, 50, 50)]

    def test_full_overlap(self):
        """New rect fully inside existing box."""
        result = detect_overlap(self._boxes(), 20, 20, 40, 40)
        assert result is not False, "Expected overlap to be detected"
        logger.info("full_overlap result: %s", result)

    def test_no_overlap(self):
        """New rect completely outside existing box."""
        result = detect_overlap(self._boxes(), 100, 100, 200, 200)
        assert result is False

    def test_overlap_edge(self):
        """New rect touching the edge of existing box."""
        result = detect_overlap(self._boxes(), 55, 30, 80, 50)
        assert result is not False

    def test_empty_list_no_overlap(self):
        result = detect_overlap([], 0, 0, 100, 100)
        assert result is False

    def test_new_box_contains_existing(self):
        """New large rect contains the existing box entirely."""
        result = detect_overlap(self._boxes(), 0, 0, 200, 200)
        assert result is not False

    def test_multiple_boxes_second_overlaps(self):
        boxes = [(100, 100, 50, 50), (200, 200, 50, 50)]
        result = detect_overlap(boxes, 210, 210, 230, 230)
        assert result is not False


# ---------------------------------------------------------------------------
# detect_out_of_range
# ---------------------------------------------------------------------------
class TestDetectOutOfRange:
    """detect_out_of_range(x, y, max_width, max_height) → bool"""

    def test_in_range(self):
        assert detect_out_of_range(50, 50, 100, 100) is False

    def test_x_exceeds_width(self):
        assert detect_out_of_range(101, 50, 100, 100) is True

    def test_y_exceeds_height(self):
        assert detect_out_of_range(50, 101, 100, 100) is True

    def test_x_at_zero(self):
        assert detect_out_of_range(0, 50, 100, 100) is True

    def test_y_at_zero(self):
        assert detect_out_of_range(50, 0, 100, 100) is True

    def test_negative_x(self):
        assert detect_out_of_range(-1, 50, 100, 100) is True

    def test_exact_max(self):
        assert detect_out_of_range(100, 100, 100, 100) is True

    def test_one_below_max(self):
        assert detect_out_of_range(99, 99, 100, 100) is False


# ---------------------------------------------------------------------------
# order_rectangle
# ---------------------------------------------------------------------------
class TestOrderRectangle:
    """order_rectangle(start_x, start_y, finish_x, finish_y) → ordered tuple"""

    def test_already_ordered(self):
        assert order_rectangle(0, 0, 100, 100) == (0, 0, 100, 100)

    def test_reversed_x(self):
        sx, sy, fx, fy = order_rectangle(100, 0, 0, 100)
        assert sx < fx
        logger.info("reversed_x result: %s", (sx, sy, fx, fy))

    def test_reversed_y(self):
        sx, sy, fx, fy = order_rectangle(0, 100, 100, 0)
        assert sy < fy

    def test_both_reversed(self):
        sx, sy, fx, fy = order_rectangle(100, 100, 0, 0)
        assert sx < fx and sy < fy

    def test_equal_x(self):
        sx, sy, fx, fy = order_rectangle(50, 10, 50, 100)
        # equal start/finish x: start_x == finish_x is allowed (swap gives same)
        assert sx <= fx

    def test_preserves_values(self):
        result = order_rectangle(10, 20, 30, 40)
        assert set(result) == {10, 20, 30, 40}


# ---------------------------------------------------------------------------
# is_overlapping
# ---------------------------------------------------------------------------
class TestIsOverlapping:
    """is_overlapping(rs, index, a, b, c, d)
    rs = list of (x, y, width, height); index = current item to exclude.
    a,b = top-left; c,d = width,height of new box.
    """

    def test_no_other_boxes(self):
        rs = [(10, 10, 50, 50)]
        # Only one box, index=0 excludes it → no others to overlap
        assert is_overlapping(rs, 0, 20, 20, 10, 10) is False

    def test_overlaps_other_box(self):
        rs = [(10, 10, 50, 50), (100, 100, 50, 50)]
        # Excluding index 0, check if (110,110,10,10) overlaps box at index 1
        assert is_overlapping(rs, 0, 110, 110, 10, 10) is True

    def test_no_overlap_with_other_box(self):
        rs = [(10, 10, 50, 50), (200, 200, 50, 50)]
        assert is_overlapping(rs, 0, 110, 110, 10, 10) is False


# ---------------------------------------------------------------------------
# find_index_for_new_box
# ---------------------------------------------------------------------------
class TestFindIndexForNewBox:
    """find_index_for_new_box(new_s_x, new_s_y, new_e_x, new_e_y, rl)
    rl items are (x, y, width, height); function returns insertion index.
    """

    def test_empty_list_returns_negative_one(self):
        """With empty list, length-1 = -1."""
        result = find_index_for_new_box(10, 10, 60, 60, [])
        assert result == -1

    def test_single_box_new_box_to_right(self):
        rl = [(10, 10, 50, 50)]
        # New box at x=80 → to the right of existing → should insert after index 0 → index 1
        result = find_index_for_new_box(80, 10, 130, 60, rl)
        assert result == 1

    def test_single_box_new_box_below(self):
        rl = [(10, 10, 50, 50)]
        # New box below existing (y=100) → should come after → index 1
        result = find_index_for_new_box(10, 100, 60, 150, rl)
        assert result == 1

    def test_returns_int(self):
        rl = [(0, 0, 100, 100), (200, 0, 100, 100)]
        result = find_index_for_new_box(110, 0, 190, 100, rl)
        assert isinstance(result, int)
