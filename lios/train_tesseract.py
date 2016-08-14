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

class TesseractTrainer(window.Window):
	def __init__(self,image_list=None):
		window.Window.__init__(self, title="Tesseract Trainer")
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
		
		self.tree_view_image_list = tree_view.TreeView([("File name ",str,False)],self.tree_view_image_list_edited_callback)
		
		for item in image_list:
			self.tree_view_image_list.append((item,));
		button_train = widget.Button("Start Training");
		button_train.connect_function(self.button_manual_train_clicked);
			
		
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
		(self.tree_view_image_list,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),		
		(button_train,1,1,containers.Grid.NO_HEXPAND,containers.Grid.VEXPAND)])		
		
		notebook.add_page(_("Manual Training (using scanned images)"),grid_manual_methord);		


		# Automatic Training (using fonts)
		label_select_font_dir = widget.Label("Font Directory");
		button_select_font_dir = widget.Button("Chose");

		label_font_automatic = widget.Label("Font ");
		fontbutton_automatic = widget.FontButton();
				
		label_select_input_text = widget.Label("Input Text File");
		button_select_input_text = widget.Button("Chose");

		label_writing_mode = widget.Label("Writing Mode");
		combobox_writing_mode = widget.ComboBox();

		
		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_select_font_dir,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(button_select_font_dir,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(fontbutton_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(button_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(combobox_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND)])		
		
		notebook.add_page(_("Automatic Training (using fonts)"),grid_manual_methord);
		
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

	def close_trainer(self,*data):
		self.destroy();
	
	def ambiguous_edited_callback(self,*data):
		print ("edited")
	
	def tree_view_image_list_edited_callback(self,*data):
		print("hello");
	
	def language_combobox_changed(self,*data):
		active = self.combobox_language.get_active()

		# While resetting combobox after training the active will be -1
		if ( active <= len(self.languages) and active != -1 ):
			self.language = self.languages[active]

	def button_manual_train_clicked(self,*data):
		index = self.tree_view_image_list.get_selected_row_index()
		items = self.tree_view_image_list.get_list()
		item = items[index][0]
		item_name_without_extension = item.split(".")[0]
		
		font_desc = self.entry_font_manual.get_text()
		
		
		if (os.path.isfile("/tmp/batch.nochop.box")):
			os.remove("/tmp/batch.nochop.box");

		if (os.path.isfile("{0}.box".format(item_name_without_extension))):
			print("Deleting {0}.box".format(item_name_without_extension))
			os.remove("{0}.box".format(item_name_without_extension));

		self.output_terminal.run_command("convert {0} -background white -flatten {1}.tif".format(item,item_name_without_extension));
		self.output_terminal.run_command("tesseract {0}.tif -l {1} batch.nochop makebox".format(item_name_without_extension,self.language.split("-")[0]));
			
		self.output_terminal.run_command("cp /tmp/batch.nochop.box {}.box".format(item_name_without_extension));
		
		# Wait for box file
		os.system("while [ ! -f {0}.box ]; do sleep 1; done".format(item_name_without_extension))
		
		boxeditor = BoxEditorDialog()

		def train_with_boxes(*data):
			boxeditor.save_boxes_to_file(item_name_without_extension+".box")
			
			language = self.language
			self.output_terminal.run_command("tesseract {0}.tif {0}.box nobatch box.train -l {1}".format(item_name_without_extension,language));
			self.output_terminal.run_command("unicharset_extractor {0}.box".format(item_name_without_extension));
			
			font = font_desc.split(" ")[0]
			italic = 0;
			if ("italic" in font_desc.lower()):
				italic = 1;
			
			bold = 0
			if ("bold" in font_desc.lower()):
				bold = 1;
				 
			self.output_terminal.run_command("echo '{0} {1} {2} 0 0 0' > font_properties".format(font,italic,bold));
			self.output_terminal.run_command("shapeclustering -F font_properties -U unicharset {0}.box.tr".format(item_name_without_extension));
			self.output_terminal.run_command("mftraining -F font_properties -U unicharset -O {0}.unicharset {0}.box.tr".format(item_name_without_extension));
			self.output_terminal.run_command("cntraining {0}.box.tr".format(item_name_without_extension));
			
			self.output_terminal.run_command("mv inttemp {0}.inttemp".format(item_name_without_extension));
			self.output_terminal.run_command("mv normproto {0}.normproto".format(item_name_without_extension));
			self.output_terminal.run_command("mv pffmtable {0}.pffmtable".format(item_name_without_extension));
			self.output_terminal.run_command("mv shapetable {0}.shapetable".format(item_name_without_extension));
			self.output_terminal.run_command("combine_tessdata {0}.".format(item_name_without_extension));

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
				os.system("gksudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(item_name_without_extension,language));
				#self.output_terminal.run_command("gksudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(item_name_without_extension,language));
			else:
				os.system("gksudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(item_name_without_extension,language));
				#self.output_terminal.run_command("gksudo cp {0}.traineddata /usr/share/tessdata/{1}.traineddata".format(item_name_without_extension,language));

		boxeditor.set_image(item)
		boxeditor.load_boxes_from_file(item_name_without_extension+".box")

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
		self.imageview.show()
		self.maximize()
		self.add_widget(box)
		box.show_all()

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
		


if __name__ == "__main__":
	win = TesseractTrainer(["/home/linux/Desktop/TrainingNet/test.png",
							"/home/linux/Desktop/TrainingNet/test3.png",
							"/home/linux/Desktop/test2.png",
							"/home/linux/Desktop/test3.png"])
	win.show()
	loop.start_main_loop()		
