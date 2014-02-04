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
from gi.repository import GdkPixbuf


def ocr_image_to_text(name,engine,language,angle):
	try:
		pb = GdkPixbuf.Pixbuf.new_from_file(name)
	except:
		return ""
	pb = pb.rotate_simple(angle)
	pb.savev("{0}for_ocr.png".format(global_var.tmp_dir), "png",[],[])
	if engine == "CUNEIFORM":
		pb = GdkPixbuf.Pixbuf.new_from_file("{0}for_ocr.png".format(global_var.tmp_dir))
		pb.savev("{0}for_ocr.bmp".format(global_var.tmp_dir), "bmp",[],[])
		os.system("cuneiform -f text -l {0} -o {1}output.txt {1}for_ocr.bmp".format(language,global_var.tmp_dir))
		os.remove("{0}for_ocr.bmp".format(global_var.tmp_dir))		
	elif engine == "TESSERACT":
		os.system("tesseract {0}for_ocr.png {0}output -l {1}".format(global_var.tmp_dir,language))
	else:
		pass
	
	#Remove tmp file
	os.remove("{0}for_ocr.png".format(global_var.tmp_dir))
		
	try:
		with open("{0}output.txt".format(global_var.tmp_dir),encoding="utf-8") as file:
			text = file.read().strip()
			os.remove("{0}output.txt".format(global_var.tmp_dir))
			return text
	except:
		return ""
	
