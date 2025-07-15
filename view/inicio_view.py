# view/inicio_view.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from components.query import INVENTORY_SQL
from components.data_transformer import pivot_existencias, pivot_existencias_sucursales, pivot_existencias_casa_matriz

class InicioView(ctk.CTk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.df_original = None

        self.title("Inicio - Importación de Datos")
        self.geometry("800x500")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Nuevo dropdown con 3 opciones
        self.pivot_selector = ctk.CTkComboBox(self, values=["Todo", "Solo Sucursales", "Solo Casa Matriz"], command=self.actualizar_treeview)
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.button_importar = ctk.CTkButton(self, text="Importar Datos", command=self.importar_datos)
        self.button_importar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=lambda *args: None)
        self.scroll_x.grid(row=3, column=0, sticky="ew", padx=10)

    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)
            self.actualizar_treeview()
            messagebox.showinfo("Importación", f"Datos importados correctamente. Ahora puedes seleccionar el tipo de pivot.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar datos: {e}")

    def actualizar_treeview(self, *args):
        if self.df_original is None:
            return

        try:
            opcion = self.pivot_selector.get()

            if opcion == "Solo Sucursales":
                df_pivot = pivot_existencias_sucursales(self.df_original)
            elif opcion == "Solo Casa Matriz":
                df_pivot = pivot_existencias_casa_matriz(self.df_original)
            else:
                df_pivot = pivot_existencias(self.df_original)

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = list(df_pivot.columns)

            for col in df_pivot.columns:
                self.tree.heading(col, text=col)

            for _, row in df_pivot.iterrows():
                self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar vista: {e}")
