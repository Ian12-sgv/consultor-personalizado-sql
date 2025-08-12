# view/inicio_view.py
import sys
import os
import time
from contextlib import contextmanager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from tkinter import messagebox

from Style.styleInicioView import configure_ctk_style, configure_treeview_style
from components.exporter import exportar_dataframe_a_excel, export_pdfs_por_sucursal
from components.services.inventory_service import InventoryService

# UI modular
from components.ui.filter_panel import FilterPanel
from components.ui.botones_panel import BotonesPanel
from components.ui.datos_treeview import DatosTreeview
from components.ui.selector_pdf import SelectorPDF


class InicioView(ctk.CTk):
    def __init__(self, engine, config_sql):
        super().__init__()
        self.engine = engine
        self.config_sql = config_sql

        self.inventory_service = InventoryService(engine)

        # Orquestación
        self._last_filters = None
        self._is_updating = False

        self.title("Inicio - Importación de Datos")
        self.geometry("1100x700")
        configure_ctk_style()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Panel de filtros
        self.filter_panel = FilterPanel(self, on_filter_change=self._update_view)
        self.filter_panel.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Panel de botones con callbacks
        callbacks = {
            "importar_datos": self.importar_datos,
            "exportar_excel": self.exportar_excel,
            "exportar_pdf": self._open_pdf_selector,
            "importar_excel": self.importar_excel,
            "importar_catalogo_descuento": self.importar_catalogo_descuento,
        }
        self.botones_panel = BotonesPanel(self, callbacks)
        self.botones_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Tabla
        self.datos_treeview = DatosTreeview(self)
        self.datos_treeview.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Label de carga
        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.grid(row=3, column=0, pady=(0, 10))

        self._style_treeview()

    # ==========
    # Helpers de orquestación
    # ==========
    @contextmanager
    def _busy(self, msg: str):
        """Context manager para estados de carga y log simple."""
        self.loading_label.configure(text=msg)
        self.update_idletasks()
        start = time.time()
        try:
            yield
        finally:
            self.loading_label.configure(text="")
            print(f"[InicioView] {msg} -> listo en {round(time.time()-start, 2)}s")

    def _hydrate_filters_from_df(self):
        """Cargar valores (región/referencia) en el panel, según columnas disponibles."""
        df = self.inventory_service.df_original
        if df is None:
            return

        # Región
        if 'Region' in df.columns:
            suc = df[df['Region'].str.contains('Sucursales', na=False)]
            regiones = ["Todas"] + sorted(suc['Region'].dropna().unique())
            print("[InicioView] set_region_values ->", regiones[:5], "..." if len(regiones) > 5 else "")
            self.filter_panel.set_region_values(regiones)
        else:
            print("[InicioView] df_original sin 'Region' -> ['Todas']")
            self.filter_panel.set_region_values(["Todas"])

        # Referencia
        if 'Referencia' in df.columns:
            refs = sorted(df['Referencia'].dropna().astype(str).unique())
            print("[InicioView] set_referencia_values ->", refs[:5], "..." if len(refs) > 5 else "")
            self.filter_panel.set_referencia_values(refs)
        else:
            print("[InicioView] df_original sin 'Referencia' -> ['']")
            self.filter_panel.set_referencia_values([""])

    def _apply_filters_and_render(self, *, force: bool = False):
        """
        Toma los filtros, aplica en el service y renderiza la tabla.
        Usa cache (_last_filters) y anti-reentrada (_is_updating).
        """
        if self.inventory_service.df_original is None:
            print("[InicioView] _apply_filters_and_render: no hay df_original")
            return

        # Evitar reentradas (p. ej. múltiples eventos encadenados)
        if self._is_updating:
            print("[InicioView] _apply_filters_and_render: ocupado, salto")
            return
        self._is_updating = True
        try:
            filters = self.filter_panel.get_filters()
            # Si nada cambió y no es un refresh forzado (cambio de datos), no recomputar
            if not force and filters == self._last_filters:
                print("[InicioView] filtros sin cambios; no se recomputa")
                return

            print("[InicioView] filtros actuales:", filters)

            # Mostrar/ocultar botones de duplicados
            if filters["desc_dup"]:
                self.filter_panel.btn_unique.grid()
                self.filter_panel.btn_dup.grid()
            else:
                self.filter_panel.btn_unique.grid_remove()
                self.filter_panel.btn_dup.grid_remove()

            df_view = self.inventory_service.aplicar_filtros(
                filters["pivot"],
                filters["region"],
                filters["referencia"],
                filters["exclude_marcas"],
                filters["solo_promo_1"],
                filters["solo_promo_1"],          # promo_var (reutilizamos el mismo)
                filters["desc_dup"],
                filters["filter_solo_coincide"],
                filters["filter_solo_no_coincide"],
                filters["filter_mode"],
                exclude_year=filters.get("exclude_year")  # <-- NUEVO
            )

            if df_view is None:
                print("[InicioView] aplicar_filtros devolvió None")
                return

            self.datos_treeview.render_data(df_view, highlight_dups=filters["desc_dup"])
            # Actualizar cache de filtros tras render exitoso
            self._last_filters = filters
        finally:
            self._is_updating = False

    def _ingest_and_refresh(self, ingest_callable, success_msg: str):
        """
        Orquesta un flujo de ingesta (SQL/Excel) + hidratar filtros + refrescar vista.
        Fuerza recomputar tras cambiar la fuente de datos.
        """
        with self._busy("Procesando..."):
            ingest_callable()
            self._hydrate_filters_from_df()
            self._apply_filters_and_render(force=True)
        messagebox.showinfo("Listo", success_msg)

    # ==========
    # Acciones (orquestadas)
    # ==========
    def importar_datos(self):
        print("[InicioView] importar_datos()")
        try:
            self._ingest_and_refresh(
                ingest_callable=self.inventory_service.importar_datos_sql,
                success_msg="Datos importados correctamente."
            )
        except Exception as e:
            messagebox.showerror("Error al importar datos", str(e))

    def importar_excel(self):
        print("[InicioView] importar_excel()")
        try:
            from components.excelPy import run_excelPy
            df = run_excelPy()
            if df is None:
                messagebox.showwarning("Importación cancelada", "No se importó ningún archivo.")
                return

            def _ingest():
                self.inventory_service.importar_excel(df)

            self._ingest_and_refresh(
                ingest_callable=_ingest,
                success_msg="Excel importado correctamente."
            )
        except Exception as e:
            messagebox.showerror("Error al importar Excel", str(e))

    def importar_catalogo_descuento(self):
        print("[InicioView] importar_catalogo_descuento()")
        try:
            from components.excelPy import run_excelPy
            df_catalogo = run_excelPy()
            if df_catalogo is None:
                messagebox.showwarning("Importación cancelada", "No se importó catálogo de descuentos.")
                return

            needed = {'Concatenar', '% Descuento'}
            cols_norm = set(df_catalogo.columns.str.strip())
            if not needed.issubset(cols_norm):
                messagebox.showerror(
                    "Error en catálogo",
                    f"El catálogo debe contener las columnas: {', '.join(sorted(needed))}\n"
                    f"Columnas encontradas: {', '.join(sorted(cols_norm))}"
                )
                return

            def _ingest():
                self.inventory_service.importar_catalogo_descuento(df_catalogo)

            # Ingerimos catálogo y refrescamos (cambia coincidencias, aunque filtros sean iguales)
            with self._busy("Cargando catálogo..."):
                _ingest()
                self._apply_filters_and_render(force=True)

            messagebox.showinfo("Catálogo", "Catálogo de descuentos cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar catálogo", str(e))

    def _update_view(self):
        """Callback central desde el FilterPanel: solo aplica filtros + render."""
        with self._busy("Aplicando filtros..."):
            self._apply_filters_and_render()

    # ==========
    # Exportaciones
    # ==========
    def _open_pdf_selector(self):
        df = self.inventory_service.df_actual
        if df is None or df.empty:
            messagebox.showwarning("Sin datos", "Primero importa o filtra datos.")
            return

        def _do_export(selected_data_cols, selected_branch_cols):
            cols_to_export = list(selected_data_cols) + list(selected_branch_cols)
            if not cols_to_export:
                messagebox.showwarning("Exportación", "Selecciona al menos una columna.")
                return
            df_to_export = df.loc[:, df.columns.intersection(cols_to_export)].copy()
            print(f"[InicioView] Exportando PDF con columnas: {list(df_to_export.columns)}")
            export_pdfs_por_sucursal(df_to_export, list(df_to_export.columns))
            messagebox.showinfo("Exportación", "PDFs generados correctamente.")

        SelectorPDF(self, df, on_export=_do_export)

    def exportar_excel(self):
        exportar_dataframe_a_excel(self.inventory_service.df_actual)

    # ==========
    # Estilos tabla
    # ==========
    def _style_treeview(self):
        configure_treeview_style()
