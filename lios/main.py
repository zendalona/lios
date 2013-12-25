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
import os
import sys
import enchant
import configparser

from espeak import espeak

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

from lios import converter
from lios import global_var
from lios.basic_editor import editor
from lios.basic_editor import spell_check
from lios.basic_editor import find
from lios.basic_editor import find_and_replace

from lios.preferences import lios_preferences

class linux_intelligent_ocr_solution(editor,lios_preferences):
	def __init__ (self,filename=None):
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(global_var.data_dir))
		self.window = self.guibuilder.get_object("window")
		self.textbuffer = self.guibuilder.get_object("textbuffer")
		self.textview = self.guibuilder.get_object("textview")
		self.guibuilder.connect_signals(self)
		
		


		#Espeak Voice List
		self.voice_list=[]
		for item in espeak.list_voices():
			self.voice_list.append(item.name)
#		espeak.set_SynthCallback(self.espeak_event)

		#Reading Dictionarys		
		self.key_value = {"eng" : "en","afr" : "af","am" : "am","ara" : "ar","ara" : "ar","bul" : "bg","ben" : "bn","br" : "br","cat" : "ca","ces" : "cs","cy" : "cy","dan" : "da","ger" : "de","ger" : "de","ell" : "el","eo" : "eo","spa" : "es","est" : "et","eu" : "eu","fa" : "fa","fin" : "fi","fo" : "fo","fra" : "fr","ga" : "ga","gl" : "gl","gu" : "gu","heb" : "he","hin" : "hi","hrv" : "hr","hsb" : "hsb","hun" : "hu","hy" : "hy","id" : "id","is" : "is","ita" : "it","kk" : "kk","kn" : "kn","ku" : "ku","lit" : "lt","lav" : "lv","mal" : "ml ","mr" : "mr ","dut" : "nl","no" : "no","nr" : "nr","ns" : "ns ","or" : "or ","pa" : "pa ","pol" : "pl ","por" : "pt","por" : "pt","por" : "pt","ron" : "ro","rus" : "ru ","slk" : "sk","slv" : "sl","ss" : "ss","st" : "st","swe" : "sv","tam" : "ta","tel" : "te","tl" : "tl","tn" : "tn","ts" : "ts","ukr" : "uk","uz" : "uz","xh" : "xh","zu" : "zu" }

		#Getting Preferences Values
		self.read_preferences()
		self.activate_preferences()


		#Preferences signals
		General_Preferences = self.guibuilder.get_object("General_Preferences")
		General_Preferences.connect("activate",self.preferences,0)
		Preferences_Recognition = self.guibuilder.get_object("Preferences_Recognition")
		Preferences_Recognition.connect("activate",self.preferences,1)
		Preferences_Scanning = self.guibuilder.get_object("Preferences_Scanning")
		Preferences_Scanning.connect("activate",self.preferences,2)
		Preferences_CamaraWebcam = self.guibuilder.get_object("Preferences_CamaraWebcam")
		Preferences_CamaraWebcam.connect("activate",self.preferences,3)		

		
		self.window.maximize();
		self.window.show()
		Gtk.main();
					
		
		
if __name__ == "__main__":
	linux_intelligent_ocr_solution()
	
