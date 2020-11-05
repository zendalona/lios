#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2014-2015 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

import os

def capture_entire_screen(filename):
    """
    Capture screen screen.

    Args:
        filename: (str): write your description
    """
	os.system("import -window root {} -delay 2".format(filename))
	
def capture_rectangle_selection(filename):
    """
    Capture a rectangle to a rectangle.

    Args:
        filename: (str): write your description
    """
	os.system("import {}".format(filename))
	
