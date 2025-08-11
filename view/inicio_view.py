import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
import pandas as pd
from components.excelPy import run_excelPy

from Style.styleInicioView import configure_ctk_style, configure_treeview_style
from components.exporter import exportar_dataframe_a_excel, export_pdfs_por_sucursal
from components.services.inventory_service import InventoryService

# UI modularizados
from components.ui.placeholder_combo import PlaceholderCombo
from components.ui.debounce import Debouncer
from components.ui.treeview_renderer import render as render_tree
from components.ui.button import Button

PLACEHOLDER_REGION     = "Región"
PLACEHOLDER_REFERENCIA = "Referencia"
PLACEHOLDER_EXCLUDE    = "CodigoMarcas a excluir (separadas por coma)"

class InicioView(ctk.CTk):
    def __init__(self, engine, config_sql):
        super().__init__()
        self.engine = engine
        self.config_sql = config_sql

        self.inventory_service = InventoryService(engine)

        self.filter_solo_coincide = ctk.BooleanVar(value=False)
        self.filter_solo_no_coincide = ctk.BooleanVar(value=False)

        self.title("Inicio - Importación de Datos")
        self.geometry("1100x700")
        configure_ctk_style()
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._style_treeview()

    def _build_ui(self):
        filtro_frame = ctk.CTkFrame(self)
        filtro_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filtro_frame.grid_columnconfigure((0,1), weight=1)

        self.pivot_selector = ctk.CTkComboBox(
            filtro_frame,
            values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=lambda _: self._update_view()
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.region_selector = PlaceholderCombo(
            filtro_frame,
            placeholder=PLACEHOLDER_REGION,
            values=["Todas"], state="disabled",
            command=lambda _: self._update_view()
        )
        self.region_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.referencia_entry = PlaceholderCombo(
            filtro_frame,
            placeholder=PLACEHOLDER_REFERENCIA,
            values=[""], state="normal",
            command=lambda _: self._update_view()
        )
        self.referencia_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self._debounce_ref = Debouncer(self, delay_ms=300)
        self.referencia_entry.bind("<KeyRelease>", lambda e: self._debounce_ref.call(self._update_view))

        self.exclude_entry = ctk.CTkEntry(
            filtro_frame,
            placeholder_text=PLACEHOLDER_EXCLUDE,
            width=200
        )
        self.exclude_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.exclude_entry.bind("<Return>", lambda e: self._update_view())

        self.promo_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filtro_frame,
            text="Solo Promoción = 1",
            variable=self.promo_var,
            command=self._update_view
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.desc_dup_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filtro_frame,
            text="Resaltar Descuento Duplicados",
            variable=self.desc_dup_var,
            command=self._update_view
        ).grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.btn_unique = Button(
            filtro_frame,
            text="Solo no duplicados",
            command=lambda: self._set_filter_mode('unique'),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            row=5,
            column=0,
            padx=10,
            pady=5
        )
        self.btn_dup = Button(
            filtro_frame,
            text="Solo duplicados",
            command=lambda: self._set_filter_mode('dup'),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            row=5,
            column=1,
            padx=10,
            pady=5
        )
        self.btn_unique.grid_remove()
        self.btn_dup.grid_remove()

        ctk.CTkCheckBox(
            filtro_frame,
            text="Mostrar solo coincidencias",
            variable=self.filter_solo_coincide,
            command=self._update_view
        ).grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkCheckBox(
            filtro_frame,
            text="Mostrar solo no coincidencias",
            variable=self.filter_solo_no_coincide,
            command=self._update_view
        ).grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        boton_frame = ctk.CTkFrame(self)
        boton_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        boton_frame.grid_columnconfigure((0,1,2,3,4), weight=1, uniform="btns")

        Button(boton_frame, text="Importar Datos", command=self.importar_datos, fg_color="#3498db", hover_color="#2980b9", row=0, column=0)
        Button(boton_frame, text="Exportar a Excel", command=self.exportar_excel, fg_color="#27ae60", hover_color="#2ecc71", row=0, column=1)
        Button(boton_frame, text="Exportar PDF", command=self._open_pdf_selector, fg_color="#e67e22", hover_color="#d35400", row=0, column=2)
        Button(boton_frame, text="Importar Excel", command=self.importar_excel, fg_color="#9b59b6", hover_color="#8e44ad", row=0, column=3)
        Button(boton_frame, text="Importar Catálogo Desc.", command=self.importar_catalogo_descuento, fg_color="#8e44ad", hover_color="#732d91", row=0, column=4)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.grid(row=4, column=0, sticky="ew", padx=10)

        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.grid(row=5, column=0, pady=(0,10))

    def importar_datos(self):
        try:
            self.loading_label.configure(text="Cargando datos desde la base, por favor espere...")
            self.update_idletasks()

            self.inventory_service.importar_datos_sql()

            suc = self.inventory_service.df_original[self.inventory_service.df_original['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique())
            self.region_selector.reset_placeholder(values=regiones)
            self.region_selector.configure(state="normal")
            refs = sorted(self.inventory_service.df_original['Referencia'].dropna().astype(str).unique())
            self.referencia_entry.reset_placeholder(values=refs)

            self.loading_label.configure(text="Procesando datos...")
            self.update_idletasks()

            self._update_view()

            self.loading_label.configure(text="")
            messagebox.showinfo("Importación", "Datos importados correctamente.")
        except Exception as e:
            self.loading_label.configure(text="")
            messagebox.showerror("Error al importar datos", str(e))

    def importar_excel(self):
        df = run_excelPy()
        if df is None:
            messagebox.showwarning("Importación cancelada", "No se importó ningún archivo.")
            return

        self.loading_label.configure(text="Procesando archivo Excel importado...")
        self.update_idletasks()

        self.inventory_service.importar_excel(df)
        try:
            suc = self.inventory_service.df_original[self.inventory_service.df_original['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique())
            self.region_selector.reset_placeholder(values=regiones)
            self.region_selector.configure(state="normal")
            refs = sorted(self.inventory_service.df_original['Referencia'].dropna().astype(str).unique())
            self.referencia_entry.reset_placeholder(values=refs)

            self._update_view()
            self.loading_label.configure(text="")
            messagebox.showinfo("Importación", "Excel importado correctamente.")
        except Exception as e:
            self.loading_label.configure(text="")
            messagebox.showerror("Error al importar Excel", str(e))

    def importar_catalogo_descuento(self):
        df_catalogo = run_excelPy()
        if df_catalogo is None:
            messagebox.showwarning("Importación cancelada", "No se importó catálogo de descuentos.")
            return

        self.inventory_service.importar_catalogo_descuento(df_catalogo)

        messagebox.showinfo("Catálogo importado", "Catálogo de descuentos cargado correctamente.")
        self._update_view()

    def _update_view(self):
        if self.inventory_service.df_original is None:
            return

        start_time = time.time()
        self.loading_label.configure(text="Aplicando filtros y procesando vista...")
        self.update_idletasks()

        if self.desc_dup_var.get():
            self.btn_unique.grid()
            self.btn_dup.grid()
        else:
            self.btn_unique.grid_remove()
            self.btn_dup.grid_remove()
            self.inventory_service.filter_mode = None

        opc = self.pivot_selector.get()
        region = self.region_selector.get_value()
        referencia = self.referencia_entry.get_value()
        exclude_list = [m.strip() for m in self.exclude_entry.get().split(',') if m.strip()]
        solo_1 = self.promo_var.get()

        df_view = self.inventory_service.aplicar_filtros(
            opc,
            region,
            referencia,
            exclude_list,
            solo_1,
            self.promo_var.get(),
            self.desc_dup_var.get(),
            self.filter_solo_coincide.get(),
            self.filter_solo_no_coincide.get()
        )

        if df_view is None:
            self.loading_label.configure(text="")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        render_tree(self.tree, df_view)

        if self.desc_dup_var.get():
            self._highlight_desc_duplicados()
        else:
            for iid in self.tree.get_children():
                self.tree.item(iid, tags=())

        self.loading_label.configure(text="")
        print("Tiempo total _update_view:", round(time.time() - start_time, 2), "segundos")

    def _set_filter_mode(self, mode):
        self.inventory_service.set_filter_mode(mode)
        self._update_view()

    def _highlight_desc_duplicados(self):
        self.tree.tag_configure('dup', background='#3E1E50')
        self.tree.tag_configure('uniq', background='#1E502E')
        for item_id, (_, row) in zip(self.tree.get_children(), self.inventory_service.df_actual.iterrows()):
            tag = 'dup' if row['_dup_desc'] else 'uniq'
            self.tree.item(item_id, tags=(tag,))

    def _open_pdf_selector(self):
        if self.inventory_service.df_actual is None or self.inventory_service.df_actual.empty:
            messagebox.showwarning("Sin datos", "Primero importa o filtra datos.")
            return

        all_columns = list(self.inventory_service.df_actual.columns)

        branch_keywords = ['Casa Matriz', 'Sucursal']

        data_columns = [col for col in all_columns if not any(kw in col for kw in branch_keywords)]

        if not data_columns:
            messagebox.showinfo("Sin columnas de datos", "No hay columnas de datos para exportar.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Seleccionar columnas para PDF")
        modal.geometry("320x400")
        modal.transient(self)
        scroll = ctk.CTkScrollableFrame(modal, width=300, height=300)
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        vars_chk = {}
        for c in data_columns:
            var = ctk.BooleanVar(master=modal, value=False)
            chk = ctk.CTkCheckBox(scroll, text=c, variable=var)
            chk.pack(anchor='w', pady=2)
            vars_chk[c] = var
        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        Button(btn_frame, text="Cancelar", command=modal.destroy).grid(row=0, column=1, padx=(0, 5), pady=5)

        def _confirm_columns():
            selected_cols = [s for s, v in vars_chk.items() if v.get()]
            if not selected_cols:
                messagebox.showwarning("Selección requerida", "Seleccione al menos una columna.")
                return
            modal.destroy()
            self._open_branch_selector(selected_cols)

        Button(btn_frame, text="Aceptar", command=_confirm_columns).grid(row=0, column=2, padx=5, pady=5)

    def _open_branch_selector(self, selected_columns):
        if self.inventory_service.df_actual is None or self.inventory_service.df_actual.empty:
            messagebox.showwarning("Sin datos", "Primero importa o filtra datos.")
            return

        all_columns = list(self.inventory_service.df_actual.columns)
        branch_keywords = ['Casa Matriz', 'Sucursal']
        branch_columns = [col for col in all_columns if any(kw in col for kw in branch_keywords)]

        if not branch_columns:
            messagebox.showinfo("Sin sucursales", "No hay columnas de sucursales para exportar.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Seleccionar sucursales para PDF")
        modal.geometry("320x400")
        modal.transient(self)
        scroll = ctk.CTkScrollableFrame(modal, width=300, height=300)
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        vars_chk = {}
        for c in branch_columns:
            var = ctk.BooleanVar(master=modal, value=False)
            chk = ctk.CTkCheckBox(scroll, text=c, variable=var)
            chk.pack(anchor='w', pady=2)
            vars_chk[c] = var
        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        Button(btn_frame, text="Cancelar", command=modal.destroy).grid(row=0, column=1, padx=(0, 5), pady=5)

        def _confirm_branches():
            selected_branches = [s for s, v in vars_chk.items() if v.get()]
            if not selected_branches:
                messagebox.showwarning("Selección requerida", "Seleccione al menos una sucursal o casa matriz.")
                return
            modal.destroy()
            self._export_pdfs(selected_columns, selected_branches)

        Button(btn_frame, text="Aceptar", command=_confirm_branches).grid(row=0, column=2, padx=5, pady=5)

    def _export_pdfs(self, selected_columns, selected_branches):
        cols_to_export = selected_columns + selected_branches

        if not cols_to_export:
            messagebox.showwarning("Exportación", "Debe seleccionar al menos una columna para exportar.")
            return

        df_to_export = self.inventory_service.df_actual.loc[:, self.inventory_service.df_actual.columns.intersection(cols_to_export)].copy()

        print(f"Exportando PDF con columnas: {cols_to_export}")

        export_pdfs_por_sucursal(df_to_export, list(df_to_export.columns))

    def exportar_excel(self):
        exportar_dataframe_a_excel(self.inventory_service.df_actual)

    def _style_treeview(self):
        configure_treeview_style()
