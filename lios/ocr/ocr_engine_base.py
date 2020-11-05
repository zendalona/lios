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
	def __init__(self,language=None):
     """
     Initialize the language.

     Args:
         self: (todo): write your description
         language: (str): write your description
     """
		self.language = language
	
	@staticmethod
	@abc.abstractmethod
	def get_available_languages():
     """
     Returns a list of available languages.

     Args:
     """
		return

	@staticmethod
	@abc.abstractmethod
	def support_multiple_languages():
     """
     Returns a list of all languages languages.

     Args:
     """
		return
	
	@abc.abstractmethod
	def ocr_image_to_text(self,image_file_name):
     """
     Convert image_image_file.

     Args:
         self: (todo): write your description
         image_file_name: (str): write your description
     """
		pass
	
	def cancel():
     """
     Cancel a function that task.

     Args:
     """
		pass
		

	def set_language(self,language):
     """
     Sets the language.

     Args:
         self: (todo): write your description
         language: (str): write your description
     """
		if language in self.__class__.get_available_languages():
			self.language = language
			return True
		else:
			return False

	def set_language_2(self,language):
     """
     Sets the language language.

     Args:
         self: (todo): write your description
         language: (str): write your description
     """
		if language in self.__class__.get_available_languages():
			self.language_2 = language
			return True
		else:
			self.language_2 = False
			return False

	def set_language_3(self,language):
     """
     Sets the language language.

     Args:
         self: (todo): write your description
         language: (str): write your description
     """
		if language in self.__class__.get_available_languages():
			self.language_3 = language
			return True
		else:
			self.language_3 = False
			return False
	
	def ocr_image_to_text_with_multiprocessing(self,image_file_name):
     """
     Return image image_image_image.

     Args:
         self: (todo): write your description
         image_file_name: (str): write your description
     """
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
     """
     Return a list of available resources.

     Args:
     """
		return		
