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
import subprocess

class text_to_audio_converter:
	def __init__(self,text="Blank",volume=100,voice="english",split_time=5,pitch=50,speed=170):
     """
     Init pitch

     Args:
         self: (todo): write your description
         text: (str): write your description
         volume: (todo): write your description
         voice: (todo): write your description
         split_time: (int): write your description
         pitch: (todo): write your description
         speed: (int): write your description
     """
		self.text = text
		self.set_volume(volume)
		self.set_voice(voice)
		self.set_split_time(split_time)
		self.set_pitch(pitch)
		self.set_speed(speed)	
		
	
	def list_voices():
     """
     Return a list of skillices

     Args:
     """
		voice_list = []
		output = subprocess.getoutput("espeak --voices")
		for line in output.split("\n"):
			if(line.split()[3] != "VoiceName"):
				voice_list.append(line.split()[3])
		return voice_list

		
	def get_volume(self):
     """
     Get the volume.

     Args:
         self: (todo): write your description
     """
		return self.volume

	def get_voice(self):
     """
     Return the voice voice.

     Args:
         self: (todo): write your description
     """
		return self.voice

	def get_split_time(self):
     """
     Returns the split time.

     Args:
         self: (todo): write your description
     """
		return self.split_time
				
	def get_pitch(self):
     """
     : returns : class :.

     Args:
         self: (todo): write your description
     """
		return self.pitch

	def get_speed(self):
     """
     Return the speed

     Args:
         self: (str): write your description
     """
		return self.speed


	def set_volume(self,value):
     """
     Set the volume.

     Args:
         self: (todo): write your description
         value: (todo): write your description
     """
		if ( 0 <= value and value <= 200):
			self.volume = value
		else:
			self.volume = 100
			return False;

	def set_voice(self,value):
     """
     Sets the audio value to the audio

     Args:
         self: (todo): write your description
         value: (todo): write your description
     """
		if (value in text_to_audio_converter.list_voices()):
			self.voice = value
			return True;
		else:
			self.voice = "english"
			return False;
			

	def set_split_time(self,value):
     """
     Set the split time.

     Args:
         self: (todo): write your description
         value: (str): write your description
     """
		self.split_time  = value
				
	def set_pitch(self,value):
     """
     Sets the pitch value.

     Args:
         self: (todo): write your description
         value: (todo): write your description
     """
		if ( 0 <= value and value <= 100):
			self.pitch = value
			return True
		else:
			self.pitch = 50
			return False;

	def set_speed(self,value):
     """
     Sets the speed.

     Args:
         self: (todo): write your description
         value: (todo): write your description
     """
		if ( 100 <= value and value <= 450):
			self.speed = value
			return True
		else:
			self.speed = 170
			return False;
		
	def record_to_wave(self,output_file_name):
     """
     Write a record to disk.

     Args:
         self: (todo): write your description
         output_file_name: (str): write your description
     """
		to_convert = open("tmp.txt",'w')
		to_convert.write(self.text)
		to_convert.close()
		os.system('espeak -a %s -v %s -f tmp.txt -w %s.wav --split=%s -p %s -s %s' % (self.volume,self.voice,output_file_name,self.split_time,self.pitch,self.speed))

	def record_to_mp3(self,output_file_name):
     """
     Convert mp3 output file

     Args:
         self: (todo): write your description
         output_file_name: (str): write your description
     """
		to_convert = open("tmp.txt",'w')
		to_convert.write(self.text)
		to_convert.close()
		os.system("rm -rf /tmp/lios_audio")
		os.system("mkdir /tmp/lios_audio")
		os.system('espeak -a %s -v %s -f tmp.txt -w /tmp/lios_audio/%s.wav --split=%s -p %s -s %s'%(self.volume,self.voice,output_file_name.split("/")[-1],self.split_time,self.pitch,self.speed))
		cmd = 'for f in /tmp/lios_audio/*.wav; do filename=$(basename "$f");name="${filename%.*}"; echo $name; lame --vbr-new -V 3  "$f" '+"/".join(output_file_name.split("/")[:-1])+'/$name.mp3; done;'
		os.system(cmd)


if __name__ == "__main__":
	ob = text_to_audio_converter("This is a sample of text in english")
	ob.record_to_wave("~/Hello")
	
