#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
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


import configparser
import shutil
from lios.ui.gtk import widget
from lios.ui.gtk import containers
from lios.ui.gtk import loop
from lios.ui.gtk import dialog

from lios import speech
from lios import localization

_ = localization._


class lios_preferences:
    def __init__(self):
        
        #Setting Default Values
        self.advanced_preferences_enabled = 0  # 0 = disabled, 1 = enabled
        self.font="Georgia 14";self.highlight_font="Georgia 14";
        self.highlight_color="#000000000000";
        self.background_highlight_color="#34346565a4a4";
        self.speech_module=-1;self.speech_language=-1;self.speech_person=-1;
        self.speech_rate=0;self.speech_pitch=0;self.speech_volume=100;
        self.time_between_repeated_scanning=0;self.scan_resolution=300;
        self.scan_driver=1;self.scanner_cache_calibration=0;
        self.scan_brightness=50;self.scan_area=0;self.insert_position=2;
        self.ocr_engine=0;self.language=0;self.language_2=0;self.language_3=0;
        self.mode_of_rotation=0;self.number_of_pages_to_scan=100;
        self.give_page_number = 1;self.page_numbering_type=0;
        self.starting_page_number=1;self.scanner_mode_switching=0;
        self.run_text_cleaner=0;self.rotation_angle=00;
        #Setting theme 
        self.theme = 0
        self.theme_list = [
            ["Black on White", "#000000", "#FFFFFF"],
            ["White on Black", "#FFFFFF", "#000000"],
            ["Green on Black", "#00FF00", "#000000"],
            ["Yellow on Black", "#FFFF00", "#000000"],
            ["Up Sky Blue", "#0F2447", "#A0B0CB"],
            ["Sharp Green", "#19480D", "#A6C99D"],
            ["Broad Yellow", "#322C0B", "#BDB58C"],
            ["Tragic Red", "#42190D", "#B79990"],
            ["Velvet Orchid", "#340E3E", "#B895C1"],
            ["Dollic Pink", "#410E3F", "#C695C4"],
            ["Scale Gray", "#1F2325", "#C9CEC5"],
            ["Brown Brown", "#2B1406", "#D6B9A8"]
        ]


    def set_avalable_scanner_drivers(self,list):
        self.available_scanner_drivers = list

    def set_avalable_ocr_engines(self,list):
        self.available_ocr_engine_list = list
        
    # FUNCTION TO Read PREFERENCES #
    def set_from_file(self,filename):
        config = configparser.ConfigParser()
        if config.read(filename) != []:
            try:
                self.theme = int(config.get('cfg', 'theme')) 
                self.advanced_preferences_enabled = int(config.get('cfg', 'advanced_preferences_enabled', fallback=0))
                self.time_between_repeated_scanning=int(config.get('cfg',"time_between_repeated_scanning"))
                self.scan_resolution=int(config.get('cfg',"scan_resolution"))
                self.scan_brightness=int(config.get('cfg',"scan_brightness"))
                self.ocr_engine=int(config.get('cfg',"ocr_engine"))
                self.scan_area=int(config.get('cfg',"scan_area"))
                self.scan_driver=int(config.get('cfg',"scan_driver"))
                self.insert_position=int(config.get('cfg',"insert_position"))
                self.language=int(config.get('cfg',"language"))
                self.language_2=int(config.get('cfg',"language_2"))
                self.language_3=int(config.get('cfg',"language_3"))
                self.speech_module=int(config.get('cfg',"speech_module"))
                self.speech_language=int(config.get('cfg',"speech_language"))
                self.speech_person=int(config.get('cfg',"speech_person"))
                self.speech_rate=int(config.get('cfg',"speech_rate"))
                self.speech_volume=int(config.get('cfg',"speech_volume"))
                self.speech_pitch=int(config.get('cfg',"speech_pitch"))
                self.number_of_pages_to_scan=int(config.get('cfg',"number_of_pages_to_scan"))#pages
                self.mode_of_rotation = int(config.get('cfg',"mode_of_rotation"))
                self.rotation_angle = int(config.get('cfg',"rotation_angle"))
                self.give_page_number=int(config.get('cfg',"give_page_number"))
                self.page_numbering_type=int(config.get('cfg',"numbering_type"))
                self.scanner_mode_switching=int(config.get('cfg',"scanner_mode_switching"))
                self.run_text_cleaner=int(config.get('cfg',"run_text_cleaner"))
                self.scanner_cache_calibration=int(config.get('cfg',"scanner_cache_calibration"))						
                self.starting_page_number=int(config.get('cfg',"starting_page_number"))
                self.highlight_color=config.get('cfg',"highlight_color")
                self.background_highlight_color=config.get('cfg',"highlight_background_color")
                self.font=config.get('cfg',"font")
                self.highlight_font=config.get('cfg',"highlight_font")				
                self.require_scanner_refresh = True
            except:
                self.__init__()
        else:
            self.__init__()

    # Set speech module, language and person if speech_module is not set
    def set_default_speech_module_and_language(self):
        if(self.speech_module == -1):
            try:
                test = speech.Speech()
                output_modules_list = test.list_output_modules()
                if("espeak-ng" in output_modules_list):
                    self.speech_module = output_modules_list.index('espeak-ng')
                    test.set_output_module('espeak-ng')
                elif("espeak" in output_modules_list):
                    self.speech_module = output_modules_list.index('espeak')
                    test.set_output_module('espeak')

                # if espeak or espeak-ng set language
                if(self.speech_module != -1):
                    import locale
                    language_code, encoding = locale.getdefaultlocale()
                    localeValues = language_code.split('_')
                    language = localeValues[0]
                    language_person_dict = test.get_language_person_dict()
                    if(language in language_person_dict.keys()):
                        self.speech_language = list(language_person_dict.keys()).index(language)
                        self.speech_person=0;
                else:
                    self.speech_module=0;self.speech_language=0;self.speech_person=0;

                #Closing
                test.close()
            except:
                self.speech_module=0;self.speech_language=0;self.speech_person=0;
                pass

    def save_to_file(self,filename):
        #Removing old configuration file
        try:
            os.remove(filename)
        except:
            pass		
        config = configparser.ConfigParser()
        config.add_section('cfg')
        config.set('cfg', 'advanced_preferences_enabled', str(self.advanced_preferences_enabled))
        config.set('cfg', 'theme', str(self.theme))
        config.set('cfg',"time_between_repeated_scanning",str(self.time_between_repeated_scanning))
        config.set('cfg',"scan_resolution",str(self.scan_resolution))
        config.set('cfg',"scan_brightness",str(self.scan_brightness))
        config.set('cfg',"ocr_engine",str(self.ocr_engine))
        config.set('cfg',"insert_position",str(self.insert_position))
        config.set('cfg',"scan_area",str(self.scan_area))
        config.set('cfg',"scan_driver",str(self.scan_driver))
        config.set('cfg',"language",str(self.language))
        config.set('cfg',"language_2",str(self.language_2))
        config.set('cfg',"language_3",str(self.language_3))
        config.set('cfg',"speech_module",str(self.speech_module))
        config.set('cfg',"speech_language",str(self.speech_language))
        config.set('cfg',"speech_person",str(self.speech_person))
        config.set('cfg',"speech_pitch",str(self.speech_pitch))
        config.set('cfg',"speech_volume",str(self.speech_volume))
        config.set('cfg',"speech_rate",str(self.speech_rate))
        config.set('cfg',"number_of_pages_to_scan",str(self.number_of_pages_to_scan))
        config.set('cfg',"mode_of_rotation",str(self.mode_of_rotation))
        config.set('cfg',"rotation_angle",str(self.rotation_angle))
        config.set('cfg',"give_page_number",str(self.give_page_number))
        config.set('cfg',"numbering_type",str(self.page_numbering_type))
        config.set('cfg',"scanner_mode_switching",str(self.scanner_mode_switching))
        config.set('cfg',"run_text_cleaner",str(self.run_text_cleaner))
        config.set('cfg',"scanner_cache_calibration",str(self.scanner_cache_calibration))				
        config.set('cfg',"starting_page_number",str(self.starting_page_number))
        config.set('cfg',"highlight_color",str(self.highlight_color))
        config.set('cfg',"highlight_background_color",str(self.background_highlight_color))
        config.set('cfg',"font",str(self.font))
        config.set('cfg',"highlight_font",str(self.highlight_font))
        with open(filename, 'w') as configfile:
            config.write(configfile)


    def update_page_number(self):
        loop.acquire_lock()
        if (self.page_numbering_type == 0):
            self.starting_page_number = self.starting_page_number + 1
        else:
            self.starting_page_number = self.starting_page_number + 2
        loop.release_lock()

    def get_page_number_as_string(self):
        if (self.page_numbering_type == 0):
            return ("{0}".format(self.starting_page_number))
        else:
            return ("{0}-{1}".format(self.starting_page_number,self.starting_page_number + 1))
    
    
    #Function for manipulating preferences		
    def open_configure_dialog(self, page=0):
        def change_engine(*data):
            index_engine = combobox_engine.get_active()
            combobox_language.clear()
            combobox_language_2.clear()
            combobox_language_3.clear()
            combobox_language_2.add_item("---")
            combobox_language_3.add_item("---")

            for item in self.available_ocr_engine_list[index_engine][1]:
                combobox_language.add_item(item)
                combobox_language_2.add_item(item)
                combobox_language_3.add_item(item)
            combobox_language.set_active(self.language)
            combobox_language_2.set_active(self.language_2)
            combobox_language_3.set_active(self.language_3)

            if (self.available_ocr_engine_list[index_engine][2] == True):
                label_language_2.set_sensitive(True)
                label_language_3.set_sensitive(True)
                combobox_language_2.set_sensitive(True)
                combobox_language_3.set_sensitive(True)
            else:
                label_language_2.set_sensitive(False)
                label_language_3.set_sensitive(False)
                combobox_language_2.set_sensitive(False)
                combobox_language_3.set_sensitive(False)

        def change_speech_module(*data):
            module_index = combobox_speech_module.get_active()

            test = speech.Speech()
            output_modules_list = test.list_output_modules()
            test.set_output_module(output_modules_list[module_index])

            self.speech_language_person_dict = test.get_language_person_dict()
            test.close()

            try:
                combobox_speech_language.disconnect_by_func(change_speech_language)
            except(TypeError):
                pass

            combobox_speech_language.clear()

            if(len(self.speech_language_person_dict.keys()) == 0):
                combobox_speech_language.add_item(_("Default"))
                self.speech_language = 0
            else:
                for item in self.speech_language_person_dict.keys():
                    combobox_speech_language.add_item(item)

            combobox_speech_language.connect_change_callback_function(change_speech_language)

            if(self.speech_language < len(self.speech_language_person_dict.keys())):
                combobox_speech_language.set_active(self.speech_language)
            else:
                combobox_speech_language.set_active(0)
                self.speech_language = 0

        def change_speech_language(*data):
            combobox_speech_person.clear()

            if(self.speech_person == -1):
                self.speech_person = 0

            if(len(list(self.speech_language_person_dict.keys())) == 0):
                combobox_speech_person.add_item(_("Default"))
                combobox_speech_person.set_active(0)
                self.speech_person = 0
                return

            index_language = combobox_speech_language.get_active()
            language = list(self.speech_language_person_dict.keys())[index_language]

            for item in self.speech_language_person_dict[language]:
                combobox_speech_person.add_item(item)

            if(self.speech_person >= len(self.speech_language_person_dict[language])):
                self.speech_person = 0
            combobox_speech_person.set_active(self.speech_person)

        def change_mode_of_rotation(*data):
            if(combobox_mode_of_rotation.get_active() == 2):
                combobox_angle.show()
                label_angle.show()
            else:
                combobox_angle.hide()
                label_angle.hide()

        def toggle_advanced_preferences(*data):
            """Smoothly toggle advanced preferences visibility"""
            is_advanced = checkbutton_advanced_pref.get_active()
            self.advanced_preferences_enabled = int(is_advanced)

            # General page advanced widgets
            advanced_general_widgets = [
                label_highlight_font, fontbutton_highlight_font,
                label_speech_module, combobox_speech_module,
                label_speech_language, combobox_speech_language,
                label_speech_person, combobox_speech_person,
                label_speech_rate, spin_speech_rate,
                label_speech_pitch, spin_speech_pitch,
                label_speech_volume, spin_speech_volume
            ]

            # Recognition page advanced widgets
            advanced_recognition_widgets = [
                checkbutton_run_text_cleaner,
                label_insert_position, combobox_insert_position,
                seperator_1, seperator_2,
                checkbutton_give_page_number,
                label_numbering_type, combobox_numbering_type
            ]

            # Scanning page advanced widgets  
            advanced_scanning_widgets = [
                sparator_3,
                label_number_of_pages_to_scan, spin_number_of_pages_to_scan,
                label_time_bitween_repeted_scanning, spin_time_bitween_repeted_scanning,
                sparator_4,
                checkbutton_scan_mode_switching,
                checkbutton_scanner_cache_calibration
            ]

            # Show/hide widgets based on advanced mode
            all_advanced_widgets = (advanced_general_widgets + 
                                  advanced_recognition_widgets + 
                                  advanced_scanning_widgets)

            for widget in all_advanced_widgets:
                if is_advanced:
                    widget.show()
                else:
                    widget.hide()

            # Handle spacer visibility (opposite of advanced widgets)
            if is_advanced:
                spacer.hide()
            else:
                spacer.show()

        self.require_scanner_refresh = False
        outer_box = containers.Box(containers.Box.VERTICAL)

        # Advanced preferences checkbox
        checkbutton_advanced_pref = widget.CheckButton(_("Enable Advanced Preferences"))
        checkbutton_advanced_pref.set_active(self.advanced_preferences_enabled)
        checkbutton_advanced_pref.connect("toggled", toggle_advanced_preferences)
        outer_box.add(checkbutton_advanced_pref)

        notebook = containers.NoteBook()
        outer_box.add(notebook)

        # GENERAL PAGE
        label_theme = widget.Label(_("Editor Theme"))
        combobox_theme = widget.ComboBox()
        for item in self.theme_list:
            combobox_theme.add_item(item[0])
        combobox_theme.set_active(self.theme)

        # Spacer for non-advanced mode
        spacer = widget.Label("")
        spacer.set_size_request(-1, 270)

        label_font = widget.Label(_("Font"))
        fontbutton_font = widget.FontButton()
        fontbutton_font.set_font_name(self.font)
        label_font.set_mnemonic_widget(fontbutton_font)

        # Advanced widgets for general page
        label_highlight_font = widget.Label(_("Highlight Font"))
        fontbutton_highlight_font = widget.FontButton()
        fontbutton_highlight_font.set_font_name(self.highlight_font)
        label_highlight_font.set_mnemonic_widget(fontbutton_highlight_font)

        label_highlight_color = widget.Label(_("Highlight Color"))
        colorbutton_highlight = widget.ColorButton()
        colorbutton_highlight.set_color_from_string(self.highlight_color)
        label_highlight_color.set_mnemonic_widget(colorbutton_highlight)

        label_highlight_background = widget.Label(_("Highlight Background"))
        colorbutton_highlight_background = widget.ColorButton()
        colorbutton_highlight_background.set_color_from_string(self.background_highlight_color)
        label_highlight_background.set_mnemonic_widget(colorbutton_highlight_background)

        label_speech_module = widget.Label(_("Speech Module"))
        combobox_speech_module = widget.ComboBox()
        for item in speech.Speech().list_output_modules():
            combobox_speech_module.add_item(item)
        combobox_speech_module.connect_change_callback_function(change_speech_module)
        label_speech_module.set_mnemonic_widget(combobox_speech_module)

        label_speech_language = widget.Label(_("Speech Language"))
        combobox_speech_language = widget.ComboBox()
        label_speech_language.set_mnemonic_widget(combobox_speech_language)

        label_speech_person = widget.Label(_("Speech Person"))
        combobox_speech_person = widget.ComboBox()
        label_speech_person.set_mnemonic_widget(combobox_speech_person)

        combobox_speech_module.set_active(self.speech_module)

        label_speech_rate = widget.Label(_("Speech Rate"))
        spin_speech_rate = widget.SpinButton(self.speech_rate,-100,100,1,10,0)
        label_speech_rate.set_mnemonic_widget(spin_speech_rate)

        label_speech_volume = widget.Label(_("Speech Volume"))
        spin_speech_volume = widget.SpinButton(self.speech_volume,-100,100,1,10,0)
        label_speech_volume.set_mnemonic_widget(spin_speech_volume)

        label_speech_pitch = widget.Label(_("Speech Pitch"))
        spin_speech_pitch = widget.SpinButton(self.speech_pitch,-100,100,1,10,0)
        label_speech_pitch.set_mnemonic_widget(spin_speech_pitch)

        # Create grid with all widgets (both basic and advanced)
        grid_general = containers.Grid()
        grid_general.add_widgets([
            (label_theme, 1, 1), (combobox_theme, 1, 1), containers.Grid.NEW_ROW,
            (label_font,1,1),(fontbutton_font,1,1),containers.Grid.NEW_ROW,
            (label_highlight_font,1,1),(fontbutton_highlight_font,1,1),containers.Grid.NEW_ROW,
            (label_speech_module,1,1),(combobox_speech_module,1,1),containers.Grid.NEW_ROW,
            (label_speech_language,1,1),(combobox_speech_language,1,1),containers.Grid.NEW_ROW,
            (label_speech_person,1,1),(combobox_speech_person,1,1),containers.Grid.NEW_ROW,
            (label_speech_rate,1,1),(spin_speech_rate,1,1),containers.Grid.NEW_ROW,
            (label_speech_pitch,1,1),(spin_speech_pitch,1,1),containers.Grid.NEW_ROW,
            (label_speech_volume,1,1),(spin_speech_volume,1,1),containers.Grid.NEW_ROW,
            (spacer,1,9),containers.Grid.NEW_ROW])

        notebook.add_page(_("General"), grid_general)

        # RECOGNITION PAGE
        label_engine = widget.Label(_("Engine"))
        combobox_engine = widget.ComboBox()
        combobox_engine.connect_change_callback_function(change_engine)
        label_engine.set_mnemonic_widget(combobox_engine)

        for item in self.available_ocr_engine_list:
            combobox_engine.add_item(item[0])

        label_language = widget.Label(_("Language"))
        combobox_language = widget.ComboBox()
        label_language.set_mnemonic_widget(combobox_language)

        label_language_2 = widget.Label(_("Language - 2"))
        combobox_language_2 = widget.ComboBox()
        label_language_2.set_mnemonic_widget(combobox_language_2)

        label_language_3 = widget.Label(_("Language - 3"))
        combobox_language_3 = widget.ComboBox()
        label_language_3.set_mnemonic_widget(combobox_language_3)

        combobox_engine.set_active(self.ocr_engine)
        combobox_language.set_active(self.language)
        combobox_language_2.set_active(self.language_2)
        combobox_language_3.set_active(self.language_3)

        # Advanced widgets for recognition page
        checkbutton_run_text_cleaner = widget.CheckButton(_("Run Text Cleaner"))
        checkbutton_run_text_cleaner.set_active(self.run_text_cleaner)

        label_insert_position = widget.Label(_("Insert Position"))
        combobox_insert_position = widget.ComboBox()
        combobox_insert_position.add_item(_("Start"))
        combobox_insert_position.add_item(_("Cursor"))
        combobox_insert_position.add_item(_("End"))
        combobox_insert_position.set_active(self.insert_position)
        label_insert_position.set_mnemonic_widget(combobox_insert_position)

        seperator_1 = widget.Separator()

        label_mode_of_rotation = widget.Label(_("Mode Of Rotation"))
        combobox_mode_of_rotation = widget.ComboBox()
        combobox_mode_of_rotation.add_item(_("Full Automatic"))
        combobox_mode_of_rotation.add_item(_("Partial Automatic"))
        combobox_mode_of_rotation.add_item(_("Manual"))
        combobox_mode_of_rotation.connect_change_callback_function(change_mode_of_rotation)
        label_mode_of_rotation.set_mnemonic_widget(combobox_mode_of_rotation)

        label_angle = widget.Label(_("Angle"))
        combobox_angle = widget.ComboBox()
        combobox_angle.add_item(_("00"))
        combobox_angle.add_item(_("90"))
        combobox_angle.add_item(_("180"))
        combobox_angle.add_item(_("270"))
        label_angle.set_mnemonic_widget(combobox_angle)

        seperator_2 = widget.Separator()

        checkbutton_give_page_number = widget.CheckButton(_("Give Page Number"))
        checkbutton_give_page_number.set_active(self.give_page_number)

        label_numbering_type = widget.Label(_("Page Numbering Type"))
        combobox_numbering_type = widget.ComboBox()
        combobox_numbering_type.add_item(_("Single Page"))
        combobox_numbering_type.add_item(_("Double Page"))
        combobox_numbering_type.set_active(self.page_numbering_type)
        label_numbering_type.set_mnemonic_widget(combobox_numbering_type)

        label_starting_page_number = widget.Label(_("Starting Page Number"))
        spin_starting_page_number = widget.SpinButton(0,0,100000,1,5,0)
        spin_starting_page_number.set_value(self.starting_page_number)
        label_starting_page_number.set_mnemonic_widget(spin_starting_page_number)

        grid_recognition = containers.Grid()
        grid_recognition.add_widgets([
            (label_engine,1,1),(combobox_engine,1,1),containers.Grid.NEW_ROW,
            (label_language,1,1),(combobox_language,1,1),containers.Grid.NEW_ROW,
            (label_language_2,1,1),(combobox_language_2,1,1),containers.Grid.NEW_ROW,
            (label_language_3,1,1),(combobox_language_3,1,1),containers.Grid.NEW_ROW,
            (checkbutton_run_text_cleaner,1,1),containers.Grid.NEW_ROW,
            (label_insert_position,1,1),(combobox_insert_position,1,1),containers.Grid.NEW_ROW,
            (seperator_1,2,1),containers.Grid.NEW_ROW,
            (label_mode_of_rotation,1,1),(combobox_mode_of_rotation,1,1),containers.Grid.NEW_ROW,
            (label_angle,1,1),(combobox_angle,1,1),containers.Grid.NEW_ROW,
            (seperator_2,2,1),containers.Grid.NEW_ROW,
            (checkbutton_give_page_number,1,1),containers.Grid.NEW_ROW,
            (label_numbering_type,1,1),(combobox_numbering_type,1,1),containers.Grid.NEW_ROW,
            (label_starting_page_number,1,1),(spin_starting_page_number,1,1)])

        notebook.add_page(_("Recognition"), grid_recognition)

        combobox_mode_of_rotation.set_active(self.mode_of_rotation)
        combobox_angle.set_active(self.rotation_angle)

        # SCANNING PAGE
        label_resolution = widget.Label(_("Resolution"))
        spin_resolution = widget.SpinButton(300,100,1200,1,5,0)
        spin_resolution.set_value(self.scan_resolution)
        label_resolution.set_mnemonic_widget(spin_resolution)

        label_brightness = widget.Label(_("Brightness"))
        spin_brightness = widget.SpinButton(50,0,100,1,5,0)
        spin_brightness.set_value(self.scan_brightness)
        label_brightness.set_mnemonic_widget(spin_brightness)

        label_scan_area = widget.Label(_("Scan Area"))
        combobox_scan_area = widget.ComboBox()
        label_scan_area.set_mnemonic_widget(combobox_scan_area)
        combobox_scan_area.add_item(_("Full Scan Area"))
        combobox_scan_area.add_item(_("Three Quarters"))
        combobox_scan_area.add_item(_("Two Quarters"))
        combobox_scan_area.add_item(_("One Quarter"))
        combobox_scan_area.set_active(self.scan_area)

        label_scan_driver = widget.Label(_("Driver"))
        combobox_scan_driver = widget.ComboBox()
        label_scan_driver.set_mnemonic_widget(combobox_scan_driver)
        for item in self.available_scanner_drivers:
            combobox_scan_driver.add_item(item)
        combobox_scan_driver.set_active(self.scan_driver)

        # Advanced widgets for scanning page
        sparator_3 = widget.Separator()

        label_number_of_pages_to_scan = widget.Label(_("Number of Pages to Scan"))
        spin_number_of_pages_to_scan = widget.SpinButton(10,2,100,1,5,0)
        spin_number_of_pages_to_scan.set_value(self.number_of_pages_to_scan)
        label_number_of_pages_to_scan.set_mnemonic_widget(spin_number_of_pages_to_scan)

        label_time_bitween_repeted_scanning = widget.Label(_("Time Between Repeated Scanning"))
        spin_time_bitween_repeted_scanning = widget.SpinButton(0,0,30,1,5,0)
        spin_time_bitween_repeted_scanning.set_value(self.time_between_repeated_scanning)
        label_time_bitween_repeted_scanning.set_mnemonic_widget(spin_time_bitween_repeted_scanning)

        sparator_4 = widget.Separator()

        checkbutton_scan_mode_switching = widget.CheckButton(_("Change to binary or linear if possible"))
        checkbutton_scan_mode_switching.set_active(self.scanner_mode_switching)

        checkbutton_scanner_cache_calibration = widget.CheckButton(_("Cache Calibration"))
        checkbutton_scanner_cache_calibration.set_active(self.scanner_cache_calibration)

        grid_scanning = containers.Grid()
        grid_scanning.add_widgets([
            (label_resolution,1,1),(spin_resolution,1,1),containers.Grid.NEW_ROW,
            (label_brightness,1,1),(spin_brightness,1,1),containers.Grid.NEW_ROW,
            (label_scan_driver,1,1),(combobox_scan_driver,1,1),containers.Grid.NEW_ROW,
            (sparator_3,2,1),containers.Grid.NEW_ROW,
            (label_number_of_pages_to_scan,1,1),(spin_number_of_pages_to_scan,1,1),containers.Grid.NEW_ROW,
            (label_time_bitween_repeted_scanning,1,1),(spin_time_bitween_repeted_scanning,1,1),containers.Grid.NEW_ROW,
            (sparator_4,2,1),containers.Grid.NEW_ROW,
            (checkbutton_scan_mode_switching,2,1),containers.Grid.NEW_ROW,
            (checkbutton_scanner_cache_calibration,2,1)])

        notebook.add_page(_("Scanning"), grid_scanning)

        # Show all widgets initially
        grid_general.show_all()
        grid_recognition.show_all()  
        grid_scanning.show_all()

        # Apply initial visibility state
        toggle_advanced_preferences()

        notebook.set_current_page(page)

        dlg = dialog.Dialog(_("Lios Preferences"),(_("Apply"),dialog.Dialog.BUTTON_ID_1,_("Close"),dialog.Dialog.BUTTON_ID_2))
        dlg.add_widget(outer_box)
        outer_box.show_all()

        if (dlg.run()==True):
            self.advanced_preferences_enabled = int(checkbutton_advanced_pref.get_active())
            self.font=fontbutton_font.get_font_name()
            self.highlight_font=fontbutton_highlight_font.get_font_name()
            self.highlight_color=colorbutton_highlight.get_color_as_string()
            self.background_highlight_color=colorbutton_highlight_background.get_color_as_string()
            self.theme = combobox_theme.get_active()
            self.ocr_engine=combobox_engine.get_active()
            self.language=combobox_language.get_active()
            self.language_2=combobox_language_2.get_active()
            self.language_3=combobox_language_3.get_active()
            self.speech_module=combobox_speech_module.get_active()
            self.speech_language=combobox_speech_language.get_active()
            self.speech_person=combobox_speech_person.get_active()
            self.speech_rate=spin_speech_rate.get_value()
            self.speech_pitch=spin_speech_pitch.get_value()
            self.speech_volume=spin_speech_volume.get_value()
            self.insert_position=combobox_insert_position.get_active()
            self.mode_of_rotation=combobox_mode_of_rotation.get_active()
            self.rotation_angle = combobox_angle.get_active()
            self.give_page_number=int(checkbutton_give_page_number.get_active())
            self.page_numbering_type=combobox_numbering_type.get_active()
            self.starting_page_number=spin_starting_page_number.get_value_as_int()
            self.scan_resolution = spin_resolution.get_value_as_int()
            self.scan_brightness=spin_brightness.get_value_as_int()
            self.scan_area=combobox_scan_area.get_active()
            self.scan_driver=combobox_scan_driver.get_active()
            self.number_of_pages_to_scan=spin_number_of_pages_to_scan.get_value_as_int()
            self.time_between_repeated_scanning=spin_time_bitween_repeted_scanning.get_value_as_int()
            self.scanner_mode_switching=int(checkbutton_scan_mode_switching.get_active())
            self.run_text_cleaner=int(checkbutton_run_text_cleaner.get_active())
            self.scanner_cache_calibration=int(checkbutton_scanner_cache_calibration.get_active())

            dlg.destroy()
            return True
        dlg.destroy()
        return False
if "__main__" == __name__:
    a = lios_preferences()
    a.set_avalable_ocr_engines([])
    a.set_avalable_scanner_drivers([])
    a.open_configure_dialog()
    a.open_configure_dialog()
    
    loop.start_main_loop()




