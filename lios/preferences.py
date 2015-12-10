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


import configparser
import shutil
from lios.ui.gtk import widget
from lios.ui.gtk import containers
from lios.ui.gtk import loop
from lios.ui.gtk import dialog

from lios import speech
from lios import localization

_ = localization._


class lios_preferences:
	def __init__(self):
		
		#Setting Default Values
		self.font="Georgia 14";self.highlight_font="Georgia 14";
		self.background_color="#000";self.font_color="#fff";
		self.highlight_color="#1572ffff0000";
		self.background_highlight_color="#00000bacffff";
		self.speech_module=0;self.speech_language=0;
		self.speech_rate=0;self.speech_pitch=0;self.speech_volume=100;
		self.time_between_repeated_scanning=0;self.scan_resolution=300;
		self.scan_driver=1;self.scanner_cache_calibration=1;
		self.scan_brightness=100;self.scan_area=0;self.insert_position=2;
		self.ocr_engine=0;self.language=0;self.mode_of_rotation=0;
		self.number_of_pages_to_scan=100;self.page_numbering_type=0;
		self.starting_page_number=1;self.scanner_mode_switching=1;
		self.rotation_angle=00;
		self.available_scanner_drivers = []
		self.available_ocr_engine_list = []

	def set_avalable_scanner_drivers(self,list):
		self.available_scanner_drivers = list

	def set_avalable_ocr_engines(self,list):
		self.available_ocr_engine_list = list
		
	# FUNCTION TO Read PREFERENCES #
	def set_from_file(self,filename):
		config = configparser.ConfigParser()
		if config.read(filename) != []:
			try:
				self.time_between_repeated_scanning=int(config.get('cfg',"time_between_repeated_scanning"))
				self.scan_resolution=int(config.get('cfg',"scan_resolution"))
				self.scan_brightness=int(config.get('cfg',"scan_brightness"))
				self.ocr_engine=int(config.get('cfg',"ocr_engine"))
				self.scan_area=int(config.get('cfg',"scan_area"))
				self.scan_driver=int(config.get('cfg',"scan_driver"))
				self.insert_position=int(config.get('cfg',"insert_position"))
				self.language=int(config.get('cfg',"language"))
				self.speech_module=int(config.get('cfg',"speech_module"))
				self.speech_language=int(config.get('cfg',"speech_language"))
				self.speech_rate=int(config.get('cfg',"speech_rate"))
				self.speech_volume=int(config.get('cfg',"speech_volume"))
				self.speech_pitch=int(config.get('cfg',"speech_pitch"))
				self.number_of_pages_to_scan=int(config.get('cfg',"number_of_pages_to_scan"))#pages
				self.mode_of_rotation = int(config.get('cfg',"mode_of_rotation"))
				self.rotation_angle = int(config.get('cfg',"rotation_angle"))		
				self.page_numbering_type=int(config.get('cfg',"numbering_type"))
				self.scanner_mode_switching=int(config.get('cfg',"scanner_mode_switching"))
				self.scanner_cache_calibration=int(config.get('cfg',"scanner_cache_calibration"))						
				self.starting_page_number=int(config.get('cfg',"starting_page_number"))
				self.background_color=config.get('cfg',"background_color")
				self.font_color=config.get('cfg',"font_color")
				self.highlight_color=config.get('cfg',"highlight_color")
				self.background_highlight_color=config.get('cfg',"highlight_background_color")
				self.font=config.get('cfg',"font")
				self.highlight_font=config.get('cfg',"highlight_font")				
				self.require_scanner_refresh = True
			except:
				self.__init__()
		else:
			self.__init__()

	def save_to_file(self,filename):
		#Removing old configuration file
		try:
			os.remove(filename)
		except:
			pass		
		config = configparser.ConfigParser()
		config.add_section('cfg')
		config.set('cfg',"time_between_repeated_scanning",str(self.time_between_repeated_scanning))
		config.set('cfg',"scan_resolution",str(self.scan_resolution))
		config.set('cfg',"scan_brightness",str(self.scan_brightness))
		config.set('cfg',"ocr_engine",str(self.ocr_engine))
		config.set('cfg',"insert_position",str(self.insert_position))
		config.set('cfg',"scan_area",str(self.scan_area))
		config.set('cfg',"scan_driver",str(self.scan_driver))
		config.set('cfg',"language",str(self.language))
		config.set('cfg',"speech_module",str(self.speech_module))
		config.set('cfg',"speech_language",str(self.speech_language))
		config.set('cfg',"speech_pitch",str(self.speech_pitch))
		config.set('cfg',"speech_volume",str(self.speech_volume))
		config.set('cfg',"speech_rate",str(self.speech_rate))
		config.set('cfg',"number_of_pages_to_scan",str(self.number_of_pages_to_scan))
		config.set('cfg',"mode_of_rotation",str(self.mode_of_rotation))
		config.set('cfg',"rotation_angle",str(self.rotation_angle))
		config.set('cfg',"numbering_type",str(self.page_numbering_type))
		config.set('cfg',"scanner_mode_switching",str(self.scanner_mode_switching))
		config.set('cfg',"scanner_cache_calibration",str(self.scanner_cache_calibration))				
		config.set('cfg',"starting_page_number",str(self.starting_page_number))
		config.set('cfg',"background_color",str(self.background_color))
		config.set('cfg',"font_color",str(self.font_color))
		config.set('cfg',"highlight_color",str(self.highlight_color))
		config.set('cfg',"highlight_background_color",str(self.background_highlight_color))
		config.set('cfg',"font",str(self.font))
		config.set('cfg',"highlight_font",str(self.highlight_font))
		with open(filename, 'w') as configfile:
			config.write(configfile)


	def update_page_number(self):
		if (self.page_numbering_type == 0):
			self.starting_page_number = self.starting_page_number + 1
		else:
			self.starting_page_number = self.starting_page_number + 2

	def get_page_number_as_string(self):
		if (self.page_numbering_type == 0):
			return ("{0}".format(self.starting_page_number))
		else:
			return ("{0}-{1}".format(self.starting_page_number,self.starting_page_number + 1))
	
	
	#Function for manipulating preferences		
	def open_configure_dialog(self,page=0):
		def change_engine(*data):
			index_engine = combobox_engine.get_active()
			combobox_language.clear()
			for item in self.available_ocr_engine_list[index_engine][1]:
				combobox_language.add_item(item)
			combobox_language.set_active(self.language)

		def change_speech_module(*data):
			index_engine = combobox_speech_module.get_active()
			combobox_speech_language.clear()
			test = speech.Speech()
			list = test.list_output_modules()
			test.set_output_module(list[index_engine])
			for item in test.list_voices():
				combobox_speech_language.add_item(item)
			combobox_speech_language.set_active(self.speech_language)

		def change_mode_of_rotation(*data):
			if(combobox_mode_of_rotation.get_active() == 2):
				combobox_angle.show()
				self.label_angle.show()
			else:
				combobox_angle.hide()
				self.label_angle.hide()


		self.require_scanner_refresh = False
		
		#Notebook
		notebook = containers.NoteBook()
		notebook.show_all()
		
		#GENERAL - PAGE #########	
		label_font = widget.Label(_("Font"))
		fontbutton_font = widget.FontButton()
		fontbutton_font.set_font_name(self.font)
		label_font.set_mnemonic_widget(fontbutton_font)

		label_font_color = widget.Label(_("Font Color"))
		colorbutton_font = widget.ColorButton()
		colorbutton_font.set_color_from_string(self.font_color)
		label_font_color.set_mnemonic_widget(colorbutton_font)
		

		label_background_color = widget.Label(_("Background Color"))
		colorbutton_background = widget.ColorButton()
		colorbutton_background.set_color_from_string(self.background_color)
		label_background_color.set_mnemonic_widget(colorbutton_background)
		

		label_highlight_font = widget.Label(_("Highlight Font"))
		fontbutton_highlight_font = widget.FontButton()
		fontbutton_highlight_font.set_font_name(self.highlight_font)
		label_highlight_font.set_mnemonic_widget(fontbutton_highlight_font)
		
		label_highlight_color = widget.Label(_("Highlight Color"))
		colorbutton_highlight = widget.ColorButton()
		colorbutton_highlight.set_color_from_string(self.highlight_color)
		label_highlight_color.set_mnemonic_widget(colorbutton_highlight)

		label_highlight_background = widget.Label(_("Highlight Background"))
		colorbutton_highlight_background = widget.ColorButton()
		colorbutton_highlight_background.set_color_from_string(self.background_highlight_color)
		label_highlight_background.set_mnemonic_widget(colorbutton_highlight_background)
		
		label_speech_module = widget.Label(_("Speech-Module"))
		combobox_speech_module = widget.ComboBox()
		for item in speech.Speech().list_output_modules():
			combobox_speech_module.add_item(item)
		combobox_speech_module.connect_change_callback_function(change_speech_module)
		label_speech_module.set_mnemonic_widget(combobox_speech_module)		

		label_speech_language = widget.Label(_("Speech-Language"))
		combobox_speech_language = widget.ComboBox()
		combobox_speech_module.set_active(self.speech_module)
		combobox_speech_language.set_active(self.speech_language)
		label_speech_language.set_mnemonic_widget(combobox_speech_language)

		label_speech_rate = widget.Label(_("Speech-Rate"))
		spin_speech_rate = widget.SpinButton(self.speech_rate,-100,100,1,10,0)
		label_speech_rate.set_mnemonic_widget(spin_speech_rate)
		label_speech_volume = widget.Label(_("Speech-Volume"))
		spin_speech_volume = widget.SpinButton(self.speech_volume,-100,100,1,10,0)
		label_speech_volume.set_mnemonic_widget(spin_speech_volume)
		label_speech_pitch = widget.Label(_("Speech-Pitch"))
		spin_speech_pitch = widget.SpinButton(self.speech_pitch,-100,100,1,10,0)
		label_speech_pitch.set_mnemonic_widget(spin_speech_pitch)

		
		grid_general = containers.Grid()
		grid_general.add_widgets(
			[(label_font,1,1),(fontbutton_font,1,1),containers.Grid.NEW_ROW,								  
			(label_font_color,1,1),(colorbutton_font,1,1),containers.Grid.NEW_ROW,								  
			(label_background_color,1,1),(colorbutton_background,1,1),containers.Grid.NEW_ROW,								  
			(label_highlight_font,1,1),(fontbutton_highlight_font,1,1),containers.Grid.NEW_ROW,								  
			(label_highlight_color,1,1),(colorbutton_highlight,1,1),containers.Grid.NEW_ROW,							  
			(label_highlight_background,1,1),(colorbutton_highlight_background,1,1),containers.Grid.NEW_ROW,
			(label_speech_module,1,1),(combobox_speech_module,1,1),containers.Grid.NEW_ROW,
			(label_speech_language,1,1),(combobox_speech_language,1,1),containers.Grid.NEW_ROW,
			(label_speech_rate,1,1),(spin_speech_rate,1,1),containers.Grid.NEW_ROW,
			(label_speech_pitch,1,1),(spin_speech_pitch,1,1),containers.Grid.NEW_ROW,
			(label_speech_volume,1,1),(spin_speech_volume,1,1)])
		notebook.add_page(_("General"),grid_general)
		grid_general.show_all()

		#RECOGNITION - PAGE ########
		#Engine		
		label_engine = widget.Label(_("Engine"))
		combobox_engine = widget.ComboBox()
		combobox_engine.connect_change_callback_function(change_engine)
		label_engine.set_mnemonic_widget(combobox_engine)
		
		for item in self.available_ocr_engine_list:
			combobox_engine.add_item(item[0])		
		
		#Language
		label_language = widget.Label(_("Language"))		
		combobox_language = widget.ComboBox()
		label_language.set_mnemonic_widget(combobox_language)
		
		#setting current engine - This can't be done before creating language combobox
		combobox_engine.set_active(self.ocr_engine)
		combobox_language.set_active(self.language)
		
		#insert_position
		label_insert_position = widget.Label(_("Insert Position"))
		combobox_insert_position = widget.ComboBox()
		combobox_insert_position.add_item(_("Start"))
		combobox_insert_position.add_item(_("Cursor"))
		combobox_insert_position.add_item(_("End"))
		combobox_insert_position.set_active(self.insert_position)
		label_insert_position.set_mnemonic_widget(combobox_insert_position)
		
		#Seperator
		seperator_1 = widget.Separator()

		#Mode of Rotation
		label_mode_of_rotation = widget.Label(_("Mode Of Rotation"))
		combobox_mode_of_rotation = widget.ComboBox()
		combobox_mode_of_rotation.add_item(_("Full Automatic"))
		combobox_mode_of_rotation.add_item(_("Partial Automatic"))
		combobox_mode_of_rotation.add_item(_("Manual"))
		combobox_mode_of_rotation.connect_change_callback_function(change_mode_of_rotation)
		label_mode_of_rotation.set_mnemonic_widget(combobox_mode_of_rotation)
		
		#Angle
		self.label_angle = widget.Label(_("Angle"))		
		combobox_angle = widget.ComboBox()
		combobox_angle.add_item(_("00"))
		combobox_angle.add_item(_("90"))
		combobox_angle.add_item(_("180"))
		combobox_angle.add_item(_("270"))
		self.label_angle.set_mnemonic_widget(combobox_angle)		

		#Seperator 2
		seperator_2 = widget.Separator()
		
		#Page-Numbering
		label_numbering_type = widget.Label(_("Page Numbering Type"))				
		combobox_numbering_type = widget.ComboBox()
		combobox_numbering_type.add_item(_("Single Page"))
		combobox_numbering_type.add_item(_("Double Page"))
		combobox_numbering_type.set_active(self.page_numbering_type)
		label_numbering_type.set_mnemonic_widget(combobox_numbering_type)
		
		#Starting Page Number
		label_starting_page_number = widget.Label(_("Starting Page Number"))
		spin_starting_page_number = widget.SpinButton(0,0,100000,1,5,0)
		spin_starting_page_number.set_value(self.starting_page_number)
		label_starting_page_number.set_mnemonic_widget(spin_starting_page_number)
		
		grid_recognition = containers.Grid()
		grid_recognition.add_widgets([
			(label_engine,1,1),(combobox_engine,1,1),containers.Grid.NEW_ROW,
			(label_language,1,1),(combobox_language,1,1),containers.Grid.NEW_ROW,
			(label_insert_position,1,1),(combobox_insert_position,1,1),containers.Grid.NEW_ROW,
			(seperator_1,2,1),containers.Grid.NEW_ROW,
			(label_mode_of_rotation,1,1),(combobox_mode_of_rotation,1,1),containers.Grid.NEW_ROW,
			(self.label_angle,1,1),(combobox_angle,1,1),containers.Grid.NEW_ROW,
			(seperator_2,2,1),containers.Grid.NEW_ROW,
			(label_numbering_type,1,1),	(combobox_numbering_type,1,1),containers.Grid.NEW_ROW,
			(label_starting_page_number,1,1),
			(spin_starting_page_number,1,1)])
		notebook.add_page(_("Recognition"),grid_recognition)
		grid_recognition.show_all()

		#setting current mode of rotation - This can't be done before creating angle combobox
		#also it should be here because the show_all function of grid will make angle combobox show again
		combobox_mode_of_rotation.set_active(self.mode_of_rotation)
		combobox_angle.set_active(self.rotation_angle)
		
		
		#SCANNING - PAGE ##############
		label_resolution = widget.Label(_("Resolution"))
		spin_resolution = widget.SpinButton(300,100,1200,1,5,0)
		spin_resolution.set_value(self.scan_resolution)
		label_resolution.set_mnemonic_widget(spin_resolution)

		label_brightness = widget.Label(_("Brightness"))
		spin_brightness = widget.SpinButton(50,0,100,1,5,0)
		spin_brightness.set_value(self.scan_brightness)
		label_brightness.set_mnemonic_widget(spin_brightness)

		label_scan_area = widget.Label(_("Scan Area"))
		combobox_scan_area = widget.ComboBox()
		label_scan_area.set_mnemonic_widget(combobox_scan_area)
		combobox_scan_area.add_item(_("Full Scan Area"))
		combobox_scan_area.add_item(_("Three Quarters"))
		combobox_scan_area.add_item(_("Two Quarters"))
		combobox_scan_area.add_item(_("One Quarters"))
		combobox_scan_area.set_active(self.scan_area)

		label_scan_driver = widget.Label(_("Driver"))
		combobox_scan_driver = widget.ComboBox()
		label_scan_driver.set_mnemonic_widget(combobox_scan_driver)		
		for item in self.available_scanner_drivers:
			combobox_scan_driver.add_item(item)
			print(item)
		print(self.scan_driver)
		combobox_scan_driver.set_active(self.scan_driver)

		sparator_3 = widget.Separator()
		
		label_number_of_pages_to_scan = widget.Label(_("Number of Pages to Scan"))
		spin_number_of_pages_to_scan = widget.SpinButton(10,2,100,1,5,0)
		spin_number_of_pages_to_scan.set_value(self.number_of_pages_to_scan)
		label_number_of_pages_to_scan.set_mnemonic_widget(spin_number_of_pages_to_scan)

		label_time_bitween_repeted_scanning = widget.Label(_("Time Bitween Repeted Scanning"))
		spin_time_bitween_repeted_scanning = widget.SpinButton(0,0,30,1,5,0)
		spin_time_bitween_repeted_scanning.set_value(self.time_between_repeated_scanning)
		label_time_bitween_repeted_scanning.set_mnemonic_widget(spin_time_bitween_repeted_scanning)

		sparator_4 = widget.Separator()

		checkbutton_scan_mode_switching = widget.CheckButton(_("Change to binary or lineart if possible"))
		checkbutton_scan_mode_switching.set_active(self.scanner_mode_switching)

		checkbutton_scanner_cache_calibration = widget.CheckButton(_("Cache Calibration"))
		checkbutton_scanner_cache_calibration.set_active(self.scanner_cache_calibration)
		
		grid_scanning = containers.Grid()
		grid_scanning.add_widgets([
			(label_resolution,1,1),(spin_resolution,1,1),containers.Grid.NEW_ROW,
			(label_brightness,1,1),(spin_brightness,1,1),containers.Grid.NEW_ROW,
			(label_scan_area,1,1),(combobox_scan_area,1,1),containers.Grid.NEW_ROW,
			(label_scan_driver,1,1),(combobox_scan_driver,1,1),containers.Grid.NEW_ROW,
			(sparator_3,2,1),containers.Grid.NEW_ROW,
			(label_number_of_pages_to_scan,1,1),(spin_number_of_pages_to_scan,1,1),containers.Grid.NEW_ROW,
			(label_time_bitween_repeted_scanning,1,1),(spin_time_bitween_repeted_scanning,1,1),containers.Grid.NEW_ROW,
			(sparator_4,2,1),containers.Grid.NEW_ROW,
			(checkbutton_scan_mode_switching,2,1),containers.Grid.NEW_ROW,
			(checkbutton_scanner_cache_calibration,2,1)])
		
		notebook.add_page(_("Scanning"),grid_scanning)
		grid_scanning.show_all()
		
		#Setting page
		notebook.set_current_page(page)
		
		dlg = dialog.Dialog(_("Lios Preferences"),(_("Apply"),dialog.Dialog.BUTTON_ID_1,_("Close"),dialog.Dialog.BUTTON_ID_2))
		dlg.add_widget(notebook)
		if (dlg.run()==True):
			self.font=fontbutton_font.get_font_name();
			self.font_color=colorbutton_font.get_color_as_string()			
			self.background_color=colorbutton_background.get_color_as_string()
			
			self.highlight_font=fontbutton_highlight_font.get_font_name();
			self.highlight_color=colorbutton_highlight.get_color_as_string()
			self.background_highlight_color=colorbutton_highlight_background.get_color_as_string()
			
			self.ocr_engine=combobox_engine.get_active()
			self.language=combobox_language.get_active()
			self.speech_module=combobox_speech_module.get_active()
			self.speech_language=combobox_speech_language.get_active()
			self.speech_rate=spin_speech_rate.get_value()
			self.speech_pitch=spin_speech_pitch.get_value()
			self.speech_volume=spin_speech_volume.get_value()
			self.insert_position=combobox_insert_position.get_active();
			self.mode_of_rotation=combobox_mode_of_rotation.get_active()
			self.rotation_angle = combobox_angle.get_active()
			self.page_numbering_type=combobox_numbering_type.get_active();
			self.starting_page_number=spin_starting_page_number.get_value_as_int();
			
			self.scan_resolution = spin_resolution.get_value_as_int();
			self.scan_brightness=spin_brightness.get_value_as_int();
			self.scan_area=combobox_scan_area.get_active();
			self.scan_driver=combobox_scan_driver.get_active();
			self.number_of_pages_to_scan=spin_number_of_pages_to_scan.get_value_as_int();
			self.time_between_repeated_scanning=spin_time_bitween_repeted_scanning.get_value_as_int();
			self.scanner_mode_switching=int(checkbutton_scan_mode_switching.get_active())
			self.scanner_cache_calibration=int(checkbutton_scanner_cache_calibration.get_active())
			
			dlg.destroy()
			return True
		dlg.destroy()
		return False

	
if "__main__" == __name__:
	a = lios_preferences()
	a.open_configure_dialog()
	a.open_configure_dialog()
	
	loop.start_main_loop()
		

	

