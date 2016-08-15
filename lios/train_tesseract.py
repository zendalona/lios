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

		label_language = widget.Label(_("Language "));
		self.combobox_language = widget.ComboBox();
		self.combobox_language.connect_change_callback_function(self.language_combobox_changed);


		self.languages = []
		for item in ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_languages():
			self.combobox_language.add_item(item)
			self.languages.append(item)
		self.combobox_language.set_active(0)

		#Notebook
		notebook = containers.NoteBook()
		notebook.show_all()

		# Manual Training (using scanned images)
		label_font_manual = widget.Label("Font ");
		self.entry_font_manual = widget.Entry()
		self.fontbutton_manual = widget.FontButton();
		self.fontbutton_manual.connect_function(self.font_manual_changed)
		self.entry_font_manual.set_text(self.fontbutton_manual.get_font_name())
		
		seperator_select_images = widget.Separator()
		
		label_select_images = widget.Label(_("Select scanned images for training"));
		
		self.icon_view_image_list = icon_view.IconView()
		scroll_box_iconview = containers.ScrollBox()
		self.icon_view_image_list.set_vexpand(True)
		scroll_box_iconview.add(self.icon_view_image_list)
		
		for item in image_list:
			self.icon_view_image_list.add_item(item);
		self.icon_view_image_list.show()

		button_train = widget.Button("Start Training");
		button_train.connect_function(self.button_manual_train_clicked);

		button_add_image = widget.Button("Add Image");
		button_add_image.connect_function(self.button_manual_add_image);
			
		
		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_font_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.entry_font_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.fontbutton_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_images,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		containers.Grid.NEW_ROW,
		(seperator_select_images,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(scroll_box_iconview,2,2,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(button_add_image,1,1,containers.Grid.NO_HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(button_train,1,1,containers.Grid.NO_HEXPAND,containers.Grid.VEXPAND)])		
		
		notebook.add_page(_("Manual Training (using scanned images)"),grid_manual_methord);		


		# Automatic Training (using fonts)
		label_font_automatic = widget.Label(_("Font"));
		self.entry_font_automatic = widget.Entry()
		self.fontbutton_automatic = widget.FontButton();
		self.fontbutton_automatic.set_font("FreeMono")
		self.entry_font_automatic.set_editable(False)
		self.entry_font_automatic.set_text(self.fontbutton_automatic.get_font_name())
		self.fontbutton_automatic.connect_function(self.fontbutton_automatic_clicked)
		button_choose_font_automatic = widget.Button(_("Choose-Font-File"));
		button_choose_font_automatic.connect_function(self.button_choose_font_automatic_clicked)

		label_font_size = widget.Label(_("Font Size"));
		self.spin_font_size = widget.SpinButton(10,8,96)

		label_select_input_text = widget.Label(_("Input Text File"));
		self.entry_input_text_automatic = widget.Entry()
		self.entry_input_text_automatic.set_editable(False)
		button_select_input_text = widget.Button(_("Choose"));
		button_select_input_text.connect_function(self.button_select_input_text_clicked)

		label_writing_mode = widget.Label(_("Writing Mode"));
		self.combobox_writing_mode = widget.ComboBox();
		self.combobox_writing_mode.add_item("horizontal")
		self.combobox_writing_mode.add_item("vertical")
		self.combobox_writing_mode.add_item("vertical-upright")
		self.combobox_writing_mode.set_active(0)

		label_writing_char_spacing_automatic = widget.Label(_("Inter-character space"));
		self.spinbutton_writing_char_spacing_automatic = widget.SpinButton(0,0,50)

		label_writing_resolution_automatic = widget.Label(_("Resolution"));
		self.spinbutton_writing_resolution_automatic = widget.SpinButton(300,100,1200)

		self.check_button_writing_degrade_image_automatic = widget.CheckButton(_("Degrade-image"))

		label_writing_exposure_level_automatic = widget.Label(_("Exposure-Level"));
		self.spinbutton_writing_exposure_level_automatic = widget.SpinButton(0,0,50)

		self.check_button_writing_ligature_mode_automatic = widget.CheckButton(_("Ligatur-Mode"))

		button_generate_and_train = widget.Button(_("Generate and Train"))
		button_generate_and_train.connect_function(self.button_generate_and_train_clicked)
		
		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.entry_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(self.fontbutton_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(button_choose_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_font_size,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.spin_font_size,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.entry_input_text_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(button_select_input_text,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.combobox_writing_mode,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_char_spacing_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.spinbutton_writing_char_spacing_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_resolution_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.spinbutton_writing_resolution_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_exposure_level_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(self.spinbutton_writing_exposure_level_automatic,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(self.check_button_writing_degrade_image_automatic,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		(self.check_button_writing_ligature_mode_automatic,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(button_generate_and_train,4,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND)])
		
		notebook.add_page(_("Train using fonts"),grid_manual_methord);
		
		#Ambiguous Editor
		self.treeview_ambiguous = tree_view.TreeView([("match",str,False),
		("Replacement",int,True),("Mandatory",int,True)],self.ambiguous_edited_callback)
		notebook.add_page("Ambiguous",self.treeview_ambiguous);
		
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
		 
		
		self.output_terminal = terminal.Terminal("/tmp")
		scroll_box_output = containers.ScrollBox()
		scroll_box_output.add(self.output_terminal)
		paned = containers.Paned(containers.Paned.VERTICAL)
		paned.add(notebook);
		paned.add(scroll_box_output);
		
		
		
		button_close = widget.Button(_("Close"));
		button_close.connect_function(self.close_trainer);
		
		grid.add_widgets([(label_language,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		(self.combobox_language,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,(paned,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,(button_close,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])
		
		
		self.add(grid)
		grid.show_all()
		self.maximize()
	
	def font_manual_changed(self,*data):
		fontname = self.fontbutton_manual.get_font_name()
		self.entry_font_manual.set_text(fontname)

	def fontbutton_automatic_clicked(self,*data):
		fontname = self.fontbutton_automatic.get_font_name()
		self.entry_font_automatic.set_text(fontname)

	def button_choose_font_automatic_clicked(self,*data):
		file_chooser = FileChooserDialog(_("Select font file"),
				FileChooserDialog.OPEN,"*",
				  "/usr/share/fonts/")
		response = file_chooser.run()
		if response == FileChooserDialog.ACCEPT:
			font_file = file_chooser.get_filename()
			file_chooser.destroy()
			if (os.path.isfile(font_file)):
				self.entry_font_automatic.set_text(font_file)
		else:
			file_chooser.destroy()

	def button_select_input_text_clicked(self,*data):
		file_chooser = FileChooserDialog(_("Select input file"),
				FileChooserDialog.OPEN,macros.supported_text_formats,macros.home_dir)
		response = file_chooser.run()
		if response == FileChooserDialog.ACCEPT:
			font_file = file_chooser.get_filename()
			file_chooser.destroy()
			if (os.path.isfile(font_file)):
				self.entry_input_text_automatic.set_text(font_file)
		else:
			file_chooser.destroy()

	def close_trainer(self,*data):
		self.destroy();
	
	def ambiguous_edited_callback(self,*data):
		print ("edited")
	
	def language_combobox_changed(self,*data):
		active = self.combobox_language.get_active()

		# While resetting combobox after training the active will be -1
		if ( active <= len(self.languages) and active != -1 ):
			self.language = self.languages[active]

	def button_manual_add_image(self,*data):
		file_chooser = FileChooserDialog(_("Select images to add"),
				FileChooserDialog.OPEN,macros.supported_image_formats,
				  macros.home_dir)
		file_chooser.set_current_folder(macros.home_dir)
		file_chooser.set_select_multiple(True)
		response = file_chooser.run()
		if response == FileChooserDialog.ACCEPT:
			image_list = file_chooser.get_filenames()
			file_chooser.destroy()
			for item in image_list:
				self.icon_view_image_list.add_item(item);
		else:
			file_chooser.destroy()

	def button_generate_and_train_clicked(self,*data):
		font = self.entry_font_automatic.get_text()
		font = font.split(" ")[0]
		fonts_dir = "/usr/share/fonts"
		if("/" in font):
			fonts_dir = "/".join(font.split("/")[:-1])
			font = font.split("/")[-1].split(".")[0]

		font_size = self.spin_font_size.get_value()
		input_file = self.entry_input_text_automatic.get_text()

		active = self.combobox_writing_mode.get_active()
		writing_mode = ["horizontal","vertical","vertical-upright"][active]

		char_space = self.spinbutton_writing_char_spacing_automatic.get_value()
		resolution = self.spinbutton_writing_resolution_automatic.get_value()
		exposure = self.spinbutton_writing_exposure_level_automatic.get_value()
		degrade = int(self.check_button_writing_degrade_image_automatic.get_active())
		ligature = int(self.check_button_writing_ligature_mode_automatic.get_active())

		if(os.path.exists(input_file)):
			cmd = "text2image --text={0} --outputbase=/tmp/tmp_tess_image --font={1} --ptsize={2} --writing_mode={3} \
			--char_spacing={4} --resolution={5} --exposure={6} --degrade_image={7} --ligatures={8} \
			--fonts_dir={9}".format(input_file,font,font_size,writing_mode,char_space,resolution,exposure,degrade,ligature,fonts_dir)
			print(cmd)
			if (os.path.isfile("/tmp/tmp_tess_image.tif")):
				os.remove("/tmp/tmp_tess_image.tif");
			self.output_terminal.run_command(cmd)
			# Wait for image file
			os.system("while [ ! -f /tmp/tmp_tess_image.tif ]; do sleep 1; done")
			self.train_image("/tmp/tmp_tess_image.tif",font)
		else:
			dlg = dialog.Dialog(_("Input file not selected"),
			(_("Ok"), dialog.Dialog.BUTTON_ID_1))
			label = widget.Label(_("Please set the input text file"))
			dlg.add_widget(label)
			label.show()
			response = dlg.run()
			dlg.destroy()

	def button_manual_train_clicked(self,*data):
		items = self.icon_view_image_list.get_selected_item_names()
		font_desc = self.entry_font_manual.get_text()
		self.train_image(items[0],font_desc)

	def train_image(self,filename,font_desc):
		file_name_without_extension = filename.split(".")[0]
		
		if (os.path.isfile("/tmp/batch.nochop.box")):
			os.remove("/tmp/batch.nochop.box");

		if (os.path.isfile("{0}.box".format(file_name_without_extension))):
			print("Deleting {0}.box".format(file_name_without_extension))
			os.remove("{0}.box".format(file_name_without_extension));

		self.output_terminal.run_command("convert {0} -background white -flatten {1}.tif".format(filename,file_name_without_extension));
		self.output_terminal.run_command("tesseract {0}.tif -l {1} batch.nochop makebox".format(file_name_without_extension,self.language.split("-")[0]));
			
		self.output_terminal.run_command("cp /tmp/batch.nochop.box {}.box".format(file_name_without_extension));
		
		# Wait for box file
		os.system("while [ ! -f {0}.box ]; do sleep 1; done".format(file_name_without_extension))

		boxeditor = BoxEditorDialog()

		def train_with_boxes(*data):
			boxeditor.save_boxes_to_file(file_name_without_extension+".box")
			
			language = self.language
			self.output_terminal.run_command("tesseract {0}.tif {0}.box nobatch box.train -l {1}".format(file_name_without_extension,language));
			self.output_terminal.run_command("unicharset_extractor {0}.box".format(file_name_without_extension));
			
			font = font_desc.split(" ")[0]
			italic = 0;
			if ("italic" in font_desc.lower()):
				italic = 1;
			
			bold = 0
			if ("bold" in font_desc.lower()):
				bold = 1;
				 
			self.output_terminal.run_command("echo '{0} {1} {2} 0 0 0' > font_properties".format(font,italic,bold));
			self.output_terminal.run_command("shapeclustering -F font_properties -U unicharset {0}.box.tr".format(file_name_without_extension));
			self.output_terminal.run_command("mftraining -F font_properties -U unicharset -O {0}.unicharset {0}.box.tr".format(file_name_without_extension));
			self.output_terminal.run_command("cntraining {0}.box.tr".format(file_name_without_extension));
			
			self.output_terminal.run_command("mv inttemp {0}.inttemp".format(file_name_without_extension));
			self.output_terminal.run_command("mv normproto {0}.normproto".format(file_name_without_extension));
			self.output_terminal.run_command("mv pffmtable {0}.pffmtable".format(file_name_without_extension));
			self.output_terminal.run_command("mv shapetable {0}.shapetable".format(file_name_without_extension));
			self.output_terminal.run_command("combine_tessdata {0}.".format(file_name_without_extension));

			# Create tessdata dir if not existing
			self.output_terminal.run_command("mkdir -p "+os.environ['HOME']+"/tessdata/");

			if (os.path.isfile("/usr/share/tessdata/"+language+".traineddata")):
				dlg = dialog.Dialog(language+_(" Alrady exist! Please edit name to avoid replacing"),
				(_("Place it"), dialog.Dialog.BUTTON_ID_1))

				entry = widget.Entry()
				dlg.add_widget_with_label(entry,_("File Name : "))
				entry.set_text(language)
				response = dlg.run()
				language = entry.get_text()
				dlg.destroy()
			if(os.access('/usr/share/tessdata/', os.W_OK)):
				os.system("cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(file_name_without_extension,language));
			else:
				if ("/bin/pkexec" in subprocess.getoutput("whereis pkexec")):
					os.system("pkexec cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(file_name_without_extension,language));
				elif ("/bin/gksudo" in subprocess.getoutput("whereis gksudo")):
					os.system("gksudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(file_name_without_extension,language));
				elif ("/bin/kdesudo" in subprocess.getoutput("whereis kdesudo")):
					os.system("kdesudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(file_name_without_extension,language));
				elif ("/bin/gksu" in subprocess.getoutput("whereis gksu")):
					os.system("gksu cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(file_name_without_extension,language));
				else:
					dlg = dialog.Dialog(_("Copying output file failed"),
					(_("Ok"), dialog.Dialog.BUTTON_ID_1))
					label = widget.Label(_("Can't copy output trained data. Please make sure you have write access to /usr/share/tessdata/"))
					dlg.add_widget(label)
					label.show()
					response = dlg.run()
					dlg.destroy()


		boxeditor.set_image(filename)
		boxeditor.load_boxes_from_file(file_name_without_extension+".box")

		response = boxeditor.run()

		if (response == dialog.Dialog.BUTTON_ID_1):
			boxeditor.destroy()
			train_with_boxes()
			self.languages = []
			self.combobox_language.clear()
			for item in ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_languages():
				self.combobox_language.add_item(item)
				self.languages.append(item)
			self.combobox_language.set_active(0)
		else:
			boxeditor.destroy()

		
		


class BoxEditorDialog(dialog.Dialog):
	def __init__(self):
		dialog.Dialog.__init__(self, _("Tesseract Trainer"),(_("Train"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2));
		self.imageview = imageview.ImageViewer()

		self.image_name = ""

		button_zoom_in = widget.Button(_("Zoom-In"))
		button_zoom_in.connect_function(self.imageview.zoom_in)
		button_zoom_out = widget.Button(_("Zoom-Out"))
		button_zoom_out.connect_function(self.imageview.zoom_out)
		button_save = widget.Button(_("Save-Boxes"))
		button_save.connect_function(self.save_boxes_dialog)
		button_load = widget.Button(_("Load-Boxes"))
		button_load.connect_function(self.load_boxes_dialog)
		box = containers.Box(containers.Box.VERTICAL)
		box.add(self.imageview)
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
		box.add(box1)
		self.connect_configure_event_handler(self.configure_event)
		self.imageview.show()
		self.maximize()
		self.add_widget(box)
		box.show_all()

	def configure_event(self,*arg):
		width,height = self.get_size()
		self.imageview.set_position(width-400)


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
			list_.append((spl[0],float(spl[1]),float(spl[2]),float(spl[3]),float(spl[4]),float(spl[5])))
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
	
	def close(self,*data):
		self.destroy()
		
class TesseractTrainerGUI(TesseractTrainer):
	def __init__(self,image_list = []):
		win = TesseractTrainer(image_list)
		win.show()
		loop.start_main_loop()

if __name__ == "__main__":
	TesseractTrainerGUI([])
