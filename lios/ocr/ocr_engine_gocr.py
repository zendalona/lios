#!/usr/bin/python3 
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

import os
import subprocess 
from lios.ocr.ocr_engine_base import OcrEngineBase


class OcrEngineGocr(OcrEngineBase):
	name = "Gocr"
	
	def __init__(self,language=None):
     """
     Sets the language.

     Args:
         self: (todo): write your description
         language: (str): write your description
     """
		self.set_language(language)

	def is_available():
     """
     Determine is_available is available.

     Args:
     """
		if ("/bin/gocr" in subprocess.getoutput("whereis gocr")):
			return True
		else:
			return False
			
	def ocr_image_to_text(self,file_name):
     """
     Convert an image to text.

     Args:
         self: (todo): write your description
         file_name: (str): write your description
     """
		os.system("convert {} /tmp/{}_for_ocr.pnm".format(file_name,file_name.split("/")[-1]))
		os.system("gocr -i /tmp/{0}_for_ocr.pnm -o /tmp/{0}_output.txt ".format(file_name.split("/")[-1]))
		os.remove("/tmp/{0}_for_ocr.pnm".format(file_name.split("/")[-1]))
		try:
			with open("/tmp/{0}_output.txt".format(file_name.split("/")[-1]),encoding="utf-8") as file:
				text = file.read().strip()
				os.remove("/tmp/{0}_output.txt".format(file_name.split("/")[-1]))
				return text
		except:
			return ""
	def cancel():
     """
     Cancel the system.

     Args:
     """
		os.system("pkill convert")
		os.system("pkill gocr")
		
	
	def get_available_languages():
     """
     Get languages available languages. languages

     Args:
     """
		langs = ["eng"]
		return langs

	def support_multiple_languages():
     """
     Return true if all languages are available.

     Args:
     """
		return False
