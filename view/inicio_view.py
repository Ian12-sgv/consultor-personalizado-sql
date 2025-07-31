import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from components.excelPy import run_excelPy

from Style.styleInicioView import configure_ctk_style, configure_treeview_style
from components.query import INVENTORY_SQL
from components.exporter import exportar_dataframe_a_excel, export_pdfs_por_sucursal
from components.services.pivot_service import PivotService
from components.services.filter_service import apply_filters

# UI modularizados
from components.ui.placeholder_combo import PlaceholderCombo
from components.ui.debounce import Debouncer
from components.ui.button import Button

PLACEHOLDER_REGION     = "Región"
PLACEHOLDER_REFERENCIA = "Referencia"
PLACEHOLDER_EXCLUDE    = "Marcas a excluir (separadas por coma)"

class InicioView(ctk.CTk):
    def __init__(self, engine, config_sql):
        super().__init__()
        self.engine = engine
        self.config_sql = config_sql
        self.df_original = None
        self.df_actual = None
        self.catalogo_descuento = None  # Aquí almacenamos el catálogo
        self.pivot_service = PivotService()
        self.filter_mode = None  # 'unique', 'dup', or None

        # Checkbox para filtrar solo coincidencias y no coincidencias
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

        # Checkbox para filtrar solo coincidencias en Descuento_Catalogo
        ctk.CTkCheckBox(
            filtro_frame,
            text="Mostrar solo coincidencias",
            variable=self.filter_solo_coincide,
            command=self._update_view
        ).grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Checkbox para filtrar solo no coincidencias en Descuento_Catalogo
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

    def importar_datos(self):
        try:
            self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)
            suc = self.df_original[self.df_original['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique())
            self.region_selector.reset_placeholder(values=regiones)
            self.region_selector.configure(state="normal")
            refs = sorted(self.df_original['Referencia'].dropna().astype(str).unique())
            self.referencia_entry.reset_placeholder(values=refs)
            self.pivot_service.clear()
            self._update_view()
            messagebox.showinfo("Importación", "Datos importados correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar datos", str(e))

    def importar_excel(self):
        df = run_excelPy()
        if df is None:
            messagebox.showwarning("Importación cancelada", "No se importó ningún archivo.")
            return

        self.df_original = df
        try:
            suc = self.df_original[self.df_original['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique())
            self.region_selector.reset_placeholder(values=regiones)
            self.region_selector.configure(state="normal")
            refs = sorted(self.df_original['Referencia'].dropna().astype(str).unique())
            self.referencia_entry.reset_placeholder(values=refs)
            self.pivot_service.clear()
            self._update_view()
            messagebox.showinfo("Importación", "Excel importado correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar Excel", str(e))

    def importar_catalogo_descuento(self):
        df_catalogo = run_excelPy()
        if df_catalogo is None:
            messagebox.showwarning("Importación cancelada", "No se importó catálogo de descuentos.")
            return

        # Limpiar espacios en nombres de columnas
        df_catalogo.columns = df_catalogo.columns.str.strip()

        # Mostrar columnas y primeras filas para diagnosticar
        print("Columnas catálogo Excel:", df_catalogo.columns.tolist())
        print("Primeras filas catálogo:\n", df_catalogo.head(10))

        col_0 = df_catalogo['Concatenar']
        col_6 = df_catalogo['% Descuento']

        self.catalogo_descuento = pd.DataFrame({
            'Concatenar': col_0,
            'Descuento_Catalogo': col_6
        })

        print("Valores únicos en catálogo de descuentos:", self.catalogo_descuento['Descuento_Catalogo'].unique())

        messagebox.showinfo("Catálogo importado", "Catálogo de descuentos cargado correctamente.")
        self._update_view()  # refrescar vista para aplicar catálogo

    def _update_view(self):
        if self.df_original is None:
            return

        # Manejo botones filtro duplicados
        if self.desc_dup_var.get():
            self.btn_unique.grid()
            self.btn_dup.grid()
        else:
            self.btn_unique.grid_remove()
            self.btn_dup.grid_remove()
            self.filter_mode = None

        opc = self.pivot_selector.get()
        df_base = self.df_original
        if opc == "Solo Sucursales":
            df_base = df_base[df_base['Region'].str.contains('Sucursales', na=False)]
        elif opc == "Solo Casa Matriz":
            df_base = df_base[df_base['Region'].str.contains('Casa Matatriz', na=False)]
        pivot_df = self.pivot_service.get_pivot(opc, df_base)

        region = self.region_selector.get_value()
        referencia = self.referencia_entry.get_value()
        exclude_list = [m.strip() for m in self.exclude_entry.get().split(',') if m.strip()]
        solo_1 = self.promo_var.get()

        df_view = apply_filters(
            pivot_df,
            opc,
            region,
            marca='',
            referencia=referencia,
            exclude_marcas=exclude_list,
            solo_promo_1=solo_1
        ).copy()

        # Merge con catálogo si existe
        if self.catalogo_descuento is not None:
            df_view = df_view.merge(
                self.catalogo_descuento,
                how='left',
                on='Concatenar'
            )

            # Para filas sin descuento en catálogo usar descuento original
            def obtener_descuento(row):
                if pd.isna(row['Descuento_Catalogo']):
                    return row['Descuento']
                return row['Descuento_Catalogo']

            df_view['Descuento_Catalogo'] = df_view.apply(obtener_descuento, axis=1)
        else:
            df_view['Descuento_Catalogo'] = df_view['Descuento']

        # Reordenar columnas para poner Descuento_Catalogo justo al lado de Descuento
        if 'Descuento' in df_view.columns and 'Descuento_Catalogo' in df_view.columns:
            cols = list(df_view.columns)
            cols.remove('Descuento_Catalogo')
            idx = cols.index('Descuento')
            cols.insert(idx + 1, 'Descuento_Catalogo')
            df_view = df_view[cols]

        self.df_actual = df_view.copy()

        # Limpiar el Treeview (items y columnas)
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

        # Configurar columnas y encabezados en orden correcto
        self.tree["columns"] = list(df_view.columns)
        for col in df_view.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")  # Ajusta el width si quieres

        # Insertar filas en el Treeview
        for _, row in df_view.iterrows():
            values = [row[col] for col in df_view.columns]
            self.tree.insert("", "end", values=values)

        # Resaltar duplicados si aplica
        if self.desc_dup_var.get():
            self._highlight_desc_duplicados()
        else:
            for iid in self.tree.get_children():
                self.tree.item(iid, tags=())

    def _set_filter_mode(self, mode):
        self.filter_mode = None if self.filter_mode == mode else mode
        self._update_view()

    def _highlight_desc_duplicados(self):
        self.tree.tag_configure('dup', background='#3E1E50')
        self.tree.tag_configure('uniq', background='#1E502E')
        for item_id, (_, row) in zip(self.tree.get_children(), self.df_actual.iterrows()):
            tag = 'dup' if row['_dup_desc'] else 'uniq'
            self.tree.item(item_id, tags=(tag,))

    def _open_pdf_selector(self):
        if self.df_actual is None or self.df_actual.empty:
            messagebox.showwarning("Sin datos", "Primero importa o filtra datos.")
            return
        cols = [c for c in self.df_actual.columns if c not in
                ['Concatenar', 'Sucursal_Total', 'Casa_matriz_Total',
                 'Total_Existencia', 'Porcentaje_Existencia_CasaMatriz',
                 'Porcentaje_Existencia_Sucursales']]
        if not cols:
            messagebox.showinfo("Sin sucursales", "No hay columnas de sucursales para exportar.")
            return
        modal = ctk.CTkToplevel(self)
        modal.title("Seleccionar sucursales para PDF")
        modal.geometry("320x400")
        modal.transient(self)
        scroll = ctk.CTkScrollableFrame(modal, width=300, height=300)
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        vars_chk = {}
        for c in cols:
            var = ctk.BooleanVar(master=modal, value=False)
            chk = ctk.CTkCheckBox(scroll, text=c, variable=var)
            chk.pack(anchor='w', pady=2)
            vars_chk[c] = var
        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        Button(btn_frame, text="Cancelar", command=modal.destroy).grid(row=0, column=1, padx=(0, 5), pady=5)

        def _confirm():
            sel = [s for s, v in vars_chk.items() if v.get()]
            modal.destroy()
            if sel:
                self._exportar_pdfs_por_sucursal(sel)

        Button(btn_frame, text="Aceptar", command=_confirm).grid(row=0, column=2, padx=5, pady=5)

    def _exportar_pdfs_por_sucursal(self, sucursales):
        export_pdfs_por_sucursal(self.df_actual, sucursales)

    def exportar_excel(self):
        exportar_dataframe_a_excel(self.df_actual)

    def _style_treeview(self):
        configure_treeview_style()
