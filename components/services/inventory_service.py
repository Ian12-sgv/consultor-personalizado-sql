# components/services/inventory_service.py
import pandas as pd
from components.query import INVENTORY_SQL
from components.services.filter_service import apply_filters
from components.services.pivot_service import PivotService


class InventoryService:
    def __init__(self, engine):
        self.engine = engine
        self.df_original = None
        self.df_actual = None
        self.catalogo_descuento = None
        self.filter_mode = None  # 'unique', 'dup' o None
        self.pivot_service = PivotService()
        # recordar último año excluido para invalidar caché sólo cuando cambie
        self._last_exclude_year = None

    # -----------------------
    # Cargas de datos
    # -----------------------
    def importar_datos_sql(self):
        self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)
        # Normaliza nombres de columnas
        self.df_original.columns = self.df_original.columns.str.strip()
        self.df_actual = self.df_original.copy()
        self.catalogo_descuento = None
        self.filter_mode = None
        self._last_exclude_year = None
        self.pivot_service.clear()

    def importar_excel(self, df_excel: pd.DataFrame):
        self.df_original = df_excel.copy()
        # Normaliza nombres de columnas
        self.df_original.columns = self.df_original.columns.str.strip()
        self.df_actual = self.df_original.copy()
        self.catalogo_descuento = None
        self.filter_mode = None
        self._last_exclude_year = None
        self.pivot_service.clear()

    def importar_catalogo_descuento(self, df_catalogo: pd.DataFrame):
        """
        Espera columnas:
          - 'Concatenar'
          - '% Descuento'
        """
        df_catalogo.columns = df_catalogo.columns.str.strip()
        if 'Concatenar' in df_catalogo.columns and '% Descuento' in df_catalogo.columns:
            self.catalogo_descuento = pd.DataFrame({
                'Concatenar': df_catalogo['Concatenar'],
                'Descuento_Catalogo': df_catalogo['% Descuento']
            })
        else:
            raise ValueError(
                "El catálogo de descuentos debe contener las columnas "
                "'Concatenar' y '% Descuento'."
            )

    # -----------------------
    # Helper: excluir por AÑO (robusto)
    # -----------------------
    def _exclude_year_pre_pivot(self, df: pd.DataFrame, exclude_year):
        """
        Excluye filas cuyo AÑO == exclude_year. Ignora día/mes.

        Soporta:
          - columna de año: 'Año' / 'Anio' / 'Year' (con/sin espacios, cualquier casing)
          - columna de fecha: cualquier col cuyo nombre contenga 'fecha',
            o iguale 'fechadoc' / 'date' / 'fecharegistro' (con/sin espacios, cualquier casing)

        Si no encuentra columnas compatibles o el año no es válido, devuelve df sin cambios.
        """
        if df is None or df.empty:
            return df
        if exclude_year is None or str(exclude_year).strip() == "":
            return df

        try:
            year = int(str(exclude_year).strip())
        except Exception:
            return df

        # mapa normalizado -> nombre original
        norm_map = {c.strip().lower(): c for c in df.columns}

        # 1) columna de AÑO numérico
        for key in ("año", "anio", "year"):
            if key in norm_map:
                col = norm_map[key]
                s = pd.to_numeric(df[col], errors="coerce")
                return df[s.ne(year)]

        # 2) columnas de FECHA (buscar candidatas por nombre)
        fecha_candidates = []
        for norm_name, original in norm_map.items():
            if (
                "fecha" in norm_name
                or norm_name in ("fechadoc", "date", "fecharegistro")
            ):
                fecha_candidates.append(original)

        # probar candidatas de fecha hasta que alguna parsee
        for col in fecha_candidates:
            years = pd.to_datetime(df[col], errors="coerce", dayfirst=True).dt.year
            if years.notna().any():
                return df[years.ne(year)]

        # 3) último intento: escanear todas las columnas y ver si alguna parsea a fecha
        for col in df.columns:
            years = pd.to_datetime(df[col], errors="coerce", dayfirst=True).dt.year
            # si al menos un 50% parsea a fechas, lo consideramos columna de fecha
            if years.notna().mean() >= 0.5:
                return df[years.ne(year)]

        # 4) no se encontró nada compatible
        return df

    # -----------------------
    # Filtros + composición
    # -----------------------
    def aplicar_filtros(
        self,
        opc,
        region,
        referencia,
        exclude_list,
        solo_1,
        promo_var,  # firma compatible (no se usa directamente)
        desc_dup_var,
        filter_solo_coincide,
        filter_solo_no_coincide,
        filter_mode,
        exclude_year=None,   # NUEVO (opcional)
    ):
        """
        Aplica:
          - filtro de región (si existe)
          - exclusión de año (pre-pivot)
          - pivot (via PivotService)
          - filtros base (marca='', referencia, marcas excluidas, solo_promo_1)
          - merge con catálogo de descuentos si existe
          - modo coincidencias / no coincidencias
          - normaliza Promocion a 0/1
          - marca duplicados por ('Concatenar','Descuento') y aplica filter_mode
        """
        if self.df_original is None:
            return None

        # Base
        df_base = self.df_original

        # Región (si existe)
        if 'Region' in df_base.columns:
            if opc == "Solo Sucursales":
                df_base = df_base[df_base['Region'].str.contains('Sucursales', na=False)]
            elif opc == "Solo Casa Matriz":
                df_base = df_base[df_base['Region'].str.contains('Casa Matriz', na=False)]

        # Excluir año ANTES del pivot
        df_base = self._exclude_year_pre_pivot(df_base, exclude_year)

        # Si cambió el año a excluir, invalida caché del pivot
        if exclude_year != self._last_exclude_year:
            self.pivot_service.clear()
            self._last_exclude_year = exclude_year

        # Pivot (cacheado)
        pivot_df = self.pivot_service.get_pivot(opc, df_base)

        # Si no existe 'Referencia' en el pivot, no se filtra por referencia
        if 'Referencia' not in pivot_df.columns:
            referencia = ''  # evita filtrar por referencia si no está

        # Filtros base
        df_view = apply_filters(
            pivot_df,
            opc,
            region,
            marca='',
            referencia=referencia,
            exclude_marcas=exclude_list,
            solo_promo_1=solo_1
        ).copy()

        # Merge catálogo de descuentos (si está disponible)
        if self.catalogo_descuento is not None:
            if 'Concatenar' in df_view.columns and 'Concatenar' in self.catalogo_descuento.columns:
                df_view = df_view.merge(self.catalogo_descuento, how='left', on='Concatenar')

                # Normalizar vacío/NaN y rellenar con 'Descuento' si está vacío
                df_view['Descuento_Catalogo'] = (
                    df_view['Descuento_Catalogo']
                    .fillna("")
                    .replace(["nan", "NaN"], "")
                )
                mask_vacio = df_view['Descuento_Catalogo'].astype(str).str.strip() == ""
                if 'Descuento' in df_view.columns:
                    df_view.loc[mask_vacio, 'Descuento_Catalogo'] = df_view.loc[mask_vacio, 'Descuento']

                # Formatear como porcentaje entero (e.g., "23%")
                def _formatea_pct(serie):
                    s = serie.astype(str).str.replace('%', '', regex=False).str.strip()
                    s_num = pd.to_numeric(s, errors='coerce')
                    s_fmt = s_num.dropna().apply(lambda x: f"{int(round(x))}%")
                    serie.update(s_fmt)
                    return serie

                df_view['Descuento_Catalogo'] = _formatea_pct(df_view['Descuento_Catalogo'])
            else:
                df_view['Descuento_Catalogo'] = ""
        else:
            df_view['Descuento_Catalogo'] = ""

        # Colocar 'Descuento_Catalogo' junto a 'Descuento' si ambas existen
        if 'Descuento' in df_view.columns and 'Descuento_Catalogo' in df_view.columns:
            cols = list(df_view.columns)
            if 'Descuento_Catalogo' in cols:
                cols.remove('Descuento_Catalogo')
                idx = cols.index('Descuento') if 'Descuento' in cols else len(cols) - 1
                cols.insert(idx + 1, 'Descuento_Catalogo')
                df_view = df_view[cols]

        # Filtros de coincidencia / no coincidencia
        if filter_solo_coincide and not filter_solo_no_coincide:
            if 'Descuento' in df_view.columns and 'Descuento_Catalogo' in df_view.columns:
                df_view = df_view[
                    (df_view['Descuento_Catalogo'].notna()) &
                    (df_view['Descuento'].notna()) &
                    (df_view['Descuento_Catalogo'] == df_view['Descuento'])
                ]
        elif filter_solo_no_coincide and not filter_solo_coincide:
            if 'Descuento' in df_view.columns and 'Descuento_Catalogo' in df_view.columns:
                df_view = df_view[
                    (df_view['Descuento_Catalogo'].isna()) |
                    (df_view['Descuento'].isna()) |
                    (df_view['Descuento_Catalogo'] != df_view['Descuento'])
                ]

        # Promocion -> 0/1 si es posible
        if 'Promocion' in df_view.columns:
            serie = df_view['Promocion']
            df_view['Promocion'] = (
                serie.map({
                    True: 1, False: 0,
                    'True': 1, 'False': 0,
                    'true': 1, 'false': 0,
                    '1': 1, '0': 0
                })
                .fillna(serie)
                .astype(int, errors='ignore')
            )

        # Marcar duplicados por ('Concatenar', 'Descuento')
        if desc_dup_var and 'Concatenar' in df_view.columns and 'Descuento' in df_view.columns:
            df_view['_dup_desc'] = df_view.duplicated(subset=['Concatenar', 'Descuento'], keep=False)
        else:
            df_view['_dup_desc'] = False

        # Aplicar modo de filtro (unique / dup)
        if filter_mode == 'unique':
            df_view = df_view[~df_view['_dup_desc']]
        elif filter_mode == 'dup':
            df_view = df_view[df_view['_dup_desc']]

        self.df_actual = df_view.copy()
        return self.df_actual

    # -----------------------
    # Utilidades
    # -----------------------
    def clear_cache(self):
        self.pivot_service.clear()

    def set_filter_mode(self, mode):
        self.filter_mode = None if self.filter_mode == mode else mode
