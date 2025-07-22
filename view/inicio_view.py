import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from sqlalchemy import text
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
        self.geometry("1100x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_widgets()

    def setup_widgets(self):
        # Marco superior para filtros
        filtro_frame = ctk.CTkFrame(self)
        filtro_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filtro_frame.grid_columnconfigure((0, 1), weight=1)

        self.pivot_selector = ctk.CTkComboBox(
            filtro_frame,
            values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=self.on_tipo_cambio
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.region_selector = ctk.CTkComboBox(
            filtro_frame,
            values=["Todas"],
            command=self.actualizar_treeview,
            state="disabled"
        )
        self.region_selector.set("Todas")
        self.region_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.codigo_marca_entry = ctk.CTkComboBox(
            filtro_frame,
            values=[""],
            state="normal"
        )
        self.codigo_marca_entry.set("")
        self.codigo_marca_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        self.codigo_marca_entry.bind("<Return>", self.filtrar_codigo_marca)

        # Marco central para botones
        boton_frame = ctk.CTkFrame(self)
        boton_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        boton_frame.grid_columnconfigure((0, 1), weight=1)

        self.button_importar = ctk.CTkButton(boton_frame, text="Importar Datos", command=self.importar_datos)
        self.button_importar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.button_exportar = ctk.CTkButton(boton_frame, text="Exportar a Excel", command=self.exportar_excel)
        self.button_exportar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Marco adicional para import/export BD
        bd_frame = ctk.CTkFrame(self)
        bd_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        bd_frame.grid_columnconfigure((0, 1), weight=1)

        self.button_excel_bd = ctk.CTkButton(
            bd_frame,
            text="Importar Excel a BD",
            command=self.importar_excel_a_bd,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.button_excel_bd.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.button_bd_py = ctk.CTkButton(
            bd_frame,
            text="Importar BD a PY",
            command=self.importar_bd_a_py,
            fg_color="#f39c12",
            hover_color="#e67e22"
        )
        self.button_bd_py.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Treeview
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.grid(row=4, column=0, sticky="ew", padx=10)

    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)

            sucursales = self.df_original[self.df_original['Region'].str.contains('Sucursales')]
            regiones = sucursales['Region'].unique().tolist()
            regiones.sort()
            self.region_selector.configure(values=["Todas"] + regiones)
            self.region_selector.set("Todas")

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
        self.actualizar_treeview()

    def actualizar_treeview(self, *args):
        if self.df_original is None:
            return

        try:
            df = self.df_original.copy()
            opcion = self.pivot_selector.get()
            region_filtro = self.region_selector.get()
            marca_filtro = self.codigo_marca_entry.get().strip()

            if opcion == "Solo Sucursales" and region_filtro != "Todas":
                df = df[df['Region'] == region_filtro]

            if marca_filtro != "":
                df = df[df['CodigoMarca'].astype(str) == marca_filtro]

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

    def importar_excel_a_bd(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx *.xls")],
                title="Selecciona el archivo Excel para cargar a BD"
            )

            if not file_path:
                return

            df_excel = pd.read_excel(file_path)

            df_excel.to_sql("Catalogo_Descuentos_Import", con=self.engine, if_exists="replace", index=False)

            messagebox.showinfo("Carga completa", "El Excel se cargó exitosamente a la base de datos.")

        except Exception as e:
            messagebox.showerror("Error al cargar Excel a BD", str(e))

    def importar_bd_a_py(self):
        try:
            query = "SELECT * FROM Catalogo_Descuentos_Import"
            df = pd.read_sql(query, self.engine)

            self.df_original = df

            limpiar_treeview(self.tree)
            cargar_dataframe_en_treeview(self.tree, df)

            messagebox.showinfo("Importación completa", "Datos importados desde BD a Python correctamente.")

        except Exception as e:
            messagebox.showerror("Error al importar BD a Python", str(e))
