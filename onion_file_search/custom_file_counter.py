import tkinter as tk
import tkinter.ttk as ttk
import platform


class file_counter_win(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.master = master
        self.title("Progress")
        self.set_geometry()
        self.innit_widgets()

    def set_geometry(self):
        self.resizable(False, False)
        if platform.system() == "Linux":
            self.wm_attributes("-type", "splash")
        else:
            self.overrideredirect(1)
        self.attributes("-topmost", True)
        self.geometry(
            "150x22+{:.0f}+{:.0f}".format(
                self.master.winfo_x() + (self.master.winfo_width()) - 150,
                self.master.winfo_y() + (self.master.winfo_height()) - 22,
            )
        )

    def innit_widgets(self):
        self.curr_prog = ttk.Label(self, text="Files Found: ")
        self.curr_prog.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def set_count(self, file_count):
        self.curr_prog["text"] = "Files Found: {0}".format(file_count)
        self.curr_prog.update()

    def count(self, files):
        for file_count in range(len(files)):
            if file_count % 100 == 1:
                self.set_count(file_count)

        self.set_count(file_count)
        self.master.after(1000, self.destroy)
