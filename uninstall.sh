#!/bin/bash

if [ $UID -ne 0 ];
then
echo "Please run this script as root"
exit
fi


echo "============ Checking and removing existing files ================"
if [ -d /usr/share/lios ];
then 
rm -rf /usr/share/lios
echo "Removing existing Data...............Ok"
fi

if [ -d /usr/lib/python2.7/dist-packages/lios ];
then 
rm -rf /usr/lib/python2.7/dist-packages/lios
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
echo "============ Compleated==========================================="
