import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from components.query import INVENTORY_SQL
from components.data_transformer import (
    pivot_existencias,
    pivot_existencias_sucursales_detallado,
    pivot_existencias_casa_matriz
)

class InicioView(ctk.CTk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.df_original = None

        self.title("Inicio - Importación de Datos")
        self.geometry("900x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dropdown principal (Tipo de vista)
        self.pivot_selector = ctk.CTkComboBox(self, values=["Todo", "Solo Sucursales", "Solo Casa Matriz"], command=self.on_tipo_cambio)
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Dropdown secundario (Región de sucursales)
        self.region_selector = ctk.CTkComboBox(self, values=["Todas"], command=self.actualizar_treeview, state="disabled")
        self.region_selector.set("Todas")
        self.region_selector.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Botón importar datos
        self.button_importar = ctk.CTkButton(self, text="Importar Datos", command=self.importar_datos)
        self.button_importar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Treeview
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=lambda *args: None)
        self.scroll_x.grid(row=4, column=0, sticky="ew", padx=10)

    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)

            # Cargar regiones de sucursales únicas para el segundo dropdown
            sucursales = self.df_original[self.df_original['Region'].str.contains('Sucursales')]
            regiones = sucursales['Region'].unique().tolist()
            regiones.sort()
            self.region_selector.configure(values=["Todas"] + regiones)
            self.region_selector.set("Todas")

            self.actualizar_treeview()

            messagebox.showinfo("Importación", "Datos importados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar datos: {e}")

    def on_tipo_cambio(self, *args):
        opcion = self.pivot_selector.get()

        if opcion == "Solo Sucursales":
            self.region_selector.configure(state="normal")
            self.region_selector.set("Todas")  # ✅ Resetea a "Todas" automáticamente
        else:
            self.region_selector.configure(state="disabled")
            self.region_selector.set("Todas")  # ✅ Mantén el reset para consistencia

        self.actualizar_treeview()

    def actualizar_treeview(self, *args):
        if self.df_original is None:
            return

        try:
            opcion = self.pivot_selector.get()
            region_filtro = self.region_selector.get()

            if opcion == "Solo Sucursales":
                df = self.df_original

                if region_filtro != "Todas":
                    df = df[df['Region'] == region_filtro]

                df_pivot = pivot_existencias_sucursales_detallado(df)

            elif opcion == "Solo Casa Matriz":
                df_pivot = pivot_existencias_casa_matriz(self.df_original)

            else:
                df_pivot = pivot_existencias(self.df_original)

            # Mostrar en Treeview aunque esté vacío
            self.tree.delete(*self.tree.get_children())

            if df_pivot.empty:
                self.tree["columns"] = ["Sin datos"]
                self.tree.heading("Sin datos", text="Sin datos disponibles")
                return

            self.tree["columns"] = list(df_pivot.columns)

            for col in df_pivot.columns:
                self.tree.heading(col, text=col)

            for _, row in df_pivot.iterrows():
                self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar vista: {e}")
