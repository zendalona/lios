# coding: latin-1

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
import enchant
import subprocess
import configparser
import shutil
from espeak import espeak
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

from lios import global_var



class lios_preferences:
	# FUNCTION TO Read PREFERENCES #
	def set_preferences_from_file(self,filename):
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
				self.auto_skew=int(config.get('cfg',"auto_skew"))			
				self.language=int(config.get('cfg',"language"))
				self.number_of_pages_to_scan=int(config.get('cfg',"number_of_pages_to_scan"))#pages
				self.mode_of_rotation = int(config.get('cfg',"mode_of_rotation"))
				self.rotation_angle = int(config.get('cfg',"angle"))		
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
				self.voice_message_state=int(config.get('cfg',"voice_message_state"))
				self.voice_message_voice=int(config.get('cfg',"voice_message_voice"))
				self.voice_message_rate=int(config.get('cfg',"voice_message_rate"))
				self.voice_message_volume=int(config.get('cfg',"voice_message_volume"))
				self.voice_message_pitch=int(config.get('cfg',"voice_message_pitch"))
				self.cam_x=int(config.get('cfg',"cam_x"))
				self.cam_y=int(config.get('cfg',"cam_y"))
				self.cam_device=int(config.get('cfg',"cam_device"))				
				self.require_scanner_refresh = True
			except:
				self.set_default_preferences(self,data=None)
		else:
			self.set_default_preferences(self,data=None)
			

	def on_Save_preferences_activate(self,wedget,data=None):
		save_preferences_dlg = Gtk.FileChooserDialog(title="save_preferences as ",
		action=Gtk.FileChooserAction.SAVE,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		save_preferences_dlg.set_current_folder("%s/Lios"%(os.environ['HOME']))
		response = save_preferences_dlg.run()		
		if response == Gtk.ResponseType.OK:
			shutil.copy2('{0}/.lios_preferences.cfg'.format(global_var.home_dir),
			"%s.cfg"%(save_preferences_dlg.get_filename()))
			#self.notify("preferences saved as %s.cfg" % (save_preferences_dlg.get_filename()),False,None,True)
		save_preferences_dlg.destroy()



	def on_Load_preferences_activate(self,wedget,data=None):
		load_preferences_dlg = Gtk.FileChooserDialog("Select the image",None,
		Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		load_preferences_dlg.set_default_response(Gtk.ResponseType.OK)
		load_preferences_dlg.set_current_folder("%s/Lios"%(os.environ['HOME']))
		filter = Gtk.FileFilter()
		filter.add_pattern("*.cfg")
		load_preferences_dlg.add_filter(filter)
		response = load_preferences_dlg.run()
		if response == Gtk.ResponseType.OK:
			self.set_preferences_from_file(load_preferences_dlg.get_filename())
			self.require_scanner_refresh = True
			self.activate_preferences()
			#self.notify("preferences loaded from %s" % (load_preferences_dlg.get_filename()),False,None,True)
		load_preferences_dlg.destroy()
		
		
				
	def set_default_preferences(self,wedget,data=None):
		#Setting Default Values
		self.font="Georgia 14";self.highlight_font="Georgia 14";
		self.background_color="#000";self.font_color="#fff";
		self.highlight_color="#1572ffff0000";
		self.background_highlight_color="#00000bacffff";
		self.time_between_repeated_scanning=0;self.scan_resolution=300;
		self.scan_brightness=100;self.scan_area=0;self.insert_position=2;
		self.ocr_engine=0;self.language=0;self.mode_of_rotation=0;
		self.number_of_pages_to_scan=100;self.page_numbering_type=0;
		self.starting_page_number=1;self.scanner_mode_switching=1;
		self.scanner_cache_calibration=1;self.auto_skew=0;self.rotation_angle=00;
		self.voice_message_state=0;self.voice_message_rate=170;
		self.voice_message_volume=150;self.voice_message_pitch=50;
		self.voice_message_voice=11;self.scan_driver=1;
		self.cam_x=1280;self.cam_y=800;self.cam_device=0;
		#Writing it to user configuration file
		self.save_preferences_to_file('{0}/.lios_preferences.cfg'.format(global_var.home_dir))				
		#self.notify("preferences restored!",False,None,True)
		self.require_scanner_refresh = True

	def save_preferences_to_file(self,filename):
		#Removing old configuration file
		try:
			os.remove(filename)
		except:
			pass		
		config = configparser.ConfigParser()
		config.read(filename)
		config.add_section('cfg')
		config.set('cfg',"time_between_repeated_scanning",str(self.time_between_repeated_scanning))
		config.set('cfg',"scan_resolution",str(self.scan_resolution))
		config.set('cfg',"scan_brightness",str(self.scan_brightness))
		config.set('cfg',"ocr_engine",str(self.ocr_engine))
		config.set('cfg',"insert_position",str(self.insert_position))
		config.set('cfg',"scan_area",str(self.scan_area))
		config.set('cfg',"scan_driver",str(self.scan_driver))
		config.set('cfg',"auto_skew",str(self.auto_skew))
		config.set('cfg',"language",str(self.language))
		config.set('cfg',"number_of_pages_to_scan",str(self.number_of_pages_to_scan))
		config.set('cfg',"mode_of_rotation",str(self.mode_of_rotation))
		config.set('cfg',"angle",str(self.rotation_angle))
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
		config.set('cfg',"voice_message_state",str(self.voice_message_state))
		config.set('cfg',"voice_message_voice",str(self.voice_message_voice))
		config.set('cfg',"voice_message_rate",str(self.voice_message_rate))
		config.set('cfg',"voice_message_volume",str(self.voice_message_volume))
		config.set('cfg',"voice_message_pitch",str(self.voice_message_pitch))
		config.set('cfg',"cam_x",str(self.cam_x))
		config.set('cfg',"cam_y",str(self.cam_y))
		config.set('cfg',"cam_device",str(self.cam_device))
		with open(filename, 'w') as configfile:
			config.write(configfile)
	
	
	#Function for manipulating preferences		
	def configure_preferences_dialog(self,wedget,data=None):
		self.preferences_guibuilder = Gtk.Builder()
		self.preferences_guibuilder.add_from_file("%s/ui/preferences.glade" %(global_var.data_dir))
		self.preferences_window = self.preferences_guibuilder.get_object("window")
		self.preferences_guibuilder.connect_signals(self)
		self.require_scanner_refresh = False


		#General
		
		#Font and font color
		self.start_spin = self.preferences_guibuilder.get_object("spinbutton_page_start")
		self.start_spin.set_value(self.starting_page_number)
		self.pages_spin = self.preferences_guibuilder.get_object("spinbutton_number_of_pages_to_scan")
		self.pages_spin.set_value(self.number_of_pages_to_scan)		
		
		self.background_color_button = self.preferences_guibuilder.get_object("colorbutton_background")
		self.background_color_button.set_color(Gdk.color_parse(self.background_color))	

		self.highlight_color_button = self.preferences_guibuilder.get_object("colorbutton_highlight")
		self.highlight_color_button.set_color(Gdk.color_parse(self.highlight_color))	

		self.highlight_background_color_button = self.preferences_guibuilder.get_object("colorbutton_highlight_background")
		self.highlight_background_color_button.set_color(Gdk.color_parse(self.background_highlight_color))
					
		self.font_color_button = self.preferences_guibuilder.get_object("colorbutton_font")		
		self.font_color_button.set_color(Gdk.color_parse(self.font_color))
			
		self.font_button = self.preferences_guibuilder.get_object("fontbutton")
		self.font_button.set_font_name(self.font)

		self.fontbutton_highlight_button = self.preferences_guibuilder.get_object("fontbutton_highlight")
		self.fontbutton_highlight_button.set_font_name(self.highlight_font)
		
		#Voice Message
		self.hscale_rate = self.preferences_guibuilder.get_object("scale_rate")
		self.hscale_rate.set_value(self.voice_message_rate)
		self.hscale_volume = self.preferences_guibuilder.get_object("scale_volume")
		self.hscale_volume.set_value(self.voice_message_volume)
		self.hscale_pitch = self.preferences_guibuilder.get_object("scale_pitch")
		self.hscale_pitch.set_value(self.voice_message_pitch)
		self.combobox_voice = self.preferences_guibuilder.get_object("combobox_voice")
		
		voice_store = Gtk.ListStore(str)		
		for item in espeak.list_voices():
			voice_store.append([item.name])
		
		self.combobox_voice.set_model(voice_store)
		renderer_text = Gtk.CellRendererText()
		self.combobox_voice.pack_start(renderer_text, True)
		self.combobox_voice.add_attribute(renderer_text, "text", 0)		
		self.combobox_voice.set_active(self.voice_message_voice)
		
		self.checkbutton_say = self.preferences_guibuilder.get_object("checkbutton_say")
		if self.voice_message_state == 1:
			self.checkbutton_say.set_active(True)
		else:
			self.checkbutton_say.set_active(False)
		

		
		# Scanning
		self.time_spin = self.preferences_guibuilder.get_object("spinbutton_time")
		self.re_spin = self.preferences_guibuilder.get_object("spinbutton_resolution")
		self.bt_spin = self.preferences_guibuilder.get_object("spinbutton_brightness")
		self.time_spin.set_value(self.time_between_repeated_scanning)
		self.re_spin.set_value(self.scan_resolution)
		self.bt_spin.set_value(self.scan_brightness)
		
		#Angle
		self.angle_cb = self.preferences_guibuilder.get_object("combobox_angle")
		self.label_angle = self.preferences_guibuilder.get_object("label_angle")
		
		#AREA						      
		area = self.preferences_guibuilder.get_object("combobox_scan_area")
		area.connect('changed', self.change_area)
		area.set_active(self.scan_area)

		#Driver
		self.scan_driver_old = self.scan_driver						      
		driver_combobox = self.preferences_guibuilder.get_object("combobox_scan_driver")
		driver_combobox.connect('changed', self.change_driver)

		driver_list_store = Gtk.ListStore(str)
		for item in self.available_driver_list:
			driver_list_store.append([item.name])
		driver_combobox.set_model(driver_list_store)
		
		renderer_text = Gtk.CellRendererText()
		driver_combobox.pack_start(renderer_text, True)
		driver_combobox.add_attribute(renderer_text, "text", 0)
		driver_combobox.set_active(self.scan_driver)

		#insert_position						      
		insert_position = self.preferences_guibuilder.get_object("combobox_insert_position")
		insert_position.connect('changed', self.change_insert_position)
		insert_position.set_active(self.insert_position)
		
		
		#ENGINE
		combobox_engine = self.preferences_guibuilder.get_object("combobox_engine")	
		combobox_engine.connect('changed', self.change_engine)
		
		self.ocr_engine_list_store = Gtk.ListStore(str)
		for item in self.available_ocr_engine_list:
			self.ocr_engine_list_store.append([item.name])
		combobox_engine.set_model(self.ocr_engine_list_store)
		
		renderer_text = Gtk.CellRendererText()
		combobox_engine.pack_start(renderer_text, True)
		combobox_engine.add_attribute(renderer_text, "text", 0)
		combobox_engine.set_active(self.ocr_engine)
		
		#LANGUAGE
		self.language_cb = self.preferences_guibuilder.get_object("combobox_language")
		renderer_text = Gtk.CellRendererText()
		self.language_cb.pack_start(renderer_text, True)
		self.language_cb.add_attribute(renderer_text, "text", 0)
		self.language_cb.set_active(self.language)	
		
		#ROTATION
		rotation = self.preferences_guibuilder.get_object("combobox_rotation")
		rotation.connect("changed",self.change_rotation)
		rotation.set_active(self.mode_of_rotation)
		

		#Mode Switching
		self.scanner_mode_switching_old = self.scanner_mode_switching
		self.checkbutton_scanner_mode_switching = self.preferences_guibuilder.get_object("checkbutton_scanner_mode_switching")
		self.checkbutton_scanner_mode_switching.set_active(self.scanner_mode_switching)
		
		#Cache Calibration
		self.scanner_cache_calibration_old = self.scanner_cache_calibration
		self.checkbutton_scanner_cache_calibration = self.preferences_guibuilder.get_object("checkbutton_scanner_cache_calibration")
		self.checkbutton_scanner_cache_calibration.set_active(self.scanner_cache_calibration)

		#Skew
		self.checkbutton_skew = self.preferences_guibuilder.get_object("checkbutton_skew")
		self.checkbutton_skew.set_active(self.auto_skew)
		

	
		#PAGE-NUMBARING
		numbering = self.preferences_guibuilder.get_object("combobox_page_type")
		numbering.connect("changed",self.change_numbering)
		numbering.set_active(self.page_numbering_type)
		
		
		#Cam_and_Webcam
		self.combobox_cam_resolution = self.preferences_guibuilder.get_object("combobox_cam_resolution")
		self.liststore_cam_resolution = self.preferences_guibuilder.get_object("liststore_cam_resolution")
		for intex,item in enumerate(self.liststore_cam_resolution):
			if (self.cam_x == item[1] and self.cam_y == item[2]):
				self.combobox_cam_resolution.set_active(intex)
						
		
		
		self.combobox_cam_device = self.preferences_guibuilder.get_object("combobox_cam_device")
		self.combobox_cam_device.set_active(self.cam_device)
		

		notebook = self.preferences_guibuilder.get_object("notebook")
		try:
			notebook.set_current_page(data)
		except TypeError:
			pass
		self.preferences_window.show()		
	
	#FUNCTIONS-COMBOBOX	
	def change_area(self, area):
		self.model_area = area.get_model()
		self.index_area = area.get_active()

	def change_driver(self, driver):
		self.model_driver = driver.get_model()
		self.index_driver = driver.get_active()

	def change_insert_position(self, insert_position):
		self.model_insert_position = insert_position.get_model()
		self.index_insert_position = insert_position.get_active()
		
	
	def change_engine(self, engine):
		self.model_engine = engine.get_model()
		self.index_engine = engine.get_active()
		
		self.language_cb = self.preferences_guibuilder.get_object("combobox_language")
		
		language_list_store = Gtk.ListStore(str)
		for item in self.available_ocr_engine_list[self.index_engine].get_available_languages():
			language_list_store.append([item])			
		
		self.language_cb.set_model(language_list_store)			
		self.language_cb.set_active(0)	


	def change_rotation(self,rotation):
		self.model_rotation = rotation.get_model()
		self.index_rotation = rotation.get_active()
		if self.model_rotation[self.index_rotation][0] == "Manual":
			self.angle_cb.show()
			self.label_angle.show()
			if int(self.rotation_angle) == 00:
				self.angle_cb.set_active(0)
			elif int(self.rotation_angle) == 90:
				self.angle_cb.set_active(1)
			elif int(self.rotation_angle) == 180:
				self.angle_cb.set_active(2)
			else:
				self.angle_cb.set_active(3)					
		else:
			self.angle_cb.hide()
			self.label_angle.hide()
		
	
	def change_numbering(self,numbering):
		self.model_numbering = numbering.get_model()
		self.index_numbering = numbering.get_active()

	
	#FUNCTIONS-BUTTONS
	def close_preferences(self,widget,data=None):
		#self.notify("Its-all-right!",False,None,True)
		self.preferences_window.destroy()

	def apply_preferences(self,widget,data=None):
		value=self.combobox_cam_resolution.get_active()
		self.cam_x = self.liststore_cam_resolution[value][1]
		self.cam_y = self.liststore_cam_resolution[value][2]
		self.cam_device=self.combobox_cam_device.get_active()
		
		
		self.voice_message_voice=self.combobox_voice.get_active()
		self.voice_message_rate=int(self.hscale_rate.get_value())
		self.voice_message_volume=int(self.hscale_volume.get_value())
		self.voice_message_pitch=int(self.hscale_pitch.get_value())
		self.voice_message_state = self.checkbutton_say.get_active()
			
		
		self.font=self.font_button.get_font_name();
		self.highlight_font=self.fontbutton_highlight_button.get_font_name();
		self.background_color=self.background_color_button.get_color().to_string();
		self.font_color=self.font_color_button.get_color().to_string();
		self.highlight_color=self.highlight_color_button.get_color().to_string();
		self.time_between_repeated_scanning=self.time_spin.get_value_as_int();
		self.background_highlight_color=self.highlight_background_color_button.get_color().to_string();
		self.scan_resolution = self.re_spin.get_value_as_int();
		self.scan_brightness=self.bt_spin.get_value_as_int();
		self.scan_area=self.index_area;self.scan_driver=self.index_driver;
		self.insert_position=self.index_insert_position;
		self.ocr_engine=self.index_engine;self.language=self.language_cb.get_active()
		self.mode_of_rotation=self.index_rotation;
		self.number_of_pages_to_scan=self.pages_spin.get_value_as_int();
		self.page_numbering_type=self.index_numbering;
		self.starting_page_number=self.start_spin.get_value_as_int();
		self.scanner_mode_switching=int(self.checkbutton_scanner_mode_switching.get_active())
		self.scanner_cache_calibration=int(self.checkbutton_scanner_cache_calibration.get_active())
		
		if self.angle_cb.get_visible() ==True:
			model_angle = self.angle_cb.get_model()
			self.rotation_angle = model_angle[self.angle_cb.get_active()][0]
		
		self.auto_skew = int(self.checkbutton_skew.get_active())
		if (self.scan_driver_old != self.scan_driver or self.scanner_mode_switching_old != self.scanner_mode_switching or self.scanner_cache_calibration_old != self.scanner_cache_calibration ):
			self.require_scanner_refresh = True
			self.scan_driver_old = self.scan_driver
			self.scanner_mode_switching_old = self.scanner_mode_switching
			self.scanner_cache_calibration_old = self.scanner_cache_calibration
			
		self.activate_preferences()
		self.save_preferences_to_file('{0}/.lios_preferences.cfg'.format(global_var.home_dir))
		self.preferences_window.destroy()

	
	def activate_preferences(self):
		espeak.set_parameter(espeak.Parameter.Rate,self.voice_message_rate)
		espeak.set_parameter(espeak.Parameter.Pitch,self.voice_message_pitch)
		espeak.set_parameter(espeak.Parameter.Volume,self.voice_message_volume)
		espeak.set_voice(espeak.list_voices()[self.voice_message_voice].name)
		
		self.highlight_tag = self.textbuffer.create_tag('Reading')
		self.highlight_tag.set_property('foreground',Gdk.color_parse(self.highlight_color).to_string())
		self.highlight_tag.set_property('font',self.highlight_font)
		self.highlight_tag.set_property('background',Gdk.color_parse(self.background_highlight_color).to_string())
		
		pangoFont = Pango.FontDescription(self.font)
		self.textview.modify_font(pangoFont)
		self.textview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.font_color))
		self.textview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.background_color))
		
		
		languages = self.available_ocr_engine_list[self.ocr_engine].get_available_languages()
		self.ocr_engine_object = self.available_ocr_engine_list[self.ocr_engine](languages[self.language])
		
		self.set_dict("%s" % self.dictionary_language_dict[languages[self.language]])
		if (self.require_scanner_refresh):
			self.scanner_refresh(self)
		

	
	def set_dict(self,language):
		try:
			self.dict = enchant.Dict(language)
		except	enchant.errors.DictNotFoundError:
			self.dict = enchant.Dict("en")
			dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,
			Gtk.ButtonsType.OK, "Dict not found!")
			
			dialog.format_secondary_text("Please install the aspell dict for your " +
			"language({0}) and restart Lios.\n Otherwise spellchecker will".format(language) + 
			"be disabled and auto-rotation will work with english(fallback) ")
			dialog.run()
			dialog.destroy()
