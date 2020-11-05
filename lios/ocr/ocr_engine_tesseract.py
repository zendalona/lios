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
	"/usr/share/tesseract-ocr/tessdata",
	"/usr/share/tesseract-ocr/4.00/tessdata",
	"/usr/share/tesseract/tessdata",
	"/usr/share/tessdata",
	"/usr/local/share/tesseract-ocr/tessdata",
	"/usr/local/share/tesseract/tessdata",
	"/usr/local/share/tessdata",
	"/usr/share/tesseract-ocr/4.00/tessdata" ]

TESSDATA_EXTENSION = ".traineddata"


class OcrEngineTesseract(OcrEngineBase):
	name = "Tesseract"
	
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
		if ("/bin/tesseract" in subprocess.getoutput("whereis tesseract")):
			return True
		else:
			return False

	def ocr_image_to_text(self,file_name):
     """
     Convert an image to text

     Args:
         self: (todo): write your description
         file_name: (str): write your description
     """
		os.system("convert {} -background white -flatten +matte /tmp/{}_for_ocr.png".format(file_name,file_name.split("/")[-1]))
		
		languages = self.language
		if(self.language_2 != False):
			languages = languages+"+"+self.language_2
		if(self.language_3 != False):
			languages = languages+"+"+self.language_3

		os.system("tesseract /tmp/{0}_for_ocr.png /tmp/{0}_output -l {1}".format(file_name.split("/")[-1],languages))

		os.remove("/tmp/{0}_for_ocr.png".format(file_name.split("/")[-1]))
		
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
		os.system("pkill tesseract")
		
	
	def get_available_languages_in_dirpath(dirpath):
     """
     Return a list of a list.

     Args:
         dirpath: (str): write your description
     """
		langs = []
		if os.access(dirpath, os.R_OK):
			for filename in os.listdir(dirpath):
				if filename.lower().endswith(TESSDATA_EXTENSION):
					lang = filename[:(-1 * len(TESSDATA_EXTENSION))]
					langs.append(lang)
		return langs

	def get_available_languages():
     """
     Return a list of available languages.

     Args:
     """
		langs = []
		for dirpath in TESSDATA_POSSIBLE_PATHS[::-1]:
			if (os.path.isfile(dirpath+"/configs/box.train")):
				for item in OcrEngineTesseract.get_available_languages_in_dirpath(dirpath):
					langs.append(item)
				return sorted(langs)
		return langs

	def get_all_available_dirs():
     """
     Return a list of all available directories.

     Args:
     """
		result = []
		for root, dirs, files in os.walk("/"):
			if "tessdata" in dirs:
				dir = os.path.join(root, "tessdata")
				if (os.path.isfile(dir+"/configs/box.train")):
					result.append(dir)

		# Sorting according to possible list
		# [::-1] is used to reverse
		for path in TESSDATA_POSSIBLE_PATHS[::-1]:
			if (path in result):
				result.insert(0, result.pop(result.index(path)))
		return result

	def get_available_dirs():
     """
     Return a list of directories.

     Args:
     """
		dir_list = [];
		for path in TESSDATA_POSSIBLE_PATHS:
			if (os.path.exists(path)):
				if (os.path.isfile(path+"/configs/box.train")):
					dir_list.append(path);
		return dir_list;


	def support_multiple_languages():
     """
     Returns a list of a list of languages.

     Args:
     """
		return True
