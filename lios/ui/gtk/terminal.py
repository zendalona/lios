from gi.repository import Gtk, GObject, Vte
from gi.repository import GLib


class Terminal(Vte.Terminal):
	def __init__(self,path):
		super(Terminal,self).__init__()
		self.spawn_sync(Vte.PtyFlags.DEFAULT, #default is fine
                path, #where to start the command?
                ["/bin/sh"], #where is the emulator?
                [], #it's ok to leave this list empty
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None, #at least None is required
                None);
	def run_command(self,command):
		command = command+"\n"
		length = len(command)
		self.feed_child(command, length)

	def connect_child_exit(self,function):
		self.connect ("child-exited", function)  
         
		

class TheWindow(Gtk.Window):

    def __init__(self):
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
	    command = "echo \"Sending this command to a virtual terminal.\""
	    self.terminal.run_command(command);


if (__name__ == "__main__"):
	win = TheWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
