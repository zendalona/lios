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
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Atk
from lios.ui.gtk import icon		


class Entry(Gtk.Entry):
	def __init__(self):
		super(Entry,self).__init__()
		
	def connect_change_handler(self,function):
		self.connect("changed",function)
	#set_text()
	#get_text()		
		

class Label(Gtk.Label):
	def __init__(self,text):
		super(Label,self).__init__(text)

	#set_use_markup()

class Button(Gtk.Button):
	def __init__(self,label):
		super(Button,self).__init__(label)

	def connect_function(self,function):
		self.connect("clicked",function)

class IconButton(Gtk.Button):
	def __init__(self,label):
		super(IconButton,self).__init__()
		image = Gtk.Image()
		image.set_from_icon_name(icon.stock_icon_dict[label],8)
		self.set_image(image)
		self.set_hexpand(False)
		self.set_vexpand(False)

	def connect_function(self,function):
		self.connect("clicked",function)

class SpinButton(Gtk.SpinButton):
	def __init__(self,value=1,lower=0,upper=100,step_incr=1,page_incr=5,page_size=0):
		super(SpinButton,self).__init__()
		adj = Gtk.Adjustment(value, lower, upper, step_incr, page_incr, page_size)
		self.set_adjustment(adj)
		self.set_value(value)

	def connect_function(self,function):
		self.connect("clicked",function)
		
	#def set_value(self,value):
	#	self.set_value(value)
	
	def get_value(self):
		return self.get_value_as_int()

class ComboBox(Gtk.ComboBoxText):
	def __init__(self):
		super(ComboBox,self).__init__()
		model = Gtk.ListStore(str)
		self.set_model(model)
		renderer_text = Gtk.CellRendererText()
		self.pack_start(renderer_text, True)

	def add_item(self,item):
		model = self.get_model()
		model.append([item])
	def connect_change_callback_function(self,function):
		self.connect("changed",function);
	def clear(self):
		model = self.get_model()
		model.clear()
	#set_active


class ListView(Gtk.TreeView):
	def __init__(self,title):
		super(ListView,self).__init__()
		model = Gtk.ListStore(str)
		self.set_model(model)
		
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn(title, renderer, text=0)
		self.append_column(column)
	
	def add_item(self,item):
		model = self.get_model()
		model.append([item])
	
	def get_selected_item(self):
		tree_selection =  self.get_selection()
		model,tree_iter = tree_selection.get_selected()
		return model.get_value(tree_iter,0)

	def get_selected_item_index(self):
		tree_selection =  self.get_selection()
		model,tree_iter = tree_selection.get_selected()
		i = 0;
		for item in model:
			if item[0] == model[tree_iter][0]:
				return i;
			i = i + 1;
		return -1;

	def remove_selected_item(self):
		tree_selection =  self.get_selection()
		model,tree_iter = tree_selection.get_selected()
		model.remove(tree_iter)

	
	def clear(self):
		model = self.get_model()
		model.clear()
		
	def connect_on_select_callback(self,function):
		self.connect("row-activated",function)

class ColorButton(Gtk.ColorButton):
	def __init__(self):
		super(ColorButton,self).__init__()
	
	def set_color_from_string(self,color):
		self.set_color(Gdk.color_parse(color))
	
	def get_color_as_string(self):
		return self.get_color().to_string();
		
		

class FontButton(Gtk.FontButton):
	def __init__(self):
		super(FontButton,self).__init__()
	def connect_function(self,function):
		self.connect("font-set",function)

	
	#set_font(font desc)
	#get_font_name()

class Separator(Gtk.HSeparator):
	def __init__(self):
		super(Separator,self).__init__()

class CheckButton(Gtk.CheckButton):
	def __int__(self,label):
		super(CheckButton,self).__int__()
		self.set_label(label)	

	def connect_handler_function(self,function):
		self.connect("clicked",function)

class ProgressBar(Gtk.ProgressBar):
	def __init__(self):
		super(ProgressBar,self).__init__()
		self.activity_mode = True
		a = GLib.timeout_add(20, self.progressbar_timeout, None)

	def progressbar_timeout(self, user_data):
		if self.activity_mode:
			self.pulse()
		#else:
		#	new_value = self.get_fraction() + 0.01
		#	if new_value > 1:
		#		new_value = 0
		#	self.set_fraction(new_value)
		return True	

	def set_pulse_mode(self,mode):
		self.activity_mode = mode;

class Statusbar(Gtk.Frame):
	def __init__(self):
		super(Statusbar,self).__init__()
		self.label = Gtk.Label()
		frame_inner = Gtk.Frame()
		frame_inner.add(self.label)
		atk_ob1 = frame_inner.get_accessible()
		atk_ob1.set_role(Atk.Role.NOTIFICATION)
		
		self.add(frame_inner)
		atk_ob = self.get_accessible()
		atk_ob.set_role(Atk.Role.STATUSBAR)
		
		
	def set_text(self,text):
		self.label.set_text(text)
		child = self.get_children()[0]
		atk_ob = child.get_accessible()
		atk_ob.notify_state_change(Atk.StateType.SHOWING,True);
	
	def set_line_wrap(self,val):
		self.label.set_line_wrap(val)
