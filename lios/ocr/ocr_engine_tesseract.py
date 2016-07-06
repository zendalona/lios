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

TESSDATA_POSSIBLE_PATHS = [
    "/usr/local/share/tessdata",
    "/usr/share/tessdata",
    "/usr/share/tesseract/tessdata",
    "/usr/local/share/tesseract-ocr/tessdata",
    "/usr/share/tesseract-ocr/tessdata",
    "/app/vendor/tesseract-ocr/tessdata",  # Heroku
    "/opt/local/share/tessdata",  # OSX MacPorts
]

TESSDATA_EXTENSION = ".traineddata"

class OcrEngineTesseract(OcrEngineBase):
	name = "Tesseract"
	
	def __init__(self,language=None):
		self.set_language(language)

	def is_available():
		if ("/bin/tesseract" in subprocess.getoutput("whereis tesseract")):
			return True
		else:
			return False
			
	def ocr_image_to_text(self,file_name):
		os.system("convert {} /tmp/{}_for_ocr.png".format(file_name,file_name.split("/")[-1]))

		if os.environ['HOME'] in self.language:
			os.system("tesseract /tmp/{0}_for_ocr.png /tmp/{0}_output -l {1} --tessdata-dir {2}".format(file_name.split("/")[-1],self.language.split("-")[0],os.environ['HOME']))
			print("tesseract /tmp/{0}_for_ocr.png /tmp/{0}_output -l {1} --tessdir {2}".format(file_name.split("/")[-1],self.language.split("-")[0],os.environ['HOME']))
		else:
			os.system("tesseract /tmp/{0}_for_ocr.png /tmp/{0}_output -l {1}".format(file_name.split("/")[-1],self.language))
		os.remove("/tmp/{0}_for_ocr.png".format(file_name.split("/")[-1]))
		
		try:
			with open("/tmp/{0}_output.txt".format(file_name.split("/")[-1]),encoding="utf-8") as file:
				text = file.read().strip()
				os.remove("/tmp/{0}_output.txt".format(file_name.split("/")[-1]))
				return text
		except:
			return ""
	def cancel():
		os.system("pkill convert")
		os.system("pkill tesseract")
		
	

	def get_available_languages():
		langs = []
		for dirpath in TESSDATA_POSSIBLE_PATHS:
			if not os.access(dirpath, os.R_OK):
				continue
			for filename in os.listdir(dirpath):
				if filename.lower().endswith(TESSDATA_EXTENSION):
					lang = filename[:(-1 * len(TESSDATA_EXTENSION))]
					langs.append(lang)

		#Adding user languages
		if( os.path.exists(os.environ['HOME']+"/tessdata")):
			for filename in os.listdir(os.environ['HOME']+"/tessdata"):
				if filename.lower().endswith(TESSDATA_EXTENSION):
					lang = filename[:(-1 * len(TESSDATA_EXTENSION))]+"-"+os.environ['HOME']+"/tessdata"
					langs.append(lang)
		return langs


