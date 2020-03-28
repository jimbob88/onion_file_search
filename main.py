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
import mmap

try:
    import ttkthemes
except:
    pass

try:
    import scandir_rs
except:
    pass

from custom_treeview import ScrolledTreeView


def os_walk_search(search_loc, search_var):
    dirs = []
    for root, directories, filenames in os.walk(search_loc):
        if any([search_var in filename for filename in filenames]):
            dirs.append(root)
    return dirs


def scandir_rs_search(search_loc, search_var):
    dirs = []
    for root, directories, filenames in scandir_rs.walk.Walk(search_loc):
        if any([search_var in filename for filename in filenames]):
            dirs.append(root)
    return dirs


def windows_cmd_search(search_var, search_loc):
    os.system(
        r"dir /s/b {search} > files.txt".format(
            search=os.path.join(search_loc, "*{file}*".format(file=search_var),)
        )
    )
    with open("files.txt", "r") as f:
        return [(os.path.dirname(line)) for line in f]


def linux_cmd_search(search_var, search_loc):
    os.system(
        'find {location} -name "*{search_term}*" > ./files.txt'.format(
            location=search_loc, search_term=search_var,
        )
    )
    with open("files.txt", "r") as f:
        return [(os.path.dirname(line)) for line in f]


def not_darwin_search(search_loc, search_var):
    if platform.system() == "Linux":
        return linux_cmd_search(search_loc, search_var)
    else:
        if "scandir_rs" in sys.modules:
            return scandir_rs_search(search_loc, search_var)
        else:
            return windows_cmd_search(search_loc, search_var)


def file_counter_win(top_master):
    prog_win = tk.Toplevel(master=top_master)
    prog_win.title("Progress")
    prog_win.resizable(False, False)
    if platform.system() == "Linux":
        prog_win.wm_attributes("-type", "splash")
    else:
        prog_win.overrideredirect(1)
    prog_win.attributes("-topmost", True)
    prog_win.geometry(
        "150x22+{:.0f}+{:.0f}".format(
            top_master.winfo_x() + (top_master.winfo_width()) - 150,
            top_master.winfo_y() + (top_master.winfo_height()) - 22,
        )
    )
    return prog_win


class file_walker:
    def __init__(self, master):
        self.master = master
        self.master.title("Onion Search")

        self.menubar = tk.Menu(self.master)
        self.master.configure(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.show_prog = tk.BooleanVar()
        self.filemenu.add_checkbutton(label="Show Progress", variable=self.show_prog)
        self.inside_search_files = []
        self.search_inside_var = tk.BooleanVar()
        self.filemenu.add_checkbutton(
            label="Search Inside TextFiles", variable=self.search_inside_var
        )
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.search_loc = tk.StringVar()
        self.search_loc.set(os.path.expanduser("~"))
        ttk.Combobox(
            self.master,
            values=(os.path.expanduser("~"),),
            textvariable=self.search_loc,
            justify="center",
        ).grid(row=0, column=0, sticky="ns")

        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(self.master, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=1, sticky="nsew")

        self.search_vew = ScrolledTreeView(self.master)
        self.search_vew.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.search_vew.heading("#0", text="File")
        self.search_vew["columns"] = ("fullpath", "type", "size", "Last Access")
        self.search_vew["displaycolumns"] = ("size", "Last Access")
        for col in self.search_vew["columns"]:
            self.search_vew.heading(col, text=col[0].upper() + col[1:])

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        self.search_but = ttk.Button(self.master, text="Search", command=self.search)
        self.search_but.grid(row=0, column=2)

        self.master.bind("<<TreeviewOpen>>", self.update_tree)

        self.dirs = []

    def search(self, *args):
        if not os.path.isdir(self.search_loc.get()):
            return
        if self.show_prog.get():
            return self.search_win(self, *args)
        self.search_but.configure(state="disabled")

        if platform.system() == "Darwin":
            self.dirs = os_walk_search(self.search_loc.get(), self.search_var.get())
        else:
            self.dirs = not_darwin_search(self.search_loc.get(), self.search_var.get())

        if self.search_inside_var.get():
            self.dirs += self.search_inside()

        self.search_vew.delete(*self.search_vew.get_children())
        dir = os.path.abspath(self.search_loc.get())
        node = self.search_vew.insert("", "end", text=dir, values=[dir, "directory"])
        self.populate_tree(self.search_vew, node)
        self.search_but.configure(state="normal")

    def search_win(self, *args):
        """
        Search but with a counter for the number of currently found files
        Tries to mimic the functionality of catfish but if you mimize onion_file_search it stays open, needs fixing
        """

        prog_win = file_counter_win(self.master)

        curr_prog = ttk.Label(prog_win, text="Files Found: ")
        curr_prog.grid(row=0, column=0, sticky="nsew")

        prog_win.grid_rowconfigure(0, weight=1)
        prog_win.grid_columnconfigure(0, weight=1)

        self.search_but.configure(state="disabled")

        if platform.system() == "Darwin":
            self.dirs = os_walk_search(self.search_loc.get(), self.search_var.get())
        else:
            self.dirs = not_darwin_search(self.search_loc.get(), self.search_var.get())

        for file_count, directory in enumerate(self.dirs):
            if file_count % 100 == 1:
                curr_prog["text"] = "Files Found: {0}".format(file_count)
                curr_prog.update()
            curr_prog["text"] = "Files Found: {0}".format(file_count)
            curr_prog.update()

        if self.search_inside_var.get():
            self.dirs += self.search_inside()

        self.search_vew.delete(*self.search_vew.get_children())
        dir = os.path.abspath(self.search_loc.get())
        node = self.search_vew.insert("", "end", text=dir, values=[dir, "directory"])
        self.populate_tree(self.search_vew, node)
        self.search_vew.update()
        self.search_but.configure(state="normal")

        self.master.after(1000, prog_win.destroy)

    def search_inside(self):
        files = []
        self.inside_search_files = []
        # if sys.version_info >= (3, 0):
        if platform.system() == "Linux":
            os.system(
                'grep -sRil "{text}" {location} > files.txt'.format(
                    text=self.search_var.get(), location=self.search_loc.get()
                )
            )
        elif platform.system() == "Windows":
            os.system(
                'findstr /s /m /p /i /c:"{text}" {location} > files.txt'.format(
                    text=self.search_var.get(),
                    location=os.path.join(self.search_loc.get(), "*"),
                )
            )
        with open("files.txt", "r") as f:
            for line in f:
                files.append(os.path.dirname(line))
                self.inside_search_files.append(os.path.normpath(line.strip()))
        return files

    def populate_tree(self, tree, node):
        if tree.set(node, "type") != "directory":
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
            elif os.path.isfile(p):
                ptype = "file"
            fname = os.path.split(p)[1]
            if ptype != "file":
                id = tree.insert(node, "end", text=fname, values=[p, ptype])
            else:
                if self.search_var.get() in fname or p in self.inside_search_files:
                    id = tree.insert(node, "end", text=fname, values=[p, ptype])
                else:
                    continue
            if ptype == "directory":
                tree.insert(id, 0, text="dummy")
                tree.item(id, text=fname)
            elif ptype == "file":
                _stat = os.stat(p)
                size = _stat.st_size
                tree.set(id, "size", "%d bytes" % size)
                modified = time.ctime(_stat[stat.ST_MTIME])
                tree.set(id, "Last Access", modified)

    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())


def main():
    if "ttkthemes" in sys.modules:
        root = ttkthemes.ThemedTk()
        file_walker_gui = file_walker(root)

        if platform.system() == "Linux":
            root.set_theme("equilux")
        elif platform.system() == "Windows":
            root.set_theme("vista")
        elif platform.system() == "Darwin":
            root.set_theme("aqua")
        root.mainloop()
    else:
        root = tk.Tk()
        file_walker_gui = file_walker(root)
        root.mainloop()


if __name__ == "__main__":
    main()
