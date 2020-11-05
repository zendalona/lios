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
#!/usr/bin/env python3


from lios.scanner.driver_base import DriverBase
from lios.scanner.sane_driver import DriverSane
from lios.scanner.scanimage_driver import DriverScanimage

def get_available_drivers():
    """
    Returns a list of all available classes.

    Args:
    """
	list = []
	for item in DriverBase.__subclasses__():
		if item.is_available():
			list.append(item)
	return list

