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
		



class DrawingArea(Gtk.DrawingArea):
	def __init__(self):
     """
     Init the drawing events

     Args:
         self: (todo): write your description
     """
		super(DrawingArea,self).__init__()
		self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.connect("draw",self.__drawingarea_draw)
		self.rectangles = [];
		self.drawing_rectangle = None;
	
	def set_rectangle_list(self,list):
     """
     Set the rectangle list.

     Args:
         self: (todo): write your description
         list: (todo): write your description
     """
		self.rectangles = list;
	
	def set_drawing_rectangle(self,rectangle):
     """
     Set the drawing rectangle.

     Args:
         self: (todo): write your description
         rectangle: (todo): write your description
     """
		self.drawing_rectangle = rectangle
	
	def connect_button_press_event(self,function):
     """
     Connects the mouse press events.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("button_press_event",lambda x,y: function(y.get_coords(),y.button))

	def connect_button_release_event(self,function):
     """
     Connects the mouse release.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("button_release_event",lambda x,y: function(y.get_coords(),y.button))

	def connect_motion_notify_event(self,function):
     """
     Connects a connection to a connection.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("motion_notify_event",lambda x,y: function(y.get_coords()))

	def __drawingarea_draw(self, widget, cr):
     """
     Draws the rectangle on the image.

     Args:
         self: (todo): write your description
         widget: (todo): write your description
         cr: (todo): write your description
     """
		   Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
		   cr.paint()
		   
		   for item in self.rectangles:
			   #cr.move_to(10, 90)
			   cr.rectangle(item[1], item[2], item[3], item[4])

			   # Red color for selected item blue for unselected items
			   if item[0] == True:
				   cr.set_source_rgb(0.9, 0, 0)
			   else:
				   cr.set_source_rgb(0, 0.1, 1)

			   cr.set_line_width (2.0);
			   #cr.fill()
			   cr.stroke()
		   
		   if (self.drawing_rectangle):
			   cr.rectangle(self.drawing_rectangle[0],self.drawing_rectangle[1],self.drawing_rectangle[2],self.drawing_rectangle[3])
			   # Green Color for currently drawing rectangle
			   cr.set_source_rgb(0, 1.0, 0)
			   cr.set_line_width (2.0);
			   cr.stroke()
		   return True
	def save_image_rectangle(self,filename,x,y,width,height):
     """
     Save the image to a new image.

     Args:
         self: (todo): write your description
         filename: (str): write your description
         x: (todo): write your description
         y: (todo): write your description
         width: (int): write your description
         height: (todo): write your description
     """
		new_pixbuf = self.pixbuf_original.new_subpixbuf(x,y,width,height)
		new_pixbuf.savev(filename, "png",[],[])		

	
	def get_width(self):
     """
     Return the width of the column.

     Args:
         self: (todo): write your description
     """
		return self.pixbuf.get_width()		

	def get_height(self):
     """
     Return the height of the image

     Args:
         self: (todo): write your description
     """
		return self.pixbuf.get_height()
	
	def redraw(self):
     """
     Redraw the queue.

     Args:
         self: (todo): write your description
     """
		self.queue_draw();		

	def load_image(self,filename,list,parameter):
     """
     Load image from file.

     Args:
         self: (todo): write your description
         filename: (str): write your description
         list: (todo): write your description
         parameter: (todo): write your description
     """
		self.filename = filename
		
		self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
		self.pixbuf_file_name = filename

		# Keeping a original copy, later used to create sub-images
		self.pixbuf_original = self.pixbuf.copy();

		width = self.pixbuf.get_width()
		height = self.pixbuf.get_height()
		self.orig_height = height

		if (parameter != 1 ):
			self.set_size_request(width*parameter,height*parameter)
			self.pixbuf = self.pixbuf.scale_simple(width*parameter,height*parameter,GdkPixbuf.InterpType.HYPER)
		else:
			self.set_size_request(width,height)
		
		self.rectangles = list;	
		self.queue_draw()
	
	def get_original_height(self):
     """
     Returns the height of the row

     Args:
         self: (todo): write your description
     """
		return self.orig_height

	def set_mouse_pointer_type(self,_type):
     """
     Sets the mouse pointer type.

     Args:
         self: (todo): write your description
         _type: (str): write your description
     """
		list = [Gdk.CursorType.ARROW,
		Gdk.CursorType.TOP_LEFT_CORNER,Gdk.CursorType.SB_V_DOUBLE_ARROW,Gdk.CursorType.TOP_RIGHT_CORNER,
		Gdk.CursorType.SB_H_DOUBLE_ARROW,Gdk.CursorType.FLEUR,Gdk.CursorType.SB_H_DOUBLE_ARROW,
		Gdk.CursorType.BOTTOM_LEFT_CORNER,Gdk.CursorType.SB_V_DOUBLE_ARROW,Gdk.CursorType.BOTTOM_RIGHT_CORNER]	
		arrow = Gdk.Cursor(list[_type])
		gdk_window = self.get_root_window()
		gdk_window.set_cursor(arrow)

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


