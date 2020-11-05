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

import os
import subprocess
from lios.scanner.driver_base import DriverBase

class DriverScanimage(DriverBase):
	name = "Scanimage"
	
	def __init__(self,device,scanner_mode_switching,resolution=300,brightness=40,scan_area=0):
     """
     Initialize the led.

     Args:
         self: (todo): write your description
         device: (str): write your description
         scanner_mode_switching: (bool): write your description
         resolution: (todo): write your description
         brightness: (todo): write your description
         scan_area: (todo): write your description
     """
		self.device = device.split()[1][1:-1]
		self.device_name = device;
		
		self.scanner_mode = "Color"
		self.light_parameter_state = False

		device_info = subprocess.getoutput("scanimage -d {} --all-options"\
		.format(self.device))		
		
		for line in device_info.split("\n"):
			if ("--mode" in line):
				 self.available_modes = line.split()[1].split("|")
				 print(self.available_modes)
			
			if ("--brightness" in line):
				self.light_parameter_state = True
				self.light_parameter = "brightness"
				print("Brightness available")
			
			#if ("--threshold" in line and self.light_parameter_state == False):
			#	self.light_parameter_state = True
			#	self.light_parameter = "threshold"
			#	print("Threshold available")

			if ("-y" in line):
				self.max_y = line.split()[1].split(".")[2].split("mm")[0]
				print(self.max_y)

			if ("-x" in line):
				self.max_x = line.split()[1].split(".")[2].split("mm")[0]
				print(self.max_x)

		super(DriverScanimage, self).__init__(device,scanner_mode_switching,
			resolution,brightness,scan_area)
		self.brightness_multiplier = 2
		self.brightness_offset = -100
				

	
	def scan(self,filename,brightness=-1,resolution=-1,scan_area=-1):
     """
     Perform the led area.

     Args:
         self: (todo): write your description
         filename: (str): write your description
         brightness: (todo): write your description
         resolution: (todo): write your description
         scan_area: (int): write your description
     """
		super(DriverScanimage, self).scan(filename,brightness,resolution,scan_area)

		command = "scanimage --device-name='{}' --resolution {} --mode {} -x {} -y {}"\
		.format(self.device,self.resolution,self.scanner_mode,self.max_x,self.y)
		
		
			
		#if (self.calibration_cache):
		#	command += (" --calibration-cache=yes")
			
		if (self.check_brightness_support()):
			command += (" --{}={}".format(self.light_parameter,self.brightness))	
				
		command += (" > {}".format(filename))
		print(command)
		os.system(command)
		os.system("convert -strip -quality 90 {0} {0}".format(filename))
				


	def get_resolution(self):
     """
     Return the resolution.

     Args:
         self: (todo): write your description
     """
		return self.resolution

	def set_resolution(self,resolution):
     """
     Set the resolution of a resolution.

     Args:
         self: (todo): write your description
         resolution: (todo): write your description
     """
		self.resolution = resolution

	def get_brightness(self):
     """
     Get the brightness.

     Args:
         self: (todo): write your description
     """
		return self.brightness

	def set_brightness(self,brightness):
     """
     Set the brightness.

     Args:
         self: (todo): write your description
         brightness: (todo): write your description
     """
		self.brightness = brightness

	def set_scan_area(self,scan_area):
     """
     Sets area area.

     Args:
         self: (todo): write your description
         scan_area: (todo): write your description
     """
		if scan_area == self.SCAN_AREA_FULL:
			self.y = int(self.max_y)
		elif scan_area == self.SCAN_AREA_THREE_QUARTER:
			self.y = 3*(int(self.max_y)/4)
		elif scan_area == self.SCAN_AREA_HALF:
			self.y = int(self.max_y)/2
		else:
			self.y = int(self.max_y)/4
				
	def get_scan_area(self):
     """
     Returns the area area area.

     Args:
         self: (todo): write your description
     """
		return self.scan_area

	def set_scan_mode(self,mode):
     """
     Set the scan mode.

     Args:
         self: (todo): write your description
         mode: (str): write your description
     """
		self.scanner_mode = mode

	def get_scan_mode(self,scan_mode):
     """
     Get the scan mode.

     Args:
         self: (todo): write your description
         scan_mode: (str): write your description
     """
		return self.scanner_mode

	def get_available_scan_modes(self):
     """
     Return a list of available nodes.

     Args:
         self: (todo): write your description
     """
		return self.available_modes

	def check_brightness_support(self):
     """
     Checks if the light support support support check check.

     Args:
         self: (todo): write your description
     """
		return self.light_parameter_state

	#static method
	def get_available_devices():
     """
     Returns a list.

     Args:
     """
		scanner_list = []
		output = subprocess.getoutput("scanimage --list")
		for line in output.split("\n"):
			if (("device" in line) and ("v4l" not in line)):
				try:
					scanner_list.append(line)
				except:
					pass
		return scanner_list

	#static method
	def is_available():
     """
     Determine is_available is available.

     Args:
     """
		if ("/bin/scanimage" in subprocess.getoutput("whereis scanimage")):
			return True
		else:
			return False
	
	def cancel(self):
     """
     Cancel the job.

     Args:
         self: (todo): write your description
     """
		os.system("pkill scanimage")

	def close(self):
     """
     Closes the connection.

     Args:
         self: (todo): write your description
     """
		return
		
		
if __name__ == "__main__":
	scanners = []
	scanner_list = DriverScanimage.get_available_devices()
	print(scanner_list)
	for device in scanner_list:
		scanners.append(DriverScanimage(device))
	scanners[0].scan("Hello.png")		

	
