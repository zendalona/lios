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

try:
	import sane
	available = True
except:
	available = False
	
	
from lios.scanner.driver_base import DriverBase
import os

class DriverSane(DriverBase):
	name = "Sane"
	
	def __init__(self,device,resolution=300,brightness=40,scan_area=0):
		sane_version = sane.init()
		self.device_name = device[2];
		try:
			self.scanner = sane.open(device[0])
		except sane._sane.error:
			print("sane error!")
		else:
			#Brightness and Threshold
			self.light_parameter_state = False 
			options = self.get_scanner_option ('brightness')
			if options:
				self.light_parameter_state = True
				self.light_parameter = "brightness"
				try:
					self.min =  options[-1][0]
					self.max = options[-1][1]
				except:
					self.min = -100
					self.max = 100

			options = self.get_scanner_option ('threshold')
			if options:
				self.light_parameter_state = True
				self.light_parameter = "threshold"
				try:
					self.min =  options[-1][0]
					self.max = options[-1][1]
				except:
					self.min = 0
					self.max = 255
			
			#Calling super constructor for inetialising brightness resolution and scan area
			super(DriverSane, self).__init__(device,resolution,\
			brightness,scan_area)			
			
	
	def get_scanner_option (self,name):
		options = self.scanner.get_options()
		for option in options:
			if option[1] == name:
				return option
		return False
		

	def scan(self,file_name,brightness=-1,resolution=-1,region=-1):
		super(DriverSane, self).scan(file_name,brightness,resolution,region)
		pil_image = self.scanner.scan()
		pil_image.save("/tmp/sane_temp.png")
		os.system("convert /tmp/sane_temp.png {}".format(file_name))

			
	def check_brightness_support(self):
		return self.light_parameter_state
	

	def get_resolution(self):
		return self.scanner.resolution;
		
	def set_resolution(self,resolution):
		self.scanner.resolution = resolution


	def get_brightness(self):
		if (self.check_brightness_support()):
			if self.light_parameter == "brightness":
				return self.scanner.brightness
			if self.light_parameter == "threshold":
				return self.scanner.threshold			
		else:
			return -1;

	def set_brightness(self,brightness):
		if (self.check_brightness_support()):
			brightness_value = int(((self.max-self.min)/200)*brightness)
			if (self.min < 0):
				brightness_value = brightness_value - 100
			print("Scanner Max = {0},  Scanner Min = {1}, User Value \
			(200) = {2}, Corected Value {3}".format(self.max,self.min,
			brightness,brightness_value))	
			
			if self.light_parameter == "brightness":
				try:
					self.scanner.brightness = brightness
				except AttributeError:
					print ("ooh")
			if self.light_parameter == "threshold":
				try:
					self.scanner.threshold = brightness
				except AttributeError:
					print ("Ohhh")	

	def set_scan_area(self,scan_area):
		#X Axis for scan Area
		option = self.get_scanner_option('br-x')
		if option:
			self.scanner.br_x = option[8][1]
		
		#Y Axis for scan Area
		option = self.get_scanner_option('br-y')
		if option:
			if scan_area == self.SCAN_AREA_FULL:
				self.scanner.br_y = option[8][1]
			elif scan_area == self.SCAN_AREA_THREE_QUARTER:
				self.scanner.br_y = 3*(option[8][1]/4)
			elif scan_area == self.SCAN_AREA_HALF:
				self.scanner.br_y = option[8][1]/2
			else:
				self.scanner.br_y = option[8][1]/4
			return True
		else:
			return False

	def get_scan_area(self):
		return self.scanner.br_y

		
	def set_scan_mode(self,scan_mode):
		self.scanner.mode = scan_mode


	def get_scan_mode(self,scan_mode):
		return self.scanner.mode


	def get_available_scan_modes(self):
		option = self.get_scanner_option("mode")
		if option:
			return option[-1:][0]
		else:
			return []


	#static method
	def get_available_devices():
		sane.init()
		list = []
		for device in sane.get_devices():
			if "scanner" in device[3]:
				list.append(device)
		return list			
	
	def is_available():
		return available


	def close(self):
		self.scanner.close()

if __name__ == "__main__":
	scanners = []
	scanner_list = DriverSane.get_available_devices()
	print(scanner_list)
	for device in scanner_list:
		scanners.append(DriverSane(device))
	scanners[0].scan("Hello.png")

	
