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

SEPARATOR = 1;

class Menu(Gtk.Menu):
	def __init__(self):
		super(Menu,self).__init__()


class ImageMenuItem(Gtk.ImageMenuItem):
	def __init__(self,label):
		super(ImageMenuItem,self).__init__(label)

class SeparatorMenuItem(Gtk.SeparatorMenuItem):
	def __init__(self):
		super(SeparatorMenuItem,self).__init__()


class MenuBar(Gtk.MenuBar):
	def __init__(self,item_list):
		super(MenuBar,self).__init__()
		self.agr = Gtk.AccelGroup()
		for item in item_list:
			menu = create_menu(item,self.agr)
			self.append(menu)

	def get_accel_group(self):
		return self.agr
			
		
def create_menu(item,agr):
	if (type(item) == list ):
		menu_item = ImageMenuItem(item[0])
		menu = Gtk.Menu()
		if (item[0] in icon.stock_icon_dict.keys()):
			image = Gtk.Image()
			#image.set_from_icon_name(icon.stock_icon_dict[item[0]],10)
			image.set_from_file(macros.icon_dir+icon.stock_icon_dict[item[0]]+".png")
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
		
		for i in item[1:]:
			sub_menu = create_menu(i,agr)
			menu.append(sub_menu)
		menu_item.set_submenu(menu)
		menu_item.set_use_underline(True)
		return menu_item
	
	else:
		if(item == SEPARATOR):
			terminal_menu_item = SeparatorMenuItem()
			return (terminal_menu_item)
		else:
			terminal_menu_item = ImageMenuItem(item[0])
			if (item[0] in icon.stock_icon_dict.keys()):
				image = Gtk.Image()
				#image.set_from_icon_name(icon.stock_icon_dict[item[0]],10)
				image.set_from_file(macros.icon_dir+icon.stock_icon_dict[item[0]]+".png")
				terminal_menu_item.set_image(image)
				terminal_menu_item.set_always_show_image(True)
			terminal_menu_item.connect("activate",item[1])
				
			if(item[2] != "None"):
				key, mod = Gtk.accelerator_parse(item[2])
				terminal_menu_item.add_accelerator("activate", agr, key,
				mod, Gtk.AccelFlags.VISIBLE)
			return (terminal_menu_item)



#** Context Menu related classes and functions **#

class MenuItem(Gtk.MenuItem):
	def __init__(self,label):
		super(MenuItem,self).__init__(label)


class ContextMenu(Gtk.Menu):
	def __init__(self,item_list):
		super(ContextMenu,self).__init__()
		for item in item_list:
			menu = create_context_menu(item)
			self.append(menu)
	def pop_up(self,*data):
		self.popup(None,None,None,None,0,0)
		self.show_all()

def create_context_menu(menu_list):
	if (type(menu_list) == list ):
		menu_item = MenuItem(menu_list[0])
		menu = Gtk.Menu()
		for item in menu_list[1:]:
			sub_menu = create_context_menu(item)
			menu.append(sub_menu)
		menu_item.set_submenu(menu)
		return menu_item
	else:
		if(menu_list == SEPARATOR):
			terminal_menu_item = SeparatorMenuItem()
		else:
			terminal_menu_item = MenuItem(menu_list[0])
			terminal_menu_item.connect("activate",menu_list[1])				
		return (terminal_menu_item)

