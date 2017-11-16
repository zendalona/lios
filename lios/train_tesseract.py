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


from lios import imageview, ocr
from lios.ui.gtk import widget, containers, loop, menu, \
	window, icon_view, dialog, about, tree_view, text_view, terminal, file_chooser

from lios.ui.gtk.file_chooser import FileChooserDialog
from lios import macros
from lios import localization
_ = localization._

import os
import subprocess
import shutil
import time


import threading
from functools import wraps

def on_thread(function):
	@wraps(function)
	def inner(*args):
		print(function.__name__+" Started")
		#function(*args);
		threading.Thread(target=function,args=args).start()
	return inner

DICT_LIST = ["/tmp/tesseract-train/file."+x for x in ["word-dawg","freq-dawg","punc-dawg","number-dawg","bigram-dawg"]]


class TesseractTrainer(window.Window):
	def __init__(self,image_list=None):
		window.Window.__init__(self, title=_("Tesseract Trainer"))
		self.set_taskbar_icon(macros.logo_file)
		grid = containers.Grid()
		
		if( not ocr.ocr_engine_tesseract.OcrEngineTesseract.is_available()):
			label = widget.Label(_("Tesseract is not installed"))
			self.add(label)
			label.show()
			self.set_default_size(400,200)
			return

		if( not ocr.ocr_engine_tesseract.OcrEngineTesseract.is_training_executables_available()):
			label = widget.Label(_("""Tesseract training executable are not installed. 
Please make sure following exicutables are installed
\ncombine_tessdata, unicharset_extractor, shapeclustering, mftraining, cntraining and text2image.
\nIf you forget to build training tools then use 'make training' and 'sudo make training-install' to build it """))
			self.add(label)
			label.show()
			self.set_default_size(400,200)
			return

		if(not os.path.isdir("/tmp/tesseract-train/")):
			os.mkdir("/tmp/tesseract-train/")

		self.output_terminal = terminal.Terminal("")
		self.output_terminal.set_scrollback_lines(10000)
		scroll_box_output = containers.ScrollBox()
		scroll_box_output.add(self.output_terminal)
		self.output_terminal.connect_context_menu_button_callback(self.terminal_popup_context_menu)
		self.context_menu_terminal = menu.ContextMenu(
			[(_("Copy"),self.terminal_copy_clipboard),
			(_("Paste"),self.terminal_paste_clipboard)])

		#Notebook
		notebook = containers.NoteBook()
		notebook.show_all()
		
		paned_notebook_and_output_terminal = containers.Paned(containers.Paned.VERTICAL)
		paned_notebook_and_output_terminal.add(notebook)
		paned_notebook_and_output_terminal.add(scroll_box_output)
		

		# Train image-box pairs
		seperator_select_images = widget.Separator()
		
		self.icon_view_image_list = icon_view.IconView()
		self.icon_view_image_list.connect_on_selected_callback(self.on_iconview_item_selected)
		scroll_box_iconview = containers.ScrollBox()
		self.icon_view_image_list.set_vexpand(True)
		scroll_box_iconview.add(self.icon_view_image_list)
		
		for item in image_list:
			self.icon_view_image_list.add_item(item);
		self.icon_view_image_list.show()
		
		box_buttons = containers.Box(containers.Box.VERTICAL)

		button_add_image_box_pair = widget.Button("Add Image-Box pairs");
		button_add_image_box_pair.connect_function(self.button_add_image_box_pair_clicked);
		box_buttons.add(button_add_image_box_pair)

		button_generate_image = widget.Button("Generate-Image-Using-Fonts");
		button_generate_image.connect_function(self.button_generate_image_clicked);
		box_buttons.add(button_generate_image)

		button_remove_image_box_pair = widget.Button("Remove Image-Box pair");
		button_remove_image_box_pair.connect_function(self.button_remove_image_box_pair_clicked);
		box_buttons.add(button_remove_image_box_pair)

		button_annotate_image = widget.Button("Annotate(Detect boxes)");
		button_annotate_image.connect_function(self.button_annotate_image_clicked);
		box_buttons.add(button_annotate_image)

		button_re_annotate_image = widget.Button("Re-Annotate(Detect boxes)");
		button_re_annotate_image.connect_function(self.button_annotate_image_clicked);
		box_buttons.add(button_re_annotate_image)

		button_ocr_and_view = widget.Button("OCR & View Output");
		button_ocr_and_view.connect_function(self.button_ocr_and_view_clicked);
		box_buttons.add(button_ocr_and_view)

		button_train_image_box_pairs = widget.Button("Train Image-Box pairs");
		button_train_image_box_pairs.connect_function(self.train_image_box_pairs_clicked);

		self.box_editor = BoxEditor(self.on_image_view_box_list_updated)
		self.font_box = FontBox()
		self.font_box.connect_change_handler(self.font_changed)
		
		box_font_and_box = containers.Box(containers.Box.VERTICAL)
		box_font_and_box.add(self.font_box)
		box_font_and_box.add(self.box_editor)
		box_font_and_box.add(button_train_image_box_pairs)

		box_iconview_and_buttons = containers.Box(containers.Box.VERTICAL) 
		box_iconview_and_buttons.add(scroll_box_iconview)
		box_iconview_and_buttons.add(box_buttons)

		paned_iconview_and_image_view = containers.Paned(containers.Paned.HORIZONTAL)
		paned_iconview_and_image_view.add(box_iconview_and_buttons)
		paned_iconview_and_image_view.add(box_font_and_box)

		notebook.add_page(_("Train images-box"),paned_iconview_and_image_view);		


		#Ambiguous Editor
		self.treeview_ambiguous = tree_view.TreeView([("match",str,True),
		("Replacement",str,True),("Mandatory",int,True)],self.ambiguous_edited_callback)

		button_ambiguous_train = widget.Button(_("Train"));
		button_ambiguous_train.connect_function(self.button_ambiguous_train_clicked)

		button_ambiguous_add = widget.Button(_("Add"));
		button_ambiguous_add.connect_function(self.button_ambiguous_add_clicked)

		button_ambiguous_delete = widget.Button(_("Delete"));
		button_ambiguous_delete.connect_function(self.button_ambiguous_delete_clicked)

		button_ambiguous_delete_all = widget.Button(_("Delete-All"));
		button_ambiguous_delete_all.connect_function(self.button_ambiguous_delete_all_clicked)

		button_ambiguous_import = widget.Button(_("Import"));
		button_ambiguous_import.connect_function(self.button_ambiguous_import_clicked)

		button_ambiguous_export = widget.Button(_("Export"));
		button_ambiguous_export.connect_function(self.button_ambiguous_export_clicked)

		scrolled_ambiguous = containers.ScrollBox()
		scrolled_ambiguous.add(self.treeview_ambiguous)

		box_ambiguous_buttons = containers.Box(containers.Box.VERTICAL)
		box_ambiguous_buttons.add(button_ambiguous_add),
		box_ambiguous_buttons.add(button_ambiguous_delete)
		box_ambiguous_buttons.add(button_ambiguous_delete_all)
		box_ambiguous_buttons.add(button_ambiguous_import)
		box_ambiguous_buttons.add(button_ambiguous_export)
		box_ambiguous_buttons.set_homogeneous(True)

		self.combobox_ambiguous_write_format = widget.ComboBox()
		self.combobox_ambiguous_write_format.add_item("Write in V1")
		self.combobox_ambiguous_write_format.add_item("Write in V2")

		grid_set_ambiguous = containers.Grid()
		grid_set_ambiguous.add_widgets([
		(scrolled_ambiguous,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(box_ambiguous_buttons,1,1,containers.Grid.NO_HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(self.combobox_ambiguous_write_format,2,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(button_ambiguous_train,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])

		notebook.add_page("Ambiguous",grid_set_ambiguous);


		#Dictionary Editor
		notebook_dicts = containers.NoteBook()
		self.dictionary_objects = []
		for item in DICT_LIST+[macros.home_dir+"/lios/user-words"]:
			dict_object = Dictionary(item)
			notebook_dicts.add_page(item.split("/")[-1],dict_object)
			self.dictionary_objects.append(dict_object)

		button_bind_dictionarys = widget.Button("Bind Dictionary's ")
		button_bind_dictionarys.connect_function(self.button_bind_dictionarys_clicked)

		grid_set_dictionary = containers.Grid()
		grid_set_dictionary.add_widgets([(notebook_dicts,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(button_bind_dictionarys,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)]);
		notebook.add_page(_("Dictionary's"),grid_set_dictionary);	

		label_language = widget.Label(_("Language "));
		self.combobox_language = widget.ComboBox();
		self.combobox_language.connect_change_callback_function(self.language_combobox_changed);

		label_tessdata_dir = widget.Label(_("Tessdata directory "));
		self.combobox_tessdata_dir = widget.ComboBox();
		self.combobox_tessdata_dir.connect_change_callback_function(self.tessdata_dir_combobox_changed);

		button_import_language = widget.Button(_("Import"))
		button_import_language.connect_function(self.button_import_language_clicked)
		button_export_language = widget.Button(_("Export"))
		button_export_language.connect_function(self.button_export_language_clicked)
		button_remove_language = widget.Button(_("Remove"))
		button_remove_language.connect_function(self.button_remove_language_clicked)

		self.progress_bar = widget.ProgressBar()
		self.progress_bar.set_show_text(True)
		
		button_close = widget.Button(_("Close"));
		button_close.connect_function(self.close_trainer);
		
		grid.add_widgets([(label_tessdata_dir,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.combobox_tessdata_dir,4,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(label_language,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.combobox_language,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(button_import_language,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(button_export_language,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(button_remove_language,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,(paned_notebook_and_output_terminal,5,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,(self.progress_bar,4,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		(button_close,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])
		
		
		self.add(grid)
		grid.show_all()
		self.maximize()

		dlg = dialog.Dialog(_("Search entire filesystem for tessdata ?"),
		(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1))
		label = widget.Label(_("Do you want to search entire filesystem for tessdata ?\nThis may take awhile!"))
		dlg.add_widget(label)
		label.show()
		response = dlg.run()
		if (response == dialog.Dialog.BUTTON_ID_1):
			dir_list = ocr.ocr_engine_tesseract.OcrEngineTesseract.get_all_available_dirs()
		else:
			dir_list = ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_dirs()
		dlg.destroy()

		self.tessdata_dir_available_list = []
		for item in dir_list:
			self.combobox_tessdata_dir.add_item(item)
			self.tessdata_dir_available_list.append(item)
		self.combobox_tessdata_dir.set_active(0)
		self.box_editor.set_image("/usr/share/lios/lios.png")

	def font_changed(self,text):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name):
			font_desc = self.font_box.get_font()
			f = open(name[0]+".font_desc","w")
			f.write(font_desc)

	def terminal_popup_context_menu(self,*data):
		self.context_menu_terminal.pop_up()

	def terminal_copy_clipboard(self,*data):
		self.output_terminal.copy_clipboard()

	def terminal_paste_clipboard(self,*data):
		self.output_terminal.paste_clipboard()

	def show_progress_bar(self,text):
		self.progress_bar.set_pulse_mode(True)
		self.progress_bar.show()
		self.progress_bar.set_text(text)

	def hide_progress_bar(self):
		self.progress_bar.set_pulse_mode(False)
		self.progress_bar.hide()

#	@on_thread
	def button_bind_dictionarys_clicked(self,*data):
		self.show_progress_bar("Combining dictionarys...")
		# Saving all dictionarys to it's text files
		for dictionary in self.dictionary_objects:
			dictionary.save()

		# Copying the original in which later components will be overwrited
		self.output_terminal.run_command("""cp /usr/share/tesseract-ocr/tessdata/{0}.traineddata \
		/tmp/tesseract-train/file.traineddata""".format(self.language))

		# converting text files to DAWG
		for item in DICT_LIST:
			if os.path.isfile(item):
				cmd = "wordlist2dawg {0}.txt {0} /tmp/tesseract-train/file.unicharset".format(item)
				self.output_terminal.run_command(cmd)
				os.system("count=100; while [ ! -r {0} ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done".format(item))

				cmd = "combine_tessdata -o /tmp/tesseract-train/file.traineddata "+item
				self.output_terminal.run_command(cmd)
		self.hide_progress_bar()
		self.place_traineddata("/tmp/tesseract-train/file.traineddata",self.language)
	
	def import_ambiguous_list_from_file(self,filename):
		lines = open(filename).read().split("\n")
		if("V2" in lines):
			version = 2
			self.combobox_ambiguous_write_format.set_active(1)
		else:
			version = 1
			self.combobox_ambiguous_write_format.set_active(0)

		for line in lines[1:-1]:
			if(version == 1):
				items = line.split("\t")
				self.treeview_ambiguous.append((items[1],items[3],int(items[4])))

	def export_ambiguous_list_to_file(self,filename):
		file = open(filename,"w")
		active = self.combobox_ambiguous_write_format.get_active()
		file.write(["V1","V2"][active]+"\n")
		if(active == 0):
			for line in self.treeview_ambiguous.get_list():
				file.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(str(len(line[0].replace(" ",""))),
				line[0],str(len(line[1].replace(" ",""))),line[1],str(line[2])))
		else:
			for line in self.treeview_ambiguous.get_list():
				file.write("{0}\t{1}\t{2}\n".format(line[0],line[1],str(line[2])))

	def button_ambiguous_train_clicked(self,*data):
		self.export_ambiguous_list_to_file("/tmp/tesseract-train/file.unicharambigs")
		self.output_terminal.run_command("""cp /usr/share/tesseract-ocr/tessdata/{0}.traineddata \
		/tmp/tesseract-train/file.traineddata""".format(self.language))
		cmd = "combine_tessdata -o /tmp/tesseract-train/file.traineddata /tmp/tesseract-train/file.unicharambigs"
		self.output_terminal.run_command(cmd)
		self.place_traineddata("/tmp/tesseract-train/file.traineddata",self.language)

	def button_ambiguous_add_clicked(self,*data):
		dlg = dialog.Dialog(_("Add new ambiguous"),
		(_("Close"), dialog.Dialog.BUTTON_ID_1,_("Add"), dialog.Dialog.BUTTON_ID_2))
		entry_match = widget.Entry()
		entry_replace = widget.Entry()
		combobox_mandatory = widget.ComboBox()
		combobox_mandatory.add_item(_("No"))
		combobox_mandatory.add_item(_("Yes"))
		combobox_mandatory.set_active(0)
		dlg.add_widget_with_label(entry_match,_("Match    "))
		dlg.add_widget_with_label(entry_replace,_("Replace  "))
		dlg.add_widget_with_label(combobox_mandatory,_("Mandatory"))
		response = dlg.run()
		if(response == dialog.Dialog.BUTTON_ID_2):
			self.treeview_ambiguous.append((entry_match.get_text(),
			entry_replace.get_text(),combobox_mandatory.get_active()))
		dlg.destroy()

	def button_ambiguous_delete_clicked(self,*data):
		index = self.treeview_ambiguous.get_selected_row_index()
		self.treeview_ambiguous.remove(index)

	def button_ambiguous_delete_all_clicked(self,*data):
		self.treeview_ambiguous.clear()

	def button_ambiguous_import_clicked(self,*data):
		file_chooser_open_files = FileChooserDialog(_("Select files to import"),
				FileChooserDialog.OPEN,"*",
				  macros.home_dir)
		file_chooser_open_files.set_current_folder(macros.home_dir)
		response = file_chooser_open_files.run()
		if response == FileChooserDialog.ACCEPT:
			filename = file_chooser_open_files.get_filename()
			self.import_ambiguous_list_from_file(filename)
		file_chooser_open_files.destroy()

	def button_ambiguous_export_clicked(self,*data):
		save_file = file_chooser.FileChooserDialog(_("Save filename"),file_chooser.FileChooserDialog.SAVE,"*",None);
		save_file.set_do_overwrite_confirmation(True);
		response = save_file.run()
		if response == file_chooser.FileChooserDialog.ACCEPT:
			self.export_ambiguous_list_to_file(save_file.get_filename())
		save_file.destroy()


	def button_generate_image_clicked(self,*data):
		#Create image (using fonts)
		label_font_automatic = widget.Label(_("Font"));
		entry_font_automatic = widget.Entry()
		fontbutton_automatic = widget.FontButton();
		fontbutton_automatic.set_font("FreeMono")
		entry_font_automatic.set_editable(False)
		entry_font_automatic.set_text(fontbutton_automatic.get_font_name())
		button_choose_font_automatic = widget.Button(_("Choose-Font-File"));

		generate_and_train_text_view = text_view.TextView()
		scroll_box = containers.ScrollBox()
		scroll_box.set_size_request(-1,100);
		scroll_box.set_border_width(20);
		scroll_box.add(generate_and_train_text_view)

		def fontbutton_automatic_clicked(*data):
			fontname = fontbutton_automatic.get_font_name()
			entry_font_automatic.set_text(fontname)
			generate_and_train_text_view.set_font(fontname)
			spin_font_size.set_value(int(fontname.split()[-1]))

		def button_choose_font_automatic_clicked(*data):
			file_chooser = FileChooserDialog(_("Select font file"),
					FileChooserDialog.OPEN,"*",
					"/usr/share/fonts/")
			response = file_chooser.run()
			if response == FileChooserDialog.ACCEPT:
				font_file = file_chooser.get_filename()
				file_chooser.destroy()
				if (os.path.isfile(font_file)):
					entry_font_automatic.set_text(font_file)
					generate_and_train_text_view.set_font("FreeMono")
			else:
				file_chooser.destroy()

		def button_select_input_text_clicked(*data):
			file_chooser = FileChooserDialog(_("Select input file"),
					FileChooserDialog.OPEN,macros.supported_text_formats,macros.home_dir)
			response = file_chooser.run()
			if response == FileChooserDialog.ACCEPT:
				input_file = file_chooser.get_filename()
				file_chooser.destroy()
				if (os.path.isfile(input_file)):
					entry_input_text_automatic.set_text(input_file)
					generate_and_train_text_view.set_text(open(input_file).read())
			else:
				file_chooser.destroy()

		fontbutton_automatic.connect_function(fontbutton_automatic_clicked)		
		button_choose_font_automatic.connect_function(button_choose_font_automatic_clicked)

		label_font_size = widget.Label(_("Font Size"));
		spin_font_size = widget.SpinButton(10,8,96)

		label_select_input_text = widget.Label(_("Input Text File"));
		entry_input_text_automatic = widget.Entry()
		entry_input_text_automatic.set_editable(False)
		button_select_input_text = widget.Button(_("Choose"));
		button_select_input_text.connect_function(button_select_input_text_clicked)

		label_writing_mode = widget.Label(_("Writing Mode"));
		combobox_writing_mode = widget.ComboBox();
		combobox_writing_mode.add_item("horizontal")
		combobox_writing_mode.add_item("vertical")
		combobox_writing_mode.add_item("vertical-upright")
		combobox_writing_mode.set_active(0)

		label_writing_char_spacing_automatic = widget.Label(_("Inter-character space"));
		spinbutton_writing_char_spacing_automatic = widget.SpinButton(5,0,50)

		label_writing_resolution_automatic = widget.Label(_("Resolution"));
		spinbutton_writing_resolution_automatic = widget.SpinButton(300,100,1200)

		check_button_writing_degrade_image_automatic = widget.CheckButton(_("Degrade-image"))

		label_writing_exposure_level_automatic = widget.Label(_("Exposure-Level"));
		spinbutton_writing_exposure_level_automatic = widget.SpinButton(0,0,50)

		check_button_writing_ligature_mode_automatic = widget.CheckButton(_("Ligatur-Mode"))


		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(entry_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(fontbutton_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(button_choose_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_font_size,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(spin_font_size,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(entry_input_text_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(button_select_input_text,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(scroll_box,4,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(combobox_writing_mode,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_char_spacing_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(spinbutton_writing_char_spacing_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_resolution_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(spinbutton_writing_resolution_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_exposure_level_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(spinbutton_writing_exposure_level_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(check_button_writing_degrade_image_automatic,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(check_button_writing_ligature_mode_automatic,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND)])

		dlg = dialog.Dialog(_("Generate-Image"),(_("Generate"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
		dlg.add_widget(grid_manual_methord)
		grid_manual_methord.show_all()

		response = dlg.run();
		if(response == dialog.Dialog.BUTTON_ID_1):
			self.show_progress_bar("Generating image...");
			#saving the text in textview to /tmp/tesseract-train/input_file.txt
			open("/tmp/tesseract-train/input_file.txt","w").write(generate_and_train_text_view.get_text())
			font = entry_font_automatic.get_text()
			font = font.split(" ")[0]
			fonts_dir = "/usr/share/fonts"
			if("/" in font):
				fonts_dir = "/".join(font.split("/")[:-1])
				font = font.split("/")[-1].split(".")[0]

			font_size = spin_font_size.get_value()
			input_file = entry_input_text_automatic.get_text()

			active = combobox_writing_mode.get_active()
			writing_mode = ["horizontal","vertical","vertical-upright"][active]

			char_space = spinbutton_writing_char_spacing_automatic.get_value()
			resolution = spinbutton_writing_resolution_automatic.get_value()
			exposure = spinbutton_writing_exposure_level_automatic.get_value()
			degrade = int(check_button_writing_degrade_image_automatic.get_active())
			ligature = int(check_button_writing_ligature_mode_automatic.get_active())
			self.generate_image_with_spec(font,font_size,writing_mode,char_space,resolution,exposure,degrade,ligature,fonts_dir)
		dlg.destroy()

	@on_thread
	def generate_image_with_spec(self,font,font_size,writing_mode,char_space,resolution,exposure,degrade,ligature,fonts_dir):
		# Remove previous image
		if (os.path.isfile("/tmp/tesseract-train/tmp_tess_image.tif")):
			os.remove("/tmp/tesseract-train/tmp_tess_image.tif");
		#generating image
		name = time.strftime("%Y-%m-%d,%H:%M:%S")
		cmd = "text2image --text=/tmp/tesseract-train/input_file.txt --font={0} --ptsize={1} --writing_mode={2} \
		--char_spacing={3} --resolution={4} --exposure={5} --degrade_image={6} --ligatures={7} \
		--fonts_dir={8} --outputbase=/tmp/tesseract-train/{9}".format(font,font_size,writing_mode,char_space,resolution,exposure,degrade,ligature,fonts_dir,name)
		self.output_terminal.run_command(cmd)

		# Wait for image file
		os.system("while [ ! -f /tmp/tesseract-train/{0}.tif ]; do sleep 1; done".format(name))
		self.icon_view_image_list.add_item("/tmp/tesseract-train/{0}.tif".format(name))
		self.make_box_file_for_images(["/tmp/tesseract-train/{0}.tif".format(name)])
		f = open("/tmp/tesseract-train/{0}.tif.font_desc".format(name),"w")
		f.write(font)
		f.close()
		self.hide_progress_bar()

	def on_iconview_item_selected(self,data):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name):
			self.box_editor.set_image(name[0])
			try:
				self.box_editor.load_boxes_from_file(".".join(name[0].split(".")[:-1])+".box")
			except:
				pass
			font = open(name[0]+".font_desc").read()
			self.font_box.set_font(font)

	def close_trainer(self,*data):
		self.destroy();
	
	def ambiguous_edited_callback(self,*data):
		pass
	

	def button_import_language_clicked(self,*data):
		file_chooser = FileChooserDialog(_("Select language file"),
				FileChooserDialog.OPEN,["traineddata"])
		response = file_chooser.run()
		if response == FileChooserDialog.ACCEPT:
			file = file_chooser.get_filename()
			file_chooser.destroy()
			if (os.path.isfile(file)):
				name = file.split("/")[-1].split(".")[0]
				self.place_traineddata(file,name)
		else:
			file_chooser.destroy()

	def button_export_language_clicked(self,*data):
		save_file = file_chooser.FileChooserDialog(_("Save filename"),file_chooser.FileChooserDialog.SAVE,["traineddata"]);
		save_file.set_do_overwrite_confirmation(True);
		save_file.set_current_name(self.language+".traineddata")
		save_file.set_current_folder(macros.home_dir)
		response = save_file.run()
		if response == file_chooser.FileChooserDialog.ACCEPT:
			command = "cp {0}/{1}.traineddata {2}".format(self.tessdata_dir,self.language, save_file.get_filename())
			os.system(command)
		save_file.destroy()

	def button_remove_language_clicked(self,*data):
		command = "rm {0}/{1}.traineddata".format(self.tessdata_dir,self.language)
		self.run_command_in_super_user_mode(command,self.tessdata_dir)
		self.update_language_list()

	def tessdata_dir_combobox_changed(self,*data):
		active = self.combobox_tessdata_dir.get_active()
		self.tessdata_dir = self.tessdata_dir_available_list[active];

		#Resetting language combobox
		self.combobox_language.clear()
		self.languages = []
		for item in ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_languages_in_dirpath(self.tessdata_dir):
			self.combobox_language.add_item(item)
			self.languages.append(item)
		self.combobox_language.set_active(0)

	@on_thread
	def language_combobox_changed(self,*data):
		active = self.combobox_language.get_active()

		# While resetting combobox after training the active will be -1
		if ( active <= len(self.languages) and active != -1 ):
			self.language = self.languages[active]

			self.show_progress_bar("Loading components of "+self.language)

			#Removing all files in /tmp/tesseract-train/
			shutil.rmtree("/tmp/tesseract-train/")
			os.mkdir("/tmp/tesseract-train/")

			cmd = "combine_tessdata -u {0}/{1}.traineddata /tmp/tesseract-train/file".format(self.tessdata_dir,self.language)
			self.output_terminal.run_command(cmd)
			os.system("while [ ! -r /tmp/tesseract-train/file.unicharset ]; do sleep 0.1; done")

			#setting ambiguous table
			loop.acquire_lock()
			self.treeview_ambiguous.clear()
			loop.release_lock()
			os.system("while [ ! -r /tmp/tesseract-train/file.unicharambigs ]; do sleep 0.1; done")
			self.import_ambiguous_list_from_file("/tmp/tesseract-train/file.unicharambigs")
			for item in DICT_LIST:
				if os.path.isfile(item):
					cmd = "dawg2wordlist /tmp/tesseract-train/file.unicharset {0} {0}.txt".format(item)
					self.output_terminal.run_command(cmd)
					os.system("while kill -0 $(pidof dawg2wordlist) 2> /dev/null; do sleep .1; done")
					os.system("count=100; while [ ! -r {0}.txt ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done".format(item))
				else:
					f = open(item+".txt","w")
					f.close()

			# Create user dictionary if not exist
			if not os.path.isfile(macros.home_dir+"/lios/user-words.txt"):
				f = open(macros.home_dir+"/lios/user-words.txt","w")
				f.close()

			# Loading each dictionarys
			for d_obj in self.dictionary_objects:
				loop.acquire_lock()
				d_obj.load()
				loop.release_lock()
			self.hide_progress_bar()

	def get_shell_filename(self,filename):
		for item in " [()]":
			filename = filename.replace(item,"\{0}".format(item))
		return filename

	def button_add_image_box_pair_clicked(self,*data):
		file_chooser = FileChooserDialog(_("Select images to import"),
				FileChooserDialog.OPEN,["tif"],
				  macros.home_dir)
		file_chooser.set_current_folder(macros.home_dir)
		file_chooser.set_select_multiple(True)
		response = file_chooser.run()
		if response == FileChooserDialog.ACCEPT:
			image_list = file_chooser.get_filenames()
			file_chooser.destroy()
			no_box_file_image_list = []
			no_font_desc_file_image_list = []
			for item in image_list:
				self.icon_view_image_list.add_item(item);
				if (not os.path.isfile(".".join(item.split(".")[:-1])+".box")):
					no_box_file_image_list.append(item)
				if (not os.path.isfile(item+".font_desc")):
					no_font_desc_file_image_list.append(item)

			if (no_box_file_image_list != []):
				dlg = dialog.Dialog(_("No curresponding box files found!"),
				(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_("Do you want to auto annotate box file with existing language ?\nThis may take awhile!"))
				dlg.add_widget(label)
				label.show()
				response = dlg.run()
				if (response == dialog.Dialog.BUTTON_ID_1):
					dlg.destroy()
					self.make_box_file_for_images(no_box_file_image_list)
				dlg.destroy()

			if (no_font_desc_file_image_list != []):
				dlg = dialog.Dialog(_("No curresponding font_desc files found!"),
				(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_("Do you want to fill it with following font ?"))
				fontbox = FontBox()
				fontbox.set_font("Sans 0 0 0 0 0")
				dlg.add_widget(label)
				dlg.add_widget(fontbox)
				label.show()
				response = dlg.run()
				if (response == dialog.Dialog.BUTTON_ID_1):
					font = fontbox.get_font()
					dlg.destroy()
					for image_file in no_font_desc_file_image_list:
						f = open(image_file+".font_desc","w")
						f.write(font)
						f.close()
				dlg.destroy()
		else:
			file_chooser.destroy()

	def button_remove_image_box_pair_clicked(self,*data):
		dlg = dialog.Dialog(_("Delete file too ?"),
		(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1,_("Close"), dialog.Dialog.BUTTON_ID_3))
		label = widget.Label(_("Do you want to delete files(image,box,font_desc) too ?"))
		dlg.add_widget(label)
		label.show()
		response = dlg.run()
		if (response == dialog.Dialog.BUTTON_ID_1):
			image_list = self.icon_view_image_list.get_selected_item_names()
			for image in image_list:
				if (os.path.exists(image.replace(".tif",".box"))):
					os.remove(image.replace(".tif",".box"));
				if (os.path.exists(image+".font_desc")):
					os.remove(image+".font_desc");
			self.icon_view_image_list.remove_selected_items(True)

		elif (response == dialog.Dialog.BUTTON_ID_2):
			self.icon_view_image_list.remove_selected_items(False)

		dlg.destroy()
		self.box_editor.set_image("/usr/share/lios/lios.png")



	def button_annotate_image_clicked(self,*data):
		image_list = self.icon_view_image_list.get_selected_item_names()
		self.make_box_file_for_images(image_list)

	def place_traineddata(self,source,language):
		if (os.path.isfile(self.tessdata_dir+"/"+language+".traineddata")):
			dlg = dialog.Dialog(language+_(" Alrady exist! Please edit name to avoid replacing"),
			(_("Place it"), dialog.Dialog.BUTTON_ID_1))

			entry = widget.Entry()
			dlg.add_widget_with_label(entry,_("File Name : "))
			entry.set_text(language)
			response = dlg.run()
			language = entry.get_text()
			dlg.destroy()
		command = "cp {0} {1}/{2}.traineddata".format(source,self.tessdata_dir,language)
		self.run_command_in_super_user_mode(command,self.tessdata_dir)
		self.update_language_list()

	def update_language_list(self):
		self.languages = []
		self.combobox_language.clear()
		for item in ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_languages_in_dirpath(self.tessdata_dir):
			self.combobox_language.add_item(item)
			self.languages.append(item)
		self.combobox_language.set_active(0)

	def run_command_in_super_user_mode(self, command, directory):
		if(os.access(directory, os.W_OK)):
			os.system(command);
		else:
			if ("/bin/pkexec" in subprocess.getoutput("whereis pkexec")):
				os.system("pkexec "+command);
			elif ("/bin/gksudo" in subprocess.getoutput("whereis gksudo")):
				os.system("gksudo "+command);
			elif ("/bin/kdesudo" in subprocess.getoutput("whereis kdesudo")):
				os.system("kdesudo "+command);
			elif ("/bin/gksu" in subprocess.getoutput("whereis gksu")):
				os.system("gksu "+command);
			else:
				dlg = dialog.Dialog(_("Error : running command failed"),
				(_("Ok"), dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_("Can't run command : {0}\n Please make sure you have write access to {1}".format(command,directory)))
				dlg.add_widget(label)
				label.show()
				response = dlg.run()
				dlg.destroy()

	@on_thread
	def make_box_file_for_images(self,filenames_list):
		for file_ in filenames_list:
			filename = self.get_shell_filename(file_)
			self.show_progress_bar("Making box file for "+file_)
			# Removing previous box files if exist -- Bugs exist :(
			self.output_terminal.run_command("rm -f /tmp/tesseract-train/batch.nochop.box")
		
			self.output_terminal.run_command("cd /tmp/tesseract-train/")
			self.output_terminal.run_command("convert {0} -background white -flatten +matte file.tif".format(filename))
			self.output_terminal.run_command("")
			self.output_terminal.run_command("tesseract file.tif --tessdata-dir {0} -l {1} batch.nochop makebox".format(self.tessdata_dir,self.language))

			# Wait for box file
			os.system("while [ ! -f /tmp/tesseract-train/batch.nochop.box ]; do sleep .1; done")
			os.system("count=200; while [ ! -s /tmp/tesseract-train/batch.nochop.box ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done")
			os.system("cp /tmp/tesseract-train/batch.nochop.box {0}.box".format(".".join(filename.split(".")[:-1])))
			self.hide_progress_bar()


	def train_image_box_pairs_clicked(self,*data):
		image_list = self.icon_view_image_list.get_selected_item_names()
		if (image_list == []):
			self.icon_view_image_list.select_all_items()
			image_list = self.icon_view_image_list.get_selected_item_names()
			if (image_list == []):
				return

		dlg = dialog.Dialog(_("Training images..."),
		(_("Close"), dialog.Dialog.BUTTON_ID_2,_("Train"), dialog.Dialog.BUTTON_ID_1))
		label = widget.Label(_("Images to be trained \n{0}\n \
		\nLanguage used : {1}\nOutput tessdata directory : {2}".format("\n".join(image_list),self.language,self.tessdata_dir)))
		label.set_ellipsize(True)
		dlg.add_widget(label)
		label.show()
		response = dlg.run()
		if (response != dialog.Dialog.BUTTON_ID_1):
			dlg.destroy()
			return
		dlg.destroy()


		self.output_terminal.run_command("cd /tmp/tesseract-train/")

		self.show_progress_bar("Training images...")
		tr_list = ""
		font_set = set()
		image_list_shell_type = []
		for img in image_list:
			image = self.get_shell_filename(img)
			image_list_shell_type.append(image)
			image_name_without_extension = ".".join(image.split(".")[:-1])
			tr_name =  ".".join((image.split("/")[-1]).split(".")[:-1])+".box.tr"

			self.output_terminal.run_command("tesseract --tessdata-dir {0} -l {1} {2} {3}.box nobatch box.train".format(self.tessdata_dir,self.language,image,image_name_without_extension));
			self.output_terminal.run_command("mv {0}.box.tr /tmp/tesseract-train/{1}".format(image_name_without_extension,tr_name))
			
			# getting each font desc
			try:
				font = open(image+".font_desc").read()
				font_set.add(font)
			except:
				pass

			tr_list = tr_list+tr_name+" "

		self.output_terminal.run_command("unicharset_extractor -D /tmp/tesseract-train/ "+(" ".join(image_list_shell_type).replace(".tif",".box")));

		# Saving all font desc
		f = open("/tmp/tesseract-train/font_properties","w")
		for item in font_set:
			f.write(item+"\n")
		f.close()

		self.output_terminal.run_command("shapeclustering -F font_properties -U unicharset "+tr_list);
		self.output_terminal.run_command("mftraining -F font_properties -U unicharset -O unicharset "+tr_list);
		self.output_terminal.run_command("cntraining "+tr_list);

		self.output_terminal.run_command("mv inttemp file.inttemp");
		self.output_terminal.run_command("mv normproto file.normproto");

		self.output_terminal.run_command("mv pffmtable file.pffmtable");
		self.output_terminal.run_command("mv shapetable file.shapetable");
		self.output_terminal.run_command("mv unicharset file.unicharset")

		dlg = dialog.Dialog(_("Combine with dictionarys too ?"),
		(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1))
		label = widget.Label(_("Do you want to add dictionarys ? \
		\nDo it if only all characters used in dictionarys are going to be trained!"))
		dlg.add_widget(label)
		label.show()
		response = dlg.run()
		if (response != dialog.Dialog.BUTTON_ID_1):
			for item in DICT_LIST:
				if os.path.exists(item):
					os.remove(item)
		dlg.destroy()

		self.output_terminal.run_command("combine_tessdata file.");
		self.hide_progress_bar()
		self.place_traineddata("/tmp/tesseract-train/file.traineddata",self.language)

	@on_thread
	def button_ocr_and_view_clicked(self,*data):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name == []):
			return;

		self.show_progress_bar("Running ocr... Please wait");
		image_file = self.get_shell_filename(name[0])
		self.output_terminal.run_command("tesseract {0} /tmp/tesseract-train/output -l {1}".format(image_file,self.language));

		# Wait for output
		os.system("while [ ! -f /tmp/tesseract-train/output.txt ]; do sleep .1; done")
		os.system("count=100; while [ ! -s /tmp/tesseract-train/output.txt ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done")
		self.hide_progress_bar()
		loop.acquire_lock()

		window_output = window.Window(_("Recognised text from image {0} with {1}".format(image_file.split("/")[-1],self.language)))
		window_output.set_taskbar_icon(macros.logo_file)
		tv = text_view.TextView()
		sb = containers.ScrollBox()
		sb.add(tv)
		tv.set_vexpand(True)
		tv.set_hexpand(True)
		tv.set_text(open("/tmp/tesseract-train/output.txt").read())
		os.system("rm /tmp/tesseract-train/output.txt")
		window_output.set_default_size(500,400)
		window_output.add(sb)
		window_output.show_all()
		loop.release_lock()

	def on_image_view_box_list_updated(self,*data):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name):
			self.box_editor.save_boxes_to_file(".".join(name[0].split(".")[:-1])+".box")

class FontBox(containers.Box):
	def __init__(self):
		containers.Box.__init__(self,containers.Box.HORIZONTAL)
		label = widget.Label("Font ");
		label.set_hexpand(True)
		self.entry = widget.Entry()
		self.entry.set_hexpand(True)
		self.fontbutton = widget.FontButton();
		self.fontbutton.set_hexpand(True)
		self.fontbutton.set_font("Sans 10")
		self.entry.set_text("Sans")
		self.fontbutton.connect_function(self.font_changed)
		self.cb_italic = widget.CheckButton("Italic")
		self.cb_bold = widget.CheckButton("Bold")
		self.cb_fixed = widget.CheckButton("Fixed")
		self.cb_serif = widget.CheckButton("Serif")
		self.cb_fraktur = widget.CheckButton("Fraktur")
		self.add(label)
		self.add(self.entry)
		self.add(self.fontbutton)
		self.add(self.cb_italic)
		self.add(self.cb_bold)
		self.add(self.cb_fixed)
		self.add(self.cb_serif)
		self.add(self.cb_fraktur)
		self.show_all()

	def connect_change_handler(self,handler):
		self.fontbutton.connect_function(handler)
		self.entry.connect_change_handler(handler)
		self.cb_italic.connect_handler_function(handler)
		self.cb_bold.connect_handler_function(handler)
		self.cb_fixed.connect_handler_function(handler)
		self.cb_serif.connect_handler_function(handler)
		self.cb_fraktur.connect_handler_function(handler)

	def font_changed(self,*data):
		fontname = self.fontbutton.get_font_name()
		# The last token in fontname will be it's size so we trim it
		self.entry.set_text(' '.join(fontname.split(" ")[:-1]))
		if ("bold" in fontname.lower()):
			self.cb_bold.set_active(True)
		if ("italic" in fontname.lower()):
			self.cb_italic.set_active(True)
		if ("serif" in fontname.lower()):
			self.cb_serif.set_active(True)

	def set_font(self,font_desc):
		desc = font_desc.split(" ")
		self.fontbutton.set_font("".join(desc[:-5]).replace("_"," "))
		self.entry.set_text("".join(desc[:-5]).replace("_"," "))
		self.cb_italic.set_active(int(desc[-5]))
		self.cb_bold.set_active(int(desc[-4]))
		self.cb_fixed.set_active(int(desc[-3]))
		self.cb_serif.set_active(int(desc[-2]))
		self.cb_fraktur.set_active(int(desc[-1]))

	def get_font(self):
		text = self.entry.get_text().replace(" ","_")
		italic = int(self.cb_italic.get_active())
		bold = int(self.cb_bold.get_active())
		fixed = int(self.cb_fixed.get_active())
		serif = int(self.cb_serif.get_active())
		fraktur = int(self.cb_fraktur.get_active())
		line = "{0} {1} {2} {3} {4} {5}".format(text,italic,bold,fixed,serif,fraktur)
		return line


class BoxEditor(containers.Box):
	def __init__(self,update_handler):
		containers.Box.__init__(self,containers.Box.VERTICAL)
		self.imageview = imageview.ImageViewer()
		self.imageview.connect("list_updated",self.list_updated_event_handler);
		self.update_handler = update_handler

		self.image_name = ""

		button_zoom_in = widget.Button(_("Zoom-In"))
		button_zoom_in.connect_function(self.imageview.zoom_in)
		button_zoom_fit = widget.Button(_("Zoom-Fit"))
		button_zoom_fit.connect_function(self.imageview.zoom_fit)
		button_zoom_out = widget.Button(_("Zoom-Out"))
		button_zoom_out.connect_function(self.imageview.zoom_out)
		button_save = widget.Button(_("Export-Boxes"))
		button_save.connect_function(self.save_boxes_dialog)
		button_load = widget.Button(_("Load-Boxes"))
		button_load.connect_function(self.load_boxes_dialog)
		self.add(self.imageview)
		box1 = containers.Box(containers.Box.HORIZONTAL)
		box1.add(button_zoom_in)
		box1.add(button_zoom_fit)
		box1.add(button_zoom_out)
		box1.add(button_save)
		box1.add(button_load)
		box1.set_hexpand(True)
		button_zoom_in.set_hexpand(True)
		button_zoom_fit.set_hexpand(True)
		button_zoom_out.set_hexpand(True)
		button_save.set_hexpand(True)
		button_load.set_hexpand(True)
		self.add(box1)
		#self.connect_configure_event_handler(self.configure_event)
		self.imageview.show()
		self.show_all()

	def configure_event(self,*arg):
		width,height = self.get_size()
		self.imageview.set_position(width-200)

	def list_updated_event_handler(self,*arg):
		self.update_handler();


	def save_boxes_to_file(self,filename):
		file = open(filename,"w")
		for item in self.get_list():
			file.write("{0} {1} {2} {3} {4} 0\n".format(str(item[0]),
			str(int(item[1])),str(int(item[2])),
			str(int(item[3])),str(int(item[4]))))

	def load_boxes_from_file(self,filename):
		list_ = []
		for line in open(filename):
			spl = line.split(" ")
			try:
				list_.append((spl[0],float(spl[1]),float(spl[2]),float(spl[3]),float(spl[4]),int(spl[5])))
			except:
				pass
		self.set_list(list_)
	
	def save_boxes_dialog(self,*data):
		save_file = file_chooser.FileChooserDialog(_("Save "),
			file_chooser.FileChooserDialog.SAVE,
			"*",None)
		save_file.set_current_name(self.image_name+".box");
		save_file.set_do_overwrite_confirmation(True);
		response = save_file.run()
		if response == file_chooser.FileChooserDialog.ACCEPT:
			self.save_boxes_to_file(save_file.get_filename())
		save_file.destroy()

	def load_boxes_dialog(self,*data):
		open_file = file_chooser.FileChooserDialog(_("Select the file to open"),
			file_chooser.FileChooserDialog.OPEN,
			"*",macros.home_dir)

		response = open_file.run()
		if response == file_chooser.FileChooserDialog.ACCEPT:
			self.imageview.zoom_fit()
			self.load_boxes_from_file(open_file.get_filename())
			self.update_handler();
		open_file.destroy()


	def set_image(self,image):
		self.imageview.load_image(image,[],imageview.ImageViewer.ZOOM_FIT)
		self.image_name = "".join(image.split(".")[:-1])

	def set_list(self,list):
		image_height = self.imageview.get_original_height()
		list_ = []
		for item in list:
			width = item[3]-item[1]
			height = item[4]-item[2]
			y = image_height-item[2]-height
			list_.append((0,item[1],y,width,height,item[0]))
		
		self.imageview.set_list(list_,0)
	
	def get_list(self):
		image_height = self.imageview.get_original_height()
		list_ = []
		for item in self.imageview.get_list():
			y = round(image_height-(item[2]+item[4]))
			end_y = round(y+item[4])
			end_x = round(item[1]+item[3])
			list_.append((item[5],round(item[1]),y,end_x,end_y))
		return list_

class Dictionary(containers.Box):
	def __init__(self,file_path):
		containers.Box.__init__(self,containers.Box.VERTICAL)
		self.file_path = file_path
		
		box = containers.Box(containers.Box.HORIZONTAL)
		label = widget.Label(_("Find :"))
		box.add(label)
		self.entry = widget.Entry()
		self.entry.connect_activate_function(self.entry_activated)
		self.entry.set_hexpand(True)
		box.add(self.entry)
		self.add(box)

		self.textview = text_view.TextView()
		self.textview.set_highlight_color("#1572ffff0000")
		scrolled = containers.ScrollBox()
		scrolled.add(self.textview)
		scrolled.set_vexpand(True)
		self.add(scrolled)

	def load(self):
		with open(self.file_path+".txt") as file:
			text = file.read()
			self.textview.set_text(text)
			self.textview.move_cursor_to_line(1)

	def save(self):
		f = open(self.file_path+".txt","w")
		f.write(self.textview.get_text())
		f.close()

	def entry_activated(self,*data):
		text = self.entry.get_text()
		if(not self.textview.move_forward_to_word(text)):
			dlg = dialog.Dialog(_("Not found!"),(_("Yes"),
			dialog.Dialog.BUTTON_ID_1,_("No"), dialog.Dialog.BUTTON_ID_2))
			label = widget.Label(_("The word '{0}' not found! Search from start ?".format(text)))
			dlg.add_widget(label)
			label.show()
			response = dlg.run()
			if response == dialog.Dialog.BUTTON_ID_1:
				self.textview.move_cursor_to_line(1)
				dlg.destroy()
				self.entry_activated()
			dlg.destroy()

class TesseractTrainerGUI(TesseractTrainer):
	def __init__(self,image_list = []):
		win = TesseractTrainer(image_list)
		win.connect_close_function(self.close)
		win.show()
		loop.threads_init()
		loop.start_main_loop()
	def close(self,*data):
		loop.stop_main_loop()

if __name__ == "__main__":
	TesseractTrainerGUI([])
