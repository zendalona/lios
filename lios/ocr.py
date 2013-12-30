import os
def ocr_image_to_text_file(name,engine,language):
	os.system("convert %s.pnm image"%(name))
	if self.engine == "CUNEIFORM":
		os.system("convert -compress none %s.pnm %s.bmp"%(name,name))
		os.system("cuneiform -f text -l %s -o %s.txt %s.bmp"%(language,name,name))		
	elif self.engine == "TESSERACT":
		os.system("convert %s.pnm %s.png"%(name,name))
		os.system("tesseract %s.png %s -l %s"%(name,name,language))
	else:
		pass
