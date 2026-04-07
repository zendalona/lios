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
import time
import subprocess

def capture_entire_screen(filename):
    """Capture the full screen to filename. Uses scrot, gnome-screenshot or import."""
    time.sleep(1)  # Give window time to minimize before capturing
    # Try scrot first (most reliable), then gnome-screenshot, then ImageMagick import
    if subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:
        result = subprocess.run(["scrot", filename], capture_output=True)
    elif subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode == 0:
        result = subprocess.run(["gnome-screenshot", "-f", filename], capture_output=True)
    else:
        result = subprocess.run(["import", "-window", "root", filename], capture_output=True)
    return os.path.exists(filename)

def capture_rectangle_selection(filename):
    """Capture a user-selected rectangle to filename."""
    time.sleep(1)  # Wait for window minimization to complete before capturing
    # Try scrot first (interactive rectangle selection)
    if subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:
        result = subprocess.run(["scrot", "-s", filename], capture_output=True)
    elif subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode == 0:
        result = subprocess.run(["gnome-screenshot", "-a", "-f", filename], capture_output=True)
    else:
        result = subprocess.run(["import", filename], capture_output=True)
    return os.path.exists(filename)
