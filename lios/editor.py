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

from lios.ui.gtk import text_view, tree_view, widget, dialog, file_chooser, containers, window

from lios.text_to_audio import text_to_audio_converter
from lios import macros
from lios import dictionary
from lios import localization
from lios.ui.gtk import print_dialog
from gi.repository import Gtk
from gi.repository import Gdk
import queue
import os

from encodings.aliases import aliases


_ = localization._

def read_text_from_file(filename,enc='utf8'):
    try:
        text = open(filename,encoding=enc).read()
        return text
    except	UnicodeDecodeError:
        list = sorted(aliases.keys())
        combobox = widget.ComboBox()
        for item in macros.major_character_encodings_list:
            if(item in list):
                combobox.add_item(item)
        for item in list:
            combobox.add_item(item)
        combobox.set_active(0)

        dlg = dialog.Dialog(_("{} Decode error Select Other Character Encoding".format(enc)),(_("Select"), dialog.Dialog.BUTTON_ID_1))
        dlg.add_widget_with_label(combobox,_("Character Encoding: "))
        combobox.grab_focus()
        dlg.show_all()
        response = dlg.run()

        if response == dialog.Dialog.BUTTON_ID_1:
            index = combobox.get_active()
            dlg.destroy()
            text = read_text_from_file(filename,enc=list[index])
            return text
        else:
            dlg.destroy()
            return ""




class BasicTextView(text_view.TextView):
    def __init__(self):
        super(BasicTextView,self).__init__()
        self.q = queue.LifoQueue()
        self.q2 = queue.LifoQueue()
        self.connect_insert(self.push)
        self.connect_delete(self.push)
        self.bookmark_list = []
        self.text_cleaner_list = []
        
        #This variable is to avoid the reverse event 
        #while pressing undo or redo that again trigger
        # insert or delete signals - Nalin.x.GNU
        self.push_change_to_undobuffer = True;
    def set_theme(self, theme_index, theme_list):
        if theme_index == 0:
            self.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#000000"))
            self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#FFFFFF"))

        else:
            fg = Gdk.color_parse(theme_list[theme_index][1])
            bg = Gdk.color_parse(theme_list[theme_index][2])
            self.modify_fg(Gtk.StateFlags.NORMAL, fg)
            self.modify_bg(Gtk.StateFlags.NORMAL, bg)

    
    def set_dictionary(self,dict):
        self.dict = dict
    
    def undo(self,arg=None):
        if( not self.q.empty()):
            text = self.q.get()
            self.push_change_to_undobuffer = False
            self.set_text(text)
            self.q2.put(text)
        
    def redo(self,arg=None):
        if( not self.q2.empty()):
            text = self.q2.get()
            self.push_change_to_undobuffer = False
            self.set_text(text)
            self.q.put(text)
    
    def push(self):
        text = self.get_text()
        if(text and self.push_change_to_undobuffer):
            self.q.put(text)
        else:
            self.push_change_to_undobuffer = True


    def new(self,*data):
        if (self.get_modified() == True):
            dlg =  dialog.Dialog(_("Start new without saving?"),
            (_("Cancel"), dialog.Dialog.BUTTON_ID_1,_("Start-New!"), dialog.Dialog.BUTTON_ID_2))
            label = widget.Label(_("Start new without saving?"))
            dlg.add_widget(label)
            label.show()
            response = dlg.run()
            dlg.destroy()				
            if response == dialog.Dialog.BUTTON_ID_1:
                self.grab_focus();
                return 0;
            else:
                self.delete_all_text()
                del self.save_file_name
                self.bookmark_list = []
                self.grab_focus();
                return 1;
        else:
            self.delete_all_text()
            del self.save_file_name
            self.bookmark_list = []
            return 1;

    def open(self):
        open_file = file_chooser.FileChooserDialog(_("Select the file to open"),
            file_chooser.FileChooserDialog.OPEN,
            macros.supported_text_formats,macros.user_home_path)
        response = open_file.run()
        if response == file_chooser.FileChooserDialog.ACCEPT:
            to_open = read_text_from_file(open_file.get_filename())
            try:
                self.set_text(to_open)
            except FileNotFoundError:
                    pass
            else:
                self.save_file_name = open_file.get_filename()
                self.import_bookmarks_using_filename()
                #self.textbuffer.place_cursor(self.textbuffer.get_end_iter())
        open_file.destroy()

    def save(self,*data):
        text = self.get_text()
        try:
            self.save_file_name
        except AttributeError:
            save_file = file_chooser.FileChooserDialog(_("Save"),
                file_chooser.FileChooserDialog.SAVE,
                macros.supported_text_formats,None)
            save_file.set_current_name(text[0:10]+".text");
            save_file.set_do_overwrite_confirmation(True);			
            response = save_file.run()
            if response == file_chooser.FileChooserDialog.ACCEPT:
                self.save_file_name = save_file.get_filename()
                if(self.save_file_name.split(".")[-1] not in macros.supported_text_formats):
                    self.save_file_name = self.save_file_name + ".text"
                open(self.save_file_name,'w').write(text)
                self.save_bookmark_table()
                self.set_modified(False)	
                save_file.destroy()
                return True
            else:
                save_file.destroy()
                return False
        else:
            open(self.save_file_name,'w').write(text)
            self.save_bookmark_table()
            self.set_modified(False)
            return True		


    def save_as(self,*data):
        try:
            del self.save_file_name
        except:
            pass
        self.save();
        
    def append(self,*data):
        append_file_dialog = file_chooser.FileChooserDialog(_("Select the file to append"),
            file_chooser.FileChooserDialog.OPEN,macros.supported_text_formats)
        append_file_dialog.set_current_folder("~/")
        append_file_dialog.run()
        text_to_append = read_text_from_file(append_file_dialog.get_filename())
        self.insert_text(text_to_append,2,True)
        append_file_dialog.destroy()
    
    def punch(self,*data):
        insert_at_cursor_dialog = file_chooser.FileChooserDialog(_("Select the file to insert at cursor"),
            file_chooser.FileChooserDialog.OPEN,macros.supported_text_formats)
        insert_at_cursor_dialog.set_current_folder("~/")
        insert_at_cursor_dialog.run()
        text_to_insert_at_cursor = read_text_from_file(insert_at_cursor_dialog.get_filename())
        self.insert_text(text_to_insert_at_cursor,1,True)
        insert_at_cursor_dialog.destroy()


    def set_text_cleaner_list_from_file(self,filename):
        self.text_cleaner_list = []
        try:
            with open(filename) as file:
                for line in file:
                    self.text_cleaner_list.append((line.split("==")[0],line.split("==")[1][:-1]))
        except:
            return False
        return True

    def save_text_cleaner_list_to_file(self,filename):
        try:
            file = open(filename,"w")
            for item in self.text_cleaner_list:
                file.write(item[0]+"=="+item[1]+"\n")
        except:
            pass

    def export_text_cleaner_list(self,*data):
        open_file = file_chooser.FileChooserDialog(_("Filename please"),
        file_chooser.FileChooserDialog.SAVE,
        macros.supported_text_formats,macros.user_home_path)
        open_file.set_current_name(".txt")
        response = open_file.run()
        if response == file_chooser.FileChooserDialog.ACCEPT:
            self.save_text_cleaner_list_to_file(open_file.get_filename())
        open_file.destroy()

    def import_text_cleaner_list(self,*data):
        open_file = file_chooser.FileChooserDialog(_("Select the file to import"),
        file_chooser.FileChooserDialog.OPEN,
        "*",macros.user_home_path)
        response = open_file.run()
        if response == file_chooser.FileChooserDialog.ACCEPT:
            self.set_text_cleaner_list_from_file(open_file.get_filename())
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);
        open_file.destroy()

    def open_text_cleaner(self,*data):
        window_text_cleaner = window.Window(_("Text Cleaner"))
        scroll_box = containers.ScrollBox()
        treeview = tree_view.TreeView([(_("Match"),str,True),(_("Replace"),str,True)],None)
        scroll_box.add(treeview)
        treeview.set_list(self.text_cleaner_list)

        def add_clicked(*data):
            entry_match = widget.Entry()
            entry_replace = widget.Entry()
            dlg = dialog.Dialog(_("Give match and replace"),(_("Ok"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
            dlg.add_widget_with_label(entry_match,_("Match : "))
            dlg.add_widget_with_label(entry_replace,_("Replace : "))
            entry_match.grab_focus()
            dlg.show_all()
            response = dlg.run()
            if (response == dialog.Dialog.BUTTON_ID_1):
                treeview.append((entry_match.get_text(),entry_replace.get_text()))
                self.text_cleaner_list = treeview.get_list()
                self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);
            dlg.destroy()

        def remove_clicked(*data):
            index = treeview.get_selected_row_index()
            treeview.remove(index)
            self.text_cleaner_list = treeview.get_list()
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);

        def export_list(*data):
            self.export_text_cleaner_list()

        def import_list(*data):
            self.import_text_cleaner_list()
            treeview.set_list(self.text_cleaner_list)
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);

        def restore(*data):
            self.set_text_cleaner_list_from_file(macros.default_text_cleaner_list_file_path)
            treeview.set_list(self.text_cleaner_list)
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);

        def clear(*data):
            self.text_cleaner_list = []
            treeview.set_list(self.text_cleaner_list)
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);

        def list_updated(*data):
            self.text_cleaner_list = treeview.get_list()
            self.save_text_cleaner_list_to_file(macros.local_text_cleaner_list_file_path);

        def close(*data):
            window_text_cleaner.close()

        treeview.connect_update_callback(list_updated)

        button_add = widget.Button(_("Add"))
        button_add.connect_function(add_clicked);
        button_remove = widget.Button(_("Remove"))
        button_remove.connect_function(remove_clicked)

        button_import = widget.Button(_("Import"))
        button_import.connect_function(import_list);
        button_export = widget.Button(_("Export"))
        button_export.connect_function(export_list)

        button_clear = widget.Button(_("Clear"))
        button_clear.connect_function(clear);
        button_restore = widget.Button(_("Restore"))
        button_restore.connect_function(restore)

        button_apply_from_cursor = widget.Button(_("Apply From Cursor"))
        button_apply_from_cursor.connect_function(self.apply_text_cleaner_from_cursor)

        button_apply = widget.Button(_("Apply on entire text"))
        button_apply.connect_function(self.apply_text_cleaner_entire_text)

        button_close = widget.Button(_("Close"))
        button_close.connect_function(close)

        grid = containers.Grid()
        grid.add_widgets([(scroll_box,3,1),containers.Grid.NEW_ROW,
            (button_add,1,1,False,False),(button_remove,1,1,False,False),(button_clear,1,1,False,False),containers.Grid.NEW_ROW,
            (button_restore,1,1,False,False),(button_apply_from_cursor,1,1,False,False),(button_apply,1,1,False,False),containers.Grid.NEW_ROW,
            (button_import,1,1,False,False),(button_export,1,1,False,False),(button_close,1,1,False,False)])

        window_text_cleaner.add(grid);
        window_text_cleaner.set_default_size(400,500)
        window_text_cleaner.show_all();

    def apply_text_cleaner_from_cursor(self,*data):
        text = self.get_text_from_cursor_to_end()
        text = self.get_text_cleaner_out(text)
        self.delete_text_from_cursor_to_end()
        self.insert_text(text,text_view.TextView.AT_END)

    def apply_text_cleaner_entire_text(self,*data):
        text = self.get_text()
        text = self.get_text_cleaner_out(text)
        self.set_text(text)

    def get_text_cleaner_out(self,text):
        for item in self.text_cleaner_list:
            text = text.replace(item[0],item[1]);
        return text
    
    def open_bookmark_table(self,*data):
        window_bookmark = window.Window(_("Bookmark Table"))
        list_view = widget.ListView(_("Select the bookmark"))
        for item in self.bookmark_list:
            name = item[0]
            list_view.add_item(name)
        
        def jump(*data):
            index = list_view.get_selected_item_index()
            self.move_cursor_to_mark(self.bookmark_list[index][1])
            self.highlights_cursor_line()
            window_bookmark.destroy()

        def scroll_to_position(*data):
            index = list_view.get_selected_item_index()
            self.move_cursor_to_mark(self.bookmark_list[index][1])
            self.highlights_cursor_line()
            
        
        def delete(*data):
            index = list_view.get_selected_item_index()
            self.bookmark_list.pop(index)
            list_view.remove_selected_item()
            self.save_bookmark_table("None")

        def close(*data):
            window_bookmark.destroy()
        
        

        scroll_box_bookmark = containers.ScrollBox()
        scroll_box_bookmark.add(list_view)
        
        button_jump = widget.Button(_("Jump"))
        button_jump.connect_function(jump)
        
        button_scroll_to_position = widget.Button(_("Scroll Text to position"))
        button_scroll_to_position.connect_function(scroll_to_position)
            
        button_delete = widget.Button(_("Delete"))
        button_delete.connect_function(delete)
                
        button_close = widget.Button(_("Close"))
        button_close.connect_function(close)	
            
        list_view.connect_on_select_callback(jump)
        

        grid_bookmark = containers.Grid()
        grid_bookmark.add_widgets([(scroll_box_bookmark,4,1),containers.Grid.NEW_ROW,
            (button_jump,1,1,False,False),(button_scroll_to_position,1,1,False,False),
            (button_delete,1,1,False,False),(button_close,1,1,False,False)])

        
        window_bookmark.add(grid_bookmark)
        window_bookmark.set_default_size(500,200)
        window_bookmark.show_all()

    def import_bookmarks_using_filename(self):
        try:
            self.bookmark_list = []
            name = self.save_file_name
            name = name.replace("/","|")
            name = name.replace(" ","#")
            with open(macros.bookmarks_dir+name) as file:
                for line in file:
                    mark = self.get_mark_at_line(int(line.split()[0]))
                    name = line.split()[1:]
                    self.bookmark_list.append((" ".join(name),mark))
        except:
            pass		

    def open_all_bookmark_table(self,*data):
        all_bookmark_list = []
        window_bookmark = window.Window(_("Bookmark Table"))		
        list_view = widget.ListView(_("Select the bookmark"))
        for bookmark_file in os.listdir(macros.bookmarks_dir):
            with open(macros.bookmarks_dir+bookmark_file) as file:
                for line in file:
                    all_bookmark_list.append(bookmark_file+"~"+line)
                    list_view.add_item(bookmark_file.split("|")[-1]+" : "+line)
        
        def jump(*data):
            index = list_view.get_selected_item_index()
            item = all_bookmark_list[index]
            filename = item.split("~")[0].replace("|","/").replace("#"," ")
            line_number = item.split("~")[1].split()[0]
            text = open(filename).read()
            self.set_text(text)

            self.save_file_name = filename
            self.import_bookmarks_using_filename()
            
            mark = self.get_mark_at_line(int(line_number))
            self.move_cursor_to_mark(mark)
            
            self.highlights_cursor_line()
            window_bookmark.destroy()			
        
        def close(*data):
            window_bookmark.destroy()
        
        

        scroll_box_bookmark = containers.ScrollBox()
        scroll_box_bookmark.add(list_view)
        
        button_jump = widget.Button(_("Jump"))
        button_jump.connect_function(jump)	
        button_close = widget.Button(_("Close"))
        button_close.connect_function(close)		
        list_view.connect_on_select_callback(jump)
        

        grid_bookmark = containers.Grid()
        grid_bookmark.add_widgets([(scroll_box_bookmark,2,1),containers.Grid.NEW_ROW,
            (button_jump,1,1,False,False),(button_close,1,1,False,False)])

        window_bookmark.add(grid_bookmark)
        window_bookmark.set_default_size(500,200)
        window_bookmark.show_all()
        

    def save_bookmark_table(self,*data):
        #name = re.sub('[^.-/#0-9a-zA-Z]+', '#', self.save_file_name)
        name = self.save_file_name
        name = name.replace("/","|")
        name = name.replace(" ","#")
        
        file = open(macros.bookmarks_dir+name,"w+")
        for item in self.bookmark_list:
            line_number = self.get_line_number_of_mark(item[1])
            file.write("{0} {1} \n".format(line_number,item[0]))
        file.close()

    def import_bookmarks_from_file(self,*data):
        open_file = file_chooser.FileChooserDialog(_("Select the bookmark file to import"),
            file_chooser.FileChooserDialog.OPEN,
            macros.supported_text_formats,macros.user_home_path)
        response = open_file.run()
        if response == file_chooser.FileChooserDialog.ACCEPT:
            with open(open_file.get_filename()) as file:
                for line in file:
                    mark = self.get_mark_at_line(int(line.split()[0]))
                    name = line.split()[1:]
                    self.bookmark_list.append((" ".join(name),mark))
        open_file.destroy()
        
        
    def create_bookmark(self,*data):
        try:
            self.save_file_name
        except:
            dlg = dialog.Dialog(_("Warning!"),(_("Close!"), dialog.Dialog.BUTTON_ID_2))
            label = widget.Label(_("File must be saved inorder to bookmark the text!"))
            dlg.add_widget(label)
            dlg.show_all()
            response = dlg.run()
            dlg.destroy()
            return
            
        entry_sentence = widget.Entry()
        text = self.get_current_line_text()
        entry_sentence.set_text(text)		
        dlg = dialog.Dialog(_("Create new Bookmark"),(_("Bookmark"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
        dlg.add_widget_with_label(entry_sentence,_("Name : "))
        entry_sentence.grab_focus()
        dlg.show_all()
        response = dlg.run()
        
        if response == dialog.Dialog.BUTTON_ID_1:
            # Note that this ### string will be deleted automatically 
            # Because it's considered as line number
            sentence = entry_sentence.get_text()
            # Note that this mark can't be used directly
            # Because it will always hold cursor position
            mark = self.get_cursor_mark()
            line_number = self.get_line_number_of_mark(mark)
            real_mark = self.get_mark_at_line(line_number)
            self.bookmark_list.append((sentence,real_mark))
            self.save_bookmark_table("None")
            dlg.destroy()
        else:
            dlg.destroy()		



    
    def open_find_dialog(self,*data):
        entry = widget.Entry()
        statusbar_context = widget.Statusbar()
        statusbar_context.set_text(_("Context label"))

        def find_next(*data):
            word = entry.get_text()
            if(not self.is_cursor_at_end()):
                if(self.move_forward_to_word(word)):
                    statusbar_context.set_text(self.get_context_text())

        def find_previous(*data):
            word = entry.get_text()
            if(not self.is_cursor_at_start()):
                if(self.move_backward_to_word(word)):
                    statusbar_context.set_text(self.get_context_text())
            
        label = widget.Label(_("<b>Find word: </b>"))
        label.set_use_markup(True)
        label.set_mnemonic_widget(entry)
        
        entry.connect_activate_function(find_next)
        
        next_button = widget.Button(_("Next"))
        next_button.connect_function(find_next)	
        previous_button = widget.Button(_("Previous"))
        previous_button.connect_function(find_previous)
        
        
        grid = containers.Grid()
        grid.add_widgets([(label,1,1),(entry,1,1),containers.Grid.NEW_ROW,
            (statusbar_context,2,1),containers.Grid.NEW_ROW,(next_button,1,1,False,False),
            (previous_button,1,1,False,False)])
        window_find = window.Window(_("Find Dialog"))
        window_find.add(grid)
        window_find.show_all()

    def open_find_and_replace_dialog(self,*data):
        entry_word = widget.Entry()
        entry_replace_word = widget.Entry()
        statusbar_context = widget.Statusbar()
        statusbar_context.set_text(_("Context label"))

        def find_next(*data):
            word = entry_word.get_text()
            if(not self.is_cursor_at_end()):
                if(self.move_forward_to_word(word)):
                    statusbar_context.set_text(self.get_context_text())

        def find_previous(*data):
            word = entry_word.get_text()
            if(not self.is_cursor_at_start()):
                if(self.move_backward_to_word(word)):
                    statusbar_context.set_text(self.get_context_text())
                else:
                    dialog.Dialog(_("No match found")).run()

        def replace(*data):
            word_replace = entry_replace_word.get_text()
            self.replace_last_word(word_replace)

        def replace_all(*data):
            word = entry_word.get_text()
            word_replace = entry_replace_word.get_text()
            while(not self.is_cursor_at_end()):
                if(self.move_forward_to_word(word)):
                    self.replace_last_word(word_replace)
                else:
                    break
            
        label_word = widget.Label(_("<b>Word: </b>"))
        label_word.set_use_markup(True)
        label_word.set_mnemonic_widget(entry_word)
        label_replace_word = widget.Label(_("<b>Replace word: </b>"))
        label_replace_word.set_use_markup(True)
        label_replace_word.set_mnemonic_widget(entry_replace_word)
        
        entry_word.connect_activate_function(find_next)
        entry_replace_word.connect_activate_function(find_next)
        
        
        button_next = widget.Button(_("Next"))
        button_next.connect_function(find_next)	
        button_previous = widget.Button(_("Previous"))
        button_previous.connect_function(find_previous)
        button_replace = widget.Button(_("Replace"))
        button_replace.connect_function(replace)	
        button_replace_all = widget.Button(_("Replace All"))
        button_replace_all.connect_function(replace_all)
        
        
        grid = containers.Grid()
        grid.add_widgets([(label_word,2,1),(entry_word,4,1),containers.Grid.NEW_ROW,
            (label_replace_word,2,1),(entry_replace_word,4,1),containers.Grid.NEW_ROW,
            (button_next,3,1,False,False),(button_previous,3,1,False,False),
            containers.Grid.NEW_ROW,(statusbar_context,6,1),containers.Grid.NEW_ROW,
            (button_replace,3,1,False,False),(button_replace_all,3,1,False,False)])
        window_find = window.Window(_("Find Dialog"))
        window_find.add(grid)
        window_find.show_all()
    
    def open_spell_check(self,*data):
        entry = widget.Entry()
        list_view = widget.ListView(_("Suggestions"))
        statusbar_context = widget.Statusbar()
        statusbar_context.set_text(_("Context label"))
        statusbar_context.set_line_wrap(True)
        change_all_dict = {}
        self.word = ""


        def find_next_mispeleed_word(*data):
            while (not self.is_cursor_at_end()):
                self.word = self.get_next_word()
                if self.word in change_all_dict.keys():
                    self.replace_last_word(change_all_dict[self.word])
                    continue
                    
                if (not self.dict.check(self.word)):
                    entry.set_text(self.word)
                    statusbar_context.set_text(self.get_context_text())
                    list_view.clear()
                    for item in self.dict.suggest(self.word):
                        list_view.add_item(item)
                    break
            if(self.is_cursor_at_end()):
                entry.set_text("")
                statusbar_context.set_text(_("Spell Check finished"))
            

        def ignore_all(*data):
            word = entry.get_text()
            self.dict.add_to_session(word)
            find_next_mispeleed_word()
        
        def change(*data):
            replace_word = entry.get_text()
            self.replace_last_word(replace_word)
            find_next_mispeleed_word()
        
        def change_all(*data):
            replace_word = entry.get_text()
            change_all_dict[self.word] = replace_word
            self.replace_last_word(replace_word)
            find_next_mispeleed_word()
        
        def delete(*data):
            self.delete_last_word()
            find_next_mispeleed_word()
        
        def on_suggestion_selected(*data):
            item = list_view.get_selected_item()
            entry.set_text(item)
        
        def close(*data):
            window1.destroy()	
        
        grid = containers.Grid()
        
        label = widget.Label(_("<b>Misspelled word: </b>"))
        label.set_use_markup(True)
        label.set_mnemonic_widget(entry)
        
        scroll_box = containers.ScrollBox()
        scroll_box.add(list_view)
        change_button = widget.Button(_("Change"))
        change_button.connect_function(change)
        change_all_button = widget.Button(_("Change All"))
        change_all_button.connect_function(change_all)
        delete_button = widget.Button(_("Delete"))
        delete_button.connect_function(delete)
        ignore_button = widget.Button(_("Ignore"))
        ignore_button.connect_function(find_next_mispeleed_word)
        ignore_all_button = widget.Button(_("Ignore All"))
        ignore_all_button.connect_function(ignore_all)
        add_to_dict_button = widget.Button(_("Add to user dict"))
        close_button = widget.Button(_("Close"))
        close_button.connect_function(close)
        
        list_view.connect_on_select_callback(on_suggestion_selected)
        entry.connect_activate_function(change)
                
        grid.add_widgets([(label,1,1,False,False),
            (entry,6,1,False,False),containers.Grid.NEW_ROW,
            (scroll_box,1,3,False,False),(change_button,1,1,False,False),(change_all_button,1,1,False,False),(delete_button,1,1,False,False),containers.Grid.NEW_ROW,
            (ignore_button,1,1,False,False),(ignore_all_button,1,1,False,False),(add_to_dict_button,1,1,False,False),containers.Grid.NEW_ROW,
            (statusbar_context,1,1),containers.Grid.NEW_ROW,
            (close_button,4,1,False,False)])
        
        find_next_mispeleed_word()
        
        window1 = window.Window(_("Spell-Check"))
        window1.add(grid)
        window1.set_default_size(500,200)
        window1.show_all()

    
    def go_to_line(self,*data):
        current_line = self.get_cursor_line_number()
        maximum_line = self.get_line_count()		
        spinbutton_line = widget.SpinButton(current_line,0,maximum_line,1,5,0)
        
        dlg = dialog.Dialog(_("Go To Line"),(_("Go"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
        #spinbutton_line.connect("activate",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
        dlg.add_widget_with_label(spinbutton_line,_("Line Number: "))
        spinbutton_line.grab_focus()
        dlg.show_all()
        response = dlg.run()
        
        if response == dialog.Dialog.BUTTON_ID_1:
            to = spinbutton_line.get_value()
            self.move_cursor_to_line(to)
            self.highlights_cursor_line()
            dlg.destroy()
        else:
            dlg.destroy()
    
    def audio_converter(self,data=None,voice=None):
        if (self.has_selection()):
            text = self.get_selected_text()
        else:
            text = self.get_text()
        
        dialog_ac = dialog.Dialog(_("Audio Converter"),(_("Convert"), dialog.Dialog.BUTTON_ID_1,_("Close!"), dialog.Dialog.BUTTON_ID_2))
        grid = containers.Grid()

        spinbutton_speed = widget.SpinButton(50,0,100,1,5,0)
        label_speed = widget.Label(_("Speed: "))
        label_speed.set_mnemonic_widget(spinbutton_speed)

        spinbutton_volume = widget.SpinButton(100,0,100,1,5,0)
        label_volume = widget.Label(_("Volume: "))
        label_volume.set_mnemonic_widget(spinbutton_volume)

        spinbutton_pitch = widget.SpinButton(50,0,100,1,5,0)
        label_pitch = widget.Label(_("Pitch: "))
        label_pitch.set_mnemonic_widget(spinbutton_pitch)

        spinbutton_split = widget.SpinButton(5,0,100,1,5,0)
        label_split_time = widget.Label(_("Split Time: "))
        label_split_time.set_mnemonic_widget(spinbutton_split)
        
        combobox = widget.ComboBox()
        for item in text_to_audio_converter.list_voices():
            combobox.append_text(item)
        if voice is not None:
            combobox.set_active(voice)
        label_voice = widget.Label(_("Voice: "))
        label_voice.set_mnemonic_widget(combobox)

        combobox_format = widget.ComboBox()
        combobox_format.append_text(_("MP3 (liblame required)"))
        combobox_format.append_text(_("WAV"))
        combobox_format.set_active(0)
        label_format = widget.Label(_("Format: "))
        label_format.set_mnemonic_widget(combobox_format)
        
        grid.add_widgets([
            (label_speed,1,1),(spinbutton_speed,1,1),containers.Grid.NEW_ROW,
            (label_volume,1,1),(spinbutton_volume,1,1),containers.Grid.NEW_ROW,
            (label_pitch,1,1),(spinbutton_pitch,1,1),containers.Grid.NEW_ROW,
            (label_split_time,1,1),(spinbutton_split,1,1),containers.Grid.NEW_ROW,
            (label_voice,1,1),(combobox,1,1),containers.Grid.NEW_ROW,
            (label_format,1,1),(combobox_format,1,1)])
        dialog_ac.add_widget(grid)
        grid.show_all()
        
        if (dialog_ac.run() == dialog.Dialog.BUTTON_ID_1):
            speed = spinbutton_speed.get_value()
            pitch = spinbutton_pitch.get_value()
            volume = spinbutton_volume.get_value()
            split = spinbutton_split.get_value()
            voice = combobox.get_active_text()
            output_format = combobox_format.get_active()
            save_file = file_chooser.FileChooserDialog(_("Save"),file_chooser.FileChooserDialog.SAVE,["wav","mp3"],macros.user_home_path)
            response = save_file.run()
            if response == file_chooser.FileChooserDialog.ACCEPT:
                converter = text_to_audio_converter(text,volume,voice,split,pitch,speed)
                if (output_format == 0 ):
                    converter.record_to_mp3(save_file.get_filename())
                else:
                    converter.record_to_wave(save_file.get_filename())
            save_file.destroy()
        dialog_ac.destroy()
        
                

    def print_preview(self,*data):
        if (self.has_selection()):
            text = self.get_selected_text()
        else:
            text = self.get_text()
        print_dialog.print_with_action(text,print_dialog.print_with_action.PREVIEW)
            
    def open_print_dialog(self,*data):
        if (self.has_selection()):
            text = self.get_selected_text()
        else:
            text = self.get_text()
        print_dialog.print_with_action(text,print_dialog.print_with_action.PRINT_DIALOG)		
        
    def print_to_pdf(self,*data):
        save_file = file_chooser.FileChooserDialog(_("Enter the file name"),
            file_chooser.FileChooserDialog.SAVE,macros.supported_pdf_formats,macros.user_home_path)
        response = save_file.run()
        if response == file_chooser.FileChooserDialog.ACCEPT:
            if (self.has_selection()):
                text = self.get_selected_text()
            else:
                text = self.get_text()
            print_dialog.print_with_action(text,print_dialog.print_with_action.EXPORT,
                save_file.get_filename())
            save_file.destroy()

