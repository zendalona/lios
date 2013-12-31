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
def ocr_image_to_text_file(name,engine,language):
	os.system("convert %s.pnm image"%(name))
	if self.engine == "CUNEIFORM":
		os.system("convert -compress none %s.pnm %s.bmp"%(name,name))
		os.system("cuneiform -f text -l %s -o %s.txt %s.bmp"%(language,name,name))		
	elif self.engine == "TESSERACT":
		os.system("convert %s.pnm %s.png"%(name,name))
		os.system("tesseract %s.png %s -l %s"%(name,name,language))
	else:
		pass
