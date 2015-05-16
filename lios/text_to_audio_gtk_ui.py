#!/usr/bin/env python3

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

from gi.repository import Gtk
from gi.repository import Gdk

import os
from threading import Thread

from lios.text_to_audio import text_to_audio_converter


class record_ui:
	def __init__(self,text):
		builder = Gtk.Builder()
		builder.add_from_file("/usr/share/lios/ui/audio_converter.glade")
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
		
		
		self.ac_object = text_to_audio_converter(text)
		voice_combo = builder.get_object("combobox_language_convert")
		
		list_store = Gtk.ListStore(str)
		for item in self.ac_object.list_voices():
			list_store.append(item)
		
		voice_combo.set_model(list_store)
		voice_combo.set_active(1)
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
		filename = Gtk.FileChooserDialog("Type the output wav name",None,Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK));
		filename.set_current_folder(os.environ['HOME'])
		filename.run()
		self.file_to_output = filename.get_filename()
		filename.destroy()
		
		self.ac_object.set_volume(self.spinbutton_vloume.get_value())
		self.ac_object.set_voice(self.model_voice[self.index_voice][0])
		self.ac_object.set_split_time(self.spinbutton_split.get_value())
		self.ac_object.set_pitch(self.spinbutton_pitch.get_value())
		self.ac_object.set_speed(self.spinbutton_speed.get_value())

		Thread(target=self.record_to_wave,args=()).start()
		self.audio_converter_window.destroy()

               
		
	def record_to_wave(self):
		self.ac_object.record_to_wave(self.file_to_output);
		os.system('espeak "Conversion finish and saved to %s"' % (self.file_to_output))
		
		
if __name__ == "__main__":
	test = record_ui("This is a sample of text in english. Are you ok ?")
	Gtk.main()		
