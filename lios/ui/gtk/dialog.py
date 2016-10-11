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


class Dialog(Gtk.Dialog):
	BUTTON_ID_1 = 1
	BUTTON_ID_2 = 2
	BUTTON_ID_3 = 3
	def __init__(self,title,buttons):
		super(Dialog,self).__init__(title,None,True,buttons)
	
	def add_widget(self,widget):
		box = self.get_content_area();
		box.add(widget)
	
	def add_widget_with_label(self,widget,label_text):
		new_box = Gtk.Box()
		label = Gtk.Label(label_text)
		label.set_mnemonic_widget(widget)
		new_box.pack_start(label, True, True, 0)
		new_box.pack_start(widget, True, True, 0)
		box = self.get_content_area();
		box.add(new_box)
		box.show_all()		

	def connect_configure_event_handler(self,function):
		self.connect("configure-event",function)
		
	#show_all()
	#run()
