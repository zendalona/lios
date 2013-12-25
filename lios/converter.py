# coding: latin-1

###########################################################################
#    SBW - Sharada-Braille-Writer
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

from gi.repository import Gtk
from gi.repository import Gdk

import os
from subprocess import getoutput
from threading import Thread

from sbw_2_0 import global_var


class record:
	def __init__(self,text):
		to_convert = open("temp.txt",'w')
		to_convert.write(text)
		to_convert.close()
		
		builder = Gtk.Builder()
		builder.add_from_file("%s/ui/audio_converter.glade" % (global_var.data_dir))
		builder.connect_signals(self)
		self.audio_converter_window = builder.get_object("window")
			
			
			
		self.spinbutton_speed = builder.get_object("spinbutton_speed")
		self.spinbutton_pitch = builder.get_object("spinbutton_pitch")
		self.spinbutton_split = builder.get_object("spinbutton_split")
		self.spinbutton_vloume = builder.get_object("spinbutton_vloume")
		self.spinbutton_speed.set_value(170)
		self.spinbutton_pitch.set_value(50)
		self.spinbutton_split.set_value(5)
		self.spinbutton_vloume.set_value(100)
			
		voice_combo = builder.get_object("combobox_language_convert")
		
		list_store = Gtk.ListStore(str)
		output = getoutput("espeak --voices")
		for line in output.split("\n"):
			list_store.append([line.split()[3]])
		
		voice_combo.set_model(list_store)
		self.model_voice = voice_combo.get_model()
		self.index_voice = voice_combo.get_active()
		
				
		voice_combo.connect('changed', self.change_voice)
		self.audio_converter_window.show()		                

	def change_voice(self, voice):
		self.model_voice = voice.get_model()
		self.index_voice = voice.get_active()
		
	def close_audio_converter(self,widget,data=None):
		self.audio_converter_window.destroy()
		
	def convert_to_audio(self,widget,data=None):
		self.filename = Gtk.FileChooserDialog("Type the output wav name",None,Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK));
		self.filename.set_current_folder(global_var.home_dir)
		self.filename.run()
		self.file_to_output = self.filename.get_filename()
		self.filename.destroy()
		Thread(target=self.record_to_wave,args=()).start()
		self.audio_converter_window.destroy()

               
		
	def record_to_wave(self):
		os.system('espeak -a %s -v %s -f temp.txt -w %s.wav --split=%s -p %s -s %s' % (self.spinbutton_vloume.get_value(),self.model_voice[self.index_voice][0],self.file_to_output,self.spinbutton_split.get_value(),self.spinbutton_pitch.get_value(),self.spinbutton_speed.get_value()))
		os.system('espeak "Conversion finish and saved to %s"' % (self.file_to_output))
