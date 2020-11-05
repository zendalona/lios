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


class FileChooserDialog(Gtk.FileChooserDialog):
	OPEN = Gtk.FileChooserAction.OPEN
	SAVE = Gtk.FileChooserAction.SAVE
	OPEN_FOLDER = Gtk.FileChooserAction.SELECT_FOLDER
	ACCEPT = Gtk.ResponseType.OK
	
	def __init__(self,title,action,filters=None,dir=None):
     """
     Initialize gtk widget

     Args:
         self: (todo): write your description
         title: (str): write your description
         action: (todo): write your description
         filters: (list): write your description
         dir: (todo): write your description
     """
		if(action == Gtk.FileChooserAction.OPEN or
			action == Gtk.FileChooserAction.SELECT_FOLDER):
			super(FileChooserDialog,self).__init__(title,None,action,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		else:
			super(FileChooserDialog,self).__init__(title,None,action,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		
		if (action != Gtk.FileChooserAction.SELECT_FOLDER):
			filter = Gtk.FileFilter()
			for item in filters:
				filter.add_pattern("*."+item)
			self.add_filter(filter)

		if (dir):
			self.set_current_folder(dir)

	#def run() distroy() get_filename()	set_current_folder()
