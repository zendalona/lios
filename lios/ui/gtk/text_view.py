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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango

class TextView(Gtk.TextView):
	AT_START=0
	AT_CURSOR=1
	AT_END=2
	
	def __init__(self):
     """
     Initialize the buffers.

     Args:
         self: (todo): write your description
     """
		super(TextView, self).__init__()
		self.set_wrap_mode(Gtk.WrapMode.WORD)
		buffer = self.get_buffer()
		self.highlight_tag = buffer.create_tag('Reading')		
	
	def connect_insert(self,function):
     """
     Connects to a function.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		buffer = self.get_buffer()
		buffer.connect("insert-text",lambda x, y,z,a  : function())

	def connect_delete(self,function):
     """
     Connects to the given function.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		buffer = self.get_buffer()
		buffer.connect("delete-range",lambda x, y,z  : function())

	def set_text(self,text):
     """
     Set text to text

     Args:
         self: (todo): write your description
         text: (str): write your description
     """
		buffer = self.get_buffer()
		buffer.set_text(text);
	
	def get_text(self):
     """
     Return text as a string.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		start,end = buffer.get_bounds()
		text = buffer.get_text(start,end,False)
		return text

	# For Text Cleaner
	def get_text_from_cursor_to_end(self):
     """
     Return text contained in cursor position.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		end = buffer.get_end_iter()
		mark = buffer.get_insert()
		start = buffer.get_iter_at_mark(mark)
		text = buffer.get_text(start,end,False)
		return text

	def delete_text_from_cursor_to_end(self):
     """
     Delete text from the cursor.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		end = buffer.get_end_iter()
		mark = buffer.get_insert()
		start = buffer.get_iter_at_mark(mark)
		buffer.delete(start,end)
	
	def insert_text(self,text,position,place_cursor=False):
     """
     Insert text at cursor position.

     Args:
         self: (todo): write your description
         text: (str): write your description
         position: (int): write your description
         place_cursor: (bool): write your description
     """
		buffer = self.get_buffer()
		if (position == TextView.AT_START):
			iter = buffer.get_start_iter()
			buffer.insert(iter,text)
			
		elif position == TextView.AT_CURSOR:
			buffer.insert_at_cursor(text)
		else:
			iter = buffer.get_end_iter()
			buffer.insert(iter,text)
	
	def set_highlight_font(self,highlight_font):
     """
     Set the font font_font.

     Args:
         self: (todo): write your description
         highlight_font: (todo): write your description
     """
		self.highlight_tag.set_property('font',highlight_font)

	def set_highlight_color(self,highlight_color):
     """
     Set the color of the foreground color.

     Args:
         self: (todo): write your description
         highlight_color: (todo): write your description
     """
		self.highlight_tag.set_property('foreground',
			Gdk.color_parse(highlight_color).to_string())

	def set_highlight_background(self,background_highlight_color):
     """
     Sets the background background color.

     Args:
         self: (todo): write your description
         background_highlight_color: (str): write your description
     """
		self.highlight_tag.set_property('background',
			Gdk.color_parse(background_highlight_color).to_string())
	
		
	def set_font(self,font_discription):
     """
     Set the font font.

     Args:
         self: (todo): write your description
         font_discription: (todo): write your description
     """
		pangoFont = Pango.FontDescription(font_discription)
		self.modify_font(pangoFont)
	
	def set_font_color(self,font_color):
     """
     Set the font color.

     Args:
         self: (todo): write your description
         font_color: (str): write your description
     """
		self.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(font_color))
		
	def set_background_color(self,background_color):
     """
     Set the background color.

     Args:
         self: (todo): write your description
         background_color: (todo): write your description
     """
		self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(background_color))
	
	def get_cursor_line_number(self):
     """
     Return the cursor position.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		offset = buffer.get_iter_at_mark(insert_mark)
		return offset.get_line()
	
	def get_line_count(self):
     """
     Return the number of lines in the line.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		return buffer.get_line_count()

	def move_cursor_to_line(self,line_number):
     """
     Moves the cursor.

     Args:
         self: (todo): write your description
         line_number: (int): write your description
     """
		buffer = self.get_buffer()
		iter = buffer.get_iter_at_line(line_number)
		buffer.place_cursor(iter)
		self.scroll_to_iter(iter, 0.0,False,0.0,0.0)
	
	def get_modified(self):
     """
     Get the modified modified modified modified modification.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		return buffer.get_modified()
	
	def set_modified(self,value):
     """
     Set the modified modified duration.

     Args:
         self: (todo): write your description
         value: (str): write your description
     """
		buffer = self.get_buffer()
		buffer.set_modified(value)
	
	def has_selection(self):
     """
     Return whether or false otherwise

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		return buffer.get_has_selection()

	def get_selected_text(self):
     """
     Return the text of the text.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		start,end = buffer.get_selection_bounds()
		return buffer.get_text(start,end,0)
	
	def delete_all_text(self):
     """
     Delete all text in the buffer.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		start, end = buffer.get_bounds()
		buffer.delete(start, end)
	
	# Placing a bookmark
	def get_mark_at_line(self,line):
     """
     Return the marker at the given line.

     Args:
         self: (todo): write your description
         line: (list): write your description
     """
		buffer = self.get_buffer()
		iter = buffer.get_iter_at_line(line)
		return buffer.create_mark(None,iter,True)
		
	# Moving to existing bookmark
	def move_cursor_to_mark(self,mark):
     """
     Move cursor to the cursor.

     Args:
         self: (todo): write your description
         mark: (array): write your description
     """
		buffer = self.get_buffer()
		iter = buffer.get_iter_at_mark(mark)
		buffer.place_cursor(iter)
		self.scroll_to_iter(iter, 0.0,False,0.0,0.0)
	
	# For saving Bookmark with line number
	def get_line_number_of_mark(self,mark):
     """
     Return the number of marker marker in the marker.

     Args:
         self: (todo): write your description
         mark: (todo): write your description
     """
		buffer = self.get_buffer()
		iter = buffer.get_iter_at_mark(mark)
		return iter.get_line()
		
	def get_cursor_mark(self):
     """
     Return the cursor marker.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		return buffer.get_insert()
	
	# For autofilling new bookmark name
	def get_current_line_text(self):
     """
     Return the start of the text.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		mark = buffer.get_insert()
		start_iter = buffer.get_iter_at_mark(mark)
		end_iter = start_iter.copy()
		start_iter.backward_sentence_start()
		end_iter.forward_to_line_end()
		return buffer.get_text(start_iter,end_iter,True)		
	
	# For highlighting bookmark position and go-to-line
	def highlights_cursor_line(self):
     """
     Highlights the cursor.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		self.remove_all_highlights()
		mark = buffer.get_insert()
		start_iter = buffer.get_iter_at_mark(mark)
		end_iter = start_iter.copy()
		end_iter.forward_to_line_end()
		self.scroll_to_iter(start_iter, 0.0,False,0.0,0.0)
		buffer.apply_tag(self.highlight_tag, start_iter, end_iter)
	
	#Find , Find and Replace , Spell check , TextReader
	

	
	def remove_all_highlights(self):
     """
     Removes all highlights from the buffer.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		buffer.remove_tag(self.highlight_tag, start, end)
		
		
			
	def replace_last_word(self,replace_word):
     """
     Replace the previous word.

     Args:
         self: (todo): write your description
         replace_word: (str): write your description
     """
		buffer = self.get_buffer()
		buffer.delete(self.start_iter, self.end_iter)
		buffer.insert(self.start_iter," "+replace_word)
		self.start_iter = self.end_iter.copy()

	def get_next_word(self):
     """
     Return the next word.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		self.start_iter = buffer.get_iter_at_mark(insert_mark)
		self.end_iter = self.start_iter.copy()
		iter0 = self.start_iter.copy()
		iter0.backward_word_start()
		self.remove_all_highlights()
		self.end_iter.forward_word_end()
		buffer.apply_tag(self.highlight_tag, self.start_iter, self.end_iter)
		buffer.place_cursor(self.end_iter)
		return buffer.get_text(self.start_iter,self.end_iter,0)			

	def get_previous_word(self):
     """
     Return the previous word.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		self.end_iter = buffer.get_iter_at_mark(insert_mark)
		self.start_iter = self.end_iter.copy()		
		iter0 = self.end_iter.copy()
		iter0.forward_word_end()
		self.remove_all_highlights()		
		self.start_iter.backward_word_start ()
		buffer.apply_tag(self.highlight_tag, self.start_iter, self.end_iter)
		buffer.place_cursor(self.start_iter)
		return buffer.get_text(self.start_iter,self.end_iter,0)

	def get_context_text(self):
     """
     Return a tuple of the buffer.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		iter1 = buffer.get_iter_at_mark(insert_mark)
		iter2 = iter1.copy()
		iter1.backward_sentence_start()
		iter2.forward_sentence_end()
		return buffer.get_text(iter1,iter2,0)
	
	def delete_last_word(self):
     """
     Delete the previous word.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		buffer.delete(self.start_iter,self.end_iter)
	
	def get_next_sentence(self):
     """
     Return the next sentence.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		iter1 = buffer.get_iter_at_mark(insert_mark)
		iter2 = iter1.copy()
		end = buffer.get_end_iter()
		self.remove_all_highlights()
		lineString = ""
		# Get text word by word till a full stop followed by a space, CR or LF found.
		# If no full stop found, stop at minimum of 1000 more chars

		# Full Stop for English(u002e),  Devanagari(u0964), Sinhala(u0df4),
		# Chinese/Japanese(u3002), Arabic(u06d4)

		# Space - 0020, Carriage return(CR) - 000d , line feed (LF) - 000a

		while( '\u002e\u0020' not in lineString \
		and '\u002e\u000d' not in lineString \
		and '\u002e\u000a' not in lineString \
		and '\u0964\u0020' not in lineString \
		and '\u0964\u000d' not in lineString \
		and '\u0964\u000a' not in lineString \
		and '\u0df4\u0020' not in lineString \
		and '\u0df4\u000d' not in lineString \
		and '\u0df4\u000a' not in lineString \
		and '\u3002\u0020' not in lineString \
		and '\u3002\u000a' not in lineString \
		and '\u3002\u000d' not in lineString \
		and '\u06d4\u0020' not in lineString \
		and '\u06d4\u000a' not in lineString \
		and '\u06d4\u000d' not in lineString \
		and len(lineString) < 1000 and not end.equal(iter2)):
			iter2.forward_char()
			lineString = buffer.get_text(iter1,iter2,0)

		buffer.apply_tag(self.highlight_tag, iter1, iter2)
		buffer.place_cursor(iter2)
		return buffer.get_text(iter1,iter2,0)
	
	def is_cursor_at_end(self):
     """
     Return true if the cursor is at the end of the buffer.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		iter1 = buffer.get_iter_at_mark(insert_mark)
		end = buffer.get_end_iter()
		if(end.equal(iter1)):
			return 1;
		else:
			return 0;

	def is_cursor_at_start(self):
     """
     Return true if the cursor is at the end.

     Args:
         self: (todo): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		iter1 = buffer.get_iter_at_mark(insert_mark)
		start = buffer.get_start_iter()
		if(start.equal(iter1)):
			return 1;
		else:
			return 0;
	
	# For Find/Find and Replace
	
	def move_forward_to_word(self,word):
     """
     Moves the cursor to the next word.

     Args:
         self: (todo): write your description
         word: (str): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		self.start_iter = buffer.get_iter_at_mark(insert_mark)
		result = self.start_iter.forward_search(word, 0, None)
		if (result):
			self.start_iter, self.end_iter = result
			buffer.place_cursor(self.end_iter)
			self.remove_all_highlights()
			buffer.apply_tag(self.highlight_tag, self.start_iter, self.end_iter)
			self.scroll_to_iter(self.start_iter,00,False,False,False)
			return True
		return False

	def move_backward_to_word(self,word):
     """
     Move back backward backward.

     Args:
         self: (todo): write your description
         word: (str): write your description
     """
		buffer = self.get_buffer()
		insert_mark = buffer.get_insert()
		self.start_iter = buffer.get_iter_at_mark(insert_mark)
		self.end_iter = self.start_iter.copy()
		result = self.start_iter.backward_search(word, 0, None)
		if (result):
			self.start_iter, self.end_iter = result
			buffer.place_cursor(self.start_iter)
			self.remove_all_highlights()
			buffer.apply_tag(self.highlight_tag, self.start_iter, self.end_iter)
			self.scroll_to_iter(self.start_iter,00,False,False,False)
			return True
		return False

