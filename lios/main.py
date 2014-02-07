# coding: latin-1

###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2014 Nalin.x.Linux GPL-3
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
import os
import sys
import time
import cairo
import shutil
import enchant
import configparser

from espeak import espeak

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkX11, GstVideo
from gi.repository import Gio
from gi.repository import Gst
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import PangoCairo
from gi.repository import GObject
from gi.repository import GdkPixbuf

import gi
gi.require_version('Gst', '1.0')

from lios import converter
from lios import scanner
from lios.basic_editor import editor
from lios.basic_editor import spell_check
from lios.basic_editor import find
from lios.basic_editor import find_and_replace

from lios.preferences import lios_preferences
from lios import global_var
from lios.ocr import *

import multiprocessing
import threading

Gst.init(None)
Gdk.threads_init()



def on_thread(function):
	def inner(*args):
		threading.Thread(target=function,args=args).start()
	return inner


class linux_intelligent_ocr_solution(editor,lios_preferences):
	def __init__ (self,file_list=None):
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(global_var.data_dir))
		self.window = self.guibuilder.get_object("window")
		self.paned = self.guibuilder.get_object("paned")
		self.textview = self.guibuilder.get_object("textview")
		self.notebook = self.guibuilder.get_object("notebook")
		self.textbuffer = self.textview.get_buffer();
		self.guibuilder.connect_signals(self)
		

		#Reading Dictionarys		
		self.key_value = {"eng" : "en","afr" : "af","am" : "am","ara" : "ar","ara" : "ar","bul" : "bg","ben" : "bn","br" : "br","cat" : "ca","ces" : "cs","cy" : "cy","dan" : "da","ger" : "de","ger" : "de","ell" : "el","eo" : "eo","spa" : "es","est" : "et","eu" : "eu","fa" : "fa","fin" : "fi","fo" : "fo","fra" : "fr","ga" : "ga","gl" : "gl","gu" : "gu","heb" : "he","hin" : "hi","hrv" : "hr","hsb" : "hsb","hun" : "hu","hy" : "hy","id" : "id","is" : "is","ita" : "it","kk" : "kk","kn" : "kn","ku" : "ku","lit" : "lt","lav" : "lv","mal" : "ml ","mr" : "mr ","dut" : "nl","no" : "no","nr" : "nr","ns" : "ns ","or" : "or ","pa" : "pa ","pol" : "pl ","por" : "pt","por" : "pt","por" : "pt","ron" : "ro","rus" : "ru ","slk" : "sk","slv" : "sl","ss" : "ss","st" : "st","swe" : "sv","tam" : "ta","tel" : "te","tl" : "tl","tn" : "tn","ts" : "ts","ukr" : "uk","uz" : "uz","xh" : "xh","zu" : "zu" }

		#Getting Preferences Values
		self.read_preferences()
		
		#Image iconview and store
		self.image_icon_view = self.guibuilder.get_object("iconview")
		self.image_icon_view.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		
		self.liststore_images = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.image_icon_view.set_pixbuf_column(0)
		self.image_icon_view.set_text_column(1)
		self.image_icon_view.set_model(self.liststore_images)
		
		#Iconview Popup menu
		self.iconview_popup_menu_selected = Gtk.Menu()
		
		item = Gtk.MenuItem.new_with_label("Save-Selected-Images")
		item.connect("activate",self.save_selected_images)
		self.iconview_popup_menu_selected.append(item)

		item = Gtk.MenuItem.new_with_label("Save-Selected-Images-As-Pdf")
		item.connect("activate",self.save_selected_images_as_pdf)
		self.iconview_popup_menu_selected.append(item)
		
		item = Gtk.MenuItem.new_with_label("Delete-selected-Images")
		item.connect("activate",self.iconview_image_delete)
		self.iconview_popup_menu_selected.append(item)

		item = Gtk.MenuItem.new_with_label("OCR-Selected-Images")
		item.connect("activate",self.ocr_selected_images)
		self.iconview_popup_menu_selected.append(item)

		item = Gtk.MenuItem.new_with_label("OCR-Selected-Images-Without-Rotating")
		item.connect("activate",self.ocr_selected_images_without_rotating)
		self.iconview_popup_menu_selected.append(item)

		item = Gtk.MenuItem.new_with_label("Rotate-selected-Images")
		submenu = Gtk.Menu()
		rotate_item = Gtk.MenuItem.new_with_label("Right")
		rotate_item.connect("activate",self.rotate_selected_images_to_right)
		submenu.append(rotate_item)
		rotate_item = Gtk.MenuItem.new_with_label("Left")
		rotate_item.connect("activate",self.rotate_selected_images_to_left)
		submenu.append(rotate_item)
		rotate_item = Gtk.MenuItem.new_with_label("Twice")
		rotate_item.connect("activate",self.rotate_selected_images_to_twice)
		submenu.append(rotate_item)
		item.set_submenu(submenu)
		self.iconview_popup_menu_selected.append(item)
		

		#Nothing selected and iconview is not empty
		self.iconview_popup_menu_none_selected = Gtk.Menu()
		
		item = Gtk.MenuItem.new_with_label("import-image")
		item.connect("activate",self.import_image)
		self.iconview_popup_menu_none_selected.append(item)
		
		self.iconview_popup_menu_zero_items = Gtk.Menu()
		item = Gtk.MenuItem.new_with_label("import-pdf")
		item.connect("activate",self.import_pdf)
		self.iconview_popup_menu_none_selected.append(item)
		
		item = Gtk.MenuItem.new_with_label("Import-Folder")
		item.connect("activate",self.import_folder)
		self.iconview_popup_menu_none_selected.append(item)
		
		item = Gtk.MenuItem.new_with_label("Save-All-Images")
		item.connect("activate",self.save_all_images)
		self.iconview_popup_menu_none_selected.append(item)

		item = Gtk.MenuItem.new_with_label("Save-All-Images-As-Pdf")
		item.connect("activate",self.save_all_images_as_pdf)
		self.iconview_popup_menu_none_selected.append(item)

		item = Gtk.MenuItem.new_with_label("OCR-All-Images")
		item.connect("activate",self.ocr_all_images)
		self.iconview_popup_menu_none_selected.append(item)

		item = Gtk.MenuItem.new_with_label("OCR-All-Images-Without-Rotating")
		item.connect("activate",self.ocr_all_images_without_rotating)
		self.iconview_popup_menu_none_selected.append(item)		

		item = Gtk.MenuItem.new_with_label("Rotate-All-Images")
		submenu = Gtk.Menu()
		rotate_item = Gtk.MenuItem.new_with_label("Right")
		rotate_item.connect("activate",self.rotate_all_images_to_right)
		submenu.append(rotate_item)
		rotate_item = Gtk.MenuItem.new_with_label("Left")
		rotate_item.connect("activate",self.rotate_all_images_to_left)
		submenu.append(rotate_item)
		rotate_item = Gtk.MenuItem.new_with_label("Twice")
		rotate_item.connect("activate",self.rotate_all_images_to_twice)
		submenu.append(rotate_item)
		item.set_submenu(submenu)
		self.iconview_popup_menu_none_selected.append(item)
		
		item = Gtk.MenuItem.new_with_label("Delete-All-Images")
		item.connect("activate",self.iconview_image_clear)
		self.iconview_popup_menu_none_selected.append(item)
		
		#ICONVIEW IS EMPTY
		self.iconview_popup_menu_zero_items = Gtk.Menu()

		item = Gtk.MenuItem.new_with_label("import-image")
		item.connect("activate",self.import_image)
		self.iconview_popup_menu_zero_items.append(item)
		
		item = Gtk.MenuItem.new_with_label("import-pdf")
		item.connect("activate",self.import_pdf)
		self.iconview_popup_menu_zero_items.append(item)
		
		item = Gtk.MenuItem.new_with_label("Import-Folder")
		item.connect("activate",self.import_folder)
		self.iconview_popup_menu_zero_items.append(item)

		
		#TextView Popup Menu
		self.textview_popup_menu = Gtk.Menu()

		item = Gtk.MenuItem.new_with_label("Cut")
		item.connect("activate",self.cut)
		self.textview_popup_menu.append(item)

		item = Gtk.MenuItem.new_with_label("Copy")
		item.connect("activate",self.copy)
		self.textview_popup_menu.append(item)

		item = Gtk.MenuItem.new_with_label("Paste")
		item.connect("activate",self.paste)
		self.textview_popup_menu.append(item)
		
		self.textview_popup_menu_no_selection = Gtk.Menu()
		item = Gtk.MenuItem.new_with_label("Paste")
		item.connect("activate",self.paste)
		self.textview_popup_menu_no_selection.append(item)

		
		#Creating Lios Folder in tmp
		try:
			os.mkdir(global_var.tmp_dir)
		except:
			pass

		#Scanner and Scanner combobox
		self.combobox_scanner = self.guibuilder.get_object("combobox_scanner")
		self.spinner = self.guibuilder.get_object("spinner")
		self.button_scan = self.guibuilder.get_object("button_scan")
		self.button_refresh = self.guibuilder.get_object("button_refresh")
		self.scan_submenu = self.guibuilder.get_object("Scan_Submenu")
		
		self.spinner.hide()
		self.scanner_objects = []
		renderer_text = Gtk.CellRendererText()
		self.combobox_scanner.pack_start(renderer_text, True)
		self.combobox_scanner.add_attribute(renderer_text, "text", 0)
		
		
		#Webcam
		self.box_drawing_area_tree_and_buttons = self.guibuilder.get_object("box_drawing_area_tree_and_buttons")
		self.box_cam_buttons = self.guibuilder.get_object("box_cam_buttons")
		# Create GStreamer pipeline
		self.pipeline = Gst.Pipeline()
		# Create bus to get events from GStreamer pipeline
		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::error', self.cam_on_error)
		# This is needed to make the video output in our DrawingArea:
		self.bus.enable_sync_message_emission()
		self.bus.connect('sync-message::element', self.cam_on_sync_message)
		self.box_cam_buttons.hide()
				
		
		#OCR Wedgets
		self.ocr_submenu = self.guibuilder.get_object("OCR_Submenu")
		
		#Breaker
		self.process_breaker = False
		
		#Printing
		self.print_settings = None

		#Espeak Voice List
		self.voice_list=[]
		for item in espeak.list_voices():
			self.voice_list.append(item.name)

		#Preferences signals
		General_Preferences = self.guibuilder.get_object("General_Preferences")
		General_Preferences.connect("activate",self.preferences,0)
		Preferences_Recognition = self.guibuilder.get_object("Preferences_Recognition")
		Preferences_Recognition.connect("activate",self.preferences,1)
		Preferences_Scanning = self.guibuilder.get_object("Preferences_Scanning")
		Preferences_Scanning.connect("activate",self.preferences,2)
		Preferences_CamaraWebcam = self.guibuilder.get_object("Preferences_CamaraWebcam")
		Preferences_CamaraWebcam.connect("activate",self.preferences,3)
		
		#Drawing Area and it's TreeView
		self.drawingarea = self.guibuilder.get_object("drawingarea")
		self.paned_drawing = self.guibuilder.get_object("paned_drawing")
		self.rectangle_store = Gtk.ListStore(int,int,int,int,int)
		self.treeview_image = self.guibuilder.get_object("treeview_image")
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
		self.on_select = False
		self.drawingarea.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.zoom_level = 1
		self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))		
		
		#Activating Preference
		self.activate_preferences()
		
		self.progressbar = self.guibuilder.get_object("progressbar")
		self.timeout_id = GLib.timeout_add(20, self.progressbar_timeout, None)
		self.activity_mode = True
		self.set_progress_bar("Welcome to Lios 1.8",False,0.01)

		if (file_list):
			for file in file_list:
				try:
					form = file.split(".")[1]
				except:
					pass
				else:
					if form == "txt":
						self.textbuffer.set_text(open(file,"r").read())
						self.save_file_name = file
				
					elif form in ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm"]:
						filename = file.split("/")[-1:][0].split(".")[0]
						destination = "{0}{1}".format(global_var.tmp_dir,filename.replace(' ','-'))
						self.load_image(file,destination,False)
					elif form == "pdf":
						self.import_images_from_pdf(file)	
		else:
			try:
				file = open("{}/.lios_recent".format(global_var.home_dir),encoding="utf-8")
				self.textbuffer.set_text(file.read())
			except:
				pass
				
		
		self.window.maximize();
		self.window.show()
		Gtk.main();
	
	def progressbar_timeout(self, user_data):
		if self.activity_mode:
			self.progressbar.pulse()
		#else:
		#	new_value = self.progressbar.get_fraction() + 0.01
		#	if new_value > 1:
		#		new_value = 0
		#	self.progressbar.set_fraction(new_value)
		return True	
	
	
	def set_progress_bar(self,text=None,fraction=None,pulse=None):
		if (pulse):
			self.progressbar.set_pulse_step(pulse)
			self.activity_mode = True
		if (text):
			self.progressbar.set_text(text)
			self.progressbar.set_show_text(True)
		if (fraction):
			self.progressbar.set_fraction(fraction)
			self.activity_mode = False

	def announce(self,text,interrupt=True):
		if (self.voice_message_state):
			if(interrupt):
				os.system("pkill paplay")
			os.system("espeak -v {} -a {} -s {} -p {} '{}' --stdout|paplay &".format(self.voice_list[self.voice_message_voice],self.voice_message_volume,self.voice_message_rate,self.voice_message_pitch,text.replace("'",'"')))	

	def scan_using_cam(self,widget):		
		self.src = Gst.ElementFactory.make('v4l2src', None)
		self.src.set_property("device", "/dev/video{0}".format(self.cam_device))
		self.pipeline.add(self.src)		
		
		self.sink = Gst.ElementFactory.make('autovideosink', None)
		self.pipeline.add(self.sink)		
		self.src.link(self.sink)
		
		self.box_drawing_area_tree_and_buttons.set_sensitive(False)
		self.box_cam_buttons.show()
		self.notebook.set_current_page(1)
		
		self.drawingarea.set_size_request(self.cam_x,self.cam_y)
		self.xid = self.drawingarea.get_property('window').get_xid()
		self.pipeline.set_state(Gst.State.PLAYING)
		
	
	def cam_close(self, window):
		self.pipeline.set_state(Gst.State.NULL)
		self.box_drawing_area_tree_and_buttons.set_sensitive(True)
		self.box_cam_buttons.hide()
		self.pipeline.remove(self.src)
		self.pipeline.remove(self.sink)	
		self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))
	
	def cam_take(self,widget):
	    window = self.drawingarea.get_window()
	    x = window.get_width()
	    y = window.get_height()
	    pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0,x, y)
	    pixbuf.savev("{0}{1}.png".format(global_var.tmp_dir,self.get_page_number_as_string()), 'png', [], [])
	    self.add_image_to_image_list("{0}{1}.png".format(global_var.tmp_dir,self.get_page_number_as_string()))
	    self.update_page_number()
	    
	def cam_on_sync_message(self, bus, msg):
		if msg.get_structure().get_name() == 'prepare-window-handle':
			print('prepare-window-handle')
			msg.src.set_property('force-aspect-ratio', True)
			msg.src.set_window_handle(self.xid)
		print(msg.get_structure().get_name())

	def cam_on_error(self, bus, msg):
		print('on_error():', msg.parse_error())
        		
		
		

	def drawingarea_draw(self, widget, cr):
		   Gdk.cairo_set_source_pixbuf(cr, self.pb, 0, 0)
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
	
	def drawingarea_load_image(self,filename):
		   self.pb = GdkPixbuf.Pixbuf.new_from_file(filename)
		   self.pb_file_name = filename
		   self.drawingarea.set_size_request(self.pb.get_width()*self.zoom_level,self.pb.get_height()*self.zoom_level)
		   if (self.zoom_level != 1):
			   self.pb = self.pb.scale_simple(self.pb.get_width()*self.zoom_level,self.pb.get_height()*self.zoom_level,GdkPixbuf.InterpType.HYPER)
		   self.treeview_image_clear(self)
	
	def drawingarea_button_release_event(self, widget, event):
		self.finish_x,self.finish_y=event.get_coords()
		self.on_select = False
		print("Finish X - {0}, Y - {1}".format(self.finish_x,self.finish_y))
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
		else:
			self.rectangle_store.append((self.start_x,self.start_y,self.finish_x-self.start_x,self.finish_y-self.start_y,0))
		
		self.drawingarea.queue_draw()
		return True

	def treeview_image_delete(self,widget):
		item = self.treeview_image.get_selection()
		model,iter = item.get_selected()
		self.rectangle_store.remove(iter)
		self.drawingarea.queue_draw()

	def treeview_image_clear(self,widget):
		self.rectangle_store.clear()
		self.drawingarea.queue_draw()

	def treeview_image_cursor_changed(self,widget):
		for item in self.rectangle_store:
			item[4] = False
		item = self.treeview_image.get_selection()
		model,iter = item.get_selected()
		if iter:
			self.rectangle_store.set(iter,4,True)
			self.drawingarea.queue_draw()
        
        
	def drawingarea_button_press_event(self, widget, event):
		self.start_x,self.start_y=event.get_coords()
		print("Start  X - {0}, Y - {1}".format(self.start_x,self.start_y))
		self.on_select = True
		return True
    
	def drawingarea_motion_notify_event(self, widget, event):
		if (self.on_select):
			self.tmp_finish_x,self.tmp_finish_y = event.get_coords()
			self.drawingarea.queue_draw()
	
	@on_thread			
	def ocr_selected_areas(self,widget):
		self.process_breaker = False
		self.make_ocr_widgets_inactive()
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		pb = GdkPixbuf.Pixbuf.new_from_file(self.pb_file_name)
		progress_step = len(self.rectangle_store)/(10^len(self.rectangle_store));progress = 0;
		for item in self.rectangle_store:
			self.set_progress_bar("Running OCR on selected Area [ X={} Y={} Width={} Height={} ]".format(item[0],item[1],item[2],item[3]),progress,None)
			progress = progress + progress_step;
			dest = pb.new_subpixbuf(item[0]/self.zoom_level,item[1]/self.zoom_level,item[2]/self.zoom_level,item[3]/self.zoom_level)
			dest.savev("{0}tmp".format(global_var.tmp_dir), "png",[],[])
			#Will always be Manual with no rotation
			text,angle = self.ocr("{0}tmp".format(global_var.tmp_dir),2,00)
			self.put_text_to_buffer(text,False,False)
			if(self.process_breaker):
				break;
		self.set_progress_bar("completed!",None,0.01)
		self.make_ocr_widgets_active()

	def zoom_in(self,widget):
		self.zoom_level = self.zoom_level * 4/3
		self.drawingarea_load_image(self.pb_file_name)

	def zoom_out(self,widget):
		self.zoom_level = self.zoom_level * 3/4
		self.drawingarea_load_image(self.pb_file_name)

	def zoom_fit(self,widget):
		self.zoom_level = 1
		self.drawingarea_load_image(self.pb_file_name)
	
	def rotate_right(self,widget):
		self.rotate(270)

	def rotate_left(self,widget):
		self.rotate(90)

	def rotate_twice(self,widget):
		self.rotate(180)

	@on_thread
	def rotate(self,angle,file_name = None):
		if (file_name == None):
			file_name = self.pb_file_name
		pb = GdkPixbuf.Pixbuf.new_from_file(file_name)
		pb = pb.rotate_simple(angle)
		pb.savev(file_name, "png",[],[])
		self.drawingarea_load_image(file_name)
		self.iconview_image_reload(file_name)

		
	def iconview_image_reload(self,filename):
		for item in self.liststore_images:
			if (item[1] == filename):
				pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
				height = pixbuff.get_height()
				width = pixbuff.get_width()
				ratio = (width*50)/height
				Gdk.threads_enter()
				buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
				Gdk.threads_leave()
				item[0] = buff
	
	def iconview_press_event(self, treeview, event):
		if ((event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3) or (event.type == Gdk.EventType.KEY_PRESS and event.hardware_keycode == 135)):
			time = event.time
			if (event.type == Gdk.EventType.KEY_PRESS):
				event.button = 0
					
			if (len(self.image_icon_view.get_selected_items()) != 0):
				self.iconview_popup_menu_selected.popup(None, None, None, None,event.button,time)
				self.iconview_popup_menu_selected.show_all()
			else:
				if (len(self.liststore_images) == 0):
					self.iconview_popup_menu_zero_items.popup(None, None, None, None,event.button,time)
					self.iconview_popup_menu_zero_items.show_all()
				else:
					self.iconview_popup_menu_none_selected.popup(None, None, None, None,event.button,time)
					self.iconview_popup_menu_none_selected.show_all()
			return True

	def iconview_selection_changed(self,widget):
		items = self.image_icon_view.get_selected_items()
		if (items):
			self.drawingarea_load_image(self.liststore_images[items[0]][1])


	def iconview_image_delete(self,widget):
		dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING,None,"Deleting !")
		dialog.add_buttons("Cancel",Gtk.ResponseType.CANCEL,"Yes Delete", Gtk.ResponseType.OK)
		dialog.format_secondary_text("Are you sure you want to delete selected images ?")
		response = dialog.run()
		dialog.destroy()
		if (response == Gtk.ResponseType.OK):
			for item in self.image_icon_view.get_selected_items():
				iter = self.liststore_images.get_iter_from_string(item.to_string())
				os.remove(self.liststore_images.get_value(iter, 1))
				self.liststore_images.remove(iter)
			self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))	

	def iconview_image_clear(self,widget):
		dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING,None,"Deleting !")
		dialog.add_buttons("Cancel",Gtk.ResponseType.CANCEL,"Yes Delete All", Gtk.ResponseType.OK)
		dialog.format_secondary_text("Are you sure you want to delete all images ?")
		response = dialog.run()
		dialog.destroy()
		if (response == Gtk.ResponseType.OK):
			for item in self.liststore_images:
				os.remove(item[1])
			self.liststore_images.clear()
			self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))

	
	def rotate_selected_images_to_right(self,widget):
		self.rotate_selected_images_to_angle(90)

	def rotate_selected_images_to_left(self,widget):
		self.rotate_selected_images_to_angle(270)	

	def rotate_selected_images_to_twice(self,widget):
		self.rotate_selected_images_to_angle(180)

	def rotate_selected_images_to_angle(self,angle):
		progress_step = len(self.image_icon_view.get_selected_items())/(10^len(self.image_icon_view.get_selected_items()));progress = 0;
		for item in reversed(self.image_icon_view.get_selected_items()):
			self.rotate(angle,self.liststore_images[item[0]][1])
			self.set_progress_bar("Rotating selected image {} to {}".format(self.liststore_images[item[0]][1],angle),progress,None)
			progress = progress + progress_step;
		self.set_progress_bar("completed!",None,0.01)

	def rotate_all_images_to_right(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_right(None)

	def rotate_all_images_to_left(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_left(None)

	def rotate_all_images_to_twice(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_twice(None)




	@on_thread
	def ocr_selected_images_without_rotating(self,widget):
		self.make_ocr_widgets_inactive()
		progress_step = len(self.image_icon_view.get_selected_items())/(10^len(self.image_icon_view.get_selected_items()));progress = 0;
		for item in reversed(self.image_icon_view.get_selected_items()):
			self.set_progress_bar("Running OCR on selected image {} (without rotating)".format(self.liststore_images[item[0]][1]),progress,None)
			self.announce("Recognising {} without rotating".format(self.liststore_images[item[0]][1]))
			progress = progress + progress_step;
			text,angle = self.ocr(self.liststore_images[item[0]][1],2,00)
			self.put_text_to_buffer(text,False,False)
			if(self.process_breaker):
				break
		self.make_ocr_widgets_active()
		self.set_progress_bar("completed!",None,0.01)
		self.announce("Completed!")
			
	def ocr_all_images_without_rotating(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images_without_rotating(self,None)

	@on_thread			
	def ocr_selected_images(self,widget):
		self.make_ocr_widgets_inactive()
		progress_step = len(self.image_icon_view.get_selected_items())/(10^len(self.image_icon_view.get_selected_items()));progress = 0;
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		for item in reversed(self.image_icon_view.get_selected_items()):
			self.set_progress_bar("Running OCR on selected image {}".format(self.liststore_images[item[0]][1]),progress,None)
			self.announce("Recognising {}".format(self.liststore_images[item[0]][1]))
			progress = progress + progress_step;			
			text,angle = self.ocr(self.liststore_images[item[0]][1],mode,angle)
			self.put_text_to_buffer(text,False,False)
			self.rotate(angle,self.liststore_images[item[0]][1])
			if mode == 1:#Changing partial automatic to Manual
				mode = 2
				self.announce("Angle to be rotated = {}".format(angle))
			if(self.process_breaker):
				break
		self.make_ocr_widgets_active()
				
	def ocr_all_images(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images(None)
	
	def save_selected_images(self,widget):
		dialog = Gtk.FileChooserDialog("Select Folder to save images",None,Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		dialog.set_current_folder(global_var.home_dir)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			directory = dialog.get_current_folder()
			for item in reversed(self.image_icon_view.get_selected_items()):
				shutil.copy(self.liststore_images[item[0]][1],directory)
		dialog.destroy()			


	def save_all_images(self,widget):
		self.image_icon_view.select_all()
		self.save_selected_images(None)
		
	def save_selected_images_as_pdf(self,widget):
		dialog = Gtk.FileChooserDialog("Give pdf filename(with extention) to save images",None,Gtk.FileChooserAction.SAVE,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		dialog.set_current_folder(global_var.home_dir)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_name = dialog.get_filename()
			command = "convert " 
			for item in reversed(self.image_icon_view.get_selected_items()):
				command += self.liststore_images[item[0]][1] + " "
			command += file_name
			os.system(command)
		dialog.destroy()

	def save_all_images_as_pdf(self,widget):
		self.image_icon_view.select_all()
		self.save_selected_images_as_pdf(None)		
								

	def add_image_to_image_list(self,filename):
		try:
			pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
		except:
			pass
		else:
			height = pixbuff.get_height()
			width = pixbuff.get_width()
			ratio = (width*50)/height
			Gdk.threads_enter()
			buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
			self.liststore_images.append([buff, filename])
			Gdk.threads_leave()
		
	def load_image(self,file_name_with_directory,destination,move):
		if os.path.exists(destination):
			#Exist
			self.load_image(file_name_with_directory,destination+"#",move)		
		else:
			if (move):
				shutil.move(file_name_with_directory,destination)
			else:
				shutil.copyfile(file_name_with_directory,destination)
			self.add_image_to_image_list(destination)

	def import_image(self,wedget,data=None):
		open_file = Gtk.FileChooserDialog("Select image file to import",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file.set_current_folder(global_var.home_dir)

		filter = Gtk.FileFilter()
		filter.set_name("Images")
		for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
			filter.add_pattern(pattern)
		open_file.add_filter(filter)
		open_file.set_select_multiple(True)

		response = open_file.run()
		if response == Gtk.ResponseType.OK:
			for file_name_with_directory in open_file.get_filenames():
				filename = file_name_with_directory.split("/")[-1:][0].split(".")[0]
				destination = "{0}{1}".format(global_var.tmp_dir,filename.replace(' ','-'))
				self.load_image(file_name_with_directory,destination,False)
			self.announce("Images imported!")			
		open_file.destroy()		

	def import_pdf(self,wedget,data=None):
		open_file = Gtk.FileChooserDialog("Select Pdf file to import",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file.set_current_folder(global_var.home_dir)
		filter = Gtk.FileFilter()
		filter.set_name("*.Pdf")
		filter.add_pattern("*.pdf")
		open_file.add_filter(filter)
		response = open_file.run()
		if response == Gtk.ResponseType.OK:
			pdf_filename_full = open_file.get_filename()
			self.import_images_from_pdf(pdf_filename_full)
			open_file.destroy()
	
	@on_thread
	def import_images_from_pdf(self,pdf_filename_full):
		pdf_filename = pdf_filename_full.split("/")[-1:][0]
		filename = pdf_filename.split(".")[0]
		pdf_filename = pdf_filename.replace(' ','-').replace(')','-').replace('(','-')
		destination = "{0}{1}".format(global_var.tmp_dir,pdf_filename)		
		shutil.copyfile(pdf_filename_full,destination)
		os.makedirs(destination.split(".")[0],exist_ok=True)
		
		self.set_progress_bar("Extracting images from Pdf",None,0.001)
		self.announce("Extracting images from Pdf please wait!")	
		p = multiprocessing.Process(target=lambda : os.system("pdfimages {} {}/{}".format(destination,destination.split(".")[0],pdf_filename.split(".")[0])) , args=())
		p.start()
		while(p.is_alive()):
			pass
		os.remove(destination)
		
		file_list = os.listdir(destination.split(".")[0])
		file_list = sorted(file_list)
						
		formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm","ppm"]
		for image in file_list:
			try:
				if image.split(".")[1] in formats:
					self.load_image("{}/{}".format(destination.split(".")[0],image),"{}{}".format(global_var.tmp_dir,image),True)
			except IndexError:
				pass
		os.rmdir(destination.split(".")[0])
		self.set_progress_bar("Completed!",None,0.01)
		self.announce("Images imported!")				



	def import_folder(self,wedget,data=None):
		folder = Gtk.FileChooserDialog("Select Folder contains images to import",None,Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		folder.set_current_folder(global_var.home_dir)
		response = folder.run()
		if response == Gtk.ResponseType.OK:
			image_directory = folder.get_current_folder()
			file_list = os.listdir(image_directory)
			progress_step = len(file_list)/(10^len(file_list));progress = 0;			
			formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm"]
			for image in sorted(file_list):
				try:
					if image.split(".")[1] in formats:
						destination = "{0}{1}".format(global_var.tmp_dir,image.split(".")[0].replace(' ','-'))
						self.set_progress_bar("Importing image {}".format(destination),progress,None)
						self.load_image("{0}/{1}".format(image_directory,image),destination,False)					
				except IndexError:
					pass
				progress = progress + progress_step;
			self.set_progress_bar("Completed!",None,0.01)
			self.announce("Images imported!")		
		folder.destroy()		

	def configure_event(self,widget,event):
		self.paned.set_position(event.width-230)
		self.paned_drawing.set_position(200)
	
	def make_ocr_widgets_inactive(self):
		self.ocr_submenu.set_sensitive(False)
		self.spinner.show()
		self.spinner.set_state(True)

	def make_ocr_widgets_active(self):
		self.ocr_submenu.set_sensitive(True)
		self.spinner.hide()
		self.spinner.set_state(False)
	
	def make_scanner_wigets_inactive(self):
		self.combobox_scanner.set_sensitive(False)
		self.spinner.set_state(True)
		self.button_scan.set_sensitive(False)
		self.button_refresh.set_sensitive(False)
		self.scan_submenu.set_sensitive(False)
		self.spinner.show()
	
	def make_scanner_wigets_active(self):
		self.combobox_scanner.set_sensitive(True)
		self.spinner.set_state(False)
		self.button_scan.set_sensitive(True)
		self.button_refresh.set_sensitive(True)
		self.scan_submenu.set_sensitive(True)
		self.spinner.hide()

	
	@on_thread
	def scanner_refresh(self,widget):
		for item in self.scanner_objects:
			item.close()
			
		#scanner.scanner.exit()
		scanner_store = Gtk.ListStore(str)
		self.scanner_objects = []
		
		self.make_scanner_wigets_inactive()
		
		self.set_progress_bar("Geting devices",None,0.001)
		self.announce("Getting devices")
		#Tuple - List Convertion is used to get all items in devices list 
		q = multiprocessing.Queue()
		p = multiprocessing.Process(target=(lambda q :q.put(tuple(scanner.scanner.get_devices()))), args=(q,))
		p.start()
		while(p.is_alive()):
			pass
		
		list_ = list(q.get())
		for device in list_:
			if "scanner" in device[3]:
				self.set_progress_bar("Setting Scanner {}".format(device),None,0.0030)
				self.announce("Setting Scanner {}".format(device[2]))
				self.scanner_objects.append(scanner.scanner(device,self.scan_driver,self.scanner_mode_switching,self.scanner_cache_calibration))
				scanner_store.append([device[2]])
		self.set_progress_bar("Completed!",None,0.01)	
			
		self.combobox_scanner.set_model(scanner_store)		
		self.combobox_scanner.set_active(0)
		#if (len(scanner_store) == 0):
		self.make_scanner_wigets_active()
					

	def scan_single_image(self,widget):
		threading.Thread(target=self.scan).start()
		self.update_page_number()

	@on_thread
	def scan_image_repeatedly(self,widget):
		self.process_breaker = False
		for i in range(0,self.number_of_pages_to_scan):
			t = threading.Thread(target=self.scan)
			t.start()
			while(t.is_alive()):
				pass
			self.update_page_number()
			if(self.process_breaker):
				break
			time.sleep(self.time_between_repeated_scanning)
			if(self.process_breaker):
				break
		self.announce("Job completed!")

	def scan(self):
		selected_scanner = self.combobox_scanner.get_active()
		self.make_scanner_wigets_inactive()
		self.announce("Scanning!")
		print("Scanning from scan")
		self.set_progress_bar("Scanning {}{}.pnm with resolution={} brightness={}".format(global_var.tmp_dir,self.get_page_number_as_string(),self.scan_resolution,self.scan_brightness),None,0.0030)
		p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()),self.scan_resolution,self.scan_brightness,self.scan_area))
		p.start()
		while(p.is_alive()):
			pass
		self.set_progress_bar("Scan Completed!",None,0.01)
			
		if(self.process_breaker):
			self.make_scanner_wigets_active()
			return
		print("Adding image to list")			
		self.add_image_to_image_list("{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()))
		self.make_scanner_wigets_active()
		print("Image added")
		if(self.process_breaker):
			self.make_scanner_wigets_active()
			return	

	def put_text_to_buffer(self,text,place_cursor = False,give_page_number = False):
		Gdk.threads_enter()
		if (self.insert_position == 0):
			iter = self.textbuffer.get_start_iter()
		elif (self.insert_position == 1):
			mark = self.textbuffer.get_insert()
			iter = self.textbuffer.get_iter_at_mark(mark)
		else:
			iter = self.textbuffer.get_end_iter()
		
		start = self.textbuffer.get_start_iter()
		length = len(self.textbuffer.get_text(start,iter,False))
		
		if (give_page_number):
			text = "\nPage-{}\n{}".format(self.get_page_number_as_string(),text)
			
		self.textbuffer.insert(iter,text)
		if(place_cursor):
			iter = self.textbuffer.get_iter_at_offset(length)
			self.textbuffer.place_cursor(iter)
		start,end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start,end,False)
		Gdk.threads_leave()
		with open("{}/.lios_recent".format(global_var.home_dir),"w",encoding="utf-8") as file:
			file.write(text)		
		
	def get_page_number_as_string(self):
		if (self.page_numbering_type == 0):
			return ("{0}".format(self.starting_page_number))
		else:
			return ("{0}-{1}".format(self.starting_page_number,self.starting_page_number + 1))

	def update_page_number(self):
		if (self.page_numbering_type == 0):
			self.starting_page_number = self.starting_page_number + 1
		else:
			self.starting_page_number = self.starting_page_number + 2

		
		
				
		
					
	
	############## Core OCR  Process Start ################################
	def ocr(self,file_name,mode,angle):
		if mode == 2:	#Manual
			text = self.ocr_with_multiprocessing(file_name,angle)
			return (text,angle)
		else: #Full_Automatic or Partial_Automatic
			list_ = []
			for angle in [00,270,180,90]:
				text = self.ocr_with_multiprocessing(file_name,angle)
				count = self.count_dict_words(text)
				list_.append((text,count,angle))
			list_ = sorted(list_, key=lambda item: item[1],reverse=True)
		return (list_[0][0],list_[0][2])
				
	
	def count_dict_words(self,text):
		count = 0
		for word in text.split(" "):
			if (len(word) > 1):
				if (self.dict.check(word) == True):
					count += 1
		return count
		
	def ocr_with_multiprocessing(self,file_name,angle):
		q = multiprocessing.Queue()
		print("Running ocr with multi proc")
		self.set_progress_bar("Running OCR on {} with Engine = {} Language = {} Angle = {}".format(file_name,self.ocr_engine,self.language,angle),None,0.001)
		p = multiprocessing.Process(target=(lambda q,file_name : q.put(ocr_image_to_text(file_name,self.ocr_engine,self.language,angle))), args=(q,file_name))
		p.start()
		while(p.is_alive()):
			pass
		self.set_progress_bar("Recognition Completed!",None,0.01)
		print("Getting text from queue")
		return q.get();		
	############## Core OCR  Process End ################################
	
	@on_thread	
	def scan_and_ocr(self,widget):
		self.process_breaker = False
		t = threading.Thread(target=self.scan)
		t.start()
		while(t.is_alive()):
			pass
		if(self.process_breaker):
			return			
		text,angle = self.ocr("{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()),self.mode_of_rotation,self.rotation_angle)
		self.put_text_to_buffer(text,True,True)
		self.rotate(angle,"{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()))
		self.announce("Page {}".format(self.get_page_number_as_string()))
		self.update_page_number()
		
			
	@on_thread			
	def scan_and_ocr_repeatedly(self,widget):
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		self.process_breaker = False
		for i in range(0,self.number_of_pages_to_scan):
			print("calling scan")
			t = threading.Thread(target=self.scan)
			t.start()
			while(t.is_alive()):
				pass
			if(self.process_breaker):
				break
			print("Sleeping")
			time.sleep(self.time_between_repeated_scanning)	
			if(self.process_breaker):
				break
			print("Running Ocr")					
			text,angle = self.ocr("{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()),mode,angle)	
			print("Placing text and cursor")
			if (i == 0):
				self.put_text_to_buffer(text,True,True)
			else:
				self.put_text_to_buffer(text,False,True)
			self.announce("Page {}".format(self.get_page_number_as_string()))
			print("Rotating image")	
			self.rotate(angle,"{0}{1}.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()))
			self.update_page_number()
			
			if mode == 1: #Change the mode partial automatic to Manual
				mode = 2
				self.announce("Angle to be rotated = {}".format(angle))
							
			if(self.process_breaker):
				break
			print("Compleated ",i);
		self.announce("Job completed!")

	@on_thread
	def optimize_brightness(self,wedget):
		selected_scanner = self.combobox_scanner.get_active()
		self.process_breaker = False
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		if (mode == 0 or mode == 1):
			self.set_progress_bar("Scanning with resolution={} brightness={}".format(self.scan_resolution,100),None,0.0030)
			p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}test.pnm".format(global_var.tmp_dir),self.scan_resolution,100,self.scan_area))
			p.start()
			while(p.is_alive()):
				pass
			text,angle = self.ocr("{0}test.pnm".format(global_var.tmp_dir),mode,angle)
			print(angle)		
		mid_value = 100; distance = 10; vary = 50;
		count = None
		result_text = "<b><span size = 'xx-large'> Click 'Forward' to start optimisation </span> </b>" 
		while(1):
			Gdk.threads_enter()
			guibuilder = Gtk.Builder()
			guibuilder.add_from_file("%s/ui/optimise_brightness_dialog.glade"%(global_var.data_dir))
			dialog = guibuilder.get_object("dialog")
			spinbutton_value = guibuilder.get_object("spinbutton_value")
			spinbutton_distance = guibuilder.get_object("spinbutton_distance")
			spinbutton_vary = guibuilder.get_object("spinbutton_vary")
			label_result = guibuilder.get_object("label_result")
			label_result.set_label(result_text)
			spinbutton_value.set_value(mid_value)
			spinbutton_distance.set_value(distance)
			spinbutton_vary.set_value(vary)
			guibuilder.get_object("button_cancel").connect("clicked",lambda x : dialog.response(Gtk.ResponseType.CANCEL))
			guibuilder.get_object("button_apply").connect("clicked",lambda x : dialog.response(Gtk.ResponseType.APPLY))
			guibuilder.get_object("button_forward").connect("clicked",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
			response = dialog.run()
			dialog.destroy()
			Gdk.threads_leave()				
			if (response == Gtk.ResponseType.APPLY):
				self.scan_brightness = mid_value
				return True
			elif (response == Gtk.ResponseType.ACCEPT):
				mid_value = spinbutton_value.get_value()
				distance = spinbutton_distance.get_value()
				vary = spinbutton_vary.get_value()
				self.scan_brightness = mid_value
			else:
				return True
							
			count, mid_value = self.optimize_with_model(mid_value,distance,vary,angle,count)			
			result_text = "<b><span size = 'xx-large'> Got {} Words at brightness {} </span> </b>".format(count, mid_value) 
			distance = distance / 2;
			vary = distance;
			
			
		
	def optimize_with_model(self,mid_value,distance,vary,angle,previous_optimised_count=None):
		selected_scanner = self.combobox_scanner.get_active()
		list = []		
		pos = mid_value - vary
		while(pos <= mid_value + vary):
			if (pos == mid_value and previous_optimised_count != None):
				list.append((mid_value,previous_optimised_count))
				self.announce("Got {} words at brightness {}.".format(previous_optimised_count,mid_value))
			else:
				self.set_progress_bar("Scanning with resolution={} brightness={}".format(self.scan_resolution,pos),None,0.0030)
				p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}test.pnm".format(global_var.tmp_dir,self.get_page_number_as_string()),self.scan_resolution,pos,self.scan_area))
				p.start()
				while(p.is_alive()):
					pass
				if(self.process_breaker):
					return
				text = self.ocr_with_multiprocessing("{0}test.pnm".format(global_var.tmp_dir),angle)
				count = self.count_dict_words(text)
				list.append((count,pos))
				self.announce("Got {} words at brightness {}.".format(count,pos))
			pos = pos + distance
		list = sorted(list, key=lambda item: item[0],reverse=True)
		return (list[0][0],list[0][1])

	def stop_process(self,widget):
		self.process_breaker = True

	def print_with_action(self, action=None,filename = None):
		if (self.textbuffer.get_has_selection()):
			start,end = self.textbuffer.get_selection_bounds()
		else:
			start,end = self.textbuffer.get_bounds()
		self.print_text = self.textbuffer.get_text(start,end,False)		
		self.layout = None
		self.page_breaks = None
		self.font_size=12
		if action==None:
			action = Gtk.PrintOperationAction.PREVIEW
		
		#paper_size = Gtk.PaperSize(Gtk.PAPER_NAME_A4)
		#paper_size = Gtk.PaperSize.get_default()
		#paper_size = Gtk.PaperSize(paper_size)
		
		setup = Gtk.PageSetup()
		#setup.set_paper_size(paper_size)
		
		# PrintOperation
		print_ = Gtk.PrintOperation()
		print_.set_default_page_setup(setup)
		print_.set_unit(Gtk.Unit.MM)
		
		print_.connect("begin_print", self.begin_print)
		print_.connect("draw_page", self.draw_page)
		
		if action == Gtk.PrintOperationAction.EXPORT:
			print_.set_export_filename(filename)
		res = print_.run(action,self.window)
    
	def begin_print(self, operation, context):
		width = context.get_width()
		height = context.get_height()
		print (height)
		self.layout = context.create_pango_layout()
		self.layout.set_font_description(Pango.FontDescription("Sans " + str(self.font_size)))
		self.layout.set_width(int(width*Pango.SCALE))

		self.layout.set_text(self.print_text,len(self.print_text))

		num_lines = self.layout.get_line_count()
		print ("num_lines: ", num_lines)
		
		page_breaks = []
		page_height = 0
		
		for line in range(num_lines):
			layout_line = self.layout.get_line(line)
			ink_rect, logical_rect = layout_line.get_extents()
			
			x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
			
			line_height = lheight / 1024.0 # 1024.0 is float(pango.SCALE)
			page_height += line_height
			
			print ("page_height ", page_height)
			if page_height + line_height > height:
				page_breaks.append(line)
				page_height = 0
				page_height += line_height
		operation.set_n_pages(len(page_breaks) + 1)
		self.page_breaks = page_breaks
    
	def draw_page (self, operation, context, page_number):
		assert isinstance(self.page_breaks, list)
		#print page_number
		if page_number == 0:
			start = 0
		else:
			start = self.page_breaks[page_number - 1]
		try:
			end = self.page_breaks[page_number]
		except IndexError:
			end = self.layout.get_line_count()
		
		cr = context.get_cairo_context()
		cr.set_source_rgb(0, 0, 0)
		i = 0
		start_pos = 0
		iter = self.layout.get_iter()
		while 1:
			if i >= start:
				line = iter.get_line()
				_, logical_rect = iter.get_line_extents()
				x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
				baseline = iter.get_baseline()
				if i == start:
					start_pos = y_bearing / 1024.0 # 1024.0 is float(pango.SCALE)
				cr.move_to(x_bearing / 1024.0, baseline / 1024.0 - start_pos)
				PangoCairo.show_layout_line(cr, line)
			i += 1
			if not (i < end and iter.next_line()):
				break


	def print_preview(self,widget):
		action = Gtk.PrintOperationAction.PREVIEW
		printer = self.print_with_action(action)
			
	def print_text(self,widget):
		action = Gtk.PrintOperationAction.PRINT_DIALOG
		printer = self.print_with_action(action)

	def print_to_pdf(self,widget):
		dialog = Gtk.FileChooserDialog("Save Text as Pdf",None,Gtk.FileChooserAction.SAVE,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))    
		dialog.set_current_folder(global_var.home_dir)
		dialog.set_do_overwrite_confirmation(True);
		filter = Gtk.FileFilter()
		filter.add_pattern("*.pdf")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			save_file_name = "%s"%(dialog.get_filename())
			action = Gtk.PrintOperationAction.EXPORT
			printer = self.print_with_action(action,save_file_name)
			dialog.destroy()

		
	def textview_button_press_event(self, treeview, event):
		if event.button == 3:
			x = int(event.x)
			y = int(event.y)
			time = event.time
			if self.textbuffer.get_has_selection():
				self.textview_popup_menu.popup(None, None, None, None,event.button,time)
				self.textview_popup_menu.show_all()
			else:
				self.textview_popup_menu_no_selection.popup(None, None, None, None,event.button,time)
				self.textview_popup_menu_no_selection.show_all()
			return True	
	

	def go_to_page(self,wedget,data=None):
		iter,end = self.textbuffer.get_bounds()
		adj = Gtk.Adjustment(value=1, lower=1, upper=self.starting_page_number-1, step_incr=1, page_incr=5, page_size=0) 
		spinbutton_line = Gtk.SpinButton()
		spinbutton_line.set_adjustment(adj)
		spinbutton_line.set_value(0)		
		spinbutton_line.show()

		dialog =  Gtk.Dialog("Go to Page ",self.window,True,("Go", Gtk.ResponseType.ACCEPT,"Close!", Gtk.ResponseType.REJECT))
		spinbutton_line.connect("activate",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
		box = dialog.get_content_area();
		box.add(spinbutton_line)
		spinbutton_line.grab_focus()
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			to_go = spinbutton_line.get_value_as_int()
			if self.page_numbering_type == 0:
				word = "Page-{0}".format(to_go)
			else:
				if to_go % 2 == 0:
					word = "Page-{0}-{1}".format(to_go-1,to_go)
				else:
					word = "Page-{0}-{1}".format(to_go,to_go+1)	
			
			results = iter.forward_search(word, 0, end)
			if results:
				start,end = results
				self.textbuffer.place_cursor(start)
				self.textview.scroll_to_iter(start, 0.0,False,0.0,0.0)
			dialog.destroy()
		else:
			dialog.destroy()


	def open_readme(self,widget,data=None):
		with open("{0}/Data/Readme".format(global_var.data_dir)) as file:
			self.textbuffer.set_text(file.read())
			start = self.textbuffer.get_start_iter()
			self.textbuffer.place_cursor(start)
					
	def about(self,wedget,data=None):
		guibuilder_about = Gtk.Builder()
		guibuilder_about.add_from_file("%s/ui/about.glade" % (global_var.data_dir))
		self.window_about = guibuilder_about.get_object("aboutdialog")
		guibuilder_about.connect_signals(self)
		self.window_about.show()

	def about_close(self,widget,data=None):
		self.window_about.destroy()
		

	def artha(self,wedget,data=None):
		os.system("artha &")

	def audio_converter(self,widget):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start,end,False)		
		converter.record(text)
	def spell_checker(self,widget):
		spell_check(self.textview,self.textbuffer,self.language,self.enchant_language)
	def find(self,widget):
		find(self.textview,self.textbuffer,self.language).window.show()
	def find_and_replace(self,widget):
		find_and_replace(self.textview,self.textbuffer,self.language).window.show()
	def delete(self,wedget,data=None):
		self.textbuffer.delete_selection(True, True)		

    # Read the text
	def Read_Stop(self,wedget,data=None):
		image_read_stop = self.guibuilder.get_object("image_read_stop")
		if espeak.is_playing() == False:
			image_read_stop.set_from_file("{0}/ui/stop".format(global_var.data_dir))
			self.textbuffer.remove_tag(self.highlight_tag, self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			mark = self.textbuffer.get_insert()
			start = self.textbuffer.get_iter_at_mark(mark)
			end = self.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textbuffer.get_text(start,end,False)
			espeak.set_SynthCallback(self.espeak_event)
			espeak.synth(text)
			self.textview.set_editable(False)
		else:
			espeak.cancel()
			espeak.set_SynthCallback(None)
			image_read_stop.set_from_file("{0}/ui/play".format(global_var.data_dir))
			self.textbuffer.remove_tag(self.highlight_tag, self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			self.textview.set_editable(True)
			
		
	def espeak_event(self, event, pos, length):
		Gdk.threads_enter()
		if event == espeak.core.event_WORD:
			pos += self.to_count-1
			s = self.textbuffer.get_iter_at_offset(pos)
			e = self.textbuffer.get_iter_at_offset(length+pos)			
			
			self.textbuffer.remove_all_tags(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			self.textbuffer.apply_tag(self.highlight_tag, s, e)

		if event == espeak.event_END:
			point = self.textbuffer.get_iter_at_offset(pos+self.to_count)
			self.textbuffer.place_cursor(point)
			self.textview.scroll_to_iter(point, 0.0, use_align=True, xalign=0.0, yalign=0.2)
							
					
		if event == espeak.event_MSG_TERMINATED:
			espeak._playing = False
			self.textview.set_editable(True)
			try:
				self.textbuffer.remove_all_tags(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			except:
				pass

		if not espeak.is_playing():
			mark = self.textbuffer.get_insert()
			start = self.textbuffer.get_iter_at_mark(mark)
			end = self.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textbuffer.get_text(start,end,False)
			if (text != ""):
				espeak.synth(text)

		Gdk.threads_leave()		
		return True
	def quit(self,data):
		try:
			shutil.rmtree(global_var.tmp_dir)
		except FileNotFoundError:
			pass
		Gtk.main_quit()
	def new(self,data):
		editor.new(self,None)
		with open("{}/.lios_recent".format(global_var.home_dir),"w",encoding="utf-8") as file:
			file.write("")
		
if __name__ == "__main__":
	linux_intelligent_ocr_solution()
