#!/usr/bin/env python3
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



from lios.ocr.ocr_engine_base import OcrEngineBase
from lios.ocr.ocr_engine_cuneiform import OcrEngineCuneiform
from lios.ocr.ocr_engine_tesseract import OcrEngineTesseract
from lios.ocr.ocr_engine_ocrad import OcrEngineOcrad
from lios.ocr.ocr_engine_gocr import OcrEngineGocr
from lios.ocr.ocr_engine_abbyy_finereader11 import OcrEngineAbbyyFineReader11
from lios.ocr.ocr_engine_abbyy_finereader9 import OcrEngineAbbyyFineReader9

def get_available_engines():
    """
    Returns a list of available engines.

    Args:
    """
	list = []
	# Note : The engine classes should be sorted otherwise each time this function
	# will return same engine list in a random order.  
	for engine_name in ["Tesseract","Cuneiform","ABBYY FineReader9","ABBYY FineReader11",
						"Gocr", "Ocrad" ]:
		for item in OcrEngineBase.__subclasses__():
			if (item.name == engine_name and item.is_available()):
				list.append(item)
	
	import operator
	return list


