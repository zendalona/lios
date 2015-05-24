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
from gi.repository import GObject
from gi.repository import GdkPixbuf


class ImageViewer(Gtk.HPaned):
	ZOOM_FIT = 4
	__gsignals__ = {
        'list_updated' : (GObject.SIGNAL_RUN_LAST,
                     GObject.TYPE_NONE,
                     ())
        }


	def __init__(self):
		Gtk.HPaned.__init__(self)
		self.set_border_width(5)

		#Drawing Area		
		self.drawingarea = Gtk.DrawingArea()
		self.drawingarea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
		
		scrolled = Gtk.ScrolledWindow()
		scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled.add_with_viewport(self.drawingarea);
		
		
		self.drawingarea.connect("draw",self.__drawingarea_draw)
		self.drawingarea.connect("button_press_event",self.__drawingarea_button_press_event)
		self.drawingarea.connect("motion_notify_event",self.__drawingarea_motion_notify_event)
		self.drawingarea.connect("button_release_event",self.__drawingarea_button_release_event)
		
		box = Gtk.VBox()
		box.add(scrolled)

		#Buttons for zoom in/out/fit
		hbox = Gtk.HBox()
		
		button1 = Gtk.Button(label="In")
		button1.connect("clicked",self.zoom_in)
		hbox.add(button1)

		button2 = Gtk.Button(label="Out")
		button2.connect("clicked",self.zoom_out)
		hbox.add(button2)		

		button3 = Gtk.Button(label="Fit")
		button3.connect("clicked",self.zoom_fit)
		hbox.add(button3)
		
		box.pack_start(hbox, False, False, 0)
		self.add(box)
				
		#Drawing List Tree View		
		self.rectangle_store = Gtk.ListStore(float,float,float,float,float)
		self.treeview_image = Gtk.TreeView()
		self.treeview_image.set_model(self.rectangle_store);
		cell = Gtk.CellRendererText()
		col = Gtk.TreeViewColumn("X", cell, text=0)
		self.treeview_image.append_column(col)
		col = Gtk.TreeViewColumn("Y", cell, text=1)
		self.treeview_image.append_column(col)
		col = Gtk.TreeViewColumn("Width", cell, text=2)
		self.treeview_image.append_column(col)
		col = Gtk.TreeViewColumn("Height", cell, text=3)
		self.treeview_image.append_column(col)
		self.treeview_image.set_reorderable(True)
		self.treeview_image.connect("cursor-changed",self.__treeview_image_cursor_changed)


		box = Gtk.VBox()
		box.add(self.treeview_image)
		
		#Buttons for editing drawn list
		hbox = Gtk.HBox()
		
		button = Gtk.Button(label="Delete")
		button.connect("clicked",self.__delete_selection)
		hbox.add(button)

		button = Gtk.Button(label="Clear")
		button.connect("clicked",self.__clear_selection)
		hbox.add(button)		
		
		box.pack_start(hbox, False, False, 0)
		self.add(box)
				

		#Inetial Values
		self.on_select = False
		self.zoom_list = [0.20,0.40,0.60,0.80,1,1.20,1.40,1.60,1.80,2]
		self.zoom_level = self.ZOOM_FIT
		self.drawingarea.show()
		self.show()		

	def load_image(self,filename,list,zoom_level):
		diff = self.zoom_level - zoom_level
		self.zoom_level = zoom_level
		parameter = self.zoom_list[self.zoom_level]
		
		self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
		self.pixbuf_file_name = filename
		if (self.zoom_level != self.ZOOM_FIT):
			self.drawingarea.set_size_request(self.pixbuf.get_width()*parameter,self.pixbuf.get_height()*parameter)
			self.pixbuf = self.pixbuf.scale_simple(self.pixbuf.get_width()*parameter,self.pixbuf.get_height()*parameter,GdkPixbuf.InterpType.HYPER)
		else:
			self.drawingarea.set_size_request(self.pixbuf.get_width(),self.pixbuf.get_height())
		
		
		if (list == None):
			list = []
			for item in self.rectangle_store:
				if (diff>0):
					list.append((item[0] - (item[0]*(abs(diff)*20)/100),
					item[1] - (item[1]*(abs(diff)*20)/100),
					item[2] - (item[2]*(abs(diff)*20)/100),
					item[3] - (item[3]*(abs(diff)*20)/100)))
				elif (diff<0):
					list.append((item[0] - (item[0]*(diff*20)/100),
					item[1] - (item[1]*(diff*20)/100),
					item[2] - (item[2]*(diff*20)/100),
					item[3] - (item[3]*(diff*20)/100)))
				else:
					list.append((item[0],item[1],item[2],item[3]))
				
		self.rectangle_store.clear()
		for item in list:
			self.rectangle_store.append((item[0],item[1],item[2],item[3],0))
		self.drawingarea.queue_draw()
		
	def redraw(self):
		self.load_image(self.pixbuf_file_name,[],self.ZOOM_FIT)

	def get_selection_list(self):
		list = []
		for item in self.rectangle_store:
			list.append((item[0],item[1],item[2],item[3]))
		return(list)
	
	def save_sub_image(self,filename,x,y,width,height):
		new_pixbuf = self.pixbuf.new_subpixbuf(x,y,width,height)
		new_pixbuf.savev(filename, "png",[],[])		
	
	def get_pixbuf(self):
		return self.pixbuf		
		   
	def zoom_in(self,data=None):
		self.load_image(self.pixbuf_file_name,None, self.zoom_level + 1)
		self.emit('list_updated')

	def zoom_out(self,data=None):
		self.load_image(self.pixbuf_file_name,None, self.zoom_level - 1)
		self.emit('list_updated')

	def zoom_fit(self,data=None):
		self.load_image(self.pixbuf_file_name,None,self.ZOOM_FIT)
		self.emit('list_updated')
	
	def get_zoom_level(self):
		return self.zoom_level

	def __drawingarea_draw(self, widget, cr):
		   Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
		   cr.paint()
		   
		   for item in self.rectangle_store:
			   cr.move_to(10, 90)
			   cr.rectangle(item[0], item[1], item[2], item[3])
			   if item[4] == True:
				   cr.set_source_rgb(0.9, 0.1, 0.1)
			   else:
				   cr.set_source_rgb(1, 0, 1)
			   cr.set_line_width (5.0);
			   #cr.fill()
			   cr.stroke()
		   
		   if (self.on_select == True):
			   cr.rectangle(self.start_x,self.start_y,self.tmp_finish_x-self.start_x,self.tmp_finish_y-self.start_y)
			   cr.set_source_rgb(0, 0, 1.0)
			   cr.set_line_width (5.0);
			   cr.stroke()
		   return True

	def __drawingarea_button_press_event(self, widget, event):
		if (event.button == 1):
			self.start_x,self.start_y=event.get_coords()
			self.on_select = True
		elif(event.button == 3):
			self.drawingarea_popupmenu.popup(None, None, None, None,event.button,event.time)
			self.drawingarea_popupmenu.show_all()
		return True
    
	def __drawingarea_motion_notify_event(self, widget, event):
		if (self.on_select):
			self.tmp_finish_x,self.tmp_finish_y = event.get_coords()
			self.drawingarea.queue_draw()	

	def __drawingarea_button_release_event(self, widget, event):
		if(self.on_select):
			self.finish_x,self.finish_y=event.get_coords()
			self.on_select = False		
			#Swap coordinate if selected in reverse direction
			if(self.start_x >= self.finish_x):
				self.start_x,self.finish_x = self.finish_x,self.start_x
			if(self.start_y >= self.finish_y):
				self.start_y,self.finish_y = self.finish_y,self.start_y
		
			out_of_range = False
			max_width = self.pixbuf.get_width()
			max_height = self.pixbuf.get_height()
			if (self.start_x > max_width or self.start_y > max_height or self.finish_x > max_width or self.finish_y > max_height ):
				out_of_range = True
		
			overlaped = False
			for item in self.rectangle_store:
				start_x = item[0]
				start_y = item[1]
				finish_x = item[2]+item[0]
				finish_y = item[3]+item[1]
				if ((start_x <= self.start_x <= finish_x or start_x <= self.finish_x <= finish_x) and (start_y <= self.start_y <= finish_y or start_y <= self.finish_y <= finish_y)):
					overlaped = True
				
			if (overlaped):
				dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,Gtk.ButtonsType.OK, "Rectangle Overlaped!")
				dialog.format_secondary_text("Rectangle overlaped with Start - ({0},{1})  End - ({2},{3})".format(start_x,start_y,finish_x,finish_y))
				dialog.run()
				dialog.destroy()
			elif (out_of_range):
				dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,Gtk.ButtonsType.OK, "Selection out of range!")
				dialog.format_secondary_text("Selection out of range! Please select area inside the image")
				dialog.run()
				dialog.destroy()
			else:
				print(((self.start_x,self.start_y,self.finish_x-self.start_x,self.finish_y-self.start_y,0)))
				self.rectangle_store.append((self.start_x,self.start_y,self.finish_x-self.start_x,self.finish_y-self.start_y,0))
				self.emit('list_updated')
		
			self.drawingarea.queue_draw()
		return True

	def __delete_selection(self,widget):
		item = self.treeview_image.get_selection()
		model,iter = item.get_selected()
		self.rectangle_store.remove(iter)
		self.drawingarea.queue_draw()
		self.emit('list_updated')

	def __clear_selection(self,widget):
		self.rectangle_store.clear()
		self.drawingarea.queue_draw()
		self.emit('list_updated')

	def __treeview_image_cursor_changed(self,widget):
		for item in self.rectangle_store:
			item[4] = False
		item = self.treeview_image.get_selection()
		model,iter = item.get_selected()
		if iter:
			self.rectangle_store.set(iter,4,True)
			self.drawingarea.queue_draw()


class TestWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        
        self.iv = ImageViewer()
        self.iv.load_image("/usr/share/lios/ui/lios",[],ImageViewer.ZOOM_FIT)

        self.box = Gtk.VBox(spacing=6)
        self.add(self.box)
        self.box.pack_start(self.iv, True, True, 0)

        self.button1 = Gtk.Button(label="Get List")
        self.button1.connect("clicked", self.on_button1_clicked)        
        self.box.pack_start(self.button1, False, False, 0)

        self.button2 = Gtk.Button(label="Set List")
        self.button2.connect("clicked", self.on_button2_clicked)        
        self.box.pack_start(self.button2, False, False, 0)

        self.add(self.box)

    def on_button1_clicked(self, widget):
        print(self.iv.get_selection_list())

    def on_button2_clicked(self, widget):
        self.iv.set_selection_list([(25,10,45,60)])


if __name__ == "__main__":
	win = TestWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
