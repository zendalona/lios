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

from gi.repository import GObject

from lios.ui.gtk import loop, dialog, widget, drawing_area, tree_view, containers, window

from lios import image_logics, localization
_ = localization._


class ImageViewer(containers.Paned):
	ZOOM_FIT = 4
	__gsignals__ = {
        'list_updated' : (GObject.SIGNAL_RUN_LAST,
                     GObject.TYPE_NONE,
                     ())
        }


	def __init__(self):
		super(ImageViewer,self).__init__(containers.Paned.HORIZONTAL)
		self.set_border_width(5)

		#Drawing Area		
		self.drawingarea = drawing_area.DrawingArea()
		
		scrolled = containers.ScrollBox()
		scrolled.add_with_viewport(self.drawingarea);
		
		
		
		self.drawingarea.connect_button_press_event(self.__drawingarea_button_press_event)
		self.drawingarea.connect_button_release_event(self.__drawingarea_button_release_event)
		self.drawingarea.connect_motion_notify_event(self.__drawingarea_motion_notify_event)
		

		self.add(scrolled)
				
		#Drawing List Tree View
		self.treeview = tree_view.TreeView([("Selected",bool,False),
		("X",int,True),("Y",int,True),
		("Width",int,True),("Height",int,True),
		("Letter",str,True)],self.edited_callback)
		
		self.treeview.connect_cursor_change_function(self.treeview_cursor_changed)
		self.treeview.connect_rows_reordered_function(self.treeview_rows_reordered)
		self.treeview.set_reorderable(True)
		scrolled_treeview = containers.ScrollBox()
		scrolled_treeview.add(self.treeview)

		self.rs = []


		button1 = widget.Button("Delete")
		button1.connect_function(self.__delete_selection)

		button2 = widget.Button("Clear")
		button2.connect_function(self.__clear_selection)

		grid = containers.Grid()
		grid.add_widgets([(scrolled_treeview,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,(button1,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(button2,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])
		self.add(grid)
		

		
		#Inetial Values
		self.on_select = False
		self.on_resize = False
		self.zoom_list = [0.20,0.40,0.60,0.80,1,1.20,1.40,1.60,1.80,2]
		self.zoom_level = self.ZOOM_FIT
		self.drawingarea.show()
		
		self.set_position(400)
		self.show()
		
	
	#set_position()
	
	def edited_callback(self,row):
		# Reset the new rectangle list
		rs = self.treeview.get_list()
		if(not image_logics.is_overlapping(
		[ [row[1],row[2],row[3],row[4] ] for row in self.rs ],
		row,rs[row][1],rs[row][2],rs[row][3],rs[row][4])):
			self.rs = rs;
			
			#applay new rectangle list on drawing area
			self.drawingarea.set_rectangle_list([[ row[0], row[1],row[2],row[3],row[4] ] for row in self.rs ])
			self.drawingarea.redraw()
		else:
			self.treeview.set_list(self.rs)
	
	def treeview_cursor_changed(self):
		selected_row = self.treeview.get_selected_row_index()
		self.set_selected_item(selected_row)				
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()
		# Note : The set list function should not again - 
		# trigger cursor-change function 
		#self.treeview.set_list(self.rs)

	def treeview_rows_reordered(self):
		self.rs = self.treeview.get_list()
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])

	def load_image(self,filename,list,zoom_level):
		self.start_type = 0;
		self.filename = filename
		diff = self.zoom_level - zoom_level
		self.zoom_level = zoom_level
		parameter = self.zoom_list[self.zoom_level]
		self.set_list(list)
		self.drawingarea.load_image(filename,list,parameter);
	def set_list(self,list_):
		if (list_ == None):
			list_ = []
			for item in self.rs:
				if (diff>0):
					list_.append([0,item[1] - (item[1]*(abs(diff)*20)/100),
					item[2] - (item[2]*(abs(diff)*20)/100),
					item[3] - (item[3]*(abs(diff)*20)/100),
					item[4] - (item[4]*(abs(diff)*20)/100),item[5]])
				elif (diff<0):
					list_.append([0,item[1] - (item[1]*(diff*20)/100),
					item[2] - (item[2]*(diff*20)/100),
					item[3] - (item[3]*(diff*20)/100),
					item[4] - (item[4]*(diff*20)/100),item[5]])
				else:
					list_.append([0,item[1],item[2],item[3],item[4],item[5]])
		self.rs = list(list(x) for x in list_)
		self.treeview.set_list(self.rs)


	def get_list(self):
		return self.rs

	def get_height(self):
		return self.drawingarea.get_height();

	def get_filename(self):
		return self.filename
	
	def set_label_entry_visible(self,value):
		self.treeview.set_column_visible(5,False);		

	def redraw(self):
		loop.acquire_lock()
		self.load_image(self.filename,[],self.ZOOM_FIT)
		loop.release_lock()

	def get_selection_list(self):
		# return with the pattern x, y , width, height, letter
		return([[ row[1],row[2],row[3],row[4], row[5] ] for row in self.rs ])
	
	def save_sub_image(self,filename,x,y,width,height):
		self.drawingarea.save_image_rectangle(filename,x,y,width,height)	
	
	def get_pixbuf(self):
		return self.pixbuf		
		   
	def zoom_in(self,data=None):
		self.load_image(self.filename,None, self.zoom_level + 1)
		self.treeview.set_list(self.rs)
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.emit('list_updated')

	def zoom_out(self,data=None):
		self.load_image(self.filename,None, self.zoom_level - 1)
		self.treeview.set_list(self.rs)
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.emit('list_updated')

	def zoom_fit(self,data=None):
		self.load_image(self.filename,None,self.ZOOM_FIT)
		self.emit('list_updated')
	
	def get_zoom_level(self):
		return self.zoom_level




	def __drawingarea_button_press_event(self, point, button_type):
		if(button_type == 1):
			self.start_x,self.start_y=point
			self.start_type, self.start_row_index, self.start_position_type = image_logics.get_point_type(self.start_x,self.start_y,[ [row[1],row[2],row[3],row[4],row[0] ] for row in self.rs ])
			
		return True
    
	def __drawingarea_motion_notify_event(self, point):
		x,y = point;
		max_width = self.drawingarea.get_width()
		max_height = self.drawingarea.get_height()
		
		# 1 - Select
		if (self.start_type == 1):
			if(image_logics.detect_out_of_range(x,y,max_width,max_height)):
				return
			
			start_x,start_y,end_x,end_y = image_logics.order_rectangle(self.start_x,self.start_y,x,y);
			if(image_logics.detect_overlap([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],start_x,start_y,end_x,end_y)):
				return

			self.tmp_finish_x,self.tmp_finish_y = point
			self.drawingarea.set_drawing_rectangle((self.start_x,self.start_y,
			self.tmp_finish_x-self.start_x,self.tmp_finish_y-self.start_y))
			
			self.drawingarea.redraw()

		# 2 - Resize
		if (self.start_type == 2):
			if(image_logics.detect_out_of_range(x,y,max_width,max_height)):
				return
			
			if(self.start_position_type == 1):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				x,y,self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x),
				self.rs[self.start_row_index][4]+(self.rs[self.start_row_index][2] - y))):
					self.rs[self.start_row_index][4] = self.rs[self.start_row_index][4]+(self.rs[self.start_row_index][2] - y)
					self.rs[self.start_row_index][2] = y
					self.rs[self.start_row_index][3] = self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x)
					self.rs[self.start_row_index][1] = x
				
			elif(self.start_position_type == 2):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				self.rs[self.start_row_index][1],y,self.rs[self.start_row_index][3],y+self.rs[self.start_row_index][4] -y)):
					self.rs[self.start_row_index][4] = self.rs[self.start_row_index][4]+(self.rs[self.start_row_index][2] - y)
					self.rs[self.start_row_index][2] = y					

			elif(self.start_position_type == 3):
				if(not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				self.rs[self.start_row_index][1],y,
				x - self.rs[self.start_row_index][1],
				self.rs[self.start_row_index][4]+(self.rs[self.start_row_index][2] - y))):
					self.rs[self.start_row_index][4] = self.rs[self.start_row_index][4]+(self.rs[self.start_row_index][2] - y)
					self.rs[self.start_row_index][2] = y
					self.rs[self.start_row_index][3] = x - self.rs[self.start_row_index][1]		
															
			elif(self.start_position_type == 4):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				x,self.rs[self.start_row_index][2],
				self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x),
				self.rs[self.start_row_index][4])):
					self.rs[self.start_row_index][3] = self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x)
					self.rs[self.start_row_index][1] = x
				
			elif(self.start_position_type == 6):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				self.rs[self.start_row_index][1],self.rs[self.start_row_index][2],
				x - self.rs[self.start_row_index][1],self.rs[self.start_row_index][4])):
					self.rs[self.start_row_index][3] = x - self.rs[self.start_row_index][1]

			elif(self.start_position_type == 7):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				x,self.rs[self.start_row_index][2],
				self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x),
				y - self.rs[self.start_row_index][2])):
					self.rs[self.start_row_index][4] = y - self.rs[self.start_row_index][2]
					self.rs[self.start_row_index][3] = self.rs[self.start_row_index][3]+(self.rs[self.start_row_index][1] - x)
					self.rs[self.start_row_index][1] = x					

			elif(self.start_position_type == 8):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				self.rs[self.start_row_index][1],self.rs[self.start_row_index][2],
				self.rs[self.start_row_index][3],y - self.rs[self.start_row_index][2])):
					self.rs[self.start_row_index][4] = y - self.rs[self.start_row_index][2]		
		
			elif(self.start_position_type == 9):
				if( not image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,
				self.rs[self.start_row_index][1],self.rs[self.start_row_index][2],
				x - self.rs[self.start_row_index][1],y - self.rs[self.start_row_index][2])):
					self.rs[self.start_row_index][4] = y - self.rs[self.start_row_index][2]
					self.rs[self.start_row_index][3] = x - self.rs[self.start_row_index][1]
			
			self.treeview.set_list(self.rs)
			self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])		
		

		# 3 - Moving
		if (self.start_type == 3):
			#Detect if anyof the new rectangle porsion is not feesible
			if(image_logics.detect_out_of_range(x - self.rs[self.start_row_index][3]/2,y - self.rs[self.start_row_index][4]/2,max_width,max_height) or
			image_logics.detect_out_of_range(x + self.rs[self.start_row_index][3]/2,y + self.rs[self.start_row_index][4]/2,max_width,max_height)):
				return
			
			if(image_logics.is_overlapping([ [row[1],row[2],row[3],row[4] ] for row in self.rs ],self.start_row_index,x - self.rs[self.start_row_index][3]/2,
			y - self.rs[self.start_row_index][4]/2,self.rs[self.start_row_index][3],self.rs[self.start_row_index][4])):
				return
			self.rs[self.start_row_index][1] = x - self.rs[self.start_row_index][3]/2;
			self.rs[self.start_row_index][2] = y - self.rs[self.start_row_index][4]/2;
			
			self.treeview.set_list(self.rs)
			self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		
		# 0 - Simply hovering 
		if (self.start_type == 0):
			_type, row_index, position_type = image_logics.get_point_type(x,y,[[row[1],row[2],row[3],row[4] ] for row in  self.rs ])
			self.drawingarea.set_mouse_pointer_type(position_type);
			self.set_selected_item(row_index)
			self.treeview.set_list(self.rs);
			self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()						
				

	def __drawingarea_button_release_event(self, point, button_type):
		if(self.start_type == 1):
			self.finish_x,self.finish_y=point
			self.drawingarea.set_drawing_rectangle(None)		
			
			#Swap coordinate if selected in reverse direction
			self.start_x,self.start_y,self.tmp_finish_x,self.tmp_finish_y = image_logics.order_rectangle(self.start_x,self.start_y,self.tmp_finish_x,self.tmp_finish_y)
		
			self.rs.append([0,self.start_x,self.start_y,self.tmp_finish_x-self.start_x,self.tmp_finish_y-self.start_y,""])
			self.set_selected_item(len([ [row[1],row[2],row[3],row[4],row[0] ] for row in self.rs ])-1)
			self.treeview.set_list(self.rs)
			self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ]  for row in self.rs ]);
			self.drawingarea.redraw()

			self.emit('list_updated')
		
			

		# 2 - Resize or 3 - Moving
		if(self.start_type == 2 or self.start_type == 3):
			self.set_selected_item(self.start_row_index)
			self.treeview.set_list(self.rs);
			

		self.start_type = 0;
	
	def set_selected_item(self,row):
		for i in range(0,len(self.rs)):
			if (i == row):
				self.rs[i][0] = 1;
			else:
				self.rs[i][0] = 0;	

	def __delete_selection(self,widget):
		list = []
		for item in self.rs:
			if (item[0] == 0):
				list.append(item)
		self.rs = list;
		# Set first element as selected 
		self.set_selected_item(0)
		self.treeview.set_list(self.rs)
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()
		self.emit('list_updated')

	def __clear_selection(self,widget):
		self.rs = []
		self.treeview.clear()
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ]);
		self.drawingarea.redraw()
		self.emit('list_updated')


	def connect_context_menu_button_callback(self,function):
		self.drawingarea.connect_context_menu_button_callback(function)


class TestWindow(window.Window):

    def __init__(self):
        window.Window.__init__(self, title="Hello World")
        
        self.iv = ImageViewer()
        li = [(0,10,10,10,10,"a"),(0,30,30,10,10,"b"),(0,50,50,10,10,"c")]
        self.iv.load_image("/usr/share/lios/lios.png",li,ImageViewer.ZOOM_FIT)

        button1 = widget.Button("Get List")
        button1.connect_function(self.on_button1_clicked)        

        button2 = widget.Button(label="Set List")
        button2.connect_function(self.on_button2_clicked)        

        button3 = widget.Button(label="Zoom-In")
        button3.connect_function(self.on_button3_clicked)        
        
        button4 = widget.Button(label="Zoom-Out")
        button4.connect_function(self.on_button4_clicked)
        
        grid = containers.Grid()
        grid.add_widgets([(self.iv,2,1,True,True),containers.Grid.NEW_ROW,
        (button1,1,1,True,False),(button2,1,1,True,False),containers.Grid.NEW_ROW,
        (button3,1,1,True,False),(button4,1,1,True,False)])        

        self.add(grid)
        grid.show()
        self.set_default_size(700,600);

    def on_button1_clicked(self, widget):
        print(self.iv.get_selection_list())

    def on_button2_clicked(self, widget):
        self.iv.set_selection_list([(25,10,45,60)])

    def on_button3_clicked(self, widget):
        self.iv.zoom_in()

    def on_button4_clicked(self, widget):
        self.iv.zoom_out()


if __name__ == "__main__":
	win = TestWindow()
	win.connect("delete-event", lambda x,y : loop.stop_main_loop())
	win.show_all()
	loop.start_main_loop()
