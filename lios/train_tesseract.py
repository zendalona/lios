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

class TesseractTrainer(window.Window):
	def __init__(self,image_list=None):
		window.Window.__init__(self, title=_("Tesseract Trainer"))
		grid = containers.Grid()
		
		if( not ocr.ocr_engine_tesseract.OcrEngineTesseract.is_available()):
			label = widget.Label(_("Tesseract is not installed"))
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

		button_annotate_image = widget.Button("Auto-Annotate(Detect boxes)");
		button_annotate_image.connect_function(self.button_annotate_image_clicked);
		box_buttons.add(button_annotate_image)

		button_ocr_and_view = widget.Button("OCR & View Output");
		button_ocr_and_view.connect_function(self.button_ocr_and_view_clicked);
		box_buttons.add(button_ocr_and_view)

		button_train_image_box_pairs = widget.Button("Train Image-Box pairs");
		button_train_image_box_pairs.connect_function(self.train_image_box_pairs_clicked);

		self.box_editor = BoxEditor(self.on_image_view_box_list_updated)
		self.font_box = FontBox()
		
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
		label_select_word_dict = widget.Label(_("Select Word dict "));
		button_select_word_dict = widget.Button(_("Select word dict"));
		label_select_freequent_word_dict = widget.Label(_("Select Freequent Word dict "));
		button_select_freequent_word_dict = widget.Button(_("Select Freequent Word dict"));
		label_select_punctation_dict = widget.Label(_("Select Punctuation dict "));
		button_select_punctation_dict = widget.Button(_("Select Punctuation dict "));
		label_select_number_dict = widget.Label(_("Select Number dict "));
		button_select_number_dict = widget.Button(_("Select Number dict "));
		label_select_word_with_digit_dict = widget.Label(_("Select Word with digit  dict "));
		button_select_word_with_digit_dict = widget.Button(_("Select Word with digit  dict "));
		
		seperator_user_words = widget.Separator()
		
		label_user_words = widget.Label(_("User Words "));
		text_view_user_words = text_view.TextView()
		text_view_user_words.set_border_width(10);
		
		button_set_dictionary = widget.Button("Apply Dictionary's ")
		
		
		grid_set_dictionary = containers.Grid()
		grid_set_dictionary.add_widgets([(label_select_word_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_word_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_freequent_word_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_freequent_word_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_punctation_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_punctation_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_number_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_number_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_word_with_digit_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_word_with_digit_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(seperator_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		containers.Grid.NEW_ROW,
		(label_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(text_view_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(button_set_dictionary,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)]);
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
		containers.Grid.NEW_ROW,(button_close,5,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])
		
		
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
		spinbutton_writing_char_spacing_automatic = widget.SpinButton(0,0,50)

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

			# Remove previous image
			if (os.path.isfile("/tmp/tesseract-train/tmp_tess_image.tif")):
				os.remove("/tmp/tesseract-train/tmp_tess_image.tif");
			#generating image
			name = time.strftime("%Y-%m-%d,%H:%M:%S")
			cmd = "text2image --text=/tmp/tesseract-train/input_file.txt --font={0} --ptsize={1} --writing_mode={2} \
			--char_spacing={3} --resolution={4} --exposure={5} --degrade_image={6} --ligatures={7} \
			--fonts_dir={8} --outputbase=/tmp/tesseract-train/{9}".format(font,font_size,writing_mode,char_space,resolution,exposure,degrade,ligature,fonts_dir,name)
			print(cmd)
			self.output_terminal.run_command(cmd)

			# Wait for image file
			os.system("while [ ! -f /tmp/tesseract-train/{0}.tif ]; do sleep 1; done".format(name))
			self.icon_view_image_list.add_item("/tmp/tesseract-train/{0}.tif".format(name))
			self.make_box_file_for_image("/tmp/tesseract-train/{0}.tif".format(name))
			f = open("/tmp/tesseract-train/{0}.tif.font_desc".format(name),"w")
			f.write(font)
			f.close()
		dlg.destroy()

	def on_iconview_item_selected(self,data):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name):
			self.box_editor.set_image(name[0])
			try:
				self.box_editor.load_boxes_from_file(".".join(name[0].split(".")[:-1])+".box")
				font = open(name[0]+".font_desc").read()
				self.font_box.set_font(font)
			except:
				pass

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

	def language_combobox_changed(self,*data):
		active = self.combobox_language.get_active()

		# While resetting combobox after training the active will be -1
		if ( active <= len(self.languages) and active != -1 ):
			self.language = self.languages[active]

			#Removing all files in /tmp/tesseract-train/
			shutil.rmtree("/tmp/tesseract-train/")
			os.mkdir("/tmp/tesseract-train/")

			cmd = "combine_tessdata -u {0}/{1}.traineddata /tmp/tesseract-train/file".format(self.tessdata_dir,self.language)
			self.output_terminal.run_command(cmd)
			os.system("while [ ! -f /tmp/tesseract-train/file.unicharset ]; do sleep 0.1; done")

			#setting ambiguous table
			self.treeview_ambiguous.clear()
			self.import_ambiguous_list_from_file("/tmp/tesseract-train/file.unicharambigs")

	def button_add_image_box_pair_clicked(self,*data):
		file_chooser = FileChooserDialog(_("Select images to import"),
				FileChooserDialog.OPEN,macros.supported_image_formats,
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
					for image_file in no_box_file_image_list:
						self.make_box_file_for_image(image_file)
				dlg.destroy()

			if (no_font_desc_file_image_list != []):
				dlg = dialog.Dialog(_("No curresponding font_desc files found!"),
				(_("No"), dialog.Dialog.BUTTON_ID_2,_("Yes"), dialog.Dialog.BUTTON_ID_1))
				label = widget.Label(_("Do you want to fill it with following font ?"))
				fontbox = FontBox()
				fontbox.set_font("Sans 10")
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
		self.icon_view_image_list.remove_selected_items()


	def button_annotate_image_clicked(self,*data):
		image_list = self.icon_view_image_list.get_selected_item_names()
		for image in image_list:
			self.make_box_file_for_image(image)

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

	def make_box_file_for_image(self,filename):
		# Removing previous box files if exist -- Bugs exist :(
		self.output_terminal.run_command("rm -f /tmp/tesseract-train/batch.nochop.box")
		
		self.output_terminal.run_command("cd /tmp/tesseract-train/")
		self.output_terminal.run_command("convert {0} -background white -flatten +matte file.tif".format(filename));
		self.output_terminal.run_command("tesseract file.tif --tessdata-dir {0} -l {1} batch.nochop makebox".format(self.tessdata_dir,self.language));

		# Wait for box file
		os.system("while [ ! -f /tmp/tesseract-train/batch.nochop.box ]; do sleep .1; done")
		os.system("count=100; while [ ! -s /tmp/tesseract-train/batch.nochop.box ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done")
		os.system("cp /tmp/tesseract-train/batch.nochop.box {0}.box".format(".".join(filename.split(".")[:-1])))


	def train_image_box_pairs_clicked(self,*data):
		image_list = self.icon_view_image_list.get_selected_item_names()
		self.output_terminal.run_command("cd /tmp/tesseract-train/")

		if (image_list == []):
			return

		tr_list = ""
		for image in image_list:
			image_name_without_extension = ".".join(image.split(".")[:-1])
			tr_name =  ".".join((image.split("/")[-1]).split(".")[:-1])+".box.tr"

			self.output_terminal.run_command("tesseract --tessdata-dir {0} -l {1} {2} {3}.box nobatch box.train".format(self.tessdata_dir,self.language,image,image_name_without_extension));
			self.output_terminal.run_command("mv {0}.box.tr /tmp/tesseract-train/{1}".format(image_name_without_extension,tr_name))
			
			#font = font_desc.split(" ")[0]
			italic = 0;
			#if ("italic" in font_desc.lower()):
			#	italic = 1;
			
			bold = 0
			#if ("bold" in font_desc.lower()):
			#	bold = 1;
			
			font="sans"
			tr_list = tr_list+tr_name+" "

		self.output_terminal.run_command("unicharset_extractor -D /tmp/tesseract-train/ "+(" ".join(image_list).replace(".tif",".box")));

		self.output_terminal.run_command("echo '{0} {1} {2} 0 0 0' > font_properties".format(font,italic,bold));
		self.output_terminal.run_command("shapeclustering -F font_properties -U unicharset "+tr_list);
		self.output_terminal.run_command("mftraining -F font_properties -U unicharset -O unicharset "+tr_list);
		self.output_terminal.run_command("cntraining "+tr_list);

		self.output_terminal.run_command("mv inttemp file.inttemp");
		self.output_terminal.run_command("mv normproto file.normproto");

		self.output_terminal.run_command("mv pffmtable file.pffmtable");
		self.output_terminal.run_command("mv shapetable file.shapetable");
		self.output_terminal.run_command("mv unicharset file.unicharset")
		self.output_terminal.run_command("combine_tessdata file.");
		self.place_traineddata("/tmp/tesseract-train/file.traineddata",self.language)

	def button_ocr_and_view_clicked(self,*data):
		name = self.icon_view_image_list.get_selected_item_names()
		if(name == []):
			return;

		#self.output_terminal.run_command("mkdir /tmp/tesseract-train/tessdata");
		#self.output_terminal.run_command("cp /tmp/tesseract-train/file.traineddata /tmp/tesseract-train/tessdata/");
		#self.output_terminal.run_command("tesseract /tmp/tesseract-train/file.tif /tmp/tesseract-train/output --tessdata-dir /tmp/tesseract-train/ -l"+image);
		self.output_terminal.run_command("tesseract {0} /tmp/tesseract-train/output -l {1}".format(name[0],self.language));

		# Wait for output
		os.system("while [ ! -f /tmp/tesseract-train/output.txt ]; do sleep .1; done")
		os.system("count=100; while [ ! -s /tmp/tesseract-train/output.txt ] && [ $count -ge 0 ]; do sleep .1; count=$(($count-1)); done")

		dlg = dialog.Dialog(_("Ocr output"),(_("Close"), dialog.Dialog.BUTTON_ID_1))
		tv = text_view.TextView()
		sb = containers.ScrollBox()
		sb.add(tv)
		tv.set_vexpand(True)
		tv.set_hexpand(True)
		tv.set_text(open("/tmp/tesseract-train/output.txt").read())
		os.system("rm /tmp/tesseract-train/output.txt")
		dlg.set_default_size(500,400)
		dlg.add_widget(sb)
		dlg.show_all()
		response = dlg.run()
		dlg.destroy()

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
		self.fontbutton.connect_function(self.font_changed)
		self.entry.set_text(self.fontbutton.get_font_name())
		self.add(label)
		self.add(self.entry)
		self.add(self.fontbutton)
		self.show_all()

	def font_changed(self,*data):
		fontname = self.fontbutton.get_font_name()
		self.entry.set_text(fontname)
		
	def set_font(self,font_desc):
		self.fontbutton.set_font_name(font_desc)
		self.entry.set_text(self.fontbutton.get_font_name())

	def get_font(self):
		return self.entry.get_text()
		


class BoxEditor(containers.Box):
	def __init__(self,update_handler):
		containers.Box.__init__(self,containers.Box.VERTICAL)
		self.imageview = imageview.ImageViewer()
		self.imageview.connect("list_updated",self.list_updated_event_handler);
		self.update_handler = update_handler

		self.image_name = ""

		button_zoom_in = widget.Button(_("Zoom-In"))
		button_zoom_in.connect_function(self.imageview.zoom_in)
		button_zoom_out = widget.Button(_("Zoom-Out"))
		button_zoom_out.connect_function(self.imageview.zoom_out)
		button_save = widget.Button(_("Export-Boxes"))
		button_save.connect_function(self.save_boxes_dialog)
		button_load = widget.Button(_("Load-Boxes"))
		button_load.connect_function(self.load_boxes_dialog)
		self.add(self.imageview)
		box1 = containers.Box(containers.Box.HORIZONTAL)
		box1.add(button_zoom_in)
		box1.add(button_zoom_out)
		box1.add(button_save)
		box1.add(button_load)
		box1.set_hexpand(True)
		button_zoom_in.set_hexpand(True)
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
			self.load_boxes_from_file(open_file.get_filename())
			self.update_handler();
		open_file.destroy()


	def set_image(self,image):
		self.imageview.load_image(image,[],imageview.ImageViewer.ZOOM_FIT)
		self.image_name = "".join(image.split(".")[:-1])

	def set_list(self,list):
		image_height = self.imageview.get_height()
		list_ = []
		for item in list:
			width = item[3]-item[1]
			height = item[4]-item[2]
			y = image_height-item[2]-height
			list_.append((0,item[1],y,width,height,item[0]))
		
		self.imageview.set_list(list_,0)
	
	def get_list(self):
		image_height = self.imageview.get_height()
		list_ = []
		for item in self.imageview.get_list():
			y = image_height-(item[2]+item[4])
			end_y = y+item[4]
			end_x = item[1]+item[3]
			list_.append((item[5],item[1],y,end_x,end_y))
		return list_
		
class TesseractTrainerGUI(TesseractTrainer):
	def __init__(self,image_list = []):
		win = TesseractTrainer(image_list)
		win.connect_close_function(self.close)
		win.show()
		loop.start_main_loop()
	def close(self,*data):
		loop.stop_main_loop()

if __name__ == "__main__":
	TesseractTrainerGUI([])
