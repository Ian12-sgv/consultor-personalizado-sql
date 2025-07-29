import tkinter.ttk as ttk
import customtkinter as ctk
from components.ui.treeview_renderer import render as render_tree

class DatosTreeview(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def render_data(self, df, highlight_dups=False):
        for item in self.tree.get_children():
            self.tree.delete(item)
        render_tree(self.tree, df)
        if highlight_dups:
            self.tree.tag_configure('dup', background='#3E1E50')
            self.tree.tag_configure('uniq', background='#1E502E')
            for item_id, (_, row) in zip(self.tree.get_children(), df.iterrows()):
                tag = 'dup' if row.get('_dup_desc', False) else 'uniq'
                self.tree.item(item_id, tags=(tag,))
