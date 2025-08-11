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
        self.filter_mode = None  # 'unique', 'dup', or None
        self.pivot_service = PivotService()

    def importar_datos_sql(self):
        self.df_original = pd.read_sql(INVENTORY_SQL, self.engine)
        self.df_actual = self.df_original.copy()
        self.catalogo_descuento = None
        self.filter_mode = None
        self.pivot_service.clear()

    def importar_excel(self, df_excel):
        self.df_original = df_excel.copy()
        self.df_actual = self.df_original.copy()
        self.catalogo_descuento = None
        self.filter_mode = None
        self.pivot_service.clear()

    def importar_catalogo_descuento(self, df_catalogo):
        df_catalogo.columns = df_catalogo.columns.str.strip()
        if 'Concatenar' in df_catalogo.columns and '% Descuento' in df_catalogo.columns:
            self.catalogo_descuento = pd.DataFrame({
                'Concatenar': df_catalogo['Concatenar'],
                'Descuento_Catalogo': df_catalogo['% Descuento']
            })
        else:
            # Opcional: lanzar aviso o mensaje de error para columnas faltantes
            raise ValueError("El catálogo de descuentos debe contener las columnas 'Concatenar' y '% Descuento'.")

    def aplicar_filtros(self, opc, region, referencia, exclude_list, solo_1,
                        promo_var, desc_dup_var, filter_solo_coincide, filter_solo_no_coincide):
        if self.df_original is None:
            return None

        df_base = self.df_original

        # Validar existencia de columna 'Region' antes de filtrar
        if 'Region' in df_base.columns:
            if opc == "Solo Sucursales":
                df_base = df_base[df_base['Region'].str.contains('Sucursales', na=False)]
            elif opc == "Solo Casa Matriz":
                df_base = df_base[df_base['Region'].str.contains('Casa Matatriz', na=False)]
        else:
            # Si no existe 'Region', no filtrar por esta columna
            pass

        pivot_df = self.pivot_service.get_pivot(opc, df_base)

        # Validar existencia de 'Referencia' antes de filtrar
        if 'Referencia' not in pivot_df.columns:
            referencia = ''  # evitar filtro por referencia si no existe

        df_view = apply_filters(
            pivot_df,
            opc,
            region,
            marca='',
            referencia=referencia,
            exclude_marcas=exclude_list,
            solo_promo_1=solo_1
        ).copy()

        # Merge catálogo descuento si existe y columnas necesarias están presentes
        if self.catalogo_descuento is not None:
            if 'Concatenar' in df_view.columns and 'Concatenar' in self.catalogo_descuento.columns:
                df_view = df_view.merge(self.catalogo_descuento, how='left', on='Concatenar')
                df_view['Descuento_Catalogo'] = df_view['Descuento_Catalogo'].fillna("").replace(["nan", "NaN"], "")
                mask_vacio = df_view['Descuento_Catalogo'].str.strip() == ""
                df_view.loc[mask_vacio, 'Descuento_Catalogo'] = df_view.loc[mask_vacio, 'Descuento']

                def formatear_descuento_vector(serie):
                    s = serie.astype(str).str.replace('%', '').str.strip()
                    s_num = pd.to_numeric(s, errors='coerce')
                    s_formateado = s_num.dropna().apply(lambda x: f"{int(round(x))}%")
                    serie.update(s_formateado)
                    return serie

                df_view['Descuento_Catalogo'] = formatear_descuento_vector(df_view['Descuento_Catalogo'])
            else:
                df_view['Descuento_Catalogo'] = ""

        else:
            df_view['Descuento_Catalogo'] = ""

        # Reordenar columnas para mostrar descuento catálogo
        if 'Descuento' in df_view.columns and 'Descuento_Catalogo' in df_view.columns:
            cols = list(df_view.columns)
            cols.remove('Descuento_Catalogo')
            idx = cols.index('Descuento')
            cols.insert(idx + 1, 'Descuento_Catalogo')
            df_view = df_view[cols]

        # Filtrar solo coincidencias o no coincidencias
        if filter_solo_coincide and not filter_solo_no_coincide:
            df_view = df_view[
                (df_view['Descuento_Catalogo'].notna()) &
                (df_view['Descuento'].notna()) &
                (df_view['Descuento_Catalogo'] == df_view['Descuento'])
            ]
        elif filter_solo_no_coincide and not filter_solo_coincide:
            df_view = df_view[
                (df_view['Descuento_Catalogo'].isna()) |
                (df_view['Descuento'].isna()) |
                (df_view['Descuento_Catalogo'] != df_view['Descuento'])
            ]

        # Ajustar formato Promocion
        if 'Promocion' in df_view.columns:
            serie = df_view['Promocion']
            df_view['Promocion'] = (
                serie.map({True:1, False:0, 'True':1, 'False':0,
                           'true':1, 'false':0, '1':1, '0':0})
                     .fillna(serie)
                     .astype(int, errors='ignore')
            )

        # Duplicados
        if desc_dup_var and 'Concatenar' in df_view.columns and 'Descuento' in df_view.columns:
            df_view['_dup_desc'] = df_view.duplicated(subset=['Concatenar', 'Descuento'], keep=False)
        else:
            df_view['_dup_desc'] = False

        if self.filter_mode == 'unique':
            df_view = df_view[~df_view['_dup_desc']]
        elif self.filter_mode == 'dup':
            df_view = df_view[df_view['_dup_desc']]

        self.df_actual = df_view.copy()
        return self.df_actual

    def clear_cache(self):
        self.pivot_service.clear()

    def set_filter_mode(self, mode):
        self.filter_mode = None if self.filter_mode == mode else mode
