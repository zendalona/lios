#!/usr/bin/python3 

###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2015-2016 Nalin.x.Linux GPL-3
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

from gi.repository import Gtk		
from gi.repository import Gdk		
		
def start_main_loop():
    """
    Start main loop.

    Args:
    """
	Gtk.main()

def threads_init():
    """
    Initialize the thread.

    Args:
    """
	Gdk.threads_init()

def stop_main_loop(data=None):
    """
    Stop the main loop.

    Args:
        data: (array): write your description
    """
	Gtk.main_quit()

def acquire_lock():
    """
    Acquire the lock.

    Args:
    """
	Gdk.threads_enter()

def release_lock():
    """
    Release the lock.

    Args:
    """
	Gdk.threads_leave()
	
