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

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import PangoCairo
import math
import shutil

from lios.ui.gtk import dialog  # Custom dialog used in LIOS

class print_with_action():
	PREVIEW = Gtk.PrintOperationAction.PREVIEW
	PRINT_DIALOG = Gtk.PrintOperationAction.PRINT_DIALOG
	EXPORT = Gtk.PrintOperationAction.EXPORT

	def __init__(self, text, action=None, filename=None):
		self.text_to_print = text	
		self.layout = None
		self.page_breaks = None
		self.font = "sans"
		self.font_size = 12

		if action is None:
			action = Gtk.PrintOperationAction.PREVIEW
		
		# Check if evince is missing and show a dialog
		if action == Gtk.PrintOperationAction.PREVIEW and not shutil.which("evince"):
			dlg = dialog.Dialog("Print Preview Error", ("OK", dialog.Dialog.BUTTON_ID_1))
			label = Gtk.Label(
				"Evince (PDF Viewer) is not installed.\nPlease install it using:\n\nsudo apt install evince"
			)
			label.set_margin_top(10)
			label.set_margin_bottom(10)
			label.set_margin_start(10)
			label.set_margin_end(10)
			dlg.add_widget(label)
			dlg.show_all()
			dlg.run()
			dlg.destroy()
			return  # Prevent running preview operation

		paper_size = Gtk.PaperSize.new(Gtk.PAPER_NAME_A4)
		
		setup = Gtk.PageSetup()
		setup.set_paper_size(paper_size)
		setup.set_orientation(Gtk.PageOrientation.LANDSCAPE)
		
		print_ = Gtk.PrintOperation()
		print_.set_default_page_setup(setup)
		print_.set_unit(Gtk.Unit.MM)
		print_.set_embed_page_setup(True)
		
		print_.connect("begin_print", self.begin_print)
		print_.connect("draw_page", self.draw_page)
		print_.connect("create-custom-widget", self.create_custom_widget)
		print_.connect("custom-widget-apply", self.custom_widget_apply)
		print_.set_custom_tab_label("Font")

		if action == Gtk.PrintOperationAction.EXPORT:
			print_.set_export_filename(filename)

		res = print_.run(action, None)

	def create_custom_widget(self, *data):
		self.fontbutton = Gtk.FontButton()
		return self.fontbutton

	def custom_widget_apply(self, *data):
		self.font = self.fontbutton.get_font_name()
		desc = Pango.FontDescription.from_string(self.font)
		self.font_size = desc.get_size() / Pango.SCALE

	def begin_print(self, operation, context):
		width = context.get_width()
		height = context.get_height()
		self.layout = context.create_pango_layout()
		self.layout.set_font_description(Pango.FontDescription(self.font))
		self.layout.set_width(int(width * Pango.SCALE))
		self.layout.set_text(self.text_to_print, len(self.text_to_print))
		num_lines = self.layout.get_line_count()
		self.lines_per_page = math.floor(height / (self.font_size / 2))
		pages = int(math.ceil(float(num_lines) / float(self.lines_per_page)))
		operation.set_n_pages(pages)

	def draw_page(self, operation, context, page_number):
		cr = context.get_cairo_context()
		cr.set_source_rgb(0, 0, 0)
		start_line = page_number * self.lines_per_page
		if page_number + 1 != operation.props.n_pages:
			end_line = start_line + self.lines_per_page
		else:
			end_line = self.layout.get_line_count()

		cr.move_to(0, 0)
		iter = self.layout.get_iter()
		i = 0
		while True:
			if i > start_line:
				line = iter.get_line_readonly()
				cr.rel_move_to(0, self.font_size / 2)
				PangoCairo.show_layout_line(cr, line)
			i += 1
			if not (i < end_line and iter.next_line()):
				break


# Optional: for testing
if __name__ == "__main__":
	import os
	from lios import macros
	data = ""
	with open(macros.readme_file, "r") as file:
		data = file.read()
	action = Gtk.PrintOperationAction.PREVIEW
	printer = print_with_action(data, action)
