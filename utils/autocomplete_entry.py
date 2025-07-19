import customtkinter as ctk
import tkinter as tk

class AutocompleteEntry(ctk.CTkEntry):
    def __init__(self, master, lista_opciones, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.lista_opciones = lista_opciones
        self.callback = callback

        self.var = tk.StringVar()
        self.configure(textvariable=self.var)

        self.var.trace("w", self.on_var_change)

        self.bind("<Return>", self.on_select)
        self.bind("<Down>", self.move_selection_down)
        self.bind("<Up>", self.move_selection_up)
        self.bind("<FocusOut>", lambda e: self.hide_suggestions())

        self.listbox = None
        self.selected_index = -1

    def on_var_change(self, *args):
        texto = self.var.get()
        if texto == "":
            self.hide_suggestions()
            return

        opciones_filtradas = [op for op in self.lista_opciones if texto.lower() in op.lower()]

        if opciones_filtradas:
            self.show_suggestions(opciones_filtradas)
        else:
            self.hide_suggestions()

    def show_suggestions(self, opciones):
        if self.listbox:
            self.listbox.destroy()

        self.listbox = tk.Listbox(self.master, height=min(5, len(opciones)))
        self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())

        for opcion in opciones:
            self.listbox.insert(tk.END, opcion)

        self.listbox.bind("<ButtonRelease-1>", self.on_click)
        self.listbox.bind("<Return>", self.on_select)
        self.selected_index = -1

    def hide_suggestions(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def on_click(self, event):
        if self.listbox:
            valor = self.listbox.get(tk.ACTIVE)
            self.var.set(valor)
            self.hide_suggestions()
            if self.callback:
                self.callback(valor)

    def on_select(self, event=None):
        if self.listbox and self.selected_index >= 0:
            valor = self.listbox.get(self.selected_index)
            self.var.set(valor)
        elif self.listbox:
            valor = self.listbox.get(tk.ACTIVE)
            self.var.set(valor)

        self.hide_suggestions()
        if self.callback:
            self.callback(self.var.get())

    def move_selection_down(self, event):
        if not self.listbox:
            return
        self.selected_index += 1
        if self.selected_index >= self.listbox.size():
            self.selected_index = 0
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.selected_index)

    def move_selection_up(self, event):
        if not self.listbox:
            return
        self.selected_index -= 1
        if self.selected_index < 0:
            self.selected_index = self.listbox.size() - 1
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.selected_index)
