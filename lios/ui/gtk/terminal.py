#!/usr/bin/python3 

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

from gi.repository import Gtk, GObject, Vte
from gi.repository import GLib
from gi.repository import Gdk

class Terminal(Vte.Terminal):
	def __init__(self,path):
     """
     Initialize the service.

     Args:
         self: (todo): write your description
         path: (str): write your description
     """
		super(Terminal,self).__init__()
		if hasattr(self, 'spawn_sync'):
			self.spawn_sync(Vte.PtyFlags.DEFAULT, #default is fine
			path, #where to start the command?
			["/bin/sh"], #where is the emulator?
			[], #it's ok to leave this list empty
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None, #at least None is required
			None);
		else:
			self.fork_command_full(Vte.PtyFlags.DEFAULT, #default is fine
			path, #where to start the command?
			["/bin/sh"], #where is the emulator?
			[], #it's ok to leave this list empty
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None, #at least None is required
			None);

	def run_command(self,command):
     """
     Run a command.

     Args:
         self: (todo): write your description
         command: (str): write your description
     """
		command = command+"\n"
		length = len(command)
		self.feed_child(command, length)

	def connect_child_exit(self,function):
     """
     Connects a child process.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		self.connect ("child-exited", function)  

	def connect_context_menu_button_callback(self,function):
     """
     Call the callback function when the mouse button is clicked.

     Args:
         self: (todo): write your description
         function: (todo): write your description
     """
		def fun(widget,event):
      """
      Reimplemented events.

      Args:
          widget: (todo): write your description
          event: (todo): write your description
      """
			if ((event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3) or
				(event.type == Gdk.EventType.KEY_PRESS and event.hardware_keycode == 135)):
				function()
		self.connect("button-release-event",fun)
		self.connect("key-press-event",fun)

class TheWindow(Gtk.Window):

    def __init__(self):
        """
        Initialize gtk box.

        Args:
            self: (todo): write your description
        """
        Gtk.Window.__init__(self, title="inherited cell renderer")
        self.set_default_size(600, 300)
        self.terminal     = Terminal("~/home")
        
        
        #Set up a button to click and run a demo command
        self.button = Gtk.Button("Do The Command")
        self.button.connect("clicked", self.InputToTerm)
        #end demo command code

        #set up the interface
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(self.button, False, True, 0)
        #a scroll window is required for the terminal
        scroller = Gtk.ScrolledWindow()
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        scroller.add(self.terminal)
        box.pack_start(scroller, False, True, 2)
        self.add(box)

    def InputToTerm(self, clicker):
        """
        Set the command to the command.

        Args:
            self: (todo): write your description
            clicker: (todo): write your description
        """
	    command = "echo \"Sending this command to a virtual terminal.\""
	    self.terminal.run_command(command);


if (__name__ == "__main__"):
	win = TheWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
