#!/usr/bin/python3 

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


def detect_overlap(list,new_start_x,new_start_y,new_end_x,new_end_y):
	for item in list:
		start_x = item[0]
		start_y = item[1]
		finish_x = item[2]+item[0]
		finish_y = item[3]+item[1]
		if (((start_x <= new_start_x <= finish_x or start_x <= new_end_x <= finish_x) and
		 (start_y <= new_start_y <= finish_y or start_y <= new_end_y <= finish_y)) or 
		 # The rectangle maybe inside the new rectangle 
		 ((new_start_x <= start_x <= new_end_x and new_start_y <= start_y <= new_end_y) or 
		 ( new_start_x <= finish_x <= new_end_x and new_start_y <= finish_y <= new_end_y))):
			return (start_x,start_y,finish_x,finish_y)
	return False


def detect_out_of_range(x,y,max_width,max_height):
	if (x >= max_width or y >= max_height or x <= 0 or y<=0 ):
		return True
	else:
		return False


def order_rectangle(start_x,start_y,finish_x,finish_y):
	#Swap coordinate if selected in reverse direction
	if(start_x >= finish_x):
		start_x,finish_x = finish_x,start_x
	if(start_y >= finish_y):
		start_y,finish_y = finish_y,start_y
	return start_x,start_y,finish_x,finish_y
		

def is_overlapping(rs,index,a,b,c,d):
	nrs = [];
	for i in range(0,len(rs)):
		if(index != i):
			nrs.append(rs[i]);
	if(detect_overlap(nrs,a,b,a+c,b+d)):
		return True
	else:
		return False
	
	
		
def get_point_type(x,y,rs):
	for i in range(0,len(rs)):
		scope_scale_y = (rs[i][3])/10
		scope_scale_x = (rs[i][2])/10
		
		#Left
		if(rs[i][0] <= x+scope_scale_x and
			rs[i][0] >= x-scope_scale_x and 
			rs[i][1] <= y and
			rs[i][3]+rs[i][1] >= y ):
				return (2,i,4)
						

		#Right 
		if(rs[i][0]+rs[i][2] <= x+scope_scale_x and
			rs[i][0]+rs[i][2] >= x-scope_scale_x and
			rs[i][1] <= y and
			rs[i][3]+rs[i][1] >= y ):
				return (2,i,6)

		#Top
		if(rs[i][1] <= y+scope_scale_y and
			rs[i][1] >= y-scope_scale_y and
			rs[i][0] <= x and
			rs[i][2]+rs[i][0] >= x ):
				return (2,i,2)

		#Bottom
		if(rs[i][3]+rs[i][1] <= y+scope_scale_y and
			rs[i][3]+rs[i][1] >= y-scope_scale_y and
			rs[i][0] <= x and
			rs[i][2]+rs[i][0] >= x ):
				return (2,i,8)

		#Top Left 
		if(rs[i][0] <= x+scope_scale_x and
			rs[i][0] >= x-scope_scale_x and
			rs[i][1] <= y+scope_scale_y and
			rs[i][1] >= y-scope_scale_y ):
				return (2,i,1)


		#Bottom Left 
		if(rs[i][0] <= x+scope_scale_x and
			rs[i][0] >= x-scope_scale_x and
			rs[i][3]+rs[i][1] <= y+scope_scale_y and
			rs[i][3]+rs[i][1] >= y-scope_scale_y):
				return (2,i,7)

		#Top Right 
		if(rs[i][0]+rs[i][2] <= x+scope_scale_x and
			rs[i][0]+rs[i][2] >= x-scope_scale_x and
			rs[i][1] <= y+scope_scale_y and
			rs[i][1] >= y-scope_scale_y ):
				return (2,i,3)


		#Bottom Right 
		if(rs[i][0]+rs[i][2] <= x+scope_scale_x and
			rs[i][0]+rs[i][2] >= x-scope_scale_x and
			rs[i][3]+rs[i][1] <= y+scope_scale_y and
			rs[i][3]+rs[i][1] >= y-scope_scale_y):
				return (2,i,9)
							

		#Moving
		if(x >= rs[i][0]+scope_scale_x and
			y >= rs[i][1]+scope_scale_y and
			x <= rs[i][0]+rs[i][2]-scope_scale_x and
			y <= rs[i][1]+rs[i][3]-scope_scale_y):
				return (3,i,5)

	return (1,-1,0)
				
