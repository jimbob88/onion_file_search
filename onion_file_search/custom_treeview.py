import tkinter as tk
import tkinter.ttk as ttk
import platform
import sys


class AutoScroll(object):
    """
    Made By Guilherme Polo:
    all rights reserved (via http://page.sourceforge.net/)
    """

    def __init__(self, master):
        
        self.set_xscroll(master)
        self.set_yscroll(master)
        
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        methods = tk.Grid.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ("config", "configure"):
                setattr(self, meth, getattr(master, meth))

    def set_xscroll(self, master):
        hsb = ttk.Scrollbar(master, orient="horizontal", command=self.xview)
        
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky="nsew")
        
        hsb.grid(column=0, row=1, sticky="ew")

    def set_yscroll(self, master):
        try:
            vsb = ttk.Scrollbar(master, orient="vertical", command=self.yview)
            self.configure(yscrollcommand=self._autoscroll(vsb))
            vsb.grid(column=1, row=0, sticky="ns")
        except Exception:
            pass

    @staticmethod
    def _autoscroll(sbar):
        """Hide and show scrollbar as needed."""

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
    """Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget."""

    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind("<Enter>", lambda e: _bound_to_mousewheel(e, container))
        container.bind(
            "<Leave>", lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)

    return wrapped


class ScrolledTreeView(AutoScroll, ttk.Treeview):
    """A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed."""

    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)


def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    def mswheel_func(e): return _on_mousewheel(e, child)
    def msshift_func(e): return _on_shiftmouse(e, child)
    if platform.system() != "Linux":
        child.bind_all("<MouseWheel>", mswheel_func)
        child.bind_all("<Shift-MouseWheel>", msshift_func)
    else:
        child.bind_all("<Button-4>", mswheel_func)
        child.bind_all("<Button-5>", mswheel_func)
        child.bind_all("<Shift-Button-4>", msshift_func)
        child.bind_all("<Shift-Button-5>", msshift_func)


def _unbound_to_mousewheel(event, widget):
    if platform.system() == "Windows" or platform.system() == "Darwin":
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Shift-MouseWheel>")
    else:
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")
        widget.unbind_all("<Shift-Button-4>")
        widget.unbind_all("<Shift-Button-5>")


def _on_mousewheel(event, widget):
    if platform.system() == "Windows":
        widget.yview_scroll(-1 * int(event.delta / 120), "units")
    elif platform.system() == "Darwin":
        widget.yview_scroll(-1 * int(event.delta), "units")
    elif event.num == 4:
        widget.yview_scroll(-1, "units")
    elif event.num == 5:
        widget.yview_scroll(1, "units")