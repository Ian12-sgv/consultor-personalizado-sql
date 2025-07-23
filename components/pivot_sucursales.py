import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias_sucursales_detallado(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'NombreTienda', 'Existencia_Total']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    sucursales = df[df['Region'].str.contains('Sucursales')]

    if sucursales.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = sucursales[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = sucursales.pivot_table(index='Concatenar',
                                      columns='NombreTienda',
                                      values='Existencia_Total',
                                      aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='Concatenar', how='left')

    sucursal_cols = sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'Concatenar'])

    # Rellenar NaN con 0 en sucursales
    for col in sucursal_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Sucursal_Total'] = resultado[sucursal_cols].sum(axis=1)

    # ❗️Eliminar filas donde Sucursal_Total es 0
    resultado = resultado[resultado['Sucursal_Total'] > 0].copy()

    # Eliminar columna de porcentaje si no la quieres calcular (opcional)
    # Si deseas dejarla vacía, mantenemos así:
    resultado['Porcentaje_Existencia_Sucursales'] = ""

    columnas_ordenadas = CAMPOS_FIJOS + sucursal_cols + ['Sucursal_Total', 'Porcentaje_Existencia_Sucursales']
    resultado = resultado[columnas_ordenadas]

    return resultado
