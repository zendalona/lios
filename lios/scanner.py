import sane
import sys
import os

import multiprocessing
from multiprocessing import Pipe
class scanner():
	def __init__(self,device):
		sane_version = sane.init()
		try:
			self.scanner = sane.open(device[0])
		except _sane.error:
			pass
		else:
			#Setting Scanning Mode
			#option = self.get_scanner_option("mode")
			#if option:
			#	print(option)
			#	for mode in ['Lineart', 'Gray', 'Color']:
			#		if mode in option[-1:][0]:
			#			self.scanner.mode = mode
			#			break
			
			#Y Axis for scan Area
			option = self.get_scanner_option('br-y')
			if option:
				self.br_y_pass = option[8][1]
			
			
			#Brightness and Threshold
			self.light_parameter_state = False 
			options = self.get_scanner_option ('brightness')
			if options:
				self.light_parameter_state = True
				self.light_parameter = "brightness"
			options = self.get_scanner_option ('threshold')
			if options:
				self.light_parameter_state = True
				self.light_parameter = "threshold"
				if type(options[8]) == types.ListType:
					min =  options[8][0]
					max = options[8][-1]
				else:
					min =  options[8][0]
					max = options[8][1]
				self.vary = max-min

			
			
			
	
	def get_scanner_option (self,name):
		options = self.scanner.get_options()
		for option in options:
			if option[1] == name:
				return option
		return False
		

	def scan(self,file_name,resolution,brightness,region):
		#Setting Brightness and Threshold
		if self.check_brightness_support():
			if self.light_parameter == "brightness":
				try:
					self.scanner.brightness = brightness
				except AttributeError:
					print ("ooh")
			if self.light_parameter == "threshold":
				if self.vary == 100:
					try:
						self.scanner.threshold = brightness
					except AttributeError:
						print ("Ohhh")
				else:
					try:
						self.scanner.threshold = brightness+100
					except AttributeError:
						print ("Ohhh 100")
		
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


	
