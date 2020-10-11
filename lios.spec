###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2018 Nalin.x.Linux GPL-3
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/

Name:           lios
Version:        2.8
Release:        0
License:        GPL-3.0+
Summary:        Linux-Intelligent-Ocr-Solution
Url:            http://sourceforge.net/projects/lios/
Group:          Graphics
Source0:        lios-2.8.tar.gz
BuildArch:      noarch
Requires:       espeak 
Requires:       python3-gobject
Requires:       python3-enchant
Requires:       python3-speechd
Requires:       python3-sane
# Requires:       python3-pillow-sane for fedora 20
Requires:	PackageKit-gtk3-module
Requires:       aspell-en 
Requires:       cuneiform 
Requires:       tesseract
Requires:       poppler-utils
Requires:       ImageMagick

%description
Lios is a free and open source software for converting print in to text using either scanner, camera, or screenshot, It can also produce text out of scanned images from other sources such as Pdf, Image or Folder containing Images. Program is given total accessibility for visually impaired.  Lios is written in python3, and we release it under GPL-3 license.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install -O1 --skip-build --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root)
%doc COPYING NEWS
#%{python3_sitelib}/*
/usr/lib/python3.6/site-packages/*

%{_datadir}/lios/*
%{_datadir}/lios/icons/*
%{_datadir}/applications/*
%{_datadir}/doc/*
%{_datadir}/man/man1/*
%{_datadir}/pixmaps/*
%{_bindir}/*


#%changelog
#* Mon Jan 27 1014 
#- license update: GPL-3.0+
#  No indication of GPL-3.0 (only) files.
