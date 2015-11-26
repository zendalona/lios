###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2014-2015 Nalin.x.Linux GPL-3
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

import enchant

dictionary_language_dict = {"eng" : "en","afr" : "af","am" : "am",
		"ara" : "ar","ara" : "ar","bul" : "bg","ben" : "bn","br" : "br",
		"cat" : "ca","ces" : "cs","cy" : "cy","dan" : "da","ger" : "de",
		"ger" : "de","ell" : "el","eo" : "eo","spa" : "es","est" : "et",
		"eu" : "eu","fa" : "fa","fin" : "fi","fo" : "fo","fra" : "fr",
		"ga" : "ga","gl" : "gl","gu" : "gu","heb" : "he","hin" : "hi",
		"hrv" : "hr","hsb" : "hsb","hun" : "hu","hy" : "hy","id" : "id",
		"is" : "is","ita" : "it","kk" : "kk","kn" : "kn","ku" : "ku",
		"lit" : "lt","lav" : "lv","mal" : "ml ","mr" : "mr ","dut" : "nl",
		"no" : "no","nr" : "nr","ns" : "ns ","or" : "or ","pa" : "pa ",
		"pol" : "pl ","por" : "pt","por" : "pt","por" : "pt","ron" : "ro",
		"rus" : "ru ","slk" : "sk","slv" : "sl","ss" : "ss","st" : "st",
		"swe" : "sv","tam" : "ta","tel" : "te","tl" : "tl","tn" : "tn",
		"ts" : "ts","ukr" : "uk","uz" : "uz","xh" : "xh","zu" : "zu" }

class Dict(enchant.Dict):
	def __init__(self,language="en"):
		super(Dict,self).__init__(language)
	
	#list_languages()
	#suggest(word)
	#check(word)


