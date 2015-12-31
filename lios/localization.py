#!/usr/bin/env python3
import gettext
from lios import macros
gettext.bindtextdomain(macros.app_name, '/usr/share/locale')
gettext.textdomain(macros.app_name)
_ = gettext.gettext
