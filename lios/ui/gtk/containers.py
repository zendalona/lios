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
from lios.ui.gtk import icon

		

class Grid(Gtk.Grid):
	BOTTOM = Gtk.PositionType.BOTTOM
	RIGHT = Gtk.PositionType.RIGHT
	NEW_ROW = 1;
	VEXPAND = 1;
	HEXPAND = 1;
	NO_VEXPAND = 0;
	NO_HEXPAND = 0;
	ALIGN_END = Gtk.Align.END
	ALIGN_START = Gtk.Align.START
	
	def __init__(self):
		super(Grid,self).__init__()
		self.x = 0;
		self.y = 0;
		self.x_pad = 0;
		self.x_pad_count = 0;
		self.y_pad = 0;
		self.y_pad_count = 0;		
	
	def add_widgets(self,list):
		for item in list:
			if (item == Grid.NEW_ROW):
				self.__add_new_row()
			else:
				self.__add_widget(*item)
	
	#attach(widget, left, top, width, height)
	#attach_next_to(child, sibling, side, width, height)
	def __add_widget(self,child, width, height,hexpand=True,vexpand=True,halign=None,valign=None):
		child.set_hexpand(hexpand)
		child.set_vexpand(vexpand)
		if(halign):
			child.set_halign(halign)
		if(valign):
			child.set_valign(valign)
		
		if (self.x_pad_count > 1 and self.x < self.x_pad):
			self.x = self.x_pad
			self.x_pad_count = self.x_pad_count - 1 
			
		self.attach(child, self.x, self.y, width, height)
		if (height > 1):
			self.x_pad = width;
			self.x_pad_count = height
		
		self.x = self.x + width

	def __add_new_row(self):
		self.x = 0
		self.y = self.y + 1
		
		 
	
class ScrollBox(Gtk.ScrolledWindow):
	def __init__(self):
		super(ScrollBox,self).__init__()
		self.set_border_width(2)

class NoteBook(Gtk.Notebook):
	def __init__(self):
		super(NoteBook,self).__init__()
	
	def add_page(self,title,widget):
		label = Gtk.Label(title)
		self.append_page(widget,label)


class Frame(Gtk.Frame):
	def __init__(self,label_text):
		super(Frame,self).__init__()
		self.set_label(label_text)


class Paned(Gtk.Paned):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;
	def __init__(self,orientation):
		super(Paned,self).__init__()
		self.set_orientation(orientation)
		
class Box(Gtk.Box):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;	
	def __init__(self,orientation):
		super(Box,self).__init__()
		self.set_orientation(orientation)

class Toolbar(Gtk.Toolbar):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;
	SEPARATOR = 1;

	def __init__(self,orientation,specification):
		super(Toolbar,self).__init__()
		self.set_orientation(orientation)
		for item in specification:
			if item == Toolbar.SEPARATOR:
				toolbar_item = Gtk.SeparatorToolItem()
			else:
				toolbar_item = Gtk.ToolButton(item[0])
				toolbar_item.connect("clicked",item[1])
				if item[0] in icon.stock_icon_dict.keys():
					toolbar_item.set_icon_name(icon.stock_icon_dict[item[0]])
				else:
					label = Gtk.Label(item[0])
					if(orientation == Gtk.Orientation.VERTICAL):
						label.set_angle(90)
					toolbar_item.set_icon_widget(label)
				toolbar_item.set_tooltip_text(item[0])
			self.add(toolbar_item)
	
	def set_show_nth_item(self,n,value):
		item = self.get_nth_item(n)
		item.set_sensitive(value)
			
		
		
