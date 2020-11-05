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
from gi.repository import GdkPixbuf
import os


class IconView(Gtk.IconView):
	def __init__(self):
     """
     Initialize the mode

     Args:
         self: (todo): write your description
     """
		super(IconView,self).__init__()
		self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		self.liststore_images = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.set_pixbuf_column(0)
		self.set_text_column(1)
		self.set_columns(1)
		self.set_model(self.liststore_images)

	#methord is not thread safe
	def add_item(self,filename):
     """
     Add a new item to the image.

     Args:
         self: (todo): write your description
         filename: (str): write your description
     """
		try:
			pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
		except:
			pass
		else:
			height = pixbuff.get_height()
			width = pixbuff.get_width()
			ratio = (height*50)/width
			buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
			del pixbuff
			self.liststore_images.append([buff, filename])
			self.queue_draw()
			del buff

	def remove_selected_items(self,remove_file_too=True):
     """
     Removes selected items.

     Args:
         self: (todo): write your description
         remove_file_too: (str): write your description
     """
		for item in self.get_selected_items():
			iter = self.liststore_images.get_iter_from_string(item.to_string())
			if(remove_file_too):
				os.remove(self.liststore_images.get_value(iter, 1))
			self.liststore_images.remove(iter)
	
	def select_all_items(self):
     """
     Select all items.

     Args:
         self: (todo): write your description
     """
		self.select_all()

	def select_item(self,filename):
     """
     Selects selected item from the list

     Args:
         self: (todo): write your description
         filename: (str): write your description
     """
		model = self.get_model()
		#iter = model.get_iter_first()
		for item in self.get_selected_items():
			iter = self.liststore_images.get_iter_from_string(item.to_string())
			if (filename == self.liststore_images.get_value(iter, 1)):		
				path = model.get_path(iter)
				self.select_path(path)
				break;
				
	
	def reload_preview(self,filename):
     """
     Reload preview of the image.

     Args:
         self: (todo): write your description
         filename: (str): write your description
     """
		for item in self.liststore_images:
			if (item[1] == filename):
				pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
				height = pixbuff.get_height()
				width = pixbuff.get_width()
				ratio = (height*50)/width
				buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
				del pixbuff
				item[0] = buff
				del buff
		
	
	def get_selected_item_names(self):
     """
     Return a list of all selected in the store.

     Args:
         self: (todo): write your description
     """
		items = []
		for item in reversed(self.get_selected_items()):
			items.append(self.liststore_images[item[0]][1])
		return items;

	def invert_list(self,*data):
     """
     Invert a gtk.

     Args:
         self: (todo): write your description
         data: (list): write your description
     """
		liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		for item in reversed(self.liststore_images):
			liststore.append((item[0],item[1]))
		self.liststore_images = liststore
		self.set_model(self.liststore_images)
	
	def connect_on_selected_callback(self,function):
     """
     Connects a callback function.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("selection-changed",function)
	
	def connect_context_menu_button_callback(self,function):
     """
     Call the callback function when the mouse button is clicked.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		def fun(widget,event):
      """
      Reimplemented events.

      Args:
          widget: (todo): write your description
          event: (todo): write your description
      """
			if ((event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3) or
				(event.type == Gdk.EventType.KEY_PRESS and event.hardware_keycode == 135)):
				function()
		self.connect("button-release-event",fun)
		self.connect("key-press-event",fun)

