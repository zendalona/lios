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
import re
import subprocess 
from lios.ocr.ocr_engine_base import OcrEngineBase


LANGUAGES_LINE_PREFIX = "Supported languages: "
LANGUAGES_SPLIT_RE = re.compile("[^a-z]")


class OcrEngineCuneiform(OcrEngineBase):
	name = "Cuneiform"
	
	def __init__(self,language=None):
		self.set_language(language)

	def is_available():
		if ("/bin/cuneiform" in subprocess.getoutput("whereis cuneiform")):
			return True
		else:
			return False
			
	def ocr_image_to_text(self,file_name):
		os.system("convert {} /tmp/{}_for_ocr.png".format(file_name,file_name.split("/")[-1]))
		os.system("cuneiform -f text -l {0} -o /tmp/{1}_output.txt /tmp/{1}_for_ocr.png".format(self.language,file_name.split("/")[-1]))
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
		os.system("pkill cuneiform")
		
	
	def get_available_languages():
		langs = []
		for line in subprocess.getoutput("cuneiform -l").split("\n"):
			if line.startswith(LANGUAGES_LINE_PREFIX):
				line = line[len(LANGUAGES_LINE_PREFIX):]
				for language in LANGUAGES_SPLIT_RE.split(line):
					if language != "":
						langs.append(language)
		return langs
