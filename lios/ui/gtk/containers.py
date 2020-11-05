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
from lios import macros
		

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
     """
     Initializes all the grid.

     Args:
         self: (todo): write your description
     """
		super(Grid,self).__init__()
		self.x = 0;
		self.y = 0;
		self.x_pad = 0;
		self.x_pad_count = 0;
		self.y_pad = 0;
		self.y_pad_count = 0;		
	
	def add_widgets(self,list):
     """
     Add a new widget to the grid.

     Args:
         self: (todo): write your description
         list: (todo): write your description
     """
		for item in list:
			if (item == Grid.NEW_ROW):
				self.__add_new_row()
			else:
				self.__add_widget(*item)
	
	#attach(widget, left, top, width, height)
	#attach_next_to(child, sibling, side, width, height)
	def __add_widget(self,child, width, height,hexpand=True,vexpand=True,halign=None,valign=None):
     """
     Add a child to the scene.

     Args:
         self: (todo): write your description
         child: (todo): write your description
         width: (int): write your description
         height: (int): write your description
         hexpand: (int): write your description
         vexpand: (int): write your description
         halign: (int): write your description
         valign: (int): write your description
     """
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
     """
     Add a new row.

     Args:
         self: (todo): write your description
     """
		self.x = 0
		self.y = self.y + 1
		
		 
	
class ScrollBox(Gtk.ScrolledWindow):
	def __init__(self):
     """
     Initialize the border.

     Args:
         self: (todo): write your description
     """
		super(ScrollBox,self).__init__()
		self.set_border_width(2)

	def scroll(self,h_value,v_value):
     """
     Scroll the scroll value.

     Args:
         self: (todo): write your description
         h_value: (todo): write your description
         v_value: (todo): write your description
     """
		adj = self.get_vadjustment()
		adj.set_value(v_value)
		adj = self.get_hadjustment()
		adj.set_value(h_value)

	def get_size_on_screen(self):
     """
     Returns the size of the screen.

     Args:
         self: (todo): write your description
     """
		alc = self.get_allocation()
		return (alc.width,alc.height)

	def get_current_start_points(self):
     """
     Get the start and end points

     Args:
         self: (todo): write your description
     """
		hadj = self.get_hadjustment()
		start_x = hadj.get_value()
		vadj = self.get_vadjustment()
		start_y = vadj.get_value()
		return start_x,start_y

class NoteBook(Gtk.Notebook):
	def __init__(self):
     """
     Initialize the note.

     Args:
         self: (todo): write your description
     """
		super(NoteBook,self).__init__()
	
	def add_page(self,title,widget):
     """
     Add a gtk. page

     Args:
         self: (todo): write your description
         title: (str): write your description
         widget: (todo): write your description
     """
		label = Gtk.Label(title)
		self.append_page(widget,label)


class Frame(Gtk.Frame):
	def __init__(self,label_text):
     """
     Stub

     Args:
         self: (todo): write your description
         label_text: (str): write your description
     """
		super(Frame,self).__init__()
		self.set_label(label_text)


class Paned(Gtk.Paned):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;
	def __init__(self,orientation):
     """
     Initialize the orientation.

     Args:
         self: (todo): write your description
         orientation: (todo): write your description
     """
		super(Paned,self).__init__()
		self.set_orientation(orientation)
		
class Box(Gtk.Box):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;	
	def __init__(self,orientation):
     """
     Initializes the orientation.

     Args:
         self: (todo): write your description
         orientation: (todo): write your description
     """
		super(Box,self).__init__()
		self.set_orientation(orientation)

	def connect_configure_event_handler(self,function):
     """
     Connects a handler.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("configure-event",function)

class Toolbar(Gtk.Toolbar):
	HORIZONTAL = Gtk.Orientation.HORIZONTAL;
	VERTICAL = Gtk.Orientation.VERTICAL;
	SEPARATOR = 1;

	def __init__(self,orientation,specification):
     """
     Initialize the widget

     Args:
         self: (todo): write your description
         orientation: (todo): write your description
         specification: (todo): write your description
     """
		super(Toolbar,self).__init__()
		self.set_orientation(orientation)
		for item in specification:
			if item == Toolbar.SEPARATOR:
				toolbar_item = Gtk.SeparatorToolItem()
			else:
				toolbar_item = Gtk.ToolButton(item[0])
				toolbar_item.connect("clicked",item[1])
				if item[0] in icon.stock_icon_dict.keys():
					image = Gtk.Image()
					image.set_from_file(macros.icon_dir+icon.stock_icon_dict[item[0]]+".png")
					toolbar_item.set_icon_widget(image)
				else:
					label = Gtk.Label(item[0])
					if(orientation == Gtk.Orientation.VERTICAL):
						label.set_angle(90)
					toolbar_item.set_icon_widget(label)
				toolbar_item.set_tooltip_text(item[0])
			self.add(toolbar_item)
	
	def set_show_nth_item(self,n,value):
     """
     Set the number.

     Args:
         self: (todo): write your description
         n: (todo): write your description
         value: (todo): write your description
     """
		item = self.get_nth_item(n)
		item.set_sensitive(value)
			
		
		
