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
import shutil
import enchant
import configparser

from espeak import espeak

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GdkPixbuf


from lios import converter
from lios import scanner
from lios.basic_editor import editor
from lios.basic_editor import spell_check
from lios.basic_editor import find
from lios.basic_editor import find_and_replace

from lios.preferences import lios_preferences
from lios import global_var
from lios.ocr import *

from multiprocessing import Process


Gdk.threads_init()

class linux_intelligent_ocr_solution(editor,lios_preferences):
	def __init__ (self,filename=None):
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(global_var.data_dir))
		self.window = self.guibuilder.get_object("window")
		self.paned = self.guibuilder.get_object("paned")
		self.textview = self.guibuilder.get_object("textview")
		self.image_icon_view = self.guibuilder.get_object("iconview")
		self.combobox_scanner = self.guibuilder.get_object("combobox_scanner")
		self.textbuffer = self.textview.get_buffer();
		self.guibuilder.connect_signals(self)
		

		#Reading Dictionarys		
		self.key_value = {"eng" : "en","afr" : "af","am" : "am","ara" : "ar","ara" : "ar","bul" : "bg","ben" : "bn","br" : "br","cat" : "ca","ces" : "cs","cy" : "cy","dan" : "da","ger" : "de","ger" : "de","ell" : "el","eo" : "eo","spa" : "es","est" : "et","eu" : "eu","fa" : "fa","fin" : "fi","fo" : "fo","fra" : "fr","ga" : "ga","gl" : "gl","gu" : "gu","heb" : "he","hin" : "hi","hrv" : "hr","hsb" : "hsb","hun" : "hu","hy" : "hy","id" : "id","is" : "is","ita" : "it","kk" : "kk","kn" : "kn","ku" : "ku","lit" : "lt","lav" : "lv","mal" : "ml ","mr" : "mr ","dut" : "nl","no" : "no","nr" : "nr","ns" : "ns ","or" : "or ","pa" : "pa ","pol" : "pl ","por" : "pt","por" : "pt","por" : "pt","ron" : "ro","rus" : "ru ","slk" : "sk","slv" : "sl","ss" : "ss","st" : "st","swe" : "sv","tam" : "ta","tel" : "te","tl" : "tl","tn" : "tn","ts" : "ts","ukr" : "uk","uz" : "uz","xh" : "xh","zu" : "zu" }

		#Getting Preferences Values
		self.read_preferences()
		self.activate_preferences()
		
		#Image list store
		self.liststore_images = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.image_icon_view.set_pixbuf_column(0)
		self.image_icon_view.set_text_column(1)
		self.image_icon_view.set_model(self.liststore_images)
		
		#Creating Lios Folder in tmp
		try:
			os.mkdir(global_var.temp_dir)
		except:
			pass

		#Scanner combobox
		renderer_text = Gtk.CellRendererText()
		self.combobox_scanner.pack_start(renderer_text, True)
		self.combobox_scanner.add_attribute(renderer_text, "text", 0)		
		#self.scanner_refresh(None)
		

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

		if (filename):
			 self.textbuffer.set_text(open(filename,"r").read())
			 self.save_file_name = filename
		
		screen = self.window.get_screen()
		print(screen.get_width())
		self.paned.set_position(screen.get_width()-100)

		self.window.maximize();
		
		self.window.show_all()
		Gtk.main();
	
	def scanner_refresh(self,widget):
		scanner_store = Gtk.ListStore(str)
		self.scanner_objects = []
		scanner_list = scanner.scanner.get_devices()
		for device in scanner_list:
			self.scanner_objects.append(scanner.scanner(device))
			scanner_store.append([device[2]])
		self.combobox_scanner.set_model(scanner_store)		
		self.combobox_scanner.set_active(0)
		
	def scan_single_image(self,widget):
		selected_scanner = self.combobox_scanner.get_active()
		self.scanner_objects[selected_scanner].scan("{0}{1}.png".format(global_var.temp_dir,self.starting_page_number),self.scan_resolution,self.scan_brightness,self.scan_area)
		self.add_image_to_image_list("{0}{1}.png".format(global_var.temp_dir,self.starting_page_number))

					
		

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
			destination = "{0}{1}".format(global_var.temp_dir,filename.replace(' ','-'))
			shutil.copyfile(file_name_with_directory,destination)
			self.add_image_to_image_list(destination)
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
			destination = "{0}{1}".format(global_var.temp_dir,pdf_filename.replace(' ','-').replace(')','-').replace('(','-'))		
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
		filter = Gtk.FileFilter()
		filter.set_name("Images")
		for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
			filter.add_pattern(pattern)
		folder.add_filter(filter)
		response = folder.run()
		if response == Gtk.ResponseType.OK:
			image_directory = folder.get_current_folder()
			file_list = os.listdir(image_directory)
			formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm"]
			for image in file_list:
				try:
					if image.split(".")[1] in formats:
						destination = "{0}{1}".format(global_var.temp_dir,image.split(".")[0])
						shutil.copyfile("{0}/{1}".format(image_directory,image),destination)
						self.add_image_to_image_list(destination)						
				except IndexError:
					pass
		folder.destroy()		

		
		
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
			image_read_stop.set_from_file("/usr/share/lios/ui/stop")
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
			image_read_stop.set_from_file("/usr/share/lios/ui/play")
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
			shutil.rmtree(global_var.temp_dir)
		except FileNotFoundError:
			pass
		Gtk.main_quit()
		
if __name__ == "__main__":
	linux_intelligent_ocr_solution()
