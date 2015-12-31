#!/usr/bin/env python3
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
import abc

class DriverBase(metaclass=abc.ABCMeta):
	SCAN_AREA_FULL, SCAN_AREA_THREE_QUARTER, SCAN_AREA_HALF,\
	SCAN_AREA_QUARTER = range(4)
	
	@abc.abstractmethod
	def __init__(self,device,scanner_mode_switching,resolution=300,brightness=40,scan_area=0):
		self.set_resolution(resolution);
		self.set_brightness(brightness);
		self.set_scan_area(scan_area);
		self.brightness_multiplier = 1
		self.brightness_offset = 0
		if (scanner_mode_switching):
			modes_list = self.get_available_scan_modes()
			if "Binary" in modes_list:
				self.set_scan_mode("Binary")
			if "Lineart" in modes_list:
				self.set_scan_mode("Lineart")
	
	@abc.abstractmethod
	def scan(self,filename,resolution=-1,brightness=-1,scan_area=-1):
		if (brightness !=-1 ):
			brightness = (brightness*self.brightness_multiplier)+self.brightness_offset
			self.set_brightness(brightness)
		if (resolution !=-1 ):
			self.set_resolution(resolution);
		if (scan_area !=-1 ):
			self.set_scan_area(scan_area);			


	@abc.abstractmethod
	def get_resolution(self):
		return

	@abc.abstractmethod
	def set_resolution(self,resolution):
		return

	@abc.abstractmethod
	def get_brightness(self):
		return

	@abc.abstractmethod
	def set_brightness(self,brightness):
		return

	@abc.abstractmethod
	def set_scan_area(self,scan_area):
		return
		
	@abc.abstractmethod
	def get_scan_area(self):
		return

	@abc.abstractmethod
	def set_scan_mode(self,scan_mode):
		return

	@abc.abstractmethod
	def get_scan_mode(self,scan_mode):
		return

	@abc.abstractmethod
	def get_available_scan_modes(self):
		return;

	@abc.abstractmethod		
	def check_brightness_support(self):
		return

	@staticmethod
	@abc.abstractmethod
	def get_available_devices():
		return

	@staticmethod
	@abc.abstractmethod
	def is_available():
		return


	@abc.abstractmethod
	def cancel(self):
		return

	@abc.abstractmethod
	def close(self):
		return
