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

try:
    from benedict import benedict
except:
    raise ImportError(
        "onion_file_search now relies on python-benedict, install it with pip install python-benedict"
    )

from custom_treeview import ScrolledTreeView
from search import (
    os_walk_search,
    not_darwin_search,
)


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


def get_all_values(tree, nested_dictionary, build_path=""):
    for key, value in nested_dictionary.items():
        path = os.path.join(build_path, key)
        if type(value) is dict:
            tree.insert(build_path, "end", path, text=key, values=[path, "directory"])
            get_all_values(tree, value, path)
        else:
            tree.insert(build_path, "end", path, text=key, values=[path, "file"])
            _stat = os.stat(path.replace(":", ":\\"))
            size = _stat.st_size
            tree.set(path, "size", "%d bytes" % size)
            modified = time.ctime(_stat[stat.ST_MTIME])
            tree.set(path, "Last Access", modified)


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

        self.files = []

    def search(self, *args):
        if not os.path.isdir(self.search_loc.get()):
            return
        if self.show_prog.get():
            return self.search_win(self, *args)
        self.search_but.configure(state="disabled")

        if platform.system() == "Darwin":
            self.files = os_walk_search(self.search_loc.get(), self.search_var.get())
        else:
            self.files = not_darwin_search(self.search_loc.get(), self.search_var.get())

        if self.search_inside_var.get():
            self.files += self.search_inside()

        self.search_vew.delete(*self.search_vew.get_children())
        self.populate_tree()
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
            self.files = os_walk_search(self.search_loc.get(), self.search_var.get())
        else:
            self.files = not_darwin_search(self.search_loc.get(), self.search_var.get())

        for file_count, directory in enumerate(self.files):
            if file_count % 100 == 1:
                curr_prog["text"] = "Files Found: {0}".format(file_count)
                curr_prog.update()
            curr_prog["text"] = "Files Found: {0}".format(file_count)
            curr_prog.update()

        if self.search_inside_var.get():
            self.files += self.search_inside()

        self.search_vew.delete(*self.search_vew.get_children())
        self.populate_tree()
        self.search_vew.update()
        self.search_but.configure(state="normal")

        self.master.after(1000, prog_win.destroy)

    def search_inside(self):
        files = []
        self.inside_search_files = []
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

    def populate_tree(self):
        file_tree = benedict({}, keypath_separator=os.sep)
        for_merge = []
        for file_path in self.files:
            for_merge.append(benedict(keypath_separator=os.sep))
            for_merge[-1][file_path.replace("[", "\\[").replace("]", "\\]")] = [
                "file",
                file_path,
            ]
        file_tree.merge(*for_merge)
        self.file_tree = file_tree
        get_all_values(self.search_vew, self.file_tree, build_path="")


def main():
    if "ttkthemes" in sys.modules:
        root = ttkthemes.ThemedTk()
        file_walker(root)

        if platform.system() == "Linux":
            root.set_theme("equilux")
        elif platform.system() == "Windows":
            root.set_theme("vista")
        elif platform.system() == "Darwin":
            root.set_theme("aqua")
        root.mainloop()
    else:
        root = tk.Tk()
        file_walker(root)
        root.mainloop()


if __name__ == "__main__":
    main()
