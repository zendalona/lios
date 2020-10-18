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
from lios import localization
_ = localization._

stock_icon_dict = { _("_File") :"edit-copy",
					_("New") :"document-new",
					_("Open"):"document-open",
					_("Save"):"document-save",
					_("Save-As"):"document-save-as",
					_("Find"):"find",
					_("Find-Replace"):"find-replace",
					_("Text-Cleaner"):"find-replace",
					_("Import"):"document-open",
					_("Export"):"document-save",
					_("Apply-From-Cursor"):"find-replace",
					_("Apply-Entire"):"find-replace",
					_("Train-Tesseract"):"system-upgrade",
					_("Spell-Check"):"check-spelling",
					_("Start-Reader"):"media-playback-start",
					_("Stop-Reader"):"media-playback-stop",
					_("Increase-Reader-Speed"):"go-up",
					_("Decrease-Reader-Speed"):"go-down",
					_("Stop-All-Process"):"media-playback-stop",
					_("Go-To-Page"):"go-jump",
					_("Go-To-Line"):"go-jump",
					_("Undo"):"edit-undo",
					_("Redo"):"edit-redo",
					_("Delete"):"remove",
					_("Punch-Text"):"insert-text",
					_("Append-Text"):"insert-text",
					_("Zoom-In"):"zoom-in",
					_("Zoom-Fit"):"zoom-fit",
					_("Zoom-Out"):"zoom-out",
					_("Rotate-Left"):"rotate-left",
					_("Rotate-Right"):"rotate-right",
					_("Rotate-Twice"):"flip-vertical",
					_("_Image"):"image",
					_("Import-Pdf"):"application-pdf",
					_("Import-Folder"):"folder-pictures",
					_("Import-Image"):"image",
					_("Invert-List"):"sort-descending",
					_("Recognize"):"convert",
					_("_Recognize"):"convert",
					_("Recognize-Selected-Images"):"convert",
					_("Recognize-All-Images"):"convert",
					_("Recognize-Selected-with-rotation"):"convert",
					_("Recognize-All-with-rotation"):"convert",
					_("Recognize-Selected-Areas"):"convert",
					_("Recognize-Current-Image"):"convert",
					_("Recognize-Current-Image-With-Rotation"):"convert",
					_("Clear"):"clear",
					_("Print"):"print",
					_("Export-Text-As-Pdf"):"application-pdf",
					_("Export-As-Pdf"):"application-pdf",					
					_("Print-Preview"):"print-preview",
					_("Quit"):"quit",
					_("_Edit"):"edit-cut",
					_("Cut"):"edit-cut",
					_("Copy"):"edit-copy",
					_("Paste"):"edit-paste",
					_("Bookmark"):"emblem-favorite",
					_("Bookmark-Table"):"emblem-favorite",
					_("Import-Bookmarks"):"emblem-favorite",
					_("Bookmark-Table-Complete"):"emblem-favorite",
					_("Update-Scanner-List"):"scanner",
					_("_Scan"):"scanner",
					_("Scan-Image"):"scanner",
					_("Scan-Image-Repeatedly"):"scanner",
					_("Scan-and-Ocr"):"scanner",
					_("Scan-and-Ocr-Repeatedly"):"scanner",
					_("Optimize-Scanner-Brightness"):"scanner",
					_("Scan-Using-Webcam"):"camera-web",
					_("Take-Screenshot"):"camera",
					_("Take-and-Recognize-Screenshot"):"camera",
					_("_Preferences"):"preferences",
					_("Preferences"):"preferences",
					_("Preferences-Scanning"):"preferences",
					_("Preferences-General"):"preferences",
					_("Preferences-Recognition"):"preferences",
					_("Restore"):"clear",
					_("Load"):"document-open",
					_("_Tools"):"accessories-text-editor",
					_("Dictionary"):"accessories-dictionary",
					_("Audio-Converter"):"audio-input-microphone",
					_("Help"):"info",
					_("Open-Readme"):"info",
					_("Video-Tutorials"):"info",
					_("Open-Home-Page"):"info",
					_("Get-Source-Code"):"info",
					_("About"):"about"}
					
