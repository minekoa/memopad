
from Tkinter import *

class ScrolledListbox(Listbox):
    """ Listbox with vertical scroll bar """
    
    def __init__(self, master, **key):
        self.frame = Frame(master)
        self.yscroll = Scrollbar (self.frame, orient=VERTICAL)
        self.yscroll.pack(side=RIGHT, fill=Y, expand=1)
        key['yscrollcommand']=self.yscroll.set
        Listbox.__init__(self, self.frame, **key)
        self.pack(side=LEFT, fill=BOTH, expand=1)
        self.yscroll.config(command=self.yview)

        # Copy geometry methods of self.frame 
        for m in (Pack.__dict__.keys() + Grid.__dict__.keys() + Place.__dict__.keys()):
            m[0] == '_' or m == 'config' or m == 'configure' or \
                setattr(self, m, getattr(self.frame, m))
