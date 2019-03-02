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
try:
    import ttkthemes
except:
    pass

class file_walker:
    def __init__(self, master):
        self.master = master

        self.menubar = tk.Menu(self.master)
        self.master.configure(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.show_prog = tk.BooleanVar()
        self.filemenu.add_checkbutton(label="Show Progress", variable=self.show_prog)
        self.menubar.add_cascade(label="File", menu=self.filemenu)


        self.search_loc = tk.StringVar()
        self.search_loc.set(os.path.expanduser('~'))
        ttk.Combobox(self.master, values=(os.path.expanduser('~'),), textvariable=self.search_loc, justify='center').grid(row=0, column=0, sticky='ns')

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
        if self.show_prog.get(): return self.search_win(self, *args)
        self.search_but.configure(state='disabled')
        self.dirs = []
        if not platform.system() in ['Linux', 'Windows']:
            for root, directories, filenames in os.walk(self.search_loc.get()):
                if any([self.search_var.get() in filename for filename in filenames]):
                    self.dirs.append(root)
                for filename in filenames:
                    if self.search_var.get() in filename:
                        print(filename)
        else:
            if platform.system() == 'Linux':
                os.system('find {location} -name "*{search_term}*" > ./files.txt'.format(location=self.search_loc.get(), search_term=self.search_var.get()))
            elif platform.system() == 'Windows':
                print(os.path.join(self.search_loc.get(), '*{file}*'.format(file=self.search_var.get())))
                os.system(r'dir /s/b {search} > files.txt'.format(search=os.path.join(self.search_loc.get(), '*{file}*'.format(file=self.search_var.get()))))
            with open('files.txt', 'r') as f:
                self.dirs = [(os.path.dirname(line)) for line in f]

        print(self.dirs)
        self.search_vew.delete(*self.search_vew.get_children())
        dir = os.path.abspath(self.search_loc.get())
        node = self.search_vew.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(self.search_vew, node)
        self.search_but.configure(state='normal')

    def search_win(self, *args):
        prog_win = tk.Toplevel(master=self.master)
        prog_win.title("Progress")
        prog_win.resizable(False, False)
        if platform.system() == 'Linux':
            prog_win.wm_attributes('-type', 'splash')
        else:
            prog_win.overrideredirect(1)
        prog_win.attributes("-topmost", True)
        prog_win.geometry('150x22+{:.0f}+{:.0f}'.format(self.master.winfo_x()+(self.master.winfo_width())-150, self.master.winfo_y()+(self.master.winfo_height())-22)) #self.master.winfo_height(), self.master.winfo_width()

        curr_prog = ttk.Label(prog_win, text='Files Found: ')
        curr_prog.grid(row=0, column=0, sticky='nsew')

        prog_win.grid_rowconfigure(0, weight=1)
        prog_win.grid_columnconfigure(0, weight=1)

        self.search_but.configure(state='disabled')
        file_count = 0
        self.dirs = []
        if not platform.system() in ['Linux', 'Windows']:
            for root, directories, filenames in os.walk(self.search_loc.get()):
                if any([self.search_var.get() in filename for filename in filenames]):
                    self.dirs.append(root)
                for filename in filenames:
                    if self.search_var.get() in filename:
                        file_count += 1
                        curr_prog["text"] = 'Files Found: {0}'.format(file_count)
                        curr_prog.update()
        else:
            if platform.system() == 'Linux':
                os.system('find {location} -name "*{search_term}*" > ./files.txt'.format(location=self.search_loc.get(), search_term=self.search_var.get()))
            elif platform.system() == 'Windows':
                print(os.path.join(self.search_loc.get(), '*{file}*'.format(file=self.search_var.get())))
                os.system(r'dir /s/b {search} > files.txt'.format(search=os.path.join(self.search_loc.get(), '*{file}*'.format(file=self.search_var.get()))))
            with open('files.txt', 'r') as f:
                for line in f:
                    file_count += 1
                    self.dirs.append(os.path.dirname(line))
                    curr_prog["text"] = 'Files Found: {0}'.format(file_count)
                    curr_prog.update()

        print(self.dirs)
        self.search_vew.delete(*self.search_vew.get_children())
        dir = os.path.abspath(self.search_loc.get())
        node = self.search_vew.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(self.search_vew, node)
        self.search_vew.update()
        self.search_but.configure(state='normal')

        self.master.after(1000, prog_win.destroy)

    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return
        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))
        parent = tree.parent(node)
        for p in os.listdir(path):
            ptype = None
            p = os.path.join(path, p)
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
    if 'ttkthemes' in sys.modules:
        root = ttkthemes.ThemedTk()
        file_walker_gui = file_walker(root)

        if platform.system() == 'Linux':
            if platform.dist()[0] == 'Ubuntu':
                root.set_theme("ubuntu")
            else:
                root.set_theme("equilux")
        elif platform.system() == 'Windows':
            root.set_theme("vista")
        elif platform.system() == 'Darwin':
            root.set_theme("aqua")
        root.mainloop()
    else:
        root = tk.Tk()
        file_walker_gui = file_walker(root)
        root.mainloop()

if __name__ == '__main__':
    main()
