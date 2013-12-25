#!/bin/bash

if [ $UID -ne 0 ];
then
echo "Please run this script as root"
exit
fi


echo "============ Checking and Installing dependencies ================"
apt-get install tesseract-ocr imagemagick cuneiform python-espeak python-opencv python-imaging-sane \
python-glade2 sane-utils python-numpy espeak poppler-utils python-enchant aspell-en libgnomecanvas2-0

echo "============ Checking and removing existing files ================"
if [ -d /usr/share/lios ];
then 
rm -rf /usr/share/lios
echo "Removing existing Data...............Ok"
fi

if [ -d /usr/lib/python3/dist-packages/lios ];
then 
rm -rf /usr/lib/python3/dist-packages/lios
echo "Removing existing source.............Ok"
fi


if [ -e /usr/bin/lios ];
then 
rm /usr/bin/lios
echo "Removing bin ........................Ok"
fi

if [ -e /usr/share/applications/Lios.desktop ];
then 
rm /usr/share/applications/Lios.desktop
echo "Removing icon .......................Ok"
fi

echo "==================== Copying new files ==========================="
echo "Creating sbw folder  ................OK"
mkdir /usr/share/lios
echo "Copying data ........................OK"
cp -r Data /usr/share/lios/
echo "Copying ui xml's ....................OK"
cp -r ui /usr/share/lios/
echo "Copying source files ................OK"
cp -r lios /usr/lib/python3/dist-packages/
echo "Copying starter .....................OK"
cp icon_and_bin/lios /usr/bin/
echo "Copying icon ........................OK"
cp icon_and_bin/Lios.desktop /usr/share/applications/

ldconfig
echo "============ Compleated==========================================="
