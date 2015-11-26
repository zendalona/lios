
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
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
import shutil

from functools import wraps

from lios import scanner, editor, cam, ocr, preferences, speech
from lios.ui.gtk import widget, containers, loop, menu, image_view, \
	window, icon_view, dialog, about

from lios.ui.gtk.file_chooser import FileChooserDialog
from lios import macros
from lios import preferences
from lios import capture_screen
from lios import dictionary
from lios import localization
_ = localization._

import multiprocessing
import threading



def on_thread(function):
	@wraps(function)
	def inner(*args):
		print(function.__name__+" Started")
		#function(*args);
		threading.Thread(target=function,args=args).start()
	return inner


class linux_intelligent_ocr_solution():
	def __init__ (self,file_list=None):
		
		try:
			os.mkdir(macros.tmp_dir)
		except:
			pass
		

		#Icon View
		scroll_box_iconview = containers.ScrollBox()
		self.iconview = icon_view.IconView()
		self.iconview.set_vexpand(True)
		scroll_box_iconview.add(self.iconview)
		box_iconview = containers.Box(containers.Box.VERTICAL)
		toolbar_iconview = containers.Toolbar(containers.Toolbar.HORIZONTAL,
			[(_("Import-Pdf"),self.import_pdf),(_("Import-Image"),self.import_image),
			(_("Import-Folder"),self.import_folder),(_("Recognize"),self.ocr_selected_images),
			(_("Clear"),self.iconview_remove_all_images),])
		#Context menu
		self.context_menu_iconview = menu.ContextMenu([
			(_("Recognize"),self.ocr_selected_images),
			menu.SEPARATOR,
			(_("Rotate-Left"),self.rotate_selected_images_to_left),
			(_("Rotate-Twice"),self.rotate_selected_images_to_twice),
			(_("Rotate-Right"),self.rotate_selected_images_to_right),									
			menu.SEPARATOR, (_("Invert-List"),self.iconview.invert_list), menu.SEPARATOR,
			(_("Save"),self.save_selected_images),
			(_("Export-As-Pdf"),self.save_selected_images_as_pdf),
			menu.SEPARATOR,
			(_("Delete"),self.iconview_remove_selected_images)])
			
		self.iconview.connect_on_selected_callback(self.on_iconview_item_selected)
		self.iconview.connect_button_release_callback(self.iconview_button_release)
		box_iconview.add(toolbar_iconview)
		box_iconview.add(scroll_box_iconview)			

		
		#Image View	
		self.imageview = image_view.ImageViewer()
		self.imageview.set_vexpand(True)
		self.imageview.set_hexpand(True)
		box_imageview = containers.Box(containers.Box.HORIZONTAL)
		toolbar_imageview = containers.Toolbar(containers.Toolbar.VERTICAL,
							[(_("Rotate-Right"),self.open_text),(_("Rotate-Twice"),self.open_text),
						  (_("Rotate-Left"),self.open_text),containers.Toolbar.SEPARATOR,
						  (_("Zoom-In"),self.imageview.zoom_in),(_("Zoom-Fit"),self.imageview.zoom_fit),
						  (_("Zoom-Out"),self.imageview.zoom_out),containers.Toolbar.SEPARATOR,(_("Recognize-Selected-Areas"),self.ocr_selected_areas)]);
		
		box_imageview.add(toolbar_imageview)
		box_imageview.add(self.imageview)
		self.imageview.load_image(macros.logo_file,[],image_view.ImageViewer.ZOOM_FIT)
		
		#Editor
		self.textview = editor.BasicTextView()
		self.textview.set_vexpand(True)
		self.textview.set_hexpand(True)		
		box_editor = containers.Box(containers.Box.HORIZONTAL)
		toolbar_editor = containers.Toolbar(containers.Toolbar.VERTICAL,
			[(_("New"),self.textview.new),('Open',self.textview.open),
			(_("Save"),self.textview.save),containers.Toolbar.SEPARATOR,
			(_("Spell-Check"),self.textview.open_spell_check),containers.Toolbar.SEPARATOR,
			(_("Undo"),self.textview.undo),(_("Redo"),self.textview.redo),
			containers.Toolbar.SEPARATOR,
			(_("Find"),self.textview.open_find_dialog),
			(_("Find-Replace"),self.textview.open_find_and_replace_dialog),
			containers.Toolbar.SEPARATOR,(_("Go-To-Line"),self.textview.go_to_line),
			(_("Go-To-Page"),self.open_text),containers.Toolbar.SEPARATOR,
			(_("Read"),self.start_reading),(_("Stop"),self.stop_reading),
			])
		box_editor.add(toolbar_editor)
		scroll_box_editor = containers.ScrollBox()
		scroll_box_editor.add(self.textview)
		box_editor.add(scroll_box_editor)		

		#OCR Engine
		self.available_ocr_engine_list = ocr.get_available_engines()
		
		#Scanner Drivers
		self.available_scanner_driver_list = scanner.get_available_drivers()
		self.scanner_objects = []
		
		#Load Preferences
		self.preferences = preferences.lios_preferences()
		self.preferences.set_from_file("{}/.lios_preferences.cfg".format(macros.home_dir))
		self.preferences.set_avalable_scanner_drivers([ item.name for item in self.available_scanner_driver_list])
		self.preferences.set_avalable_ocr_engines([ (item.name,item.get_available_languages())
												for item in self.available_ocr_engine_list ])
		


		
		menubar = menu.MenuBar(
		[[_("File"),(_("New"),self.textview.new,"<Control>N"),menu.SEPARATOR,
				 (_("Import-Image"),self.import_image,"<Control>I"),(_("Import-Pdf"),self.import_pdf,"None"),
				 (_("Import-Folder"),self.import_folder,"None"),menu.SEPARATOR,
				 (_("Open"),self.open_text,"<Control>O"),		
				 (_("Save"),self.open_text,"<Control>S"),(_("Save-As"),self.open_text,"<Shift><Control>N"),
				 (_("Export-As-Pdf"),self.open_text,"<Control>E"),(_("Print"),self.open_text,"<Control>P"),
				 (_("Print-Preview"),self.open_text,"None"),menu.SEPARATOR,
				 (_("Quit"),self.quit,"<Control>Q")],
		[_("Edit"),(_("Undo"),self.textview.undo,"<Control>Z"),(_("Redo"),self.textview.redo,"<Control>Y"),
				menu.SEPARATOR,(_("Cut"),self.open_text,"<Control>X"),
				(_("Copy"),self.open_text,"<Control>C"),(_("Paste"),self.open_text,"<Control>V"),
				(_("Delete"),self.open_text,"<Control>D"),menu.SEPARATOR,
				(_("Punch-Text"),self.open_text,"None"),(_("Append-Text"),self.open_text,"None"),
				menu.SEPARATOR,(_("Find"),self.open_text,"<Control>F"),
				(_("Find-Replace"),self.open_text,"<Control>R"),menu.SEPARATOR,
				(_("Go-To-Line"),self.open_text,"<Control>L"),(_("Go-To-Page"),self.open_text,"<Control>G"),
				menu.SEPARATOR,(_("Preferences"),self.open_preferences_general_page,"None")],
		[_("Image"),[_("Rotate-Left"),(_("Current"),self.open_text,"None"),
								(_("Selected"),self.rotate_selected_images_to_left,"None"),
								(_("All"),self.rotate_all_images_to_left,"None")],
				 [_("Rotate-Twice"),(_("Current"),self.open_text,"None"),
								(_("Selected"),self.rotate_selected_images_to_twice,"None"),
								(_("All"),self.rotate_all_images_to_twice,"None")],
				 [_("Rotate-Right"),(_("Current"),self.open_text,"None"),
								(_("Selected"),self.rotate_selected_images_to_right,"None"),
								(_("All"),self.rotate_all_images_to_right,"None")],											
				 menu.SEPARATOR, (_("Invert-List"),self.iconview.invert_list,"None"), menu.SEPARATOR,
				 [_("Save"),(_("Selected-Images"),self.save_selected_images,"None"),(_("All-Images"),self.save_all_images,"None")],
				 [_("Export-As-Pdf"),(_("Selected-Images"),self.save_selected_images_as_pdf,"None"),(_("All-Images"),self.save_all_images_as_pdf,"None")], menu.SEPARATOR,
				 [_("Delete"),(_("Selected-Images"),self.iconview_remove_selected_images,"None"),(_("All-Images"),self.iconview_remove_all_images,"None")],],
		[_("Scan"),(_("Scan-Image"),self.scan_single_image,"F8"),(_("Scan-Image-Repeatedly"),self.scan_image_repeatedly,"<Control>F8"),
				(_("Scan-and-Ocr"),self.scan_and_ocr,"F9"),(_("Scan-and-Ocr-Repeatedly"),self.scan_and_ocr_repeatedly,"<Control>F9"),
				(_("Optimise-Scanner-Brightness"),self.optimize_brightness,"None"),menu.SEPARATOR,
				(_("Scan-Using-Webcam"),self.scan_using_cam,"F6"),menu.SEPARATOR,
				[_("Take-Screenshort"),(_("Selection"),self.take_rectangle_screenshot,"<Control>F6"),(_("Full"),self.take_full_screenshot,"F6")],
				[_("Take-and-Recognize-Screenshort"),(_("Selection"),self.open_text,"<Control>F10"),(_("Full"),self.open_text,"F10")]],
		[_("Recognize"),(_("Recognize-Selected-Areas"),self.ocr_selected_areas,"None"),(_("Recognize-Selected-Images"),self.ocr_selected_images,"None"),(_("Recognize-All-Images"),self.open_text,"None"),
				(_("Recognize-Selected-with-rotation"),self.ocr_selected_images_with_rotation,"None"),(_("Recognize-All-with-rotation"),self.open_text,"None")],
		[_("Tools"),(_("Spell-Check"),self.open_text,"<Control>F7"),
				(_("Audio-Converter"),self.textview.audio_converter,"None"),
				(_("Dictionary"),self.artha,"<Control><Alt>W")],
		[_("Preferences"),(_("Preferences-General"),self.open_preferences_general_page,"None"),
			(_("Preferences-Recognition"),self.open_preferences_recognition_page,"None"),
				(_("Preferences-Scanning"),self.open_preferences_scanning_page,"None"),
				menu.SEPARATOR,	(_("Save"),self.save_preferences,"None"),
				(_("Load"),self.load_preferences,"None"),(_("Restore"),self.restore_preferences,"None")],
		[_("Help"),(_("Open-Readme"),self.open_readme,"None"),(_("Video-Tutorial"),self.open_text,"None"),
				menu.SEPARATOR,(_("About"),self.about,"None")]])
		menubar.show()

		
		self.combobox_scanners = widget.ComboBox()
		button_update_scanner_list = widget.Button("Refresh-Scanner-List")
		button_update_scanner_list.connect_function(self.scanner_refresh)
		button_scan = widget.Button("Scan")
		button_scan.connect_function(self.scan_single_image)		
		toolbar_main = containers.Toolbar(containers.Toolbar.HORIZONTAL,
						[(_("Take-Screenshort"),self.take_rectangle_screenshot),(_("Scan-Using-Webcam"),self.scan_using_cam),
						(_("Preferences"),self.open_preferences_general_page),(_("About"),self.about),
						(_("Quit"),self.quit)	])		
				
		
		#Slide Panes
		self.paned_image_text = containers.Paned(containers.Paned.VERTICAL)
		self.paned_image_text.add1(box_imageview)
		self.paned_image_text.add2(box_editor)

		self.paned_main = containers.Paned(containers.Paned.HORIZONTAL)
		self.paned_main.add1(box_iconview)
		self.paned_main.add2(self.paned_image_text)	
		
		self.statusbar = widget.Statusbar() 
		self.progressbar = widget.ProgressBar() 

		self.window = window.Window(macros.app_name)
		grid_main = containers.Grid()
		grid_main.add_widgets([
			(menubar,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
			(self.combobox_scanners,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_END),
			(button_update_scanner_list,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_END),
			(button_scan,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_END),
			(toolbar_main,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_END),
			containers.Grid.NEW_ROW,
			(self.paned_main,5,1),
			containers.Grid.NEW_ROW,
			(self.statusbar,4,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
			(self.progressbar,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),])

		

				 
		text_updated = False
		if(file_list):
			for item in file_list:
				if item.split('.')[-1] in macros.supported_image_formats:
					filename = item.split("/")[-1:][0]
					destination = "{0}{1}".format(macros.tmp_dir,filename.replace(' ','-'))
					destination = self.get_feesible_filename_from_filename(destination)
					self.add_image_to_list(item,destination,False)

				if item.split('.')[-1] in ["pdf","Pdf"]:
					self.import_images_from_pdf(item)
			
				if item.split('.')[-1] in macros.supported_text_formats:
					text = open(item).read()
					self.insert_text_to_textview(text)
					text_updated = True
		if (not text_updated):
			try:
				file = open("{}/.lios_recent".format(macros.home_dir),encoding="utf-8")
				self.textview.set_text(file.read())
			except:
				pass
		
		
		self.old_language = -1
		self.old_scan_driver = -1
		#This will clear scanner combobox
		#so scanner combobox should be inetialised
		self.make_preferences_effective()

		#For connecting menubar accell group Gtk
		self.window.connect_menubar(menubar)
		
		self.window.connect_configure_event_handler(self.window_reconfigure)
		grid_main.show_all()
		self.window.add(grid_main)
		self.window.maximize()
		self.window.show()
		loop.start_main_loop()	
	
	def iconview_button_release(self,*data):
		if (self.iconview.get_selected_item_names() == []):
			self.iconview.select_all()
		if (self.iconview.get_selected_item_names() != []):
			self.context_menu_iconview.popup(None, None, None, None,0,0)
			self.context_menu_iconview.show_all()
		
	def textview_button_release(self,*data):
		self.context_menu_iconview.popup(None, None, None, None,0,0)
		self.context_menu_iconview.show_all()
	def imageview_button_release(self,*data):
		self.context_menu_iconview.popup(None, None, None, None,0,0)
		self.context_menu_iconview.show_all()
		
	def window_reconfigure(self,*arg):
		width,height = self.window.get_size()
		self.paned_image_text.set_position(height/2)
		self.paned_main.set_position(200)
		self.imageview.set_position(width-500)
		
		
	def get_feesible_filename_from_filename(self,filename):
		if (os.path.exists(filename)):
			return self.get_feesible_filename_from_filename(filename.replace('.','#.'))
		else:
			return filename 

	def add_image_to_list(self,file_name_with_directory,destination,move,lock=False):
		if (move):
			shutil.move(file_name_with_directory,destination)
		else:
			shutil.copyfile(file_name_with_directory,destination)
		
		self.iconview.add_item(destination)

	def import_image(self,wedget,data=None):
		file_chooser_open_image = FileChooserDialog(_("Select image file to import"),
				FileChooserDialog.OPEN,macros.supported_image_formats,macros.home_dir)		
		file_chooser_open_image.set_select_multiple(True)
		response = file_chooser_open_image.run()
		if response == FileChooserDialog.ACCEPT:
			for file_name_with_directory in file_chooser_open_image.get_filenames():
				filename = file_name_with_directory.split("/")[-1:][0]
				destination = "{0}{1}".format(macros.tmp_dir,filename.replace(' ','-'))
				destination = self.get_feesible_filename_from_filename(destination)
				self.add_image_to_list(file_name_with_directory,destination,False)
		file_chooser_open_image.destroy()

	def import_pdf(self,*data):
		open_file = FileChooserDialog(_("Select Pdf file to import"),
				FileChooserDialog.OPEN,["pdf","Pdf"],macros.home_dir)
		open_file.set_current_folder(macros.home_dir)
		response = open_file.run()
		if response == FileChooserDialog.ACCEPT:
			pdf_filename_full = open_file.get_filename()
			self.import_images_from_pdf(pdf_filename_full)
			open_file.destroy()
	
	@on_thread
	def import_images_from_pdf(self,pdf_filename_full):
#		self.make_image_widgets_inactive(lock=True)
		pdf_filename = pdf_filename_full.split("/")[-1:][0]
		filename = pdf_filename.split(".")[0]
		pdf_filename = pdf_filename.replace(' ','-').replace(')','-').replace('(','-')
		destination = "{0}{1}".format(macros.tmp_dir,pdf_filename)		
		shutil.copyfile(pdf_filename_full,destination)
		os.makedirs(destination.split(".")[0],exist_ok=True)
		
#		self.set_progress_bar("Extracting images from Pdf",None,0.001,lock=True)
#		self.announce(_("Extracting images from Pdf please wait!"))
		
		p = multiprocessing.Process(target=lambda : os.system("pdfimages {} {}/{}"
		.format(destination,destination.split(".")[0],pdf_filename.split(".")[0])) , args=())
		
		p.start()
		while(p.is_alive()):
			pass
		os.remove(destination)
		
		file_list = os.listdir(destination.split(".")[0])
		file_list = sorted(file_list)
						
		for image in file_list:
			if(len(image.split("."))>1):
				if (image.split(".")[1] in macros.supported_image_formats):
					filename = "{}{}".format(macros.tmp_dir,image)
					filename = self.get_feesible_filename_from_filename(filename)
					self.add_image_to_list("{}/{}".format(destination.split(".")[0],image),filename,True)
		os.rmdir(destination.split(".")[0])
#		self.set_progress_bar("Completed!",None,0.01,lock=True)
#		self.announce("Images imported!")
#		self.make_image_widgets_active(lock=True)		
	
	def import_folder(self,wedget,data=None):
		#self.make_image_widgets_inactive()
		folder = FileChooserDialog(_("Select Folder contains images to import"),
			FileChooserDialog.OPEN_FOLDER,macros.supported_image_formats,macros.home_dir)		
		response = folder.run()
		if response == FileChooserDialog.ACCEPT:
			image_directory = folder.get_current_folder()
			folder.destroy()
			file_list = os.listdir(image_directory)
			#progress_step = len(file_list)/(10^len(file_list));progress = 0;			
			for image in sorted(file_list):
				try:
					if image.split(".")[-1] in macros.supported_image_formats:
						destination = "{0}{1}".format(macros.tmp_dir,image.replace(' ','-'))
						#self.set_progress_bar("Importing image {}".format(destination),progress,None,lock=False)
						destination = self.get_feesible_filename_from_filename(destination)
						self.add_image_to_list("{0}/{1}".format(image_directory,image),destination,False)					
				except IndexError:
					pass
				#progress = progress + progress_step;
			self.set_progress_bar(_("Completed!"),None,0.01,lock=False)
			#self.announce("Images imported!")		
		#self.make_image_widgets_active()

	@on_thread	#should continue the loop to get window minimize 
	def take_full_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		os.system("sleep 1") #Time to minimize lios window
		capture_screen.capture_entire_screen(destination)
		self.window.set_keep_above(True)
		self.iconview.add_item(destination)
		self.preferences.update_page_number()

	@on_thread
	def take_rectangle_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		capture_screen.capture_rectangle_selection(destination)
		self.iconview.add_item(destination)
		self.window.set_keep_above(True)
		self.preferences.update_page_number()
		

	def on_iconview_item_selected(self,data):
		name = self.iconview.get_selected_item_names()
		if(name):
			self.imageview.load_image(name[0],[],image_view.ImageViewer.ZOOM_FIT)
		else:
			self.imageview.load_image(macros.logo_file,[],image_view.ImageViewer.ZOOM_FIT)


	@on_thread
	def scanner_refresh(self,*data):
		self.combobox_scanners.clear()
		for item in self.scanner_objects:
			item.close()
			
		#scanner.scanner.exit()
		#scanner_store = Gtk.ListStore(str)
		self.scanner_objects = []
		
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_scanner_widgets_inactive(lock=True)
		
		#self.set_progress_bar(_("Geting devices"),None,0.001,lock=True)
		#self.announce(_("Getting devices"))
		#Tuple - List Convertion is used to get all items in devices list
		
		
		parent_conn, child_conn = multiprocessing.Pipe()
		p = multiprocessing.Process(target=(lambda parent_conn, child_conn :
		child_conn.send(tuple(self.available_scanner_driver_list[self.preferences.scan_driver].get_available_devices()))),
		args=(parent_conn, child_conn))
		
		p.start()
		while(p.is_alive()):
			pass
		
		
		driver = self.available_scanner_driver_list[self.preferences.scan_driver]
		list_ = list(parent_conn.recv())
		for device in list_:
			#self.set_progress_bar(_("Setting Scanner {}").format(device),None,0.0030,lock=True)			
			scanner = driver(device,self.preferences.scan_resolution,self.preferences.scan_brightness,self.preferences.scan_area)
			if (self.preferences.scanner_mode_switching):
				for mode in scanner.get_available_scan_modes():
					if mode == "Lineart":
						scanner.set_scan_mode(mode)
					if mode == "Binary":
						scanner.set_scan_mode(mode)

			self.scanner_objects.append(scanner)
			self.combobox_scanners.add_item(scanner.device_name)
		print(self.scanner_objects)

		loop.acquire_lock()	
		#self.combobox_scanner.set_model(scanner_store)		
		
		if (len(self.scanner_objects) != 0):
			self.combobox_scanners.set_active(0)
			#self.make_scanner_widgets_active(lock=True)
			#self.set_progress_bar(_("Completed!"),None,0.01,lock=True)
		else:
			#self.button_refresh.set_sensitive(True)
			#self.spinner.set_state(False)
			#self.spinner.hide()
			#self.announce(_("No Scanner Detected!"))
			#self.set_progress_bar(_("No Scanner Detected!"),None,0.01,lock=True)
			pass
		#self.make_preferences_widgets_active(lock=True)
		loop.release_lock()

	@on_thread
	def scan_single_image(self,widget):
		#self.make_scanner_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		destination = "{0}{1}.pnm".format(macros.tmp_dir,self.preferences.get_page_number_as_string())
		destination = self.get_feesible_filename_from_filename(destination)
		t = threading.Thread(target=self.scan,args=(destination,))
		t.start()
		while(t.is_alive()):
			pass
		self.preferences.update_page_number()
		#self.make_scanner_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)


	@on_thread
	def scan_image_repeatedly(self,widget):
		#self.make_scanner_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.process_breaker = False
		for i in range(0,self.preferences.number_of_pages_to_scan):
			destination = "{0}{1}.pnm".format(macros.tmp_dir,self.preferences.get_page_number_as_string())
			destination = self.get_feesible_filename_from_filename(destination)
			t = threading.Thread(target=self.scan,args=(destination,))
			t.start()
			while(t.is_alive()):
				pass
			self.preferences.update_page_number()
			if(self.process_breaker):
				break
			time.sleep(self.preferences.time_between_repeated_scanning)
			if(self.process_breaker):
				break
		#self.announce(_("Job completed!"))
		#self.make_scanner_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)

	def scan(self,filename):
		selected_scanner = self.combobox_scanners.get_active()
		#self.announce(_("Scanning!"))

		#self.set_progress_bar(_("Scanning {} with resolution={} brightness={}")
		#.format(filename,self.preferences.scan_resolution,self.preferences.scan_brightness),None,0.0030,lock=True)
		
		p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan),
		args=(filename,self.preferences.scan_resolution,
		self.preferences.scan_brightness,self.preferences.scan_area))
		
		p.start()
		while(p.is_alive()):
			pass
		#self.set_progress_bar(_("Scan Completed!"),None,0.01,lock=True)
			
		#if(self.process_breaker):
		#	return
		print(_("Adding image to list"))			
		self.iconview.add_item(filename)
		
		print(_("Image added"))
		#if(self.process_breaker):
		#	return
		


	############## OCR ################################
	def ocr(self,file_name,mode,angle):
		self.process_breaker = False

		ocr_engine_object = self.available_ocr_engine_list[self.preferences.ocr_engine]()
		languages_available = self.available_ocr_engine_list[self.preferences.ocr_engine].get_available_languages()
		
		language = languages_available[self.preferences.language]
		ocr_engine_object.set_language(language)
		
		print(language)
		
		if mode == 2:	#Manual
			os.system("convert -rotate {0} {1} {1}".format(angle,file_name))
			text = ocr_engine_object.ocr_image_to_text_with_multiprocessing(file_name)
			return (text,angle)
		else: #Full_Automatic or Partial_Automatic
			list_ = []
			for angle in [00,270,180,90]:
				os.system("convert -rotate {0} {1} {1}".format(angle,file_name))
				text = ocr_engine_object.ocr_image_to_text_with_multiprocessing(file_name)
				count = self.count_dict_words(text)
				list_.append((text,count,angle))
				if(self.process_breaker):
					return True;
			list_ = sorted(list_, key=lambda item: item[1],reverse=True)
		return (list_[0][0],list_[0][2])
				
	
	def count_dict_words(self,text):
		count = 0
		for word in text.split(" "):
			if (len(word) > 1):
				if (self.dict.check(word) == True):
					count += 1
		return count
		
	############## OCR  END ################################

	def insert_text_to_textview(self,text,place_cursor = False,give_page_number = False):
		loop.acquire_lock()
		if (give_page_number):
			text = "\nPage-{}\n{}".format(self.preferences.get_page_number_as_string(),text)
		self.textview.insert_text(text,self.preferences.insert_position)
		text = self.textview.get_text()
		loop.release_lock()
		with open("{}/.lios_recent".format(macros.home_dir),"w",encoding="utf-8") as file:
			file.write(text)
	
	@on_thread	
	def scan_and_ocr(self,widget):
		#self.make_scanner_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_ocr_widgets_inactive(lock=True)
		self.process_breaker = False
		destination = "{0}{1}.pnm".format(macros.tmp_dir,self.preferences.get_page_number_as_string())
		destination = self.get_feesible_filename_from_filename(destination)
		t = threading.Thread(target=self.scan,args=(destination,))
		t.start()
		while(t.is_alive()):
			pass
		if(self.process_breaker):
			#self.make_scanner_widgets_active(lock=True)
			#self.make_ocr_widgets_active(lock=True)
			#self.make_preferences_widgets_active(lock=True)
			return			
		text,angle = self.ocr(destination,self.preferences.mode_of_rotation,self.preferences.rotation_angle)
		self.insert_text_to_textview(text,self.preferences.insert_position)
		#self.rotate(angle,destination,False)
		#self.announce(_("Page {}").format(self.preferences.get_page_number_as_string()))
		self.preferences.update_page_number()
		#self.make_scanner_widgets_active(lock=True)
		#self.make_ocr_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)

		
			
	@on_thread			
	def scan_and_ocr_repeatedly(self,widget):
		#self.make_scanner_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_ocr_widgets_inactive(lock=True)
		mode = self.preferences.mode_of_rotation
		angle = self.preferences.rotation_angle
		self.process_breaker = False
		for i in range(0,self.preferences.number_of_pages_to_scan):
			destination = "{0}{1}.pnm".format(macros.tmp_dir,self.preferences.get_page_number_as_string())
			destination = self.get_feesible_filename_from_filename(destination)
			t = threading.Thread(target=self.scan,args=(destination,))
			t.start()
			while(t.is_alive()):
				pass
			if(self.process_breaker):
				break
			time.sleep(self.preferences.time_between_repeated_scanning)	
			if(self.process_breaker):
				break
			text,angle = self.ocr(destination,mode,angle)	
			print(_("Placing text and cursor"))
			if (i == 0):
				self.insert_text_to_textview(text,True,True)
			else:
				self.insert_text_to_textview(text,False,True)
			#self.announce(_("Page {}".format(self.preferences.get_page_number_as_string()))
			print(_("Rotating image"))	
			self.rotate(angle,destination,False)
			self.preferences.update_page_number()
			
			if mode == 1: #Change the mode partial automatic to Manual
				mode = 2
				#self.announce(_("Angle to be rotated = {}").format(angle))
							
			if(self.process_breaker):
				break
			print(_("Compleated "),i);
		#self.announce(_("Job completed!")
		#self.make_scanner_widgets_active(lock=True)
		#self.make_ocr_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)


		
		


	@on_thread
	def optimize_brightness(self,wedget):
		#self.make_scanner_widgets_inactive(lock=True)
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)

		selected_scanner = self.combobox_scanners.get_active()
		self.process_breaker = False
		mode = self.preferences.mode_of_rotation
		angle = self.preferences.rotation_angle
		if (mode == 0 or mode == 1):
			#self.set_progress_bar(_("Scanning with resolution={} brightness={}")
			#.format(self.preferences.scan_resolution,100),None,0.0030,lock=True)
			
			p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan),
			args=("{0}test.pnm".format(macros.tmp_dir),self.preferences.scan_resolution,100,self.preferences.scan_area))
			
			p.start()
			while(p.is_alive()):
				pass
			text,angle = self.ocr("{0}test.pnm".format(macros.tmp_dir),mode,angle)
			print(angle)		
		mid_value = 100; distance = 10; vary = 50;
		count = None
		result_text = "<b>Click 'Forward' to start optimisation </b>" 
		while(1):
			loop.acquire_lock()
			dlg = dialog.Dialog(_("Optimize Brightness"),
				(_("Cancel"), dialog.Dialog.BUTTON_ID_1,
				_("Apply"), dialog.Dialog.BUTTON_ID_2,
				_("Forward"), dialog.Dialog.BUTTON_ID_3))
						
			label_value = widget.Label(_("Value"))
			spinbutton_value = widget.SpinButton(mid_value,0,200,1,5,0)
			
			label_distance = widget.Label(_("Distance"))
			spinbutton_distance = widget.SpinButton(distance,0,40,10,5,0)
			
			label_vary = widget.Label(_("Vary"))
			spinbutton_vary = widget.SpinButton(vary,0,100,10,5,0)
			
			label_result = widget.Label(_("Result"))
			label_result.set_use_markup(True)
			label_result.set_label(result_text)
			
			grid = containers.Grid()
			grid.add_widgets([(label_value,1,1),(spinbutton_value,1,1),containers.Grid.NEW_ROW,
				(label_distance,1,1),(spinbutton_distance,1,1),containers.Grid.NEW_ROW,
				(label_vary,1,1),(spinbutton_vary,1,1),containers.Grid.NEW_ROW,
				(label_result,2,1)]);
			dlg.add_widget(grid)
			grid.show_all()
			
			response = dlg.run()
			dlg.destroy()
			loop.release_lock()				
			if (response == dialog.Dialog.BUTTON_ID_2):
				self.preferences.scan_brightness = mid_value
				#self.make_scanner_widgets_active(lock=True)
				#self.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)				
				return True
			elif (response == dialog.Dialog.BUTTON_ID_3):
				mid_value = spinbutton_value.get_value()
				distance = spinbutton_distance.get_value()
				vary = spinbutton_vary.get_value()
				self.preferences.scan_brightness = mid_value
			else:
				#self.make_scanner_widgets_active(lock=True)
				#elf.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)
				return True
							
			list = self.optimize_with_model(mid_value,distance,vary,angle,count)
			if (not list):
				#self.make_scanner_widgets_active(lock=True)
				#self.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)
				return True
			count, mid_value = list[0][0],list[0][1];
			result_text = "<b>Optimisation Result "
			for item in list:
				result_text += "\nGot {} Words at brightness {}".format(item[0], item[1])
			result_text += "</b>" 
			distance = distance / 2;
			vary = distance;
			
			
		
	def optimize_with_model(self,mid_value,distance,vary,angle,previous_optimised_count=None):
		selected_scanner = self.combobox_scanners.get_active()
		list = []
		count = -1		
		pos = mid_value - vary
		while(pos <= mid_value + vary):
			if (pos == mid_value and previous_optimised_count != None):
				list.append((mid_value,previous_optimised_count))
				#self.announce(_("Got {} words at brightness {}.").format(previous_optimised_count,mid_value))
			else:
				#if (count != -1):
				#	self.set_progress_bar(_("Got {} words at brightness {}. Scanning with resolution={} brightness={}")
				#	.format(count,pos-distance,self.preferences.scan_resolution,pos),None,0.0030,lock=True)
				#else:
				#	self.set_progress_bar(_("Scanning with resolution={} brightness={}")
				#	.format(self.preferences.scan_resolution,pos),None,0.0030,lock=True)
				
				p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan),
				args=("{0}test.pnm".format(macros.tmp_dir,self.preferences.get_page_number_as_string()),
				self.preferences.scan_resolution,pos,self.preferences.scan_area))
				
				p.start()
				while(p.is_alive()):
					pass
				if(self.process_breaker):
					list = sorted(list, key=lambda item: item[0],reverse=True)
					return (list)
				text,angle = self.ocr("{0}test.pnm".format(macros.tmp_dir),2,angle)
				count = self.count_dict_words(text)
				list.append((count,pos))
				#self.announce(_("Got {} words at brightness {}.".format(count,pos)))
			pos = pos + distance
		list = sorted(list, key=lambda item: item[0],reverse=True)
		return (list)

	def stop_process(self,widget):
		self.process_breaker = True
		os.system('killall tesseract');
		os.system('killall cuneiform')

	def open_readme(self,widget,data=None):
		with open(macros.readme_file) as file:
			self.textview.set_text(file.read())


	@on_thread			
	def ocr_selected_images_with_rotation(self,widget):
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_image_widgets_inactive(lock=True)
		#progress_step = 1/len(self.iconview.get_selected_item_names())
		#progress = 0;
		mode = self.preferences.mode_of_rotation
		angle = self.preferences.rotation_angle
		for item in reversed(self.iconview.get_selected_item_names()):
			#self.set_progress_bar(_("Running OCR on selected image {}")
			#.format(self.liststore_images[item[0]][1]),progress,None,lock=True)
			
			#self.announce(_("Recognising {}").format(self.liststore_images[item[0]][1]))
			#progress = progress + progress_step;			
			text,angle = self.ocr(item,mode,angle)
			self.insert_text_to_textview(text,self.preferences.insert_position)
			#self.insert_text_to_textview(text,False,False)
			#self.rotate(angle,self.liststore_images[item[0]][1],False)
			if mode == 1:#Changing partial automatic to Manual
				mode = 2
				#self.announce(_("Angle to be rotated = {}").format(angle))
			if(self.process_breaker):
				break
		#self.make_ocr_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)
		#self.make_image_widgets_active(lock=True)
				
	def ocr_all_images_with_rotation(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images(None)


	@on_thread
	def ocr_selected_images(self,widget):
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_image_widgets_inactive(lock=True)
		#progress_step = 1/len(self.iconview.get_selected_item_names())
		#progress = 0;
		for item in reversed(self.iconview.get_selected_item_names()):
			#self.set_progress_bar(_("Running OCR on selected image {} (without rotating)")
			#.format(self.liststore_images[item[0]][1]),progress,None,lock=True)
			
			#self.announce(_("Recognising {} without rotating").format(self.liststore_images[item[0]][1]))
			#progress = progress + progress_step;
			text,angle = self.ocr(item,2,00)
			self.insert_text_to_textview(text,self.preferences.insert_position)
			if(self.process_breaker):
				break
		#self.set_progress_bar(_("completed!"),None,0.01,lock=True)
		#self.announce(_("Completed!"))
		#self.make_ocr_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)
		#self.make_image_widgets_active(lock=True)
			
	def ocr_all_images(self,widget):
		self.image_icon_view.select_all()
		self.ocr_selected_images_without_rotating(self)


	def iconview_remove_all_images(self,widget):
		self.iconview.select_all_items()
		self.iconview_remove_selected_images()

	def iconview_remove_selected_images(self,*data):
		if (len(self.iconview.get_selected_item_names()) >= 1):
			dlg = dialog.Dialog(_("Deleting !"),(_("Cancel"),dialog.Dialog.BUTTON_ID_1,_("Yes Delete"), dialog.Dialog.BUTTON_ID_2))
			label = widget.Label(_("Are you sure you want to delete selected images ?"))
			dlg.add_widget(label)
			label.show()
			response = dlg.run()
			dlg.destroy()
			if (response == dialog.Dialog.BUTTON_ID_2):
				self.iconview.remove_selected_items()
				
				#self.drawingarea_load_image("{0}/ui/lios".format(macros.data_dir))

	@on_thread
	def rotate_selected_images_to_angle(self,angle):
		#progress_step = 1/len(self.iconview.get_selected_item_names())
		#progress = 0;
		for item in reversed(self.iconview.get_selected_item_names()):
			os.system("convert -rotate {0} {1} {1}".format(angle,item))
			#pb = GdkPixbuf.Pixbuf.new_from_file(self.liststore_images[item[0]][1])
			#pb = pb.rotate_simple(angle)
			#save_format = self.liststore_images[item[0]][1].split(".")[-1]
			#if save_format not in self.writable_format:
			#	save_format = 'png'
			#pb.savev(self.liststore_images[item[0]][1], save_format,[],[])
			self.iconview.reload_preview(item)			
			#self.set_progress_bar("Rotating selected image {} to {}"
			#.format(self.liststore_images[item[0]][1],angle),progress,None,lock=True)
			
			#progress = progress + progress_step;
		#self.imageview.redraw()
		#self.set_progress_bar("completed!",None,0.01,lock=True)

	def rotate_selected_images_to_right(self,widget):
		self.rotate_selected_images_to_angle(90)

	def rotate_selected_images_to_left(self,widget):
		self.rotate_selected_images_to_angle(270)	

	def rotate_selected_images_to_twice(self,widget):
		self.rotate_selected_images_to_angle(180)


	def rotate_all_images_to_right(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_right(None)

	def rotate_all_images_to_left(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_left(None)

	def rotate_all_images_to_twice(self,widget):
		self.image_icon_view.select_all()
		self.rotate_selected_images_to_twice(None)


	def save_selected_images(self,widget):
		dlg = FileChooserDialog(_("Select Folder to save images"),
			FileChooserDialog.OPEN_FOLDER,macros.supported_image_formats,
			macros.home_dir);
		
		response = dlg.run()
		if response == FileChooserDialog.ACCEPT:
			directory = dlg.get_current_folder()
			for item in reversed(self.iconview.get_selected_item_names()):
				shutil.copy(item,directory)
		dlg.destroy()			


	def save_all_images(self,widget):
		self.iconview.select_all()
		self.save_selected_images(None)
		
	def save_selected_images_as_pdf(self,widget):
		dlg = FileChooserDialog(_("Give pdf filename(with extention) to save images"),
			FileChooserDialog.SAVE,macros.supported_pdf_formats,macros.home_dir)
		response = dlg.run()
		if response == FileChooserDialog.ACCEPT:
			file_name = dlg.get_filename()
			command = "convert " 
			for item in reversed(self.iconview.get_selected_item_names()):
				command += item + " "
			command += file_name
			os.system(command)
		dlg.destroy()

	def save_all_images_as_pdf(self,widget):
		self.iconview.select_all()
		self.save_selected_images_as_pdf(None)

	@on_thread			
	def ocr_selected_areas(self,widget):
		self.process_breaker = False
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_image_widgets_inactive(lock=True)
		#progress_step = 1/len(self.imageview.get_selection_list());
		#progress = 0;
		for item in self.imageview.get_selection_list():
			#self.set_progress_bar(_("Running OCR on selected Area [ X={} Y={} Width={} Height={} ]")
			#.format(item[0],item[1],item[2],item[3]),progress,None,lock=True)
			
			#progress = progress + progress_step;
			self.imageview.save_sub_image("{0}tmp".format(macros.tmp_dir),
				item[0],item[1],item[2],item[3])
			
			#Will always be Manual with no rotation
			text,angle = self.ocr("{0}tmp".format(macros.tmp_dir),2,00)
			self.insert_text_to_textview(text,False,False)
			if(self.process_breaker):
				break;

		#self.set_progress_bar(_("completed!"),None,0.01,lock=True)
		#self.make_preferences_widgets_active(lock=True)
		#self.make_ocr_widgets_active(lock=True)
		#self.make_image_widgets_active(lock=True)


	def make_preferences_effective(self,*data):
		if (self.old_language != self.preferences.language):
			languages = self.available_ocr_engine_list[self.preferences.ocr_engine].get_available_languages()
			self.old_language = self.preferences.language
			try:
				self.dict = dictionary.Dict(dictionary.dictionary_language_dict[languages[self.preferences.language]])
			except:
				self.dict = dictionary.Dict("en")
				dlg = dialog.Dialog(_("Dict not found!"), (_("Ok"),dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_("Please install the aspell dict for your ") +
				"language({0}) and restart Lios.\n Otherwise spellchecker will".format(languages[self.preferences.language]) + 
				"be disabled and auto-rotation will work with english(fallback) ")
				dlg.add_widget(label)
				label.show()
				dlg.run()
				dlg.destroy()				
				
		if (self.old_scan_driver != self.preferences.scan_driver):
			self.old_scan_driver = self.preferences.scan_driver
			self.scanner_refresh()
		
		self.textview.set_dictionary(self.dict)
		self.textview.set_font_color(self.preferences.font_color)
		self.textview.set_background_color(self.preferences.background_color)
		self.textview.set_font(self.preferences.font)
		self.textview.set_highlight_font(self.preferences.highlight_font)
		self.textview.set_highlight_color(self.preferences.highlight_color)
		self.textview.set_highlight_background(self.preferences.background_highlight_color)
				
	def save_preferences(self,*data):
		save_preferences_dlg = FileChooserDialog(_("save_preferences as "),
		FileChooserDialog.SAVE,["cfg"],macros.home_dir)
		response = save_preferences_dlg.run()		
		if response == FileChooserDialog.ACCEPT:
			self.preferences.save_to_file(save_preferences_dlg.get_filename()+".cfg")
		save_preferences_dlg.destroy()



	def load_preferences(self,*data):
		load_preferences_dlg = FileChooserDialog(_("Select the image"),
			FileChooserDialog.OPEN,["cfg"],macros.home_dir)
		response = load_preferences_dlg.run()
		if response == FileChooserDialog.ACCEPT:
			self.preferences.set_from_file(load_preferences_dlg.get_filename())
			self.make_preferences_effective()
			#self.notify("preferences loaded from %s" % (load_preferences_dlg.get_filename()),False,None,True)
		load_preferences_dlg.destroy()


	def restore_preferences(self,*data):
		self.preferences.__init__()
		self.make_preferences_effective()
	
	def open_preferences_general_page(self,*data):
		if(self.preferences.open_configure_dialog(0)):
			self.make_preferences_effective()		

	def open_preferences_recognition_page(self,*data):
		if(self.preferences.open_configure_dialog(1)):
			self.make_preferences_effective()		

	def open_preferences_scanning_page(self,*data):
		if(self.preferences.open_configure_dialog(2)):
			self.make_preferences_effective()

	def open_text(self,widget,data=None):
		self.textview.open()
	
	@on_thread
	def start_reading(self,*data):
		self.stop_reading = False
		speaker = speech.Speech()
		speaker.set_output_module(speaker.list_output_modules()[self.preferences.speech_module])
		if(self.preferences.speech_module != -1 and len(speaker.list_voices()) > 1):
			speaker.set_synthesis_voice(speaker.list_voices()[self.preferences.speech_language])
		speaker.set_rate(self.preferences.speech_rate)
		speaker.set_volume(self.preferences.speech_volume)
		speaker.set_pitch(self.preferences.speech_pitch)
		while(not self.textview.is_cursor_at_end()):
			loop.acquire_lock()
			sentence = self.textview.get_next_sentence()
			speaker.say(sentence)
			loop.release_lock()
			speaker.wait()
			if(self.stop_reading):
				break
				speaker.close()
	
	def stop_reading(self,*data):
		self.stop_reading = True

	def scan_using_cam(self,widget):
		devices = cam.Cam.get_available_devices()
		if(devices):
			ob = cam.Cam(devices[-1],1024,768)
			ob.connect_image_captured(self.cam_image_captured)
		
	def cam_image_captured(self,widget,filename):
		self.add_image_to_list(filename,"/tmp/Lios/{}".format(filename.split("/")[2]),True,False)
	
	def about(self,*data):
		dlg = about.AboutDialog("Lios",None)
		dlg.set_name("Linux-Intelligent-Ocr-Solution")
		dlg.set_program_name("Linux-Intelligent-Ocr-Solution")
		dlg.set_version(macros.version)
		dlg.set_logo_from_file(macros.logo_file)
		dlg.set_comments(_("Lios is a free and open source software\n \
			for converting print into text using a scanner or camara.\n\
			It can also produce text from other sources. Such as images,\n\
			Pdf, or screenshort. Program is given total accessibility \n\
			for visually impaired. Lios is written in python3 and we release \n\
			it under GPL3 licence. There are great many possibilities\n\
			for this program. Feedback is the key to it."))
		dlg.set_copyright("Copyright (C) 2011-2015 Nalin.x.Linux")
		dlg.set_license("GPL-V3")
		dlg.set_website("http://sourceforge.net/projects/lios/")
		dlg.set_website_label(_("Visit Home Page"))
		dlg.set_authors(["Nalin"])
		dlg.set_documenters(["Shalini S","Sathyaseelan K"])
		dlg.set_artists(["Nahar", "Manuel Eduardo Cortez Vallejo",
				"C V Jawahar","Naveen t.s",	"Vimal Joseph","Hakkeem IT@School",
				"Sreejith Mathil","James Mathew","Don Marang","Vinod-Kollam",
				"Rizal Muttaqin","Sunny Kallada"])
		dlg.run()
		dlg.destroy()
		
	def artha(self,*data):
		os.system("artha &")

	def quit(self,data=None):
		try:
			shutil.rmtree(macros.tmp_dir)
		except FileNotFoundError:
			pass
		loop.stop_main_loop()
		self.preferences.save_to_file("{}/.lios_preferences.cfg".format(macros.home_dir))


	def iconview_button_release_event(self, treeview, event):
		if ((event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3)
		or (event.type == Gdk.EventType.KEY_PRESS and event.hardware_keycode == 135)):
			time = event.time
			if (event.type == Gdk.EventType.KEY_PRESS):
				event.button = 0
					
			if (len(self.iconview.get_selected_item_names()) != 0):
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

		
		"""self.paned = self.guibuilder.get_object("paned")



		#Getting Preferences Values
		self.set_preferences_from_file('{0}/.lios_preferences.cfg'.format(macros.home_dir))
		
		#Image iconview and store
		self.image_icon_view = self.guibuilder.get_object("iconview")
		self.image_icon_view.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		
		self.liststore_images = Gtk.ListStore(GdkPixbuf.Pixbuf, str,object,int)
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

		item = Gtk.MenuItem.new_with_label("Invert-List")
		item.connect("activate",self.invert_image_list)
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
		
		

		
		#OCR Engine
		self.available_ocr_engine_list = ocr.get_available_engines()
		
		
		#Creating Lios Folder in tmp
		try:
			os.mkdir(macros.tmp_dir)
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
		
		#Available Scanner Driver list
		self.available_scanner_driver_list = scanner.get_available_drivers()
		
		#OCR Wedgets
		self.ocr_submenu = self.guibuilder.get_object("OCR_Submenu")
		self.toolbutton_ocr = self.guibuilder.get_object("toolbutton_ocr")

		#Image Wedgets
		self.image_submenu = self.guibuilder.get_object("ImageMenu")
		self.toolbutton_import_pdf = self.guibuilder.get_object("toolbutton_import_pdf")
		self.toolbutton_import_images = self.guibuilder.get_object("toolbutton_import_images")
		self.toolbutton_import_folder = self.guibuilder.get_object("toolbutton_import_folder")
		self.toolbar_image = self.guibuilder.get_object("toolbar_image")
		
		#Breaker
		self.process_breaker = False
		
		#Printing
		self.print_settings = None

		#Espeak Voice List
		self.voice_list=[]
		for item in espeak.list_voices():
			self.voice_list.append(item.name)
			
		#Writable formats
		self.writable_format = []
		for item in GdkPixbuf.Pixbuf.get_formats():
			if(item.is_writable()):
				self.writable_format.append(item.get_name())
		
		#Drawing Area and it's TreeView
		self.imageview = image_viewer.ImageViewer()
		self.imageview.connect("list_updated",self.on_image_view_list_update);
		self.imageview.load_image(macros.logo_file,[],image_viewer.ImageViewer.ZOOM_FIT)
		box = Gtk.VBox()
		box.add(self.imageview)
		button = Gtk.Button("OCR Selected Areas")
		button.connect("clicked",self.ocr_selected_areas)
		box.pack_end(button,False,True,0)
		self.paned_text_and_image.pack2(box,True,False)
		box.show_all()
				
		
		#Activating Preference
		self.make_preferences_effective()
		
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
						self.textview.set_text(open(file,"r").read())
						self.save_file_name = file
				
					elif form in macros.image_formats:
						filename = file.split("/")[-1:][0]
						destination = "{0}{1}".format(macros.tmp_dir,filename.replace(' ','-'))
						destination = self.get_feesible_filename_from_filename(destination)
						self.add_image_to_list(file,destination,False)
					elif form == "pdf":
						self.import_images_from_pdf(file)	
		else:
			try:
				file = open("{}/.lios_recent".format(macros.home_dir),encoding="utf-8")
				self.textview.set_text(file.read())
			except:
				pass
				
		self.textview.grab_focus()
		self.window.maximize();
		self.window.show()
		Gtk.main();"""
	


	def on_image_view_list_update(self,data=None):
		items = self.iconview.get_selected_item_names()
		if (items):
			self.liststore_images[items[0]][2] = self.imageview.get_selection_list()
			self.liststore_images[items[0]][3] = self.imageview.get_zoom_level()

	
	def progressbar_timeout(self, user_data):
		if self.activity_mode:
			self.progressbar.pulse()
		#else:
		#	new_value = self.progressbar.get_fraction() + 0.01
		#	if new_value > 1:
		#		new_value = 0
		#	self.progressbar.set_fraction(new_value)
		return True	
	
	
	def set_progress_bar(self,text=None,fraction=None,pulse=None,lock=False):
		if(lock):
			loop.acquire_lock()		
		if (pulse):
			self.progressbar.set_pulse_step(pulse)
			self.activity_mode = True
		if (text):
			self.progressbar.set_text(text)
			self.progressbar.set_show_text(True)
		if (fraction):
			self.progressbar.set_fraction(fraction)
			self.activity_mode = False
		if(lock):
			loop.release_lock()
			
	def set_status_bar(text):
		pass
		
	def announce(self,text,interrupt=True):
		if (self.voice_message_state):
			if(interrupt):
				os.system("pkill paplay")
			os.system("espeak -v {} -a {} -s {} -p {} '{}' --stdout|paplay &"
			.format(self.voice_list[self.voice_message_voice],self.voice_message_volume,
			self.voice_message_rate,self.voice_message_pitch,text.replace("'",'"')))	


        		
		

	
	@on_thread
	def rotate(self,angle,file_name,load_to_drawing_area = False):
		pb = GdkPixbuf.Pixbuf.new_from_file(file_name)
		pb = pb.rotate_simple(angle)
		save_format = file_name.split(".")[-1]
		if save_format not in self.writable_format:
			save_format = 'png'
		pb.savev(file_name,save_format,[],[])
		self.iconview.reload_preview(file_name)
		if(load_to_drawing_area):
			self.drawingarea_load_image(file_name)
	


	def iconview_selection_changed(self,widget):
		items = self.iconview.get_selected_item_names()
		if (items):
			self.imageview.load_image(self.liststore_images[items[0]][1],
			self.liststore_images[items[0]][2],self.liststore_images[items[0]][3])









	
		

	################# End of Icon View Related Handler functions  ##############

		
	
	def make_preferences_widgets_inactive(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.toolbutton_preferences.set_sensitive(False)
		self.preferences_menu.set_sensitive(False)
		if(lock):
			loop.release_lock()

	def make_preferences_widgets_active(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.toolbutton_preferences.set_sensitive(True)
		self.preferences_menu.set_sensitive(True)
		if(lock):
			loop.release_lock()

	def make_ocr_widgets_inactive(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.ocr_submenu.set_sensitive(False)
		self.toolbutton_ocr.set_sensitive(False)
		if(lock):
			loop.release_lock()

	def make_ocr_widgets_active(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.ocr_submenu.set_sensitive(True)
		self.toolbutton_ocr.set_sensitive(True)
		if(lock):
			loop.release_lock()

	def make_image_widgets_inactive(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.image_submenu.set_sensitive(False)
		self.toolbutton_import_images.set_sensitive(False)
		self.toolbutton_import_pdf.set_sensitive(False)
		self.toolbutton_import_folder.set_sensitive(False)
		self.toolbar_image.set_sensitive(False)
		if(lock):
			loop.release_lock()

	def make_image_widgets_active(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.image_submenu.set_sensitive(True)
		self.toolbutton_import_images.set_sensitive(True)
		self.toolbutton_import_pdf.set_sensitive(True)
		self.toolbutton_import_folder.set_sensitive(True)
		self.toolbar_image.set_sensitive(True)
		if(lock):
			loop.release_lock()
			
	def make_scanner_widgets_inactive(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.combobox_scanner.set_sensitive(False)
		self.spinner.set_state(True)
		self.button_scan.set_sensitive(False)
		self.button_refresh.set_sensitive(False)
		self.scan_submenu.set_sensitive(False)
		self.spinner.show()
		if(lock):
			loop.release_lock()
	
	def make_scanner_widgets_active(self,lock=False):
		if(lock):
			loop.acquire_lock()
		self.combobox_scanner.set_sensitive(True)
		self.spinner.set_state(False)
		self.button_scan.set_sensitive(True)
		self.button_refresh.set_sensitive(True)
		self.scan_submenu.set_sensitive(True)
		self.spinner.hide()
		if(lock):
			loop.release_lock()
					


	def new(self,data):
		dialog =  Gtk.Dialog("Start new ?",self.window,True,("No!",
		Gtk.ResponseType.REJECT,"Yes!", Gtk.ResponseType.ACCEPT))
		label = Gtk.Label("Start new? This will clear all text and images!")
		box = dialog.get_content_area()
		box.add(label)
		dialog.show_all()	
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.ACCEPT:
			self.textview.new()
			self.textview.grab_focus()
			self.iconview_image_clear(None)
			self.preferences.starting_page_number = 1
			with open("{}/.lios_recent".format(macros.home_dir),"w",encoding="utf-8") as file:
				file.write("")
		
if __name__ == "__main__":
	linux_intelligent_ocr_solution()
	
