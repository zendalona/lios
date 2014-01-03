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

import sane
import sys
import os

import multiprocessing
from multiprocessing import Pipe
class scanner():
	def __init__(self,device,scanner_mode_switching):
		sane_version = sane.init()
		try:
			self.scanner = sane.open(device[0])
		except _sane.error:
			pass
		else:
			if(scanner_mode_switching):
				#Setting Scanning Mode
				option = self.get_scanner_option("mode")
				if option:
					print(option)
					for mode in ['Lineart', 'Gray', 'Color']:
						if mode in option[-1:][0]:
							self.scanner.mode = mode
							break
			
			#Y Axis for scan Area
			option = self.get_scanner_option('br-y')
			if option:
				self.br_y_pass = option[8][1]
			
			
			#Brightness and Threshold
			#self.light_parameter_state = False 
			#options = self.get_scanner_option ('brightness')
			#if options:
			#	self.light_parameter_state = True
			#	self.light_parameter = "brightness"
			#	try:
			#		self.min =  options[-1][0]
			#		self.max = options[-1][1]
			#	except:
			#		self.min = -100
			#		self.max = 100

			#options = self.get_scanner_option ('threshold')
			#if options:
			#	self.light_parameter_state = True
			#	self.light_parameter = "threshold"
			#	try:
			#		min =  options[-1][0]
			#		max = options[-1][1]
			#	except:
			#		self.min = 0
			#		self.max = 255

			
			
			
	
	def get_scanner_option (self,name):
		options = self.scanner.get_options()
		for option in options:
			if option[1] == name:
				return option
		return False
		

	def scan(self,file_name,resolution,brightness,region):
		#Setting Brightness and Threshold
		#if self.check_brightness_support():
			#value = (((self.max-self.min)/200)*brightness)-abs(self.min)
			#print("Min = {0}, Max = {1}, User Value = {2}, Range = {3}, Value = {4}".format(self.min,self.max,brightness,self.max-self.min,value))  
			#if self.light_parameter == "brightness":
			#	try:
			#		self.scanner.brightness = value
			#	except AttributeError:
			#		print ("ooh")
			#if self.light_parameter == "threshold":
			#		try:
			#			self.scanner.threshold = value
			#		except AttributeError:
		#				print ("Ohhh")
		
		#Setting Resolution
		self.scanner.resolution = resolution
		
		#Setting Region
		if region == 0:
			self.scanner.br_y = self.br_y_pass
		elif region == 1:
			self.scanner.br_y = 3*(self.br_y_pass/4) 
		elif region == 2:
			self.scanner.br_y = self.br_y_pass/2
		elif region == 3:
			self.scanner.br_y = self.br_y_pass/4
		else:
			pass        
		
		#Scanning	
		#try:
		pil_image = self.scanner.scan()
		#except:
		#	print("Error")
		#else:
		pil_image.save(file_name)

	def close(self):
		self.scanner.close()

			
	def check_brightness_support(self):
		return self.light_parameter_state

		

	#static method
	def get_devices():
		sane.init()
		return sane.get_devices()

			
		
		
if __name__ == "__main__":
	scanners = []
	scanner_list = scanner.get_devices()
	print(scanner_list)
	for device in scanner_list:
		scanners.append(scanner(device))
	
	
	scanners[0].scan("Hello.png",400,30,0)		


	
