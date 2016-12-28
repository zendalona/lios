Linux-intelligent-ocr-solution
======


Lios is a free and open source software for converting print in to text using either scanner or a camera, It can also produce text out of scanned images from other sources such as Pdf, Image, Folder containing Images or screenshot. Program is given total accessibility for visually impaired. Lios is written in python3, and we release it under GPL-3 license. There are great many possibilities for this program, Feedback is the key to it, Expecting your feedback.

Features
======

1. Import images from Scanner, PDFs, Folder, or Webcam,
2. Take and Recognize Screenshot,
3. Recognize Selected Areas(Rectangle selection),
4. Support two OCR Engines (Cuneiform,Tesseract),
5. Tesseract Trainer GUI - Train your Tesseract to improve accuracy,
6. Text-Cleaner - Post process your output with match-replace dialog,
7. Tesseract-Trainer - Train your tesseract ocr engine to improve the accuracy, 
8. Full Auto Rotation for any Language(If aspell installed for the language, Eg : "sudo apt-get install aspell-hi" for Hindi,
9. Side by side view of image and output
10. Advanced Scanner Brightness optimizer,
11. Text Reader for low vision with Highlighting, With user selected Color, Font, and Background Color,
12. Audio converter(espeak),
13. Spell-checker(aspell),
14. Export as pdf (text/images),
15. Dictionary Support for English(Artha)
16. Options for save, load and reset settings,
17. Other options - Find, Find-and-Replace, Go-To-Page, Go-To-Line, Append file, Punch File,
Selection of starting page number, page numbering mode and number of pages to scan,
Selection of Scan area, brightness, resolution and time between repeated scanning,
Output Insert position, image rotation and zoom options, etc


Installing
======
Dependecy list : python3, python3-imaging-sane|python3-sane, python3-speechd, tesseract-ocr,
imagemagick, cuneiform, espeak,poppler-utils, python3-enchant,aspell-en, gir1.2-gst-plugins-base-1.0, gir1.2-gstreamer-1.0

git clone https://gitlab.com/Nalin-x-Linux/lios-3.git

cd lios-3

python3 setup.py install --install-data=/usr

Links
======
Forum : https://groups.google.com/forum/#!forum/lios

Home Page : http://sourceforge.net/projects/lios/?source=navbar

Video Tutorials : https://www.youtube.com/playlist?list=PLn29o8rxtRe1zS1r2-yGm1DNMOZCgdU0i


Disclaimer
======
    Copyright (c) 2011-2015 Lios Development Team 

    All rights reserved . Redistribution and use in source and binary forms, with or without modification,
    
    are permitted provided that the following conditions are met: 

    Redistributions of source code must retain the below copyright notice, 

    this list of conditions and the following disclaimer. 

    Redistributions in binary form must reproduce the below copyright notice, 

    this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 

    Neither the name of the nor the Lios team names of its 

    contributors may be used to endorse or promote products derived from this software without specific prior written permission. 

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
    IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
    OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
    EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE." 

FREE SOFTWARE FREE SOCIETY
