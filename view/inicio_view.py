import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from components.query import INVENTORY_SQL
from components.data_transformer import (
    pivot_existencias,
    pivot_existencias_sucursales_detallado,
    pivot_existencias_casa_matriz_filtrado
)
from components.exporter import exportar_dataframe_a_excel
from utils.treeview_utils import limpiar_treeview, cargar_dataframe_en_treeview

class InicioView(ctk.CTk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.df_original = None
        self.df_actual = None

        self.title("Inicio - Importación de Datos")
        self.geometry("1100x650")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_widgets()

    def setup_widgets(self):
        # Filtro Tipo Pivot
        self.pivot_selector = ctk.CTkComboBox(
            self,
            values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=self.on_tipo_cambio
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Filtro Región
        self.region_selector = ctk.CTkComboBox(
            self,
            values=["Todas"],
            command=self.actualizar_treeview,
            state="disabled"
        )
        self.region_selector.set("Todas")
        self.region_selector.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Filtro Código Marca (reactivo + enter)
        self.codigo_marca_entry = ctk.CTkComboBox(
            self,
            values=[""],  # Se llenará dinámicamente al importar
            state="normal"
        )
        self.codigo_marca_entry.set("")
        self.codigo_marca_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Vincular evento Enter al filtro de marca
        self.codigo_marca_entry.bind("<Return>", self.filtrar_codigo_marca)

        # Botones
        self.button_importar = ctk.CTkButton(self, text="Importar Datos", command=self.importar_datos)
        self.button_importar.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.button_exportar = ctk.CTkButton(self, text="Exportar a Excel", command=self.exportar_excel)
        self.button_exportar.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Treeview
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10)

    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)

            sucursales = self.df_original[self.df_original['Region'].str.contains('Sucursales')]
            regiones = sucursales['Region'].unique().tolist()
            regiones.sort()
            self.region_selector.configure(values=["Todas"] + regiones)
            self.region_selector.set("Todas")

            # Llenar código de marca para el filtro reactivo
            codigos_marca = sorted(self.df_original['CodigoMarca'].dropna().unique().astype(str).tolist())
            self.codigo_marca_entry.configure(values=codigos_marca)

            self.actualizar_treeview()

            messagebox.showinfo("Importación", "Datos importados correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar datos", str(e))

    def on_tipo_cambio(self, *args):
        opcion = self.pivot_selector.get()

        if opcion == "Solo Sucursales":
            self.region_selector.configure(state="normal")
            self.region_selector.set("Todas")
        else:
            self.region_selector.configure(state="disabled")
            self.region_selector.set("Todas")

        self.actualizar_treeview()

    def filtrar_codigo_marca(self, event=None):
        """Filtrar por código de marca al presionar Enter"""
        self.actualizar_treeview()

    def actualizar_treeview(self, *args):
        if self.df_original is None:
            return

        try:
            df = self.df_original.copy()
            opcion = self.pivot_selector.get()
            region_filtro = self.region_selector.get()
            marca_filtro = self.codigo_marca_entry.get().strip()

            # Filtro por región
            if opcion == "Solo Sucursales" and region_filtro != "Todas":
                df = df[df['Region'] == region_filtro]

            # Filtro por código de marca (exacto)
            if marca_filtro != "":
                df = df[df['CodigoMarca'].astype(str) == marca_filtro]

            # Pivot según opción
            if opcion == "Solo Sucursales":
                df_pivot = pivot_existencias_sucursales_detallado(df)
                if 'Descuento_Sucursales' in df_pivot.columns:
                    df_pivot = df_pivot.drop(columns=['Descuento_Sucursales'])

            elif opcion == "Solo Casa Matriz":
                df_pivot = pivot_existencias_casa_matriz_filtrado(df)
                if 'Descuento_CasaMatriz' in df_pivot.columns:
                    df_pivot = df_pivot.drop(columns=['Descuento_CasaMatriz'])
            else:
                df_pivot = pivot_existencias(df)

                # Reordenar columnas
                cols = list(df_pivot.columns)
                if 'Sucursal_Total' in cols and 'Casa_matriz_Total' in cols:
                    idx_suc_total = cols.index('Sucursal_Total')
                    cols.remove('Casa_matriz_Total')
                    cols.insert(idx_suc_total + 1, 'Casa_matriz_Total')

                if 'Descuento_Sucursales' in cols and 'Descuento_CasaMatriz' in cols:
                    cols.remove('Descuento_CasaMatriz')
                    idx_desc = cols.index('Descuento_Sucursales')
                    cols.insert(idx_desc + 1, 'Descuento_CasaMatriz')

                df_pivot = df_pivot[cols]

            self.df_actual = df_pivot.copy()

            limpiar_treeview(self.tree)

            if df_pivot.empty:
                self.tree["columns"] = ["Sin datos"]
                self.tree.heading("Sin datos", text="Sin datos disponibles")
                return

            cargar_dataframe_en_treeview(self.tree, df_pivot)

        except Exception as e:
            messagebox.showerror("Error al actualizar vista", str(e))

    def exportar_excel(self):
        exportar_dataframe_a_excel(self.df_actual)
