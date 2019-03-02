try:
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    import Tkinter as tk
    import ttk
import os
import sys
import platform
import stat
import time

class file_walker:
    def __init__(self, master):
        self.master = master

        self.search_loc = tk.StringVar()
        self.search_loc.set(os.path.expanduser('~'))
        ttk.Combobox(self.master, values=(os.path.expanduser('~'),), textvariable=self.search_loc, justify='center').grid(row=0, column=0)

        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(self.master, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=1, sticky='nsew')

        self.search_vew = ScrolledTreeView(self.master)
        self.search_vew.grid(row=1, column=0, columnspan=3, sticky='nsew')

        self.search_vew.heading("#0", text="File")
        self.search_vew["columns"] = ("fullpath", "type", "size", "Last Access")
        self.search_vew["displaycolumns"] = ("size", "Last Access")
        for col in self.search_vew["columns"]:
            #self.search_vew.column(col, width=80)
            self.search_vew.heading(col, text=col[0].upper()+col[1:])

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        self.search_but = ttk.Button(self.master, text="Search", command=self.search)
        self.search_but.grid(row=0, column=2)

        self.master.bind('<<TreeviewOpen>>', self.update_tree)

        self.dirs = []

    def search(self, *args):
        if not os.path.isdir(self.search_loc.get()): return

        self.search_but.configure(state='disabled')
        self.dirs = []
        if not platform.system() == 'Linux':
            for root, directories, filenames in os.walk(self.search_loc.get()):
                if any([self.search_var.get() in filename for filename in filenames]):
                    self.dirs.append(root)
                for filename in filenames:
                    if self.search_var.get() in filename:
                        print(filename)
        else:
            os.system('find {location} -name "*{search_term}*" > ./files.txt'.format(location=self.search_loc.get(), search_term=self.search_var.get()))
            with open('files.txt', 'r') as f:
                self.dirs = [(os.path.dirname(line)) for line in f]

        print(self.dirs)
        self.search_vew.delete(*self.search_vew.get_children())
        dir = os.path.abspath(self.search_loc.get()).replace('\\', '/')
        node = self.search_vew.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(self.search_vew, node)
        self.search_but.configure(state='normal')

    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return
        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))
        parent = tree.parent(node)
        for p in os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p):
                ptype = "directory"
                if not any(p in substring for substring in self.dirs):
                    continue
            elif os.path.isfile(p): ptype = "file"
            fname = os.path.split(p)[1]
            if ptype != "file":
                id = tree.insert(node, "end", text=fname, values=[p, ptype])
            else:
                if self.search_var.get() in fname:
                    id = tree.insert(node, "end", text=fname, values=[p, ptype])
                else:
                    continue
            if ptype == 'directory':
                tree.insert(id, 0, text="dummy")
                tree.item(id, text=fname)
            elif ptype == 'file':
                _stat = os.stat(p)
                size = _stat.st_size
                tree.set(id, "size", "%d bytes" % size)
                modified = time.ctime(_stat[stat.ST_MTIME])
                tree.set(id, "Last Access", modified)

    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())




###################### Made By Guilherme Polo - all rights reserved (via http://page.sourceforge.net/) ######################
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from Scrolledtext.py)
        if sys.version_info >= (3, 0):
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                  + tk.Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped



class ScrolledTreeView(AutoScroll, ttk.Treeview):
    '''A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')


def main():
    root = tk.Tk()
    file_walker_gui = file_walker(root)
    root.mainloop()

if __name__ == '__main__':
    main()
