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
		'list_updated': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
	}

	def __init__(self):
		super(ImageViewer, self).__init__(containers.Paned.HORIZONTAL)
		self.set_border_width(5)

		# Drawing Area        
		self.drawingarea = drawing_area.DrawingArea()
		self.scrolled = containers.ScrollBox()
		self.scrolled.add_with_viewport(self.drawingarea)
		
		self.drawingarea.connect_button_press_event(self.__drawingarea_button_press_event)
		self.drawingarea.connect_button_release_event(self.__drawingarea_button_release_event)
		self.drawingarea.connect_motion_notify_event(self.__drawingarea_motion_notify_event)

		# Add scrolled area (main image view) to the left panel
		self.add(self.scrolled)

		# Right side container
		self.panel_box = containers.Box(containers.Box.HORIZONTAL)

		# Panel toggle button
		self.panel_visible = True  # Start with panel visible
		self.toggle_button = widget.Button("◀")  # Left arrow when panel is visible
		self.toggle_button.connect_function(self.toggle_panel)

		# Panel content
		self.content_box = containers.Box(containers.Box.VERTICAL)

		# Drawing List Tree View
		self.treeview = tree_view.TreeView([(_("Selected"), bool, False),
			(_("X"), float, True), (_("Y"), float, True),
			(_("Width"), float, True), (_("Height"), float, True),
			(_("Letter"), str, True)], self.edited_callback)
		
		self.treeview.connect_cursor_change_function(self.treeview_cursor_changed)
		self.treeview.connect_rows_reordered_function(self.treeview_rows_reordered)
		self.treeview.set_column_visible(0, False)
		self.treeview.set_reorderable(True)
		
		# Make columns expand
		for i in range(1, 6):  # Columns 1 to 5 (X, Y, Width, Height, Letter)
			column = self.treeview.get_column(i)
			column.set_expand(True)

		scrolled_treeview = containers.ScrollBox()
		scrolled_treeview.add(self.treeview)
		scrolled_treeview.set_vexpand(True)  # Allow vertical expansion
		scrolled_treeview.set_hexpand(True)  # Allow horizontal expansion

		# Button container
		button_box = containers.Box(containers.Box.HORIZONTAL)
		button1 = widget.Button(_("Delete"))
		button1.set_tooltip_text(_("Shortcut Alt+D"))
		button1.connect_function(self.__delete_selection)
		button2 = widget.Button(_("Clear"))
		button2.connect_function(self.clear_selection)
		button_box.add(button1)
		button_box.add(button2)

		# Add widgets to content_box
		self.content_box.add(scrolled_treeview)
		self.content_box.add(button_box)

		# Add toggle button and content box to panel_box
		self.panel_box.add(self.toggle_button)
		self.panel_box.add(self.content_box)

		# Add panel_box to the right pane
		self.add(self.panel_box)

		# Other initializations
		self.rs = []
		self.start_row_index = -1
		self.previus_row_index = -1
		
		self.on_select = False
		self.on_resize = False
		self.zoom_list = [0.20, 0.40, 0.60, 0.80, 1, 1.20, 1.40, 1.60, 1.80, 2]
		self.zoom_level = self.ZOOM_FIT
		self.drawingarea.show()
		
		self.set_position(self.get_allocated_width() - 300)  # Show panel with fixed width
		self.show_all()

	def toggle_panel(self, *args):
		self.panel_visible = not self.panel_visible
		if self.panel_visible:
			self.content_box.show()
			self.toggle_button.set_label("◀")  # Left arrow when panel is visible
			self.set_position(self.get_allocated_width() - 300)  # Show panel with fixed width
		else:
			self.content_box.hide()
			self.toggle_button.set_label("▶")  # Right arrow when panel is hidden
			self.set_position(self.get_allocated_width() - 30)
		
	
	#set_position()
	
	def scroll_image_view(self,h_value,v_value):
		self.scrolled.scroll(h_value,v_value)

	def get_image_view_size_on_screen(self):
		return self.scrolled.get_size_on_screen()

	def get_image_view_scrolled_start_points(self):
		return self.scrolled.get_current_start_points()

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
			self.emit('list_updated')
		else:
			self.treeview.set_list(self.rs)
	
	def treeview_cursor_changed(self):
		selected_row = self.treeview.get_selected_row_index()
		self.set_selected_item(selected_row)				
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()

		#Scroll image view to new position
		width,height = self.get_image_view_size_on_screen()
		cur_rec_x = self.rs[selected_row][1]#+self.rs[selected_row][3]
		cur_rec_y = self.rs[selected_row][2]#+self.rs[selected_row][4]
		x = (cur_rec_x - (width*50/100));
		y = (cur_rec_y - (height*50/100));
		self.scroll_image_view(x,y);

		# Note : The set list function should not again - 
		# trigger cursor-change function 
		#self.treeview.set_list(self.rs)

	def treeview_rows_reordered(self):
		self.rs = self.treeview.get_list()
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.emit('list_updated')

	def load_image(self,filename,list,zoom_level):
		if(0 <= zoom_level <= 9):
			self.start_type = 0;
			self.filename = filename
			self.old_zoom_level = self.zoom_level
			diff = self.zoom_level - zoom_level
			self.zoom_level = zoom_level
			parameter = self.zoom_list[self.zoom_level]
			self.set_list(list,diff)
			self.drawingarea.load_image(filename,list,parameter);


	def set_list(self,list_,diff):
		if (list_ == None):
			old_factor = self.old_zoom_level - 4
			new_factor = self.zoom_level - 4

			list_ = []
			# Here we have to revert to the original because we always
			# zoom in/out on the original image with factors to keep the quality
			# ie zoom the image from original instead of zooming the zoomed image
			for item in self.rs:
				x_orig = item[1]*100/((old_factor*20)+100)
				x = x_orig+((x_orig*20*new_factor)/100)
				y_orig = item[2]*100/((old_factor*20)+100)
				y = y_orig+((y_orig*20*new_factor)/100)
				width_orig = item[3]*100/((old_factor*20)+100)
				width = width_orig+((width_orig*20*new_factor)/100)
				height_orig = item[4]*100/((old_factor*20)+100)
				height = height_orig+((height_orig*20*new_factor)/100)
				list_.append([0,x,y,width,height,item[5]])


		self.rs = list(list(x) for x in list_)
		self.treeview.set_list(self.rs)
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()

	def get_list(self):
		old_factor = self.zoom_level - 4
		list_ = []
		# Here we have to return the original because we always
		# zoom in/out on the original image with factors to keep the quality
		# ie zoom the image from original instead of zooming the zoomed image
		for item in self.rs:
			x_orig = item[1]*100/((old_factor*20)+100)
			y_orig = item[2]*100/((old_factor*20)+100)
			width_orig = item[3]*100/((old_factor*20)+100)
			height_orig = item[4]*100/((old_factor*20)+100)
			list_.append([0,x_orig,y_orig,width_orig,height_orig,item[5]])
		return list(list(x) for x in list_)

	def get_height(self):
		return self.drawingarea.get_height();

	def get_original_height(self):
		return self.drawingarea.get_original_height()

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
	
	# inorder to maintain the qulity the sub-image should be created from
	# original image so the rectangle coordinates should be in original points
	def save_sub_image(self,filename,x,y,width,height):
		factor = self.zoom_level - 4
		x = x*100/((factor*20)+100)
		y = y*100/((factor*20)+100)
		width = width*100/((factor*20)+100)
		height = height*100/((factor*20)+100)
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
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.emit('list_updated')
	
	def get_zoom_level(self):
		return self.zoom_level




	def __drawingarea_button_press_event(self, point, button_type):
		if(button_type == 1):
			self.start_x,self.start_y=point
			width,height = self.get_image_view_size_on_screen()
			area_x_start, area_y_start = self.get_image_view_scrolled_start_points()
			self.start_type, self.start_row_index, self.start_position_type = image_logics.get_point_type(self.start_x,self.start_y, area_x_start, area_y_start, width, height,[ [row[1],row[2],row[3],row[4],row[0] ] for row in self.rs ])
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
			area_x_start, area_y_start = self.get_image_view_scrolled_start_points()
			width,height = self.get_image_view_size_on_screen()
			_type, row_index, position_type = image_logics.get_point_type(x,y,area_x_start, area_y_start, width, height,[[row[1],row[2],row[3],row[4] ] for row in  self.rs ])
			self.drawingarea.set_mouse_pointer_type(position_type);

			# if self.previus_row_index not equll to row_index then the
			# mouse pointer moved from current box so we draw it

			if (self.previus_row_index != row_index):
				# While hovering over boxes the treeview cursor change handler function should not be called
				# because it simply scroll drawing area for each boxes which leads to flicker
				self.treeview.block_cursor_change_signal()
				if ( row_index != -1 ):
					# The mouse is over the box at row_index
					self.set_selected_item(row_index)
					self.treeview.set_list(self.rs);
					self.drawingarea.set_rectangle_list([[ row[0],row[0],row[1],row[2],row[3] ] for row in self.rs ])
					self.treeview.set_cursor(row_index)
				elif( self.start_row_index != -1 ):
					# If user made a selection then it should be preserved even after hovering other boxes
					self.set_selected_item(self.start_row_index)
					self.treeview.set_list(self.rs);
					self.drawingarea.set_rectangle_list([[ row[0],row[0],row[1],row[2],row[3] ] for row in self.rs ])
					self.treeview.set_cursor(self.start_row_index)

				self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
				self.treeview.unblock_cursor_change_signal()
			self.previus_row_index = row_index;
		self.drawingarea.redraw()

	def __drawingarea_button_release_event(self, point, button_type):
		if(self.start_type == 1):
			self.finish_x,self.finish_y=point
			self.drawingarea.set_drawing_rectangle(None)		
			
			#Swap coordinate if selected in reverse direction
			self.start_x,self.start_y,self.tmp_finish_x,self.tmp_finish_y = image_logics.order_rectangle(self.start_x,self.start_y,self.tmp_finish_x,self.tmp_finish_y)

			# finding the index of new box inside the box list
			index = image_logics.find_index_for_new_box(self.start_x,self.start_y,self.tmp_finish_x,self.tmp_finish_y,
			[[ row[1],row[2],row[3],row[4] ]  for row in self.rs ]);

			# Inserting the new box to the list
			self.rs.insert(index,[0,self.start_x,self.start_y,self.tmp_finish_x-self.start_x,self.tmp_finish_y-self.start_y,""])

			self.set_selected_item(len([ [row[1],row[2],row[3],row[4],row[0] ] for row in self.rs ])-1)
			self.treeview.set_list(self.rs)
			self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ]  for row in self.rs ]);
			self.drawingarea.redraw()

			self.emit('list_updated')
		
			

		# 2 - Resize or 3 - Moving
		if(self.start_type == 2 or self.start_type == 3):
			self.set_selected_item(self.start_row_index)
			self.treeview.set_list(self.rs);
			self.emit('list_updated')
			

		self.start_type = 0;
	
	def set_selected_item(self,row):
		self.selected_item = row;
		for i in range(0,len(self.rs)):
			if (i == row):
				self.rs[i][0] = 1;
			else:
				self.rs[i][0] = 0;	
	def get_selected_item_index(self):
		return self.selected_item;

	def __delete_selection(self,widget):
		list = []
		for item in self.rs:
			if (item[0] == 0):
				list.append(item)
		self.rs = list;
		# Set first element as selected 
		self.set_selected_item(0)
		# reset selection index
		self.start_row_index = -1;
		self.treeview.set_list(self.rs)
		self.drawingarea.set_rectangle_list([[ row[0],row[1],row[2],row[3],row[4] ] for row in self.rs ])
		self.drawingarea.redraw()
		self.emit('list_updated')

	def clear_selection(self,widget):
		self.rs = []
		self.treeview.clear()
		# reset selection index
		self.start_row_index = -1;
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
        self.iv.load_image(macros.logo_file,li,ImageViewer.ZOOM_FIT)

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
