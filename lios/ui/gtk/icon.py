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
import gettext
gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
gettext.textdomain('myapplication')
_ = gettext.gettext

stock_icon_dict = { _("File") :"edit-copy",
					_("New") :"gtk-new",
					_("Open"):"gtk-open",
					_("Save"):"gtk-save",
					_("Save-As"):"gtk-save-as",
					_("Find"):"gtk-find",
					_("Find-Replace"):"gtk-find-and-replace",
					_("Spell-Check"):"gtk-spell-check",
					_("Start-Reader"):"media-playback-start",
					_("Increase-Reader-Speed"):"gtk-go-up",
					_("Decrease-Reader-Speed"):"gtk-go-down",
					_("Stop-Reader"):"media-playback-stop",
					_("Stop-All-Process"):"media-playback-stop",
					_("Go-To-Page"):"go-jump",
					_("Go-To-Line"):"go-jump",
					_("Undo"):"edit-undo",
					_("Redo"):"edit-redo",
					_("Delete"):"gtk-remove",
					_("Punch-Text"):"insert-text",
					_("Append-Text"):"insert-text",
					_("Zoom-In"):"gtk-zoom-in",
					_("Zoom-Fit"):"gtk-zoom-fit",
					_("Zoom-Out"):"gtk-zoom-out",
					_("Rotate-Left"):"object-rotate-left",
					_("Rotate-Right"):"object-rotate-right",
					_("Rotate-Twice"):"object-flip-vertical",
					_("Image"):"insert-image",
					_("Import-Pdf"):"application-pdf",
					_("Import-Folder"):"folder-pictures",
					_("Import-Image"):"image",
					_("Invert-List"):"gtk-sort-descending",
					_("Recognize"):"gtk-convert",
					_("Recognize-Selected-Images"):"gtk-convert",
					_("Recognize-All-Images"):"gtk-convert",
					_("Recognize-Selected-with-rotation"):"gtk-convert",
					_("Recognize-All-with-rotation"):"gtk-convert",
					_("Recognize-Selected-Areas"):"gtk-convert",
					_("Recognize-Current-Image"):"gtk-convert",
					_("Recognize-Current-Image-With-Rotation"):"gtk-convert",
					_("Clear"):"gtk-clear",
					_("Print"):"gtk-print",
					_("Export-Text-As-Pdf"):"application-pdf",
					_("Export-As-Pdf"):"application-pdf",					
					_("Print-Preview"):"gtk-print-preview",
					_("Quit"):"gtk-quit",
					_("Edit"):"edit-cut",
					_("Cut"):"gtk-cut",
					_("Copy"):"gtk-copy",
					_("Paste"):"gtk-paste",
					_("Bookmark"):"emblem-favorite",
					_("Bookmark-Table"):"emblem-favorite",
					_("Import-Bookmarks"):"emblem-favorite",
					_("Bookmark-Table-Complete"):"emblem-favorite",
					_("Update-Scanner-List"):"scanner",
					_("Scan"):"scanner",
					_("Scan-Image"):"scanner",
					_("Scan-Image-Repeatedly"):"scanner",
					_("Scan-and-Ocr"):"scanner",
					_("Scan-and-Ocr-Repeatedly"):"scanner",
					_("Optimise-Scanner-Brightness"):"scanner",
					_("Scan-Using-Webcam"):"camera-web",
					_("Take-Screenshot"):"camera-photo",
					_("Take-and-Recognize-Screenshot"):"camera-photo",
					_("Preferences"):"gtk-preferences",
					_("Preferences-Scanning"):"gtk-preferences",
					_("Preferences-General"):"gtk-preferences",
					_("Preferences-Recognition"):"gtk-preferences",
					_("Restore"):"gtk-clear",
					_("Load"):"gtk-open",
					_("Tools"):"accessories-text-editor",
					_("Dictionary"):"accessories-dictionary",
					_("Audio-Converter"):"audio-input-microphone",
					_("Help"):"gtk-help",
					_("Open-Readme"):"gtk-help",
					_("Video-Tutorials"):"gtk-help",
					_("Open-Home-Page"):"gtk-help",
					_("Get-Source-Code"):"gtk-help",
					_("About"):"gtk-about"}
					
