#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
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
import itertools

def get_list_of_mixed_case_combinations(list_items):
    """
    Returns a list of lists of the combinations of items.

    Args:
        list_items: (str): write your description
    """
	return list(itertools.chain.from_iterable([[''.join(a) for a in itertools.product(*zip(s.upper(), s.lower()))] for s in list_items]))

user_home_path = os.environ['HOME']

config_dir = user_home_path+"/.lios"

tmp_dir = "/tmp/Lios/"

bookmarks_dir = config_dir+"/bookmarks/"

local_text_cleaner_list_file_path = config_dir+"/text_cleaner_list.text"

default_text_cleaner_list_file_path = "/usr/share/lios/text_cleaner_list.text"

preferences_file_path = config_dir+"/preferences.cfg"

recent_file_path = config_dir+"/recent.text"

recent_cursor_position_file_path = config_dir+"/recent_cursor_position.text"

supported_image_formats = get_list_of_mixed_case_combinations(["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm","ppm"])

supported_text_formats = get_list_of_mixed_case_combinations(["txt","text"])

supported_pdf_formats = get_list_of_mixed_case_combinations(["pdf"])

version = "2.8"

logo_file = "/usr/share/lios/lios.png"

icon_dir = "/usr/share/lios/icons/"

readme_file = "/usr/share/lios/readme.text"

default_text_cleaner_list_file_path = "/usr/share/lios/text_cleaner_list.text"

app_name = "Linux-intelligent-ocr-solution"

source_link = "https://gitlab.com/Nalin-x-Linux/lios-3"

home_page_link = "http://sourceforge.net/projects/lios/"

video_tutorials_link = "https://www.youtube.com/playlist?list=PLn29o8rxtRe1zS1r2-yGm1DNMOZCgdU0i"

major_character_encodings_list = [ 'us_ascii', 'utf-8', 'iso_8859_1','latin1',
 'iso_8859_2', 'iso_8859_7', 'iso_8859_9', 'iso_8859_15', 'eucjp', 'euckr',
 'gb2312_80', 'gb2312_1980', 'windows_1251', 'windows_1252', 'windows_1253',
 'windows_1254', 'windows_1255', 'windows_1256', 'windows_1257', 'windows_1258',
 'shiftjis', 'windows_1256', 'big5_hkscs', 'big5_tw', 'tis620']
