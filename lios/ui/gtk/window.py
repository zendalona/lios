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

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf
	
class Window(Gtk.Window):
	def __init__(self,title):
		super(Window,self).__init__()
		self.set_title(title)
		
	
	def connect_close_function(self,function):
		self.connect("delete-event",function)
	
	def connect_menubar(self,menubar):
		self.add_accel_group(menubar.get_accel_group())
	
	def connect_configure_event_handler(self,function):
		self.connect("configure-event",function)

	def set_taskbar_icon(self,file_path):
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
		self.set_icon(pixbuf)
		

	#add()
	#get_size()
