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
	
	
		
def get_point_type(x,y,area_x_start, area_y_start,width,height,rs):

	# If pointer is at the edge of drawing area then mouse pointer must become normal
	if (x < area_x_start+10 or
	(area_x_start+width-20) <= x <= area_x_start+width or
	y < area_y_start+10 or
	(area_y_start+height-20) <= y <= area_y_start+height):
		return (1,-1,0)

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


# Used to find the index of new box inside the box list 
# The box list is arranged in top-left to bottom-right order
def find_index_for_new_box(new_s_x,new_s_y,new_e_x,new_e_y,rl):

	length = len(rl);
	index = length-1;

	min_x_dist = 99999;
	min_y_dist = 99999;

	for i in range (0,length):
		cur_s_x = rl[i][0]
		cur_s_y = rl[i][1]
		cur_e_x = cur_s_x+rl[i][2]
		cur_e_y = cur_s_y+rl[i][3]

		# Checking it's on the right side or not
		if(cur_s_x < new_s_x):
			# Checking new top and new bottom are inside the current one's y axis
			if(cur_s_y <= new_s_y <= cur_e_y or
			new_s_y <= cur_s_y <= new_e_y or
			cur_s_y <= new_e_y <= cur_e_y or
			new_s_y <= cur_e_y <= new_e_y):
				dist = new_s_x - cur_s_x;
				# The new box is residing on right side so
				# if cur box having minimum x distance to new then it's more close
				if ( dist < min_x_dist):
					min_x_dist = dist;
					index = i+1;

		#if nothing in parallel to the right then new box will be drawed in first from left
		if (min_x_dist == 99999):
			if(cur_e_y <= new_s_y):
				# Checking the vertical distance bitween new box and cur box
				# if it's very low then find the right most parallel one
				dist1 = new_s_y - cur_s_y;
				dist2 = new_s_y - cur_e_y;
				dist = (dist1+dist2)/2;
				if (dist < min_y_dist):
					min_y_dist = dist
					# Checking if any box in parallel to right side
					j = i+1;
					index = i+1;

					#cur_e_y >= rl[j][1] is used to skip symbols like single quotes
					while(j < length and cur_s_x < rl[j][0] and (cur_s_y <= rl[j][1] <= cur_e_y or
						rl[j][1] <= cur_s_y <= (rl[j][1]+rl[j][3]) or
						cur_s_y <= (rl[j][1]+rl[j][3]) <= cur_e_y or
						rl[j][1] <= cur_e_y <= (rl[j][1]+rl[j][3]) or cur_e_y >= rl[j][1] )):
							j = j + 1;
							index = j;
							# Stop if end reached
							if(j == length):
								break;
	return index;
