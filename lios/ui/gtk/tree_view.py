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

class CellRendererSpin(Gtk.CellRendererSpin):
	def __init__(self,pos):
     """
     Initialize the position.

     Args:
         self: (todo): write your description
         pos: (int): write your description
     """
		super(CellRendererSpin,self).__init__()
		self.pos = pos

class CellRendererText(Gtk.CellRendererText):
	def __init__(self,pos):
     """
     Stub

     Args:
         self: (todo): write your description
         pos: (int): write your description
     """
		super(CellRendererText,self).__init__()
		self.pos = pos	

class CellRendererToggle(Gtk.CellRendererToggle):
	def __init__(self,pos):
     """
     Initialize the underlying position.

     Args:
         self: (todo): write your description
         pos: (int): write your description
     """
		super(CellRendererToggle,self).__init__()
		self.pos = pos	
		
class TreeView(Gtk.TreeView):
	def __init__(self,name_type_tuple_list,function):
     """
     Initialize a gtk table

     Args:
         self: (todo): write your description
         name_type_tuple_list: (str): write your description
         function: (callable): write your description
     """
		super(TreeView,self).__init__()
		self.function = function;
		self.cursor_change_handler_id = None
		
		type_list = []
		i = 0;
		for item in name_type_tuple_list:
			type_list.append(item[1])
			if(item[1] == float):
				cell = CellRendererSpin(i)
				adjustment = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
				cell.set_property("adjustment", adjustment)
				cell.set_property("digits", 3)
				cell.connect("edited", self.on_float_edited)
			elif(item[1] == int):
				cell = CellRendererSpin(i)
				adjustment = Gtk.Adjustment(0, 0, 10000, 1, 10, 0)
				cell.set_property("adjustment", adjustment)
				cell.connect("edited", self.on_float_edited)
			elif(item[1] == bool):
				cell = CellRendererToggle(i)
				cell.set_radio(True)
				cell.connect("toggled", self.on_bool_edited)
			else:
				cell = CellRendererText(i)
				cell.connect("edited", self.on_edited)
			
			if(item[2] == True):
				cell.set_property("editable", True)
				
			col = Gtk.TreeViewColumn(item[0], cell, text=i)
			self.append_column(col)
			i = i + 1;
			
		self.rs = Gtk.ListStore(*type_list)
		self.set_model(self.rs);	
		
		self.set_reorderable(True)
		#self.connect("cursor-changed",self.__treeview_image_cursor_changed)
	
	def append(self,item):
     """
     Append item to the end of the list.

     Args:
         self: (todo): write your description
         item: (array): write your description
     """
		self.rs.append(item);

	def remove(self,index):
     """
     Removes * index * index * index

     Args:
         self: (todo): write your description
         index: (int): write your description
     """
		iter = self.rs.get_iter(index)
		self.rs.remove(iter);
	
	def set_list(self,list):
     """
     Add a list of items

     Args:
         self: (todo): write your description
         list: (todo): write your description
     """
		if(self.cursor_change_handler_id):
			self.handler_block(self.cursor_change_handler_id)
		self.rs.clear()
		for item in list:
			self.rs.append(item)
		if(self.cursor_change_handler_id):
			self.handler_unblock(self.cursor_change_handler_id)

	def block_cursor_change_signal(self):
     """
     Handles a cursor.

     Args:
         self: (todo): write your description
     """
		if(self.cursor_change_handler_id):
			self.handler_block(self.cursor_change_handler_id)

	def unblock_cursor_change_signal(self):
     """
     Unblock_cursor signal.

     Args:
         self: (todo): write your description
     """
		if(self.cursor_change_handler_id):
			self.handler_unblock(self.cursor_change_handler_id)

	#def set_selected_row(self,row):
	#	self.handler_block(self.cursor_change_handler_id)
	#	self.set_cursor(row);
	#	self.handler_unblock(self.cursor_change_handler_id)
	
	def get_list(self):
     """
     Return a list of all items

     Args:
         self: (todo): write your description
     """
		# list comprehension used to unpack Gtk.ListStore
		return [[ i for i in item ] for item in self.rs] 
		
	def clear(self):
     """
     Clears all entries

     Args:
         self: (todo): write your description
     """
		self.rs.clear()
	
	def on_float_edited(self, widget, path, value):
     """
     Set the value of a widget

     Args:
         self: (todo): write your description
         widget: (todo): write your description
         path: (str): write your description
         value: (str): write your description
     """
		self.rs[path][widget.pos] = float(value)
		self.function(int(path))

	def on_bool_edited(self, widget, path):
     """
     Hook is clicked we have changed widget

     Args:
         self: (todo): write your description
         widget: (todo): write your description
         path: (str): write your description
     """
		self.rs[path][widget.pos] = True
		self.function(int(path))

	def on_edited(self, widget, path, value):
     """
     Function called when a widget is clicked

     Args:
         self: (todo): write your description
         widget: (todo): write your description
         path: (str): write your description
         value: (todo): write your description
     """
		self.rs[path][widget.pos] = str(value)
		self.function(int(path))
	
	def connect_update_callback(self,function):
     """
     Connects a callback function.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.function = function
	
	def connect_cursor_change_function(self,function):
     """
     Connects a cursor.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.cursor_change_handler_id = self.connect("cursor-changed", lambda x: function())

	def connect_rows_reordered_function(self,function):
     """
     Connects the given function to the given function.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.rows_reordered_handler_id = self.connect("drag-end", lambda x,y: function())
		
	def get_selected_row_index(self):
     """
     Return the index of selected item

     Args:
         self: (todo): write your description
     """
		item = self.get_selection()
		model,iter = item.get_selected()
		path = item.get_selected_rows()[0]
		if (iter == None):
			return 0;
		path = path.get_path(iter)
		return(path.get_indices()[0]);
	
	def set_column_visible(self,column_number, value):
     """
     Sets the value of the column.

     Args:
         self: (todo): write your description
         column_number: (int): write your description
         value: (todo): write your description
     """
		column = self.get_column(column_number);
		column.set_visible(value);
		
		

class TestWindow(Gtk.Window):
    def function(self,row):
        """
        Prints the function

        Args:
            self: (todo): write your description
            row: (todo): write your description
        """
		   print(row)
		   print(self.tv.get_list()) 
    def __init__(self):
        """
        Initialize the gtk button.

        Args:
            self: (todo): write your description
        """
        Gtk.Window.__init__(self, title="Hello World")
        
        self.tv = TreeView([("X",float,True),("Y",float,True),("Width",float,True),("Height",float,True),("Letter",str,True)],self.function)
        self.tv.append([10,20,40,40,"a"]);
        self.tv.append([20,30,40,40,"b"]);


        self.box = Gtk.VBox(spacing=6)
        self.add(self.box)
        self.box.pack_start(self.tv, True, True, 0)

        self.button1 = Gtk.Button(label="Get List")
        self.button1.connect("clicked", self.on_button1_clicked)        
        self.box.pack_start(self.button1, False, False, 0)

        self.button2 = Gtk.Button(label="Set List")
        self.button2.connect("clicked", self.on_button2_clicked)        
        self.box.pack_start(self.button2, False, False, 0)

        self.button3 = Gtk.Button(label="Letter Show")
        self.button3.connect("clicked", self.on_button3_clicked)        
        self.box.pack_start(self.button3, False, False, 0)

        self.button4 = Gtk.Button(label="Letter Hide")
        self.button4.connect("clicked", self.on_button4_clicked)        
        self.box.pack_start(self.button4, False, False, 0)

        self.add(self.box)
        self.set_default_size(400,400);
        
    def on_button1_clicked(self, widget):
        """
        Function called when the button clicked.

        Args:
            self: (todo): write your description
            widget: (todo): write your description
        """
		   print(self.tv.get_list())

    def on_button2_clicked(self, widget):
        """
        Hook called when the user clicks the button.

        Args:
            self: (todo): write your description
            widget: (todo): write your description
        """
        self.tv.set_list([(25,10,45,60)])
    
    def on_button3_clicked(self, widget):
        """
        Trigbutton3 button.

        Args:
            self: (todo): write your description
            widget: (todo): write your description
        """
		   self.tv.set_column_visible(4,True);
		   
    def on_button4_clicked(self, widget):
        """
        The main window4 button.

        Args:
            self: (todo): write your description
            widget: (todo): write your description
        """
		   self.tv.set_column_visible(4,False);
               



if __name__ == "__main__":
	win = TestWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
