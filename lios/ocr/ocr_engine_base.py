#! /usr/bin/python3 

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

import abc
import multiprocessing


class OcrEngineBase(metaclass=abc.ABCMeta):
	def __init__(self,language):
		self.language = language
	
	@staticmethod
	@abc.abstractmethod
	def get_available_languages():
		return
	
	@abc.abstractmethod
	def ocr_image_to_text(self,image_file_name):
		pass

	def set_language(self,language):
		if language in self.__class__.get_available_languages():
			self.language = language
			return True
		else:
			return False
	
	def ocr_image_to_text_with_multiprocessing(self,image_file_name):
		parent_conn, child_conn = multiprocessing.Pipe()
		
		p = multiprocessing.Process(target=(lambda parent_conn, child_conn,
		image_file_name : child_conn.send(self.ocr_image_to_text(image_file_name))),
		args=(parent_conn, child_conn,image_file_name))
		
		p.start()
		p.join()
		
		return parent_conn.recv();


	@staticmethod
	@abc.abstractmethod
	def is_available():
		return		
