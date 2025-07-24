# view/inicio_view.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd

from components.query import INVENTORY_SQL
from components.exporter import exportar_dataframe_a_excel, export_pdfs_por_sucursal
from components.ui.placeholder_combo import PlaceholderCombo
from components.ui.debounce import Debouncer
from components.ui.treeview_renderer import render as render_tree
from components.services.pivot_service import PivotService
from components.services.filter_service import apply_filters

PLACEHOLDER_REGION     = "Región"
PLACEHOLDER_MARCA      = "Código de marca"
PLACEHOLDER_REFERENCIA = "Referencia"

class InicioView(ctk.CTk):
    def __init__(self, engine, config_sql):
        super().__init__()

        self.engine = engine
        self.config_sql = config_sql

        self.df_original = None
        self.df_actual   = None

        self.pivot_service = PivotService()

        self.title("Inicio - Importación de Datos")
        self.geometry("1100x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._style_treeview()

    # ------------------------------ UI ---------------------------------
    def _build_ui(self):
        filtro_frame = ctk.CTkFrame(self)
        filtro_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filtro_frame.grid_columnconfigure((0, 1), weight=1)

        # Pivot selector
        self.pivot_selector = ctk.CTkComboBox(
            filtro_frame,
            values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=lambda _: self._update_view()
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Región (placeholder, deshabilitada por defecto)
        self.region_selector = PlaceholderCombo(
            filtro_frame,
            placeholder=PLACEHOLDER_REGION,
            values=["Todas"],
            state="disabled",
            command=lambda _: self._update_view()
        )
        self.region_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Código de marca
        self.codigo_marca_entry = PlaceholderCombo(
            filtro_frame,
            placeholder=PLACEHOLDER_MARCA,
            values=[""],
            state="normal",
            command=lambda _: self._update_view()
        )
        self.codigo_marca_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        self._debounce_marca = Debouncer(self, delay_ms=300)
        self.codigo_marca_entry.bind("<KeyRelease>", lambda e: self._debounce_marca.call(self._update_view))

        # Referencia
        self.referencia_entry = PlaceholderCombo(
            filtro_frame,
            placeholder=PLACEHOLDER_REFERENCIA,
            values=[""],
            state="normal",
            command=lambda _: self._update_view()
        )
        self.referencia_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        self._debounce_ref = Debouncer(self, delay_ms=300)
        self.referencia_entry.bind("<KeyRelease>", lambda e: self._debounce_ref.call(self._update_view))

        # Excluir códigos GRD/DNE/DIE
        self.exclude_var = ctk.BooleanVar(master=self, value=False)
        self.chk_excluir = ctk.CTkCheckBox(
            filtro_frame,
            text="Excluir códigos GRD / DNE / DIE",
            variable=self.exclude_var,
            command=self._update_view
        )
        self.chk_excluir.grid(row=3, column=0, padx=10, pady=5, sticky="w", columnspan=2)

        # Solo Promoción = 1
        self.promo_var = ctk.BooleanVar(master=self, value=False)
        self.chk_promo = ctk.CTkCheckBox(
            filtro_frame,
            text="Solo filas con Promoción = 1",
            variable=self.promo_var,
            command=self._update_view
        )
        self.chk_promo.grid(row=4, column=0, padx=10, pady=5, sticky="w", columnspan=2)

        # Botones
        boton_frame = ctk.CTkFrame(self)
        boton_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        boton_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(boton_frame, text="Importar Datos", command=self.importar_datos)\
            .grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(boton_frame, text="Exportar a Excel", command=self.exportar_excel)\
            .grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(boton_frame, text="Exportar PDF", command=self._open_pdf_selector)\
            .grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Treeview
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.grid(row=4, column=0, sticky="ew", padx=10)

    # --------------------------- DATA ----------------------------------
    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)

            # Regiones (solo sucursales)
            suc = self.df_original[self.df_original['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique().tolist())
            self.region_selector.reset_placeholder(values=regiones)
            self.region_selector.configure(state="disabled")

            # Marcas
            codigos = sorted(self.df_original['CodigoMarca'].dropna().astype(str).unique().tolist())
            self.codigo_marca_entry.reset_placeholder(values=codigos)

            # Referencias
            refs = sorted(self.df_original.get('Referencia', pd.Series(dtype=str))
                          .dropna().astype(str).unique().tolist())
            self.referencia_entry.reset_placeholder(values=refs)

            # Limpiar cache pivots
            self.pivot_service.clear()

            self._update_view()
            messagebox.showinfo("Importación", "Datos importados correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar datos", str(e))

    # -------------------------- VIEW LOGIC ------------------------------
    def _update_view(self):
        if self.df_original is None:
            return

        opcion = self.pivot_selector.get()

        # habilitar región solo para sucursales
        if opcion == "Solo Sucursales":
            self.region_selector.configure(state="normal")
        else:
            self.region_selector.configure(state="disabled")
            self.region_selector.reset_placeholder()

        # df base según opción
        df_base = self.df_original
        if opcion == "Solo Sucursales":
            df_base = df_base[df_base['Region'].str.contains('Sucursales', na=False)]
        elif opcion == "Solo Casa Matriz":
            df_base = df_base[df_base['Region'].str.contains('Casa Matriz', na=False)]

        pivot_df = self.pivot_service.get_pivot(opcion, df_base)

        region     = self.region_selector.get_value()
        marca      = self.codigo_marca_entry.get_value()
        referencia = self.referencia_entry.get_value()
        excluir    = self.exclude_var.get()
        solo_1     = self.promo_var.get()

        df_view = apply_filters(
            pivot_df,
            opcion,
            region,
            marca,
            referencia,
            excluir_codigos=excluir,
            solo_promo_1=solo_1
        )

        # Normalizar Promocion a 0/1
        if 'Promocion' in df_view.columns:
            serie = df_view['Promocion']
            df_view['Promocion'] = (
                serie.map({True: 1, False: 0, 'True': 1, 'False': 0,
                           'true': 1, 'false': 0, '1': 1, '0': 0})
                     .fillna(serie)
                     .astype(int, errors='ignore')
            )

        self.df_actual = df_view.copy()
        render_tree(self.tree, df_view)

    # -------------------------- PDF MODAL ---------------------------------
    def _open_pdf_selector(self):
        if self.df_actual is None or self.df_actual.empty:
            messagebox.showwarning("Sin datos", "Primero importa o filtra datos.")
            return

        # Columnas de sucursales disponibles
        sucursales = [c for c in self.df_actual.columns
                      if c not in ['Concatenar',
                                   'Sucursal_Total','Casa_matriz_Total',
                                   'Total_Existencia',
                                   'Porcentaje_Existencia_CasaMatriz',
                                   'Porcentaje_Existencia_Sucursales']]
        if not sucursales:
            messagebox.showinfo("Sin sucursales", "No hay columnas de sucursales para exportar.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Seleccionar sucursales para PDF")
        modal.geometry("320x400")
        modal.transient(self)

        scroll = ctk.CTkScrollableFrame(modal, width=300, height=300)
        scroll.pack(padx=10, pady=10, fill="both", expand=True)

        vars_chk = {}
        for suc in sucursales:
            var = ctk.BooleanVar(master=modal, value=False)
            chk = ctk.CTkCheckBox(scroll, text=suc, variable=var)
            chk.pack(anchor="w", pady=2)
            vars_chk[suc] = var

        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", hover_color="darkgray",
                      command=modal.destroy).pack(side="right", padx=(0,5))
        def _confirm():
            seleccion = [s for s,v in vars_chk.items() if v.get()]
            modal.destroy()
            if seleccion:
                self._exportar_pdfs_sucursales(seleccion)
        ctk.CTkButton(btn_frame, text="Aceptar", fg_color="#2ecc71", hover_color="#27ae60",
                      command=_confirm).pack(side="right")

    def _exportar_pdfs_sucursales(self, sucursales):
        try:
            carpeta = export_pdfs_por_sucursal(self.df_actual, sucursales)
            messagebox.showinfo("PDFs generados", f"Se han generado los PDFs en:\n{carpeta}")
        except Exception as e:
            messagebox.showerror("Error al exportar PDFs", str(e))

    # -------------------------- EXPORT ---------------------------------
    def exportar_excel(self):
        exportar_dataframe_a_excel(self.df_actual)

    # -------------------------- STYLE TREEVIEW -------------------------
    def _style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        foreground="#ffffff",
                        background="#1f6aa5")
        style.map("Treeview.Heading",
                  background=[("active", "#18527d")])

        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=22,
                        background="#1e1e1e",
                        fieldbackground="#1e1e1e",
                        foreground="#e5e5e5")
        style.map("Treeview",
                  background=[("selected", "#1f6aa5")],
                  foreground=[("selected", "white")])
