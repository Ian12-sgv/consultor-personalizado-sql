# view/inicio_view.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from components.query import INVENTORY_SQL

class InicioView(ctk.CTk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine  # Usa el engine ya conectado

        self.title("Inicio - Importación de Datos")
        self.geometry("800x500")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.button_importar = ctk.CTkButton(self, text="Importar Datos", command=self.importar_datos)
        self.button_importar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=lambda *args: None)
        self.scroll_x.grid(row=2, column=0, sticky="ew", padx=10)

    def importar_datos(self):
        try:
            df = pd.read_sql(INVENTORY_SQL, self.engine)

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = list(df.columns)

            for col in df.columns:
                self.tree.heading(col, text=col)

            for _, row in df.iterrows():
                self.tree.insert("", "end", values=list(row))

            messagebox.showinfo("Importación", f"Se importaron {len(df)} filas correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar datos: {e}")
