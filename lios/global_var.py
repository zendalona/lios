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

#Where the data is located
data_dir = "/usr/share/lios";
#data_dir = "/usr/local/share/lios";


#Home folder
home_dir = os.environ['HOME']

tmp_dir = "/tmp/Lios/"

tesseract_data = '/usr/share/tesseract/tessdata/'
#tesseract_data = '/usr/share/tesseract-ocr/tessdata/'

image_formats = ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm","ppm"]
