#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
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
from gi.repository import GdkX11, GstVideo
from gi.repository import Gtk
from gi.repository import Gst
from gi.repository import Gdk
from gi.repository import GObject

import datetime
import os.path

class Cam(Gtk.Window):
	__gsignals__ = {
        'image_captured' : (GObject.SIGNAL_RUN_LAST,
                     GObject.TYPE_NONE,
                     (str,))
        }

	def __init__(self,device,x,y,directory="/tmp/"):
     """
     Initialize the gtk engine.

     Args:
         self: (todo): write your description
         device: (todo): write your description
         x: (int): write your description
         y: (int): write your description
         directory: (str): write your description
     """
		Gtk.Window.__init__(self,title=_("Press take/close button at the right side"))
		Gst.init(None)
		self.resize(x, y)
		self.connect("destroy",self.cam_close)
		self.directory = directory
		
		box = Gtk.VBox()
		self.drawingarea = Gtk.DrawingArea()
				
		button1 = Gtk.Button(_("Take"))
		button1.connect("clicked",self.cam_take)

		button2 = Gtk.Button(_("Close"))
		button2.connect("clicked",self.cam_close)

		box.pack_end(self.drawingarea,True,True,0)
		box.pack_end(button2,False,False,0)		
		box.pack_end(button1,False,False,0)
		
		self.add(box)
		box.show_all()
		
		# Create GStreamer pipeline
		self.pipeline = Gst.Pipeline()
		# Create bus to get events from GStreamer pipeline
		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::error', self.cam_on_error)
		
		# This is needed to make the video output in our DrawingArea:
		self.bus.enable_sync_message_emission()
		self.bus.connect('sync-message::element', self.cam_on_sync_message)

		self.src = Gst.ElementFactory.make('v4l2src', None)
		self.src.set_property("device", device)
		self.pipeline.add(self.src)		
		
		self.sink = Gst.ElementFactory.make('autovideosink', None)
		self.pipeline.add(self.sink)		
		self.src.link(self.sink)
				
		self.drawingarea.set_size_request(x,y)
		self.drawingarea.realize()

		self.pipeline.set_state(Gst.State.PLAYING)
		self.xid = self.drawingarea.get_property('window').get_xid()
		self.show_all()

	def start(self):
     """
     Start gtk. gtk. gtk. gtk. gtk. gtk. gtk. gtk. gtk. gtk

     Args:
         self: (todo): write your description
     """
		Gtk.main()
	
	def cam_close(self, window):
     """
     Cam_close

     Args:
         self: (todo): write your description
         window: (int): write your description
     """
		self.pipeline.set_state(Gst.State.NULL)
		self.pipeline.remove(self.src)
		self.pipeline.remove(self.sink)
		self.destroy()
	
	def cam_take(self,widget):
     """
     Cam a window

     Args:
         self: (todo): write your description
         widget: (todo): write your description
     """
	    window = self.drawingarea.get_window()
	    x = window.get_width()
	    y = window.get_height()
	    pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0,x, y)
	    filename = "{}{}.png".format(self.directory,datetime.datetime.now().time())
	    pixbuf.savev(filename, 'png', [], [])
	    self.emit("image_captured",filename)
	
	def connect_image_captured(self,function):
     """
     Çļ»åĭł¥è¯·åıĸåįķ

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect("image_captured",function)
	    
	    
	def cam_on_error(self, bus, msg):
     """
     Called when a bus is received.

     Args:
         self: (todo): write your description
         bus: (todo): write your description
         msg: (todo): write your description
     """
		print('on_error():', msg.parse_error())

	def cam_on_sync_message(self, bus, msg):
     """
     Called when a sync message has changed

     Args:
         self: (todo): write your description
         bus: (todo): write your description
         msg: (todo): write your description
     """
		if msg.get_structure().get_name() == 'prepare-window-handle':
			msg.src.set_property('force-aspect-ratio', True)
			msg.src.set_window_handle(self.xid)
	
	def get_available_devices():
     """
     Return a list of available devices.

     Args:
     """
		list = []
		for i in range(0,4):
			device = "/dev/video{}".format(i)
			if(os.path.exists(device)):
				list.append(device)
		return list
				
		


if __name__ == "__main__":
	devices = Cam.get_available_devices()
	print(devices)

	a = Cam(devices[0],1024,768)
	a.start()
