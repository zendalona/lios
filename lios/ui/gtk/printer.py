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
from gi.repository import Pango
from gi.repository import PangoCairo


class print_with_action():
	PREVIEW = Gtk.PrintOperationAction.PREVIEW
	PRINT_DIALOG = Gtk.PrintOperationAction.PRINT_DIALOG
	EXPORT = Gtk.PrintOperationAction.EXPORT
	def __init__(self, text, action=None,filename = None):
		self.text_to_print = text	
		self.layout = None
		self.page_breaks = None
		self.font_size=12
		if action==None:
			action = Gtk.PrintOperationAction.PREVIEW
		
		#paper_size = Gtk.PaperSize(Gtk.PAPER_NAME_A4)
		#paper_size = Gtk.PaperSize.get_default()
		#paper_size = Gtk.PaperSize(paper_size)
		
		setup = Gtk.PageSetup()
		#setup.set_paper_size(paper_size)
		
		# PrintOperation
		print_ = Gtk.PrintOperation()
		print_.set_default_page_setup(setup)
		print_.set_unit(Gtk.Unit.MM)
		
		print_.connect("begin_print", self.begin_print)
		print_.connect("draw_page", self.draw_page)
		
		if action == Gtk.PrintOperationAction.EXPORT:
			print_.set_export_filename(filename)
		res = print_.run(action,None)
    
	def begin_print(self, operation, context):
		width = context.get_width()
		height = context.get_height()
		print (height)
		self.layout = context.create_pango_layout()
		self.layout.set_font_description(Pango.FontDescription("Sans " + str(self.font_size)))
		self.layout.set_width(int(width*Pango.SCALE))

		self.layout.set_text(self.text_to_print,len(self.text_to_print))

		num_lines = self.layout.get_line_count()
		print ("num_lines: ", num_lines)
		
		page_breaks = []
		page_height = 0
		
		for line in range(num_lines):
			layout_line = self.layout.get_line(line)
			ink_rect, logical_rect = layout_line.get_extents()
			
			x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
			
			line_height = lheight / 1024.0 # 1024.0 is float(pango.SCALE)
			page_height += line_height
			
			print ("page_height ", page_height)
			if page_height + line_height > height:
				page_breaks.append(line)
				page_height = 0
				page_height += line_height
		operation.set_n_pages(len(page_breaks) + 1)
		self.page_breaks = page_breaks
    
	def draw_page (self, operation, context, page_number):
		assert isinstance(self.page_breaks, list)
		#print page_number
		if page_number == 0:
			start = 0
		else:
			start = self.page_breaks[page_number - 1]
		try:
			end = self.page_breaks[page_number]
		except IndexError:
			end = self.layout.get_line_count()
		
		cr = context.get_cairo_context()
		cr.set_source_rgb(0, 0, 0)
		i = 0
		start_pos = 0
		iter = self.layout.get_iter()
		while 1:
			if i >= start:
				line = iter.get_line()
				_, logical_rect = iter.get_line_extents()
				x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
				baseline = iter.get_baseline()
				if i == start:
					start_pos = y_bearing / 1024.0 # 1024.0 is float(pango.SCALE)
				cr.move_to(x_bearing / 1024.0, baseline / 1024.0 - start_pos)
				PangoCairo.show_layout_line(cr, line)
			i += 1
			if not (i < end and iter.next_line()):
				break



