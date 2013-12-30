import os
import sys
import enchant
import subprocess
import configparser
from espeak import espeak
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

from lios import global_var



class lios_preferences:
	# FUNCTION TO Read PREFERENCES #
	def read_preferences(self):
		config = configparser.ConfigParser()
		if config.read('%s/Lios/.preferences.cfg'%(os.environ['HOME'])) != []:
			try:
				self.time_between_repeated_scanning=int(config.get('cfg',"time_between_repeated_scanning"))
				self.scan_resolution=int(config.get('cfg',"scan_resolution"))
				self.scan_brightness=int(config.get('cfg',"scan_brightness"))
				self.ocr_engine=config.get('cfg',"ocr_engine")
				self.scan_area=int(config.get('cfg',"scan_area"))
				self.auto_skew=int(config.get('cfg',"auto_skew"))			
				self.language=config.get('cfg',"language")
				self.number_of_pages_to_scan=int(config.get('cfg',"number_of_pages_to_scan"))#pages
				self.mode_of_rotation = int(config.get('cfg',"mode_of_rotation"))
				self.rotation_angle = int(config.get('cfg',"angle"))		
				self.page_numbering_type=int(config.get('cfg',"numbering_type"))
				self.scanner_driver=int(config.get('cfg',"scanner_driver"))						
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
				self.cam_take_time=int(config.get('cfg',"cam_take_time"))
				self.cam_waitkey=int(config.get('cfg',"cam_waitkey"))
				self.cam_device=int(config.get('cfg',"cam_device"))				
				self.mode_switch = True
			except:
				self.on_Restore_preferences_activate(self,data=None)
		else:
			self.on_Restore_preferences_activate(self,data=None)
			

	def on_Save_preferences_activate(self,wedget,data=None):
		save_preferences = gtk.FileChooserDialog(title="save_preferences as ",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		save_preferences.set_current_folder("%s/Lios"%(os.environ['HOME']))
		response = save_preferences.run()		
		if response == gtk.RESPONSE_OK:
			shutil.copy2("%s/Lios/.preferences.cfg"%(os.environ['HOME']),"%s.cfg"%(save_preferences.get_filename()))
			#self.notify("preferences saved as %s.cfg" % (save_preferences.get_filename()),False,None,True)
		save_preferences.destroy()



	def on_Load_preferences_activate(self,wedget,data=None):
		load_preferences = gtk.FileChooserDialog("Select the image",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		load_preferences.set_default_response(gtk.RESPONSE_OK)
		load_preferences.set_current_folder("%s/Lios"%(os.environ['HOME']))
		filter = gtk.FileFilter()
		filter.add_pattern("*.cfg")
		load_preferences.add_filter(filter)
		response = load_preferences.run()
		if response == gtk.RESPONSE_OK:
			shutil.copy2("%s"%(load_preferences.get_filename()),"%s/Lios/.preferences.cfg"%(os.environ['HOME']))
			self.read_preferences()
			#self.notify("preferences loaded from %s" % (load_preferences.get_filename()),False,None,True)
		self.set_dict("%s" % self.key_value[self.language])
		load_preferences.destroy()
		
		
				
	def on_Restore_preferences_activate(self,wedget,data=None):
		#Setting Default Values
		self.font="Georgia 14";self.highlight_font="Georgia 14";self.background_color="#000";self.font_color="#fff";self.highlight_color="#1572ffff0000"
		self.background_highlight_color="#00000bacffff";self.time_between_repeated_scanning=0;self.scan_resolution=300;self.scan_brightness=40;self.scan_area=0;self.ocr_engine="CUNEIFORM";self.language="eng"
		self.mode_of_rotation=0;self.number_of_pages_to_scan=100;self.page_numbering_type=0;self.starting_page_number=1;self.scanner_driver=1;self.auto_skew=0;self.rotation_angle=00;
		self.voice_message_state=1;self.voice_message_rate=170;self.voice_message_volume=150;self.voice_message_pitch=50;self.voice_message_voice=9;
		self.cam_take_time=7;self.cam_waitkey=30;self.cam_device=0;
		#Writing it to user configuration file
		self.set_preferences_to_file()				
		#self.notify("preferences restored!",False,None,True)

	def set_preferences_to_file(self):
		#Removing old configuration file
		try:
			os.remove('%s/Lios/.preferences.cfg'%(os.environ['HOME']))
		except:
			pass		
		config = configparser.ConfigParser()
		config.read('%s/Lios/.preferences.cfg'%(os.environ['HOME']))
		config.add_section('cfg')
		config.set('cfg',"time_between_repeated_scanning",str(self.time_between_repeated_scanning))
		config.set('cfg',"scan_resolution",str(self.scan_resolution))
		config.set('cfg',"scan_brightness",str(self.scan_brightness))
		config.set('cfg',"ocr_engine",str(self.ocr_engine))
		config.set('cfg',"scan_area",str(self.scan_area))
		config.set('cfg',"auto_skew",str(self.auto_skew))
		config.set('cfg',"language",str(self.language))
		config.set('cfg',"number_of_pages_to_scan",str(self.number_of_pages_to_scan))
		config.set('cfg',"mode_of_rotation",str(self.mode_of_rotation))
		config.set('cfg',"angle",str(self.rotation_angle))
		config.set('cfg',"numbering_type",str(self.page_numbering_type))
		config.set('cfg',"scanner_driver",str(self.scanner_driver))				
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
		config.set('cfg',"cam_take_time",str(self.cam_take_time))
		config.set('cfg',"cam_waitkey",str(self.cam_waitkey))
		config.set('cfg',"cam_device",str(self.cam_device))
		with open('{0}/Lios/.preferences.cfg'.format(os.environ['HOME']), 'w') as configfile:
			config.write(configfile)
	
	
	#Function for manipulating preferences		
	def preferences(self,wedget,data=None):
		self.preferences_guibuilder = Gtk.Builder()
		self.preferences_guibuilder.add_from_file("%s/ui/preferences.glade" %(global_var.data_dir))
		self.preferences_window = self.preferences_guibuilder.get_object("window")
		self.preferences_guibuilder.connect_signals(self)


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
		
		
		#ENGINE
		engine = self.preferences_guibuilder.get_object("combobox_engine")	
		engine.connect('changed', self.change_engine)
		set_engine = 0
		if self.ocr_engine == "CUNEIFORM":
			set_engine = 0
		elif self.ocr_engine == "TESSERACT":
			set_engine = 1
		else:
			set_engine = 2		
		engine.set_active(set_engine)
		
		#LANGUAGE
		self.language_cb = self.preferences_guibuilder.get_object("combobox_language")
		self.language_cb.connect('changed',self.change_language)
		renderer_text = Gtk.CellRendererText()
		self.language_cb.pack_start(renderer_text, True)
		self.language_cb.add_attribute(renderer_text, "text", 0)
		
		#Setting old language  
		number = 0
		for item in self.language_cb.get_model():
			if self.language == item[0]:
				self.language_cb.set_active(number)
			number += 1	
		
		#ROTATION
		rotation = self.preferences_guibuilder.get_object("combobox_rotation")
		rotation.connect("changed",self.change_rotation)
		rotation.set_active(self.mode_of_rotation)
		

		#DRIVER
		self.driver_cb = self.preferences_guibuilder.get_object("combobox_driver")
		self.driver_cb.set_active(self.scanner_driver)

		#DRIVER
		self.checkbutton_skew = self.preferences_guibuilder.get_object("checkbutton_skew")
		self.checkbutton_skew.set_active(self.auto_skew)
		

	
		#PAGE-NUMBARING
		numbering = self.preferences_guibuilder.get_object("combobox_page_type")
		numbering.connect("changed",self.change_numbering)
		numbering.set_active(self.page_numbering_type)
		
		
		#Cam_and_Webcam
		self.spinbutton_cam_time = self.preferences_guibuilder.get_object("spinbutton_cam_time")
		self.spinbutton_cam_time.set_value(self.cam_take_time)
		self.spinbutton_fps = self.preferences_guibuilder.get_object("spinbutton_fps")
		self.spinbutton_fps.set_value(self.cam_waitkey)
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
	
	def change_engine(self, engine):
		self.model_engine = engine.get_model()
		self.index_engine = engine.get_active()
		self.language_cb = self.preferences_guibuilder.get_object("combobox_language")
		ls = Gtk.ListStore(str)
		if self.model_engine[self.index_engine][0] == "CUNEIFORM":
			for i in 'eng' ,'ger','fra','rus','swe','spa','ita','ruseng','ukr','srp','hrv','pol','dan','por','dut','cze','rum','hun','bul','slo','lav','lit','est','tur':
				ls.append([i])				
		
		if self.model_engine[self.index_engine][0] == "TESSERACT":
			list = "afr","ara","aze","bel","ben","bul","cat","ces","chi-sim","chi-tra","chr","dan","deu","deu-frk","ell","eng","enm","epo","est","eus","fin","fra","frk","frm","glg","heb","hin","hrv","hun","ind","isl","ita","ita-old","jpn","kan","kor","lav","lit","mal","mkd","mlt","msa","nld","nor","pol","ron","rus","slk","slk-frak","slv","spa","spa-old","sqi","srp","swa","swe","tam","tel","tgl","tha","tur","ukr","vie"
			check_list = []
			check = subprocess.Popen(['ls', '/usr/share/tesseract-ocr/tessdata/'],stdout=subprocess.PIPE)
			for lan in check.stdout:
				lan = lan.decode('utf-8')
				if "." in lan:
					if lan.split(".")[0] in list:		
						if [lan.split(".")[0]] in check_list:
							pass
						else:
							ls.append([lan.split(".")[0]])
							check_list.append([lan.split(".")[0]])			
		
		self.language_cb.set_model(ls)			
		self.language_cb.set_active(0)					

	def change_language(self,language):
		self.model_language = language.get_model()
		self.index_language = language.get_active()	


	def change_rotation(self,rotation):
		self.model_rotation = rotation.get_model()
		self.index_rotation = rotation.get_active()
		if self.model_rotation[self.index_rotation][0] == "Manuel":
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
		try:
			language = (self.model_language[self.index_language][0])
		except AttributeError:
			language = self.language
		else:
			pass
		
		self.cam_take_time=self.spinbutton_cam_time.get_value_as_int()
		self.cam_waitkey=self.spinbutton_fps.get_value_as_int()
		self.cam_device=self.combobox_cam_device.get_active()
		
		
		self.voice_message_voice=self.combobox_voice.get_active()
		self.voice_message_rate=int(self.hscale_rate.get_value())
		self.voice_message_volume=int(self.hscale_volume.get_value())
		self.voice_message_pitch=int(self.hscale_pitch.get_value())
		if self.checkbutton_say.get_active() == True:
			self.voice_message_state = 1
		else:
			self.voice_message_state = 0
			
		
		self.font=self.font_button.get_font_name();self.highlight_font=self.fontbutton_highlight_button.get_font_name();
		self.background_color=self.background_color_button.get_color().to_string();self.font_color=self.font_color_button.get_color().to_string();
		self.highlight_color=self.highlight_color_button.get_color().to_string();self.time_between_repeated_scanning=self.time_spin.get_value_as_int();
		self.background_highlight_color=self.highlight_background_color_button.get_color().to_string();
		self.scan_resolution = self.re_spin.get_value_as_int();self.scan_brightness=self.bt_spin.get_value_as_int();self.scan_area=self.index_area;
		self.ocr_engine=self.model_engine[self.index_engine][0];self.language=language
		self.mode_of_rotation=self.index_rotation;self.number_of_pages_to_scan=self.pages_spin.get_value_as_int();self.page_numbering_type=self.index_numbering;
		self.starting_page_number=self.start_spin.get_value_as_int();self.scanner_driver=self.driver_cb.get_active()
		
		if self.angle_cb.get_visible() ==True:
			model_angle = self.angle_cb.get_model()
			self.rotation_angle = model_angle[self.angle_cb.get_active()][0]
		
		self.auto_skew = int(self.checkbutton_skew.get_active())
		self.activate_preferences()
		self.set_preferences_to_file()
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
		self.set_dict("%s" % self.key_value[self.language])
	
	def set_dict(self,language):
		try:
			self.dict = enchant.Dict(language)
		except	enchant.errors.DictNotFoundError:
			self.dict = enchant.Dict("en")
			dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.OK, "Dict not found!")
			dialog.format_secondary_text("Please install the aspell dict for your language({0}) and restart Lios.\n Otherwise spellchecker will be disabled and auto-rotation will work with english(fallback) ".format(language))
			dialog.run()
			dialog.destroy()				
		
		
