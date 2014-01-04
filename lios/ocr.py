# coding: latin-1

###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2014 Nalin.x.Linux GPL-3
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
from lios import global_var


def ocr_image_to_text(name,engine,language,angle):
	if angle != 00:
		os.system("convert -rotate {0} {1} {1}".format(angle,name))
	if engine == "CUNEIFORM":
		os.system("convert -compress none {0} {1}test.bmp".format(name,global_var.temp_dir))
		os.system("cuneiform -f text -l {0} -o {1}output.txt {1}test.bmp".format(language,global_var.temp_dir))		
	elif engine == "TESSERACT":
		os.system("convert {0} {1}test.png".format(name,global_var.temp_dir))
		os.system("tesseract {0}test.png {0}output -l {1}".format(global_var.temp_dir,language))
	else:
		pass
	try:
		with open("{0}output.txt".format(global_var.temp_dir),encoding="utf-8") as file:
			text = file.read()
			return text
	except:
		return ""
	
