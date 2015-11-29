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
		super(IconView,self).__init__()
		self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		self.liststore_images = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.set_pixbuf_column(0)
		self.set_text_column(1)
		self.set_columns(1)
		self.set_model(self.liststore_images)

	def add_item(self,filename):
		try:
			pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
		except:
			pass
		else:
			height = pixbuff.get_height()
			width = pixbuff.get_width()
			ratio = (width*50)/height
			#if(lock):
			#	Gdk.threads_enter()
			buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
			del pixbuff
			self.liststore_images.append([buff, filename])
			self.queue_draw()
			del buff
			#if(lock):
			#	Gdk.threads_leave()

	def remove_selected_items(self):
		for item in self.get_selected_items():
			iter = self.liststore_images.get_iter_from_string(item.to_string())
			os.remove(self.liststore_images.get_value(iter, 1))
			self.liststore_images.remove(iter)
	
	def select_all_items(self):
		self.select_all()
	
	def reload_preview(self,filename):
		for item in self.liststore_images:
			if (item[1] == filename):
				pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
				height = pixbuff.get_height()
				width = pixbuff.get_width()
				ratio = (width*50)/height
				Gdk.threads_enter()
				buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
				Gdk.threads_leave()
				item[0] = buff		

		
	
	def get_selected_item_names(self):
		items = []
		for item in reversed(self.get_selected_items()):
			items.append(self.liststore_images[item[0]][1])
		return items;

	def invert_list(self,*data):
		liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		for item in reversed(self.liststore_images):
			liststore.append((item[0],item[1]))
		self.liststore_images = liststore
		self.set_model(self.liststore_images)
	
	def connect_on_selected_callback(self,function):
		self.connect("selection-changed",function)
	
	def connect_context_menu_button_callback(self,function):
		def fun(widget,event):
			if ((event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3) or
				(event.type == Gdk.EventType.KEY_PRESS and event.hardware_keycode == 135)):
				function()
		self.connect("button-release-event",fun)
		self.connect("key-press-event",fun)

