###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2014 Nalin.x.Linux GPL-3
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
Version:        1.9
Release:        1.9
License:        GPL-3.0+
Summary:        Linux-Intelligent-Ocr-Solution
Url:            http://sourceforge.net/projects/lios/
Group:          Graphics
Source0:        lios-1.9.tar.gz
BuildArch:      noarch
Requires:       espeak 
Requires:       python3-gobject
Requires:       python3-enchant
Requires:	PackageKit-gtk3-module
Requires:       aspell-en 
Requires:       cuneiform 
Requires:       tesseract
Requires:       python3-espeak


%description
Lios is a free and open source software for converting print in to text using either scanner or a camera, It can also produce text out of scanned images from other sources such as Pdf, Image or Folder containing Images. Program is given total accessibility for visually impaired. Lios is written in python3, and we release it under GPL-3 license. There are great many possibilities for this program, Feedback is the key to it, Expecting your feedback Nalin.x.Linux@gmail.com

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install -O1 --skip-build --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root)
%doc COPYING NEWS
%{python3_sitelib}/lios/
%{python3_sitelib}/lios-*

%{_datadir}/lios/*
%{_datadir}/applications/*
%{_bindir}/*


#%changelog
#* Mon Jan 27 1014 
#- license update: GPL-3.0+
#  No indication of GPL-3.0 (only) files.
