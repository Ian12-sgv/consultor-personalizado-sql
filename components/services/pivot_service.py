# components/services/pivot_service.py
import pandas as pd
from components.data_transformer import (
    pivot_existencias,
    pivot_existencias_sucursales_detallado,
    pivot_existencias_casa_matriz_filtrado
)

class PivotService:
    def __init__(self):
        self.cache = {}  # opcion -> df_pivot

    def get_pivot(self, opcion: str, df_base: pd.DataFrame) -> pd.DataFrame:
        if opcion in self.cache:
            return self.cache[opcion]

        if opcion == "Solo Sucursales":
            df = pivot_existencias_sucursales_detallado(df_base)
            df = df.drop(columns=['Descuento_Sucursales'], errors='ignore')
        elif opcion == "Solo Casa Matriz":
            df = pivot_existencias_casa_matriz_filtrado(df_base)
            df = df.drop(columns=['Descuento_CasaMatriz'], errors='ignore')
        else:
            df = pivot_existencias(df_base)
            cols = list(df.columns)
            if 'Sucursal_Total' in cols and 'Casa_matriz_Total' in cols:
                idx = cols.index('Sucursal_Total')
                cols.remove('Casa_matriz_Total')
                cols.insert(idx + 1, 'Casa_matriz_Total')
            if 'Descuento_Sucursales' in cols and 'Descuento_CasaMatriz' in cols:
                idx = cols.index('Descuento_Sucursales')
                cols.remove('Descuento_CasaMatriz')
                cols.insert(idx + 1, 'Descuento_CasaMatriz')
            df = df[cols]

        self.cache[opcion] = df
        return df

    def clear(self):
        self.cache.clear()
