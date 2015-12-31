#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2015-2016 Nalin.x.Linux GPL-3
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

import speechd

class Speech(speechd.SSIPClient):
	def __init__(self,client_name="lios"):
		super(Speech,self).__init__(client_name)
		self.status = False
	
	def list_voices(self):
		return [ x[0] for x in self.list_synthesis_voices()]
	
	def say(self,text):
		self.status = True
		self.speak(text,self.end,speechd.CallbackType.END)
	
	def wait(self):
		while (self.status):
			pass
	
	def end(self,*data):
		self.status = False
	
	#close()
			
		
