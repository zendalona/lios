#!/usr/bin/env python3
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
import re
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

import webbrowser

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

		try:
			os.mkdir(macros.home_dir+"/lios")
		except:
			pass

		try:
			os.mkdir(macros.bookmarks_dir)
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
			(_("Recognize-With-Rotation"),self.ocr_selected_images_with_rotation),
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
		self.iconview.connect_context_menu_button_callback(self.iconview_popup_context_menu)
		box_iconview.add(toolbar_iconview)
		box_iconview.add(scroll_box_iconview)			

		
		#Image View	
		self.imageview = image_view.ImageViewer()
		self.imageview.set_vexpand(True)
		self.imageview.set_hexpand(True)
		box_imageview = containers.Box(containers.Box.HORIZONTAL)
		toolbar_imageview = containers.Toolbar(containers.Toolbar.VERTICAL,
			[(_("Rotate-Right"),self.rotate_current_images_to_right),
			(_("Rotate-Twice"),self.rotate_current_images_to_twice),
			(_("Rotate-Left"),self.rotate_current_images_to_left),containers.Toolbar.SEPARATOR,
			(_("Zoom-In"),self.imageview.zoom_in),(_("Zoom-Fit"),self.imageview.zoom_fit),
			(_("Zoom-Out"),self.imageview.zoom_out),containers.Toolbar.SEPARATOR,
			(_("Recognize-Selected-Areas"),self.ocr_selected_areas),
			(_("Recognize-Current-Image"),self.ocr_current_image),
			(_("Recognize-Current-Image-With-Rotation"),self.ocr_current_image_with_rotation)]);
		
		box_imageview.add(toolbar_imageview)
		box_imageview.add(self.imageview)
		self.imageview.load_image(macros.logo_file,[],image_view.ImageViewer.ZOOM_FIT)
		#Context menu
		self.context_menu_imageview = menu.ContextMenu(
			[(_("Rotate-Right"),self.rotate_current_images_to_right),
			(_("Rotate-Twice"),self.rotate_current_images_to_twice),
			(_("Rotate-Left"),self.rotate_current_images_to_left),menu.SEPARATOR,
			(_("Zoom-In"),self.imageview.zoom_in),(_("Zoom-Fit"),self.imageview.zoom_fit),
			(_("Zoom-Out"),self.imageview.zoom_out),menu.SEPARATOR,
			(_("Recognize-Selected-Areas"),self.ocr_selected_areas),
			(_("Recognize-Current-Image"),self.ocr_current_image),
			(_("Recognize-Current-Image-With-Rotation"),self.ocr_current_image_with_rotation)]);
		self.imageview.connect_context_menu_button_callback(self.imageview_popup_context_menu)

		
		#Editor
		self.textview = editor.BasicTextView()
		self.textview.set_vexpand(True)
		self.textview.set_hexpand(True)		
		box_editor = containers.Box(containers.Box.HORIZONTAL)
		toolbar_editor = containers.Toolbar(containers.Toolbar.VERTICAL,
			[(_("New"),self.new),('Open',self.open_text),
			(_("Save"),self.textview.save),containers.Toolbar.SEPARATOR,
			(_("Spell-Check"),self.textview.open_spell_check),containers.Toolbar.SEPARATOR,
			(_("Undo"),self.textview.undo),(_("Redo"),self.textview.redo),
			containers.Toolbar.SEPARATOR,
			(_("Find"),self.textview.open_find_dialog),
			(_("Find-Replace"),self.textview.open_find_and_replace_dialog),
			containers.Toolbar.SEPARATOR,
			(_("Start-Reader"),self.start_reader),(_("Stop-Reader"),self.stop_reader),
			containers.Toolbar.SEPARATOR,
			(_("Go-To-Line"),self.textview.go_to_line),
			(_("Go-To-Page"),self.go_to_page),
			
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
		self.preferences.set_from_file(macros.preferences_file_path)
		self.preferences.set_avalable_scanner_drivers([ item.name for item in self.available_scanner_driver_list])
		self.preferences.set_avalable_ocr_engines([ (item.name,item.get_available_languages())
												for item in self.available_ocr_engine_list ])
		
		
		menubar = menu.MenuBar(
		[[_("File"),(_("New"),self.textview.new,"<Control>N"),menu.SEPARATOR,
			(_("Import-Image"),self.import_image,"<Control>I"),(_("Import-Pdf"),self.import_pdf,"None"),
			(_("Import-Folder"),self.import_folder,"None"),menu.SEPARATOR,
			(_("Open"),self.open_text,"<Control>O"),		
			(_("Save"),self.textview.save,"<Control>S"),(_("Save-As"),self.textview.save_as,"<Shift><Control>N"),
			(_("Export-Text-As-Pdf"),self.textview.print_to_pdf,"<Control>E"),(_("Print"),self.textview.open_print_dialog,"None"),
			(_("Print-Preview"),self.textview.print_preview,"None"),menu.SEPARATOR,
			(_("Quit"),self.quit,"<Control>Q")],
		[_("Edit"),(_("Undo"),self.textview.undo,"<Control>Z"),(_("Redo"),self.textview.redo,"<Control>Y"),
			menu.SEPARATOR,
			(_("Punch-Text"),self.textview.punch,"None"),(_("Append-Text"),self.textview.append,"None"),
			menu.SEPARATOR,(_("Find"),self.textview.open_find_dialog,"<Control>F"),
			(_("Find-Replace"),self.textview.open_find_and_replace_dialog,"<Control>R")
			,menu.SEPARATOR,
			(_("Spell-Check"),self.textview.open_spell_check,"<Control>F7"),
			menu.SEPARATOR,
			(_("Go-To-Line"),self.textview.go_to_line,"<Control>L"),(_("Go-To-Page"),self.go_to_page,"<Control>G"),
			menu.SEPARATOR,(_("Preferences"),self.open_preferences_general_page,"<Control>P")],
		[_("Image"),[_("Rotate-Left"),(_("Current"),self.rotate_current_images_to_left,"None"),
				(_("Selected"),self.rotate_selected_images_to_left,"None"),
				(_("All"),self.rotate_all_images_to_left,"None")],
			[_("Rotate-Twice"),(_("Current"),self.rotate_current_images_to_twice,"None"),
				(_("Selected"),self.rotate_selected_images_to_twice,"None"),
				(_("All"),self.rotate_all_images_to_twice,"None")],
			[_("Rotate-Right"),(_("Current"),self.rotate_current_images_to_right,"None"),
				(_("Selected"),self.rotate_selected_images_to_right,"None"),
				(_("All"),self.rotate_all_images_to_right,"None")],											
			menu.SEPARATOR, (_("Invert-List"),self.iconview.invert_list,"None"),
			menu.SEPARATOR,
			[_("Save"),(_("Selected-Images"),self.save_selected_images,"None"),
				(_("All-Images"),self.save_all_images,"None")],
			[_("Export-As-Pdf"),(_("Selected-Images"),self.save_selected_images_as_pdf,"None"),
				(_("All-Images"),self.save_all_images_as_pdf,"None")], menu.SEPARATOR,
			[_("Delete"),(_("Selected-Images"),self.iconview_remove_selected_images,"None"),
				(_("All-Images"),self.iconview_remove_all_images,"None")],],
		[_("Scan"),(_("Update-Scanner-List"),self.update_scanner_list,"None"),
			(_("Scan-Image"),self.scan_single_image,"F8"),
			(_("Scan-Image-Repeatedly"),self.scan_image_repeatedly,"<Control>F8"),
			(_("Scan-and-Ocr"),self.scan_and_ocr,"F9"),
			(_("Scan-and-Ocr-Repeatedly"),self.scan_and_ocr_repeatedly,"<Control>F9"),
			(_("Optimise-Scanner-Brightness"),self.optimize_brightness,"None"),menu.SEPARATOR,
			(_("Scan-Using-Webcam"),self.scan_using_cam,"F6"),menu.SEPARATOR,
			[_("Take-Screenshot"),
				(_("Selection"),self.take_rectangle_screenshot,"<Control>F6"),
				(_("Full"),self.take_full_screenshot,"F6")],
			[_("Take-and-Recognize-Screenshot"),
				(_("Selection"),self.take_and_recognize_rectangle_screenshot,"<Control>F10"),
				(_("Full"),self.take_and_recognize_full_screenshot,"F10")]],
		[_("Recognize"),
			(_("Recognize-Current-Image"),self.ocr_current_image,"None"),
			(_("Recognize-Current-Image-With-Rotation"),self.ocr_current_image_with_rotation,"None"),
			(_("Recognize-Selected-Areas"),self.ocr_selected_areas,"None"),
			(_("Recognize-Selected-Images"),self.ocr_selected_images,"None"),
			(_("Recognize-All-Images"),self.ocr_all_images,"None"),
			(_("Recognize-Selected-with-rotation"),self.ocr_selected_images_with_rotation,"None"),
			(_("Recognize-All-with-rotation"),self.ocr_all_images_with_rotation,"None")],
		[_("Tools"),(_("Spell-Check"),self.textview.open_spell_check,"<Control>F7"),
			(_("Audio-Converter"),self.textview.audio_converter,"None"),
			(_("Dictionary"),self.artha,"<Control><Alt>W"),
			(_("Bookmark"),self.textview.create_bookmark,"<Control>D"),
			(_("Bookmark-Table"),self.textview.open_bookmark_table,"<Control><Alt>D"),
			(_("Import-Bookmarks"),self.textview.import_bookmarks_from_file,"<Control><Alt>D"),
			(_("Bookmark-Table-Complete"),self.textview.open_all_bookmark_table,"<Control><Alt><Super>D"),
			(_("Start-Reader"),self.start_reader,"F5"),
			(_("Increase-Reader-Speed"),self.increase_reader_speed,"<Ctrl>Prior"),
			(_("Decrease-Reader-Speed"),self.decrease_reader_speed,"<Ctrl>Next"),
			(_("Stop-Reader"),self.stop_reader,"<Control>F5"),
			(_("Stop-All-Process"),self.stop_all_process,"<Control>F4")],
		[_("Preferences"),(_("Preferences-General"),self.open_preferences_general_page,"None"),
			(_("Preferences-Recognition"),self.open_preferences_recognition_page,"None"),
			(_("Preferences-Scanning"),self.open_preferences_scanning_page,"None"),
			menu.SEPARATOR,	(_("Save"),self.save_preferences,"None"),
			(_("Load"),self.load_preferences,"None"),
			(_("Restore"),self.restore_preferences,"None")],
		[_("Help"),(_("Open-Readme"),self.open_readme,"None"),
			(_("Video-Tutorials"),self.open_video_tutorials,"None"),
			(_("Open-Home-Page"),self.open_home_page,"None"),
			(_("Get-Source-Code"),self.get_source_code,"None"),
			menu.SEPARATOR,(_("About"),self.about,"None")]])
		menubar.show()

		self.combobox_scanners = widget.ComboBox()
		button_update_scanner_list = widget.Button(_("Update-Scanner-List"))
		button_update_scanner_list.connect_function(self.update_scanner_list)
		button_scan = widget.Button(_("Scan"))
		button_scan.connect_function(self.scan_single_image)		
		toolbar_main = containers.Toolbar(containers.Toolbar.HORIZONTAL,
			[(_("Take-Screenshot"),self.take_rectangle_screenshot),
			(_("Scan-Using-Webcam"),self.scan_using_cam),
			(_("Preferences"),self.open_preferences_general_page),
			(_("Video-Tutorials"),self.open_video_tutorials),
			(_("About"),self.about),
			(_("Quit"),self.quit)])				
		
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
			(menubar,5,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),containers.Grid.NEW_ROW,
			(self.combobox_scanners,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
			(button_update_scanner_list,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
			(button_scan,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
			(toolbar_main,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_END),
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
					if(len(file_list) == 2):
						self.textview.save_file_name = file_list[1]
						self.textview.import_bookmarks_using_filename()
					
		if (not text_updated):
			try:
				file = open(macros.recent_file_path,encoding="utf-8")
				self.textview.set_text(file.read())
			except:
				pass
		
		
		self.old_language = -1
		self.old_scan_driver = -1
		self.old_scanner_mode_switching = -1
		#This will clear scanner combobox
		#so scanner combobox should be inetialised
		self.make_preferences_effective()
		
		self.notify_information(_("Welcome to {} Version {}").format(macros.app_name,macros.version),0.0030,10)

		#For connecting menubar accell group Gtk
		self.window.connect_menubar(menubar)
		
		self.window.connect_configure_event_handler(self.window_reconfigure)
		self.window.connect_close_function(self.quit)
		grid_main.show_all()
		self.window.add(grid_main)
		self.window.maximize()
		self.textview.grab_focus()
		self.window.show()
		loop.start_main_loop()	

	
	def notify_information(self,text,percentage,pulsate=None):
		self.statusbar.set_text(text)
		if(pulsate):
			self.progressbar.set_pulse_step(percentage)
		else:
			self.progressbar.set_fraction(percentage)
		
	def new(self,*data):
		if(self.textview.new()):
			self.preferences.starting_page_number = 1
			with open(macros.recent_file_path,"w") as file:
				file.write("")

	def go_to_page(self,*data):
		spinbutton_page = widget.SpinButton(0,0,self.preferences.starting_page_number,1,5,0)
		dlg = dialog.Dialog(_("Go to page"),(_("Go"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
		dlg.add_widget_with_label(spinbutton_page,_("Page Number : "))
		spinbutton_page.grab_focus()
		dlg.show_all()
		response = dlg.run()
		if response == dialog.Dialog.BUTTON_ID_1:
			to_go = spinbutton_page.get_value()
			if (self.preferences.page_numbering_type == 0):
				word = "Page-{0}".format(to_go)
			else:
				if (to_go % 2 == 0):
					word = "Page-{0}-{1}".format(to_go-1,to_go)
				else:
					word = "Page-{0}-{1}".format(to_go,to_go+1)
			if(not self.textview.move_forward_to_word(word)):
				self.textview.move_backward_to_word(word)
			dlg.destroy()
		else:
			dlg.destroy()

	def open_video_tutorials(self,*data):
		webbrowser.open(macros.video_tutorials_link)

	def open_home_page(self,*data):
		webbrowser.open(macros.home_page_link)

	def get_source_code(self,*data):
		webbrowser.open(macros.source_link)

	def iconview_popup_context_menu(self,*data):
		if (self.iconview.get_selected_item_names() == []):
			self.iconview.select_all()
		if (self.iconview.get_selected_item_names() != []):
			self.context_menu_iconview.pop_up()

	def imageview_popup_context_menu(self,*data):
		self.context_menu_imageview.pop_up()
				
	def window_reconfigure(self,*arg):
		width,height = self.window.get_size()
		self.paned_image_text.set_position(height/2)
		self.paned_main.set_position(200)
		self.imageview.set_position(width-500)
		
		
	def get_feesible_filename_from_filename(self,filename):
		if (os.path.exists(re.sub('[^.-/#0-9a-zA-Z]+', '#', filename))):
			return self.get_feesible_filename_from_filename(filename.replace('.','#.'))
		else:
			return re.sub('[^.-/#0-9a-zA-Z]+', '#', filename)

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
		pdf_filename = re.sub('[^.-/#0-9a-zA-Z]+', '#', pdf_filename)
		destination = "{0}{1}".format(macros.tmp_dir,pdf_filename)		
		shutil.copyfile(pdf_filename_full,destination)
		os.makedirs(destination.split(".")[0],exist_ok=True)
		
		self.notify_information(_("Extracting images from Pdf"),0.0030,0.001)
		
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
					loop.acquire_lock()
					self.add_image_to_list("{}/{}".format(destination.split(".")[0],image),filename,True)
					loop.release_lock()
		os.rmdir(destination.split(".")[0])
		self.notify_information(_("Completed!"),0.0030,0.01)
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
			progress_step = len(file_list)/(10^len(file_list));
			progress = 0;			
			for image in sorted(file_list):
				try:
					if image.split(".")[-1] in macros.supported_image_formats:
						destination = "{0}{1}".format(macros.tmp_dir,image.replace(' ','-'))
						self.notify_information(_("Importing image {}").format(destination),progress,None)
						destination = self.get_feesible_filename_from_filename(destination)
						self.add_image_to_list("{0}/{1}".format(image_directory,image),destination,False)					
				except IndexError:
					pass
				progress = progress + progress_step;
			self.notify_information(_("Completed!"),0.0030,0.01)
		#self.make_image_widgets_active()

	@on_thread	#should continue the loop to get window minimize 
	def take_full_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		os.system("sleep 1") #Time to minimize lios window
		capture_screen.capture_entire_screen(destination)
		loop.acquire_lock()
		self.iconview.add_item(destination)
		loop.release_lock()
		self.preferences.update_page_number()

	@on_thread
	def take_rectangle_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		capture_screen.capture_rectangle_selection(destination)
		loop.acquire_lock()
		self.iconview.add_item(destination)
		loop.release_lock()
		self.preferences.update_page_number()

	@on_thread
	def take_and_recognize_full_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		os.system("sleep 1") #Time to minimize lios window
		capture_screen.capture_entire_screen(destination)
		loop.acquire_lock()
		self.iconview.add_item(destination)
		loop.release_lock()
		text,angle = self.ocr(destination,2,00)
		self.insert_text_to_textview(text,self.preferences.insert_position)
		self.preferences.update_page_number()

	@on_thread
	def take_and_recognize_rectangle_screenshot(self,data):
		destination = self.get_feesible_filename_from_filename("{}{}.png".format(macros.tmp_dir,self.preferences.starting_page_number))
		self.window.iconify() #minimize
		capture_screen.capture_rectangle_selection(destination)
		loop.acquire_lock()
		self.iconview.add_item(destination)
		loop.release_lock()
		text,angle = self.ocr(destination,2,00)
		self.insert_text_to_textview(text,self.preferences.insert_position)		
		self.preferences.update_page_number()
		

	def on_iconview_item_selected(self,data):
		name = self.iconview.get_selected_item_names()
		if(name):
			self.imageview.load_image(name[0],[],image_view.ImageViewer.ZOOM_FIT)
		else:
			self.imageview.load_image(macros.logo_file,[],image_view.ImageViewer.ZOOM_FIT)


	@on_thread
	def update_scanner_list(self,*data):
		self.combobox_scanners.clear()
		for item in self.scanner_objects:
			item.close()
			
		#scanner.scanner.exit()
		#scanner_store = Gtk.ListStore(str)
		self.scanner_objects = []
		
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_scanner_widgets_inactive(lock=True)
		
		self.notify_information(_("Getting devices"),0.0030,0.001)
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
			self.notify_information(_("Setting Scanner {}").format(device),0.0030,0.0030)			
			scanner = driver(device,self.preferences.scanner_mode_switching,
				self.preferences.scan_resolution,self.preferences.scan_brightness,
				self.preferences.scan_area)

			self.scanner_objects.append(scanner)
			self.combobox_scanners.add_item(scanner.device_name)
		print(self.scanner_objects)

		loop.acquire_lock()	
		#self.combobox_scanner.set_model(scanner_store)		
		
		if (len(self.scanner_objects) != 0):
			self.combobox_scanners.set_active(0)
			#self.make_scanner_widgets_active(lock=True)
			self.notify_information(_("Completed!"),0.0030,0.01)
		else:
			#self.button_refresh.set_sensitive(True)
			#self.spinner.set_state(False)
			#self.spinner.hide()
			self.notify_information(_("No Scanner Detected!"),0.0030,0.01)
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
		self.process_breaker = False
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
		self.notify_information(_("Job completed!"),100)
		#self.make_scanner_widgets_active(lock=True)
		#self.make_preferences_widgets_active(lock=True)

	def scan(self,filename):
		self.process_breaker = False
		selected_scanner = self.combobox_scanners.get_active()
		
		#No scanner added to list
		if(selected_scanner == -1):
			return;

		self.notify_information(_("Scanning {} with resolution={} brightness={}").
		format(filename,self.preferences.scan_resolution,self.preferences.scan_brightness),0.0030,0.0030)
		
		p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan),
		args=(filename,self.preferences.scan_resolution,
		self.preferences.scan_brightness,self.preferences.scan_area))
		
		p.start()
		while(p.is_alive()):
			pass
		self.notify_information(_("Scan Completed!"),0.0030,0.01)
			
		if(self.process_breaker):
			return
		print(_("Adding image to list"))
		loop.acquire_lock()
		self.iconview.add_item(filename)
		loop.release_lock()
		print(_("Image added"))
		if(self.process_breaker):
			return
		


	############## OCR ################################
	def ocr(self,file_name,mode,angle):
		self.process_breaker = False

		ocr_engine_object = self.available_ocr_engine_list[self.preferences.ocr_engine]()
		languages_available = self.available_ocr_engine_list[self.preferences.ocr_engine].get_available_languages()
		
		language = languages_available[self.preferences.language]
		ocr_engine_object.set_language(language)
		
		print(language)
		rotation_list = [00,90,180,270]
		print("Angle = ",angle)
		if mode == 2:	#Manual
			if(angle not in rotation_list):
				os.system("convert -rotate {0} {1} {1}".format(rotation_list[angle],file_name))
			else:
				os.system("convert -rotate {0} {1} {1}".format(angle,file_name))
			text = ocr_engine_object.ocr_image_to_text_with_multiprocessing(file_name)
			return (text,angle)
		else: #Full_Automatic or Partial_Automatic
			list_ = []
			for angle in rotation_list:
				os.system("convert -rotate {0} {1} {1}_test".format(angle,file_name))
				text = ocr_engine_object.ocr_image_to_text_with_multiprocessing(file_name+"_test")
				count = self.count_dict_words(text)
				list_.append((text,count,angle))
				if(self.process_breaker):
					return True;
			list_ = sorted(list_, key=lambda item: item[1],reverse=True)
			os.system("convert -rotate {0} {1} {1}".format(list_[0][2],file_name))
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
		with open(macros.recent_file_path,"w",encoding="utf-8") as file:
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
		self.imageview.redraw()
		loop.acquire_lock()
		self.iconview.reload_preview(destination)
		loop.release_lock()
		self.notify_information(_("Page {}").format(self.preferences.get_page_number_as_string()),10)
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
			print(_("#Scanning"))
			t = threading.Thread(target=self.scan,args=(destination,))
			t.start()
			while(t.is_alive()):
				pass
			print(_("#Scan Compleated"))
			if(self.process_breaker):
				break
			time.sleep(self.preferences.time_between_repeated_scanning)	
			if(self.process_breaker):
				break
			print(_("#Running OCR"))	
			text,angle = self.ocr(destination,mode,angle)	
			print(_("#Placing text and cursor"))
			if (i == 0):
				self.insert_text_to_textview(text,True,True)
			else:
				self.insert_text_to_textview(text,False,True)
			print(_("#Placing text and cursor Finished"))				
			print(_("#Redraw"))
			self.imageview.redraw()
			print(_("#Redraw Compleated"))
			loop.acquire_lock()
			self.iconview.reload_preview(destination)
			self.notify_information(_("Page {}").format(self.preferences.get_page_number_as_string()),100)
			loop.release_lock()
			print(_("#Preview Updated"))
			self.preferences.update_page_number()
			
			if mode == 1: #Change the mode partial automatic to Manual
				mode = 2
				#self.announce(_("Angle to be rotated = {}").format(angle))
							
			if(self.process_breaker):
				break
			print(_("#Compleated "),i);
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
		if (mode == 0 or mode == 1):
			self.notify_information(_("Scanning with resolution={} brightness={} for detecting angle of rotation")
			.format(self.preferences.scan_resolution,self.preferences.scan_brightness),0.0030,0.0030)
			
			p = multiprocessing.Process(target=(self.scanner_objects[selected_scanner].scan),
			args=("{0}rotate.pnm".format(macros.tmp_dir),self.preferences.scan_resolution,
				self.preferences.scan_brightness,self.preferences.scan_area))
			
			p.start()
			while(p.is_alive()):
				pass
			text,angle = self.ocr("{0}rotate.pnm".format(macros.tmp_dir),mode,00)
			self.notify_information("Image at {} angle.".format(angle),0.0030)
		else:
			angle = self.preferences.rotation_angle		
		value = self.preferences.scan_brightness;
		distance = 10; start = 10; end = 90;
		count = None
		result_text = "<b>Click 'Optimize' to start optimisation </b>" 
		while(1):
			loop.acquire_lock()
			dlg = dialog.Dialog(_("Optimize Scanner-Brightness"),
				(_("Optimize"), dialog.Dialog.BUTTON_ID_3,
				_("Apply"), dialog.Dialog.BUTTON_ID_2,
				_("Cancel"), dialog.Dialog.BUTTON_ID_1))		
			
			label_rotation = widget.Label(_("Angle to be rotated : "))
			spinbutton_rotation = widget.SpinButton(angle,00,360,90,90,90)
			label_rotation.set_mnemonic_widget(spinbutton_rotation)
			try:
				spinbutton_rotation.set_value([00,90,180,270][angle])
			except:
				spinbutton_rotation.set_value(angle)			
			
			label_value = widget.Label(_("Current-Value"))
			spinbutton_value = widget.SpinButton(value,0,200,1,5,0)
			label_value.set_mnemonic_widget(spinbutton_value)

			label_start = widget.Label(_("Start"))
			spinbutton_start = widget.SpinButton(start,0,100,10,5,0)
			label_start.set_mnemonic_widget(spinbutton_start)
			
			label_distance = widget.Label(_("Distance"))
			spinbutton_distance = widget.SpinButton(distance,0,40,5,5,0)
			label_distance.set_mnemonic_widget(spinbutton_distance)
			
			label_end = widget.Label(_("End"))
			spinbutton_end = widget.SpinButton(end,0,100,10,5,0)
			label_end.set_mnemonic_widget(spinbutton_end)
			
			label_result = widget.Label(_("Result"))
			label_result.set_use_markup(True)
			label_result.set_label(result_text)
			
			grid = containers.Grid()
			grid.add_widgets([(label_rotation,1,1),(spinbutton_rotation,1,1),
				containers.Grid.NEW_ROW,
				(label_value,1,1),(spinbutton_value,1,1),containers.Grid.NEW_ROW,
				(label_start,1,1),(spinbutton_start,1,1),containers.Grid.NEW_ROW,
				(label_distance,1,1),(spinbutton_distance,1,1),containers.Grid.NEW_ROW,
				(label_end,1,1),(spinbutton_end,1,1),containers.Grid.NEW_ROW,
				(label_result,2,1)]);
			dlg.add_widget(grid)
			grid.show_all()
			
			response = dlg.run()
			dlg.destroy()
			loop.release_lock()				
			if (response == dialog.Dialog.BUTTON_ID_2):
				self.preferences.scan_brightness = spinbutton_value.get_value()
				angle = spinbutton_rotation.get_value()
				loop.acquire_lock()
				dlg_set_mode = dialog.Dialog(_("Set Mode of rotation"),
				(_("Yes set this rotation"), dialog.Dialog.BUTTON_ID_1,
				_("No continue with existing mode"), dialog.Dialog.BUTTON_ID_2))
				label = widget.Label(_("Do you want to fix the angle at {}\
				\ndegree manual rotation ?".format(angle)))
				dlg_set_mode.add_widget(label)
				label.show()
				response = dlg_set_mode.run()
				if(response == dialog.Dialog.BUTTON_ID_1):
					self.preferences.mode_of_rotation = 2
					self.preferences.rotation_angle = [00,90,180,270].index(angle)
					self.notify_information(_("Rotation mode changed to manual at angle {} degree").
						format(self.preferences.rotation_angle),0.0030)
				dlg_set_mode.destroy()
				loop.release_lock()
				#self.make_scanner_widgets_active(lock=True)
				#self.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)				
				return True
			elif (response == dialog.Dialog.BUTTON_ID_3):
				value = spinbutton_value.get_value()
				start = spinbutton_start.get_value()
				distance = spinbutton_distance.get_value()
				end = spinbutton_end.get_value()
				angle = spinbutton_rotation.get_value()
				self.preferences.scan_brightness = value
			else:
				#self.make_scanner_widgets_active(lock=True)
				#elf.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)
				return True
							
			list = self.optimize_with_model(value,start,distance,end,angle,count)
			if (not list):
				#self.make_scanner_widgets_active(lock=True)
				#self.make_ocr_widgets_active(lock=True)
				#self.make_preferences_widgets_active(lock=True)
				return True
			count, value = list[0][0],list[0][1];
			result_text = "<b>Optimisation Result "
			for item in list:
				result_text += "\nGot {} Words at brightness {}".format(item[0], item[1])
			result_text += "</b>" 
			start = value-distance;
			end = value+distance;
			distance = distance / 2;
			
			
		
	def optimize_with_model(self,value,start,distance,end,angle,previous_optimised_count=None):
		selected_scanner = self.combobox_scanners.get_active()
		list = []
		count = -1		
		pos = start
		while(pos <= end):
			if (pos == value and previous_optimised_count != None):
				list.append((previous_optimised_count,value))
				#self.announce(_("Got {} words at brightness {}.").format(previous_optimised_count,mid_value))
			else:
				if (count != -1):
					self.notify_information(_("Got {} words at brightness {}. Scanning with resolution={} brightness={}")
					.format(count,pos-distance,self.preferences.scan_resolution,pos),0.0030,0.0030)
				else:
					self.notify_information(_("Scanning with resolution={} brightness={}")
					.format(self.preferences.scan_resolution,pos),0.0030,0.0030)
				
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

	def stop_all_process(self,widget):
		self.process_breaker = True
		#selected_scanner = self.combobox_scanners.get_active()
		#self.scanner_objects[selected_scanner].cancel()
		os.system("pkill convert")
		self.available_ocr_engine_list[self.preferences.ocr_engine].cancel()
		self.notify_information("Terminated",0.0030)
		
	def open_readme(self,*data):
		if(self.textview.get_modified()):
			dlg = dialog.Dialog(_("Warning!"),
			 (_("No"),dialog.Dialog.BUTTON_ID_1,_("Yes"),dialog.Dialog.BUTTON_ID_2))
			label = widget.Label(_("Current text not saved! do you want to load readme without saving ? "))
			label.show()
			dlg.add_widget(label)
			response = dlg.run()
			if response == dialog.Dialog.BUTTON_ID_2:
				with open(macros.readme_file) as file:
					self.textview.set_text(file.read())
			dlg.destroy()
		else:
			with open(macros.readme_file) as file:
				self.textview.set_text(file.read())


	@on_thread			
	def ocr_selected_images_with_rotation(self,widget):
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_image_widgets_inactive(lock=True)
		progress_step = 1/len(self.iconview.get_selected_item_names())
		progress = 0;
		mode = self.preferences.mode_of_rotation
		angle = self.preferences.rotation_angle
		for item in reversed(self.iconview.get_selected_item_names()):
			self.notify_information(_("Running OCR on selected image {}")
			.format(item),progress,None)
			
			#self.announce(_("Recognising {}").format(self.liststore_images[item[0]][1]))
			progress = progress + progress_step;			
			text,angle = self.ocr(item,mode,angle)
			self.insert_text_to_textview(text,self.preferences.insert_position)
			loop.acquire_lock()
			self.iconview.reload_preview(item)
			loop.release_lock()
			if mode == 1:#Changing partial automatic to Manual
				mode = 2
				#self.announce(_("Angle to be rotated = {}").format(angle))
			if(self.process_breaker):
				break
		self.imageview.redraw()
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
		progress_step = 1/len(self.iconview.get_selected_item_names())
		progress = 0;
		for item in reversed(self.iconview.get_selected_item_names()):
			self.notify_information(_("Running OCR on selected image {} (without rotating)")
			.format(item),progress,0.0030,)
			
			#self.announce(_("Recognising {} without rotating").format(self.liststore_images[item[0]][1]))
			progress = progress + progress_step;
			text,angle = self.ocr(item,2,00)
			self.insert_text_to_textview(text,self.preferences.insert_position)
			if(self.process_breaker):
				break
		self.notify_information(_("completed!"),0.0030,0.01)
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
		if(len(self.iconview.get_selected_item_names()) == 0):
			self.notify_information(_("Nothing selected"),0.0030,0.01)
			return
		progress_step = 1/len(self.iconview.get_selected_item_names())
		progress = 0;
		for item in reversed(self.iconview.get_selected_item_names()):
			os.system("convert -rotate {0} {1} {1}".format(angle,item))
			loop.acquire_lock()
			self.iconview.reload_preview(item)
			loop.release_lock()
			self.notify_information(_("Rotating selected image {} to {}")
			.format(item,angle),progress,None)
			progress = progress + progress_step;
		self.imageview.redraw()
		self.notify_information(_("completed!"),0.0030,0.01)

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

	def rotate_current_images_to_right(self,widget):
		filename = self.imageview.get_filename()
		self.iconview.select_item(filename)
		self.rotate_selected_images_to_right(None)

	def rotate_current_images_to_left(self,widget):
		filename = self.imageview.get_filename()
		self.iconview.select_item(filename)
		self.rotate_selected_images_to_left(None)

	def rotate_current_images_to_twice(self,widget):
		filename = self.imageview.get_filename()
		self.iconview.select_item(filename)
		self.rotate_selected_images_to_twice(None)


	def save_selected_images(self,widget):
		item_list = self.iconview.get_selected_item_names()
		if (len(item_list) == 0):
			pass
		elif (len(item_list) == 1):
			dlg = FileChooserDialog(_("Filename please"),
				FileChooserDialog.SAVE,macros.supported_image_formats,
				macros.home_dir);
			response = dlg.run()
			if response == FileChooserDialog.ACCEPT:
				shutil.copy(item_list[0],dlg.get_filename())
			dlg.destroy()
		else:
			dlg = FileChooserDialog(_("Select Folder to save images"),
				FileChooserDialog.OPEN_FOLDER,macros.supported_image_formats,
				macros.home_dir);
			response = dlg.run()
			if response == FileChooserDialog.ACCEPT:
				directory = dlg.get_current_folder()
				for item in reversed(item_list):
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
			for item in self.iconview.get_selected_item_names():
				command += item + " "
			command += '"'+file_name+'"'
			print("File name : ",file_name)
			os.system(command)
		dlg.destroy()

	def save_all_images_as_pdf(self,widget):
		self.iconview.select_all()
		self.save_selected_images_as_pdf(None)

	@on_thread
	def ocr_current_image(self,widget):
		filename = self.imageview.get_filename()
		self.iconview.select_item(filename)
		self.ocr_selected_images(None)

	@on_thread
	def ocr_current_image_with_rotation(self,widget):
		filename = self.imageview.get_filename()
		self.iconview.select_item(filename)
		self.ocr_selected_images_with_rotation(None)

	@on_thread			
	def ocr_selected_areas(self,widget):
		self.process_breaker = False
		#self.make_preferences_widgets_inactive(lock=True)
		#self.make_ocr_widgets_inactive(lock=True)
		#self.make_image_widgets_inactive(lock=True)
		progress_step = 1/len(self.imageview.get_selection_list());
		progress = 0;
		for item in self.imageview.get_selection_list():
			self.notify_information(_("Running OCR on selected Area [ X={} Y={} Width={} Height={} ]")
			.format(item[0],item[1],item[2],item[3]),progress,None)
			
			progress = progress + progress_step;
			self.imageview.save_sub_image("{0}tmp".format(macros.tmp_dir),
				item[0],item[1],item[2],item[3])
			
			#Will always be Manual with no rotation
			text,angle = self.ocr("{0}tmp".format(macros.tmp_dir),2,00)
			self.insert_text_to_textview(text,False,False)
			if(self.process_breaker):
				break;

		self.notify_information(_("completed!"),0.0030,0.01)
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
				dlg = dialog.Dialog(_("Dictionary not found!"), (_("Ok"),dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_(
 """Please install aspell, ispell, hunspell, myspell, or uspell 
dictionary for your language({0}) and restart Lios!
Otherwise spellchecker and auto-rotation will work with english(fallback). 

For example on debian based system one can install aspell or 
hunspell french dictionary using following commands
apt-get install aspell-fr
apt-get install hunspell-fr
		
or ispell dict using 
apt-get install ifrench 
 
On rpm based system use 
yum install aspell-fr
			
On arch based system use 
pacman -S aspell-fr""").format(languages[self.preferences.language]))
				dlg.add_widget(label)
				label.show()
				dlg.run()
				dlg.destroy()				
				
		if (self.old_scan_driver != self.preferences.scan_driver or
			self.old_scanner_mode_switching != self.preferences.scanner_mode_switching ):
			self.old_scan_driver = self.preferences.scan_driver
			self.old_scanner_mode_switching = self.preferences.scanner_mode_switching
			self.update_scanner_list()
		
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
			self.notify_information(_("Preferences saved to ")+save_preferences_dlg.get_filename()+".cfg",0.0030)
		save_preferences_dlg.destroy()



	def load_preferences(self,*data):
		load_preferences_dlg = FileChooserDialog(_("Select the image"),
			FileChooserDialog.OPEN,["cfg"],macros.home_dir)
		response = load_preferences_dlg.run()
		if response == FileChooserDialog.ACCEPT:
			self.preferences.set_from_file(load_preferences_dlg.get_filename())
			self.make_preferences_effective()
			self.notify_information(_("Preferences loaded from ")+load_preferences_dlg.get_filename(),0.0030)
		load_preferences_dlg.destroy()


	def restore_preferences(self,*data):
		self.preferences.__init__()
		self.make_preferences_effective()
		self.notify_information(_("Preferences Restored"),0.0030)		
	
	def open_preferences_general_page(self,*data):
		if(self.preferences.open_configure_dialog(0)):
			self.make_preferences_effective()
			self.preferences.save_to_file(macros.preferences_file_path)		

	def open_preferences_recognition_page(self,*data):
		if(self.preferences.open_configure_dialog(1)):
			self.make_preferences_effective()
			self.preferences.save_to_file(macros.preferences_file_path)		

	def open_preferences_scanning_page(self,*data):
		if(self.preferences.open_configure_dialog(2)):
			self.make_preferences_effective()
			self.preferences.save_to_file(macros.preferences_file_path)

	def open_text(self,widget,data=None):
		self.textview.open()
	
	@on_thread
	def start_reader(self,*data):
		self.reading_breaker = False
		speaker = speech.Speech()
		speaker.set_output_module(speaker.list_output_modules()[self.preferences.speech_module])
		if(self.preferences.speech_module != -1 and len(speaker.list_voices()) > 1):
			speaker.set_synthesis_voice(speaker.list_voices()[self.preferences.speech_language])
		speaker.set_volume(self.preferences.speech_volume)
		speaker.set_pitch(self.preferences.speech_pitch)
		while(not self.textview.is_cursor_at_end()):
			loop.acquire_lock()
			speaker.set_rate(self.preferences.speech_rate)
			sentence = self.textview.get_next_sentence()
			speaker.say(sentence)
			loop.release_lock()
			speaker.wait()
			if(self.reading_breaker):
				break
				speaker.close()
	
	def stop_reader(self,*data):
		self.reading_breaker = True
	
	def increase_reader_speed(self,*data):
		if (self.preferences.speech_rate < 100):
			self.preferences.speech_rate = self.preferences.speech_rate + 10;

	def decrease_reader_speed(self,*data):
		if (self.preferences.speech_rate > -100):
			self.preferences.speech_rate = self.preferences.speech_rate - 10;

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
			Pdf, or screenshot. Program is given total accessibility \n\
			for visually impaired. Lios is written in python3 and we release \n\
			it under GPL3 licence. There are great many possibilities\n\
			for this program. Feedback is the key to it."))
		dlg.set_copyright("Copyright (C) 2011-2015 Nalin.x.Linux")
		dlg.set_license("GPL-V3")
		dlg.set_website(macros.home_page_link)
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
		#Closing scanners
		for item in self.scanner_objects:
			item.close()
		loop.stop_main_loop()
		self.preferences.save_to_file(macros.preferences_file_path)

if __name__ == "__main__":
	linux_intelligent_ocr_solution()
	
