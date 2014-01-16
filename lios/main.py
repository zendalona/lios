# coding: latin-1

###########################################################################
#    Lios - Sharada-Braille-Writer
#    Copyright (C) 2012-2014 Nalin.x.Linux GPL-3
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
GObject.threads_init()



def on_thread(function):
	def inner(*args):
		threading.Thread(target=function,args=args).start()
	return inner


class linux_intelligent_ocr_solution(editor,lios_preferences):
	def __init__ (self,filename=None):
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
		self.button_ocr_selected_images = self.guibuilder.get_object("button_ocr_selected_images")
		
		#Breaker
		self.process_breaker = False

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

		
		if (filename):
			 self.textbuffer.set_text(open(filename,"r").read())
			 self.save_file_name = filename
		
		self.window.maximize();
		self.window.show()
		Gtk.main();
	
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
	    pixbuf.savev("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number), 'png', [], [])
	    self.add_image_to_image_list("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number))
	    self.starting_page_number = self.starting_page_number + 1
	    
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
		for item in self.rectangle_store:
			dest = pb.new_subpixbuf(item[0]/self.zoom_level,item[1]/self.zoom_level,item[2]/self.zoom_level,item[3]/self.zoom_level)
			dest.savev("{0}tmp".format(global_var.tmp_dir), "png",[],[])
			#Will always be Manual with no rotation
			text,angle = self.ocr("{0}tmp".format(global_var.tmp_dir),2,00)
			self.put_text_to_buffer(text)
			if(self.process_breaker):
				break;
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
				buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
				item[0] = buff
				
		


	def iconview_selection_changed(self,widget):
		items = self.image_icon_view.get_selected_items()
		if (items):
			self.drawingarea_load_image(self.liststore_images[items[0]][1])


	def iconview_image_delete(self,widget):
		for item in self.image_icon_view.get_selected_items():
			iter = self.liststore_images.get_iter_from_string(item.to_string())
			os.remove(self.liststore_images.get_value(iter, 1))
			self.liststore_images.remove(iter)
		self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))	

	def iconview_image_clear(self,widget):
		for item in self.liststore_images:
			os.remove(item[1])
		self.liststore_images.clear()
		self.drawingarea_load_image("{0}/ui/lios".format(global_var.data_dir))

	@on_thread			
	def ocr_selected_images(self,widget):
		self.make_ocr_widgets_inactive()
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		for item in self.image_icon_view.get_selected_items():
			text,angle = self.ocr(self.liststore_images[item[0]][1],mode,angle)
			self.put_text_to_buffer(text)
			self.rotate(angle,self.liststore_images[item[0]][1])
			if mode == 1:#Changing partial automatic to Manual
				mode = 2				
		self.make_ocr_widgets_active()

	@on_thread
	def ocr_selected_images_without_rotating(self,widget):
		self.make_ocr_widgets_inactive()
		for item in self.image_icon_view.get_selected_items():
			text,angle = self.ocr(self.liststore_images[item[0]][1],2,00)
			self.put_text_to_buffer(text)
		self.make_ocr_widgets_active()
			
	def ocr_all_images_without_rotating(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images_without_rotating(self,None)
		
	def ocr_all_images(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images(None)
	
	def save_selected_images(self,widget):
		dialog = Gtk.FileChooserDialog("Select Folder to save images",None,Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		dialog.set_current_folder(global_var.home_dir)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			directory = dialog.get_current_folder()
			for item in self.image_icon_view.get_selected_items():
				shutil.copy(self.liststore_images[item[0]][1],directory)
		dialog.destroy()			


	def save_all_images(self,widget):
		self.image_icon_view.select_all()
		self.save_selected_images(None)
		
						

	def add_image_to_image_list(self,filename):
		pixbuff =  GdkPixbuf.Pixbuf.new_from_file(filename)
		height = pixbuff.get_height()
		width = pixbuff.get_width()
		ratio = (width*50)/height
		buff = pixbuff.scale_simple(50,ratio,GdkPixbuf.InterpType.BILINEAR)
		self.liststore_images.append([buff, filename])

	def import_image(self,wedget,data=None):
		open_file = Gtk.FileChooserDialog("Select image file to import",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file.set_current_folder(global_var.home_dir)

		filter = Gtk.FileFilter()
		filter.set_name("Images")
		for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
			filter.add_pattern(pattern)
		open_file.add_filter(filter)

		response = open_file.run()
		if response == Gtk.ResponseType.OK:
			file_name_with_directory = open_file.get_filename()
			filename = file_name_with_directory.split("/")[-1:][0].split(".")[0]
			destination = "{0}{1}".format(global_var.tmp_dir,filename.replace(' ','-'))
			shutil.copyfile(file_name_with_directory,destination)
			self.add_image_to_image_list(destination)
			self.drawingarea_load_image(destination)
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
			directory = open_file.get_current_folder()
			open_file.destroy()
			
			pdf_filename = pdf_filename_full.split("/")[-1:][0]
			filename = pdf_filename.split(".")[0]
			destination = "{0}{1}".format(global_var.tmp_dir,pdf_filename.replace(' ','-').replace(')','-').replace('(','-'))		
			shutil.copyfile(pdf_filename_full,destination)
			os.makedirs(destination.split(".")[0],exist_ok=True)
			
			p = Process(target=lambda : os.system("pdfimages {0} {1}/out_image".format(destination,destination.split(".")[0])) , args=())
			p.start()
			while(p.is_alive()):
				print("Converting")
			#os.system("pdfimages {0} {1}/out_image".format(destination,destination.split(".")[0]))
			
			file_list = os.listdir(destination.split(".")[0])			
			formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm","ppm"]
			for image in file_list:
				try:
					if image.split(".")[1] in formats:
						self.add_image_to_image_list("{0}/{1}".format(destination.split(".")[0],image))
				except IndexError:
					pass
		open_file.destroy()



	def import_folder(self,wedget,data=None):
		folder = Gtk.FileChooserDialog("Select Folder contains images to import",None,Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		folder.set_current_folder(global_var.home_dir)
		response = folder.run()
		if response == Gtk.ResponseType.OK:
			image_directory = folder.get_current_folder()
			file_list = os.listdir(image_directory)
			formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm"]
			for image in file_list:
				try:
					if image.split(".")[1] in formats:
						destination = "{0}{1}".format(global_var.tmp_dir,image.split(".")[0].replace(' ','-'))
						shutil.copyfile("{0}/{1}".format(image_directory,image),destination)
						self.add_image_to_image_list(destination)						
				except IndexError:
					pass
		folder.destroy()		

	def configure_event(self,widget,event):
		self.paned.set_position(event.width-230)
		self.paned_drawing.set_position(200)
	
	def make_ocr_widgets_inactive(self):
		self.ocr_submenu.set_sensitive(False)
		self.spinner.show()
		self.button_ocr_selected_images.set_sensitive(False)
		self.spinner.set_state(True)

	def make_ocr_widgets_active(self):
		self.ocr_submenu.set_sensitive(True)
		self.spinner.hide()
		self.button_ocr_selected_images.set_sensitive(True)
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
		
		#Tuple - List Convertion is used to get all items in devices list 
		q = multiprocessing.Queue()
		p = multiprocessing.Process(target=(lambda q :q.put(tuple(scanner.scanner.get_devices()))), args=(q,))
		p.start()
		while(p.is_alive()):
			pass
		
		for device in list(q.get()):
			self.scanner_objects.append(scanner.scanner(device,self.scan_driver,self.scanner_mode_switching))
			scanner_store.append([device[2]])
			
		self.combobox_scanner.set_model(scanner_store)		
		self.combobox_scanner.set_active(0)
		#if (len(scanner_store) == 0):
		self.make_scanner_wigets_active()
					

	def scan_single_image(self,widget):
		threading.Thread(target=self.scan).start()

	@on_thread
	def scan_image_repeatedly(self,widget):
		self.process_breaker = False
		for i in range(0,self.number_of_pages_to_scan):
			t = threading.Thread(target=self.scan)
			t.start()
			while(t.is_alive()):
				pass
			if(self.process_breaker):
				break
			time.sleep(self.time_between_repeated_scanning)
			if(self.process_breaker):
				break

	def scan(self):
		selected_scanner = self.combobox_scanner.get_active()
		self.make_scanner_wigets_inactive()
		p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number),self.scan_resolution,self.scan_brightness,self.scan_area))
		p.start()
		while(p.is_alive()):
			pass
		if(self.process_breaker):
			return			
		self.add_image_to_image_list("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number))
		self.starting_page_number += 1
		self.make_scanner_wigets_active()
		if(self.process_breaker):
			return	

	def put_text_to_buffer(self,text):
		print("Puttig text into buffer")
		if (self.insert_position == 0):
			iter = self.textbuffer.get_start_iter()
		elif (self.insert_position == 1):
			mark = self.textbuffer.get_insert()
			iter = self.textbuffer.get_iter_at_mark(mark)
		else:
			iter = self.textbuffer.get_end_iter()
		self.textbuffer.insert(iter,text)
		
				
		
					
	
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
		p = multiprocessing.Process(target=(lambda q,file_name : q.put(ocr_image_to_text(file_name,self.ocr_engine,self.language,angle))), args=(q,file_name))
		p.start()
		while(p.is_alive()):
			pass
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
		text,angle = self.ocr("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number-1),self.mode_of_rotation,self.rotation_angle)
		self.put_text_to_buffer(text)
		self.rotate(angle,"{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number-1))
		
			
	@on_thread			
	def scan_and_ocr_repeatedly(self,widget):
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		self.process_breaker = False
		for i in range(0,self.number_of_pages_to_scan):
			t = threading.Thread(target=self.scan)
			t.start()
			while(t.is_alive()):
				pass
			if(self.process_breaker):
				break
			time.sleep(self.time_between_repeated_scanning)	
			if(self.process_breaker):
				break				
			text,angle = self.ocr("{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number-1),mode,angle)	
			self.put_text_to_buffer(text)
			self.rotate(angle,"{0}{1}.png".format(global_var.tmp_dir,self.starting_page_number-1))
			if mode == 1: #Change the mode partial automatic to Manual
				mode = 2
							
			if(self.process_breaker):
				break

	@on_thread
	def optimize_brightness(self,wedget):
		selected_scanner = self.combobox_scanner.get_active()
		self.process_breaker = False
		mode = self.mode_of_rotation
		angle = self.rotation_angle
		if (mode == 0 or mode == 1):
			p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}test.png".format(global_var.tmp_dir),self.scan_resolution,100,self.scan_area))
			p.start()
			while(p.is_alive()):
				pass
			text,angle = self.ocr("{0}test.png".format(global_var.tmp_dir),mode,angle)
			print(angle)		
		mid_value = 100; distance = 10; vary = 50;
		result_text = "<b><span size = 'xx-large'> Result Text </span> </b>" 
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
							
			count, mid_value = self.optimize_with_model(mid_value,distance,vary,angle)
			result_text = "<b><span size = 'xx-large'> Got {} Words at brightness {} </span> </b>".format(count, mid_value)  
			distance = distance / 2;
			vary = vary / 2 ;
			
		
	def optimize_with_model(self,mid_value,distance,vary,angle):
		selected_scanner = self.combobox_scanner.get_active()
		list = []
		pos = mid_value - vary
		while(pos <= mid_value + vary):
			p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan), args=("{0}test.png".format(global_var.tmp_dir,self.starting_page_number),self.scan_resolution,pos,self.scan_area))
			p.start()
			while(p.is_alive()):
				pass
			if(self.process_breaker):
				return
			text = self.ocr_with_multiprocessing("{0}test.png".format(global_var.tmp_dir),angle)
			count = self.count_dict_words(text)
			list.append((text,count,pos))
			pos = pos + distance
			
		list = sorted(list, key=lambda item: item[1],reverse=True)
		return (list[0][1],list[0][2])

	def stop_process(self,widget):
		self.process_breaker = True
		
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
			self.point = self.textbuffer.get_iter_at_offset(pos+self.to_count)
			self.textbuffer.place_cursor(self.point)
			self.textview.scroll_to_iter(self.point, 0.0, use_align=True, xalign=0.0, yalign=0.2)
							
					
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
		
if __name__ == "__main__":
	linux_intelligent_ocr_solution()
