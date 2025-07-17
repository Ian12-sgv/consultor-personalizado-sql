import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias_sucursales_detallado(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'NombreTienda', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    sucursales = df[df['Region'].str.contains('Sucursales')]

    if sucursales.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = sucursales[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = sucursales.pivot_table(index='concatenado',
                                      columns='NombreTienda',
                                      values='Existencia_Por_Tienda',
                                      aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    sucursal_cols = sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])

    resultado['Sucursal_Total'] = resultado[sucursal_cols].sum(axis=1)
    resultado['Porcentaje_Sucursales'] = ""

    columnas_ordenadas = CAMPOS_FIJOS + sucursal_cols + ['Sucursal_Total', 'Porcentaje_Sucursales']

    resultado = resultado[columnas_ordenadas]

    for col in sucursal_cols:
        resultado[col] = resultado[col].fillna(0)

    return resultado
