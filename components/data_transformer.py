import pandas as pd

CAMPOS_FIJOS = [
    'concatenado', 'Referencia', 'CodigoMarca', 'NombreMarca',
    'Nombre', 'Fabricante', 'NombreSubLinea', 'NombreCategoria', 'PorcentajeDescuento'
]

def pivot_existencias(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    df_fijos = df[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = df.pivot_table(index='concatenado',
                              columns='Region',
                              values='Existencia_Por_Tienda',
                              aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    columnas_ordenadas = CAMPOS_FIJOS + sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])
    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0
    resultado = resultado.fillna(0)

    return resultado

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

    columnas_ordenadas = CAMPOS_FIJOS + sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])
    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0
    resultado = resultado.fillna(0)

    return resultado

def pivot_existencias_casa_matriz(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    matriz = df[df['Region'].str.contains('Casa Matriz')]

    if matriz.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = matriz[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = matriz.pivot_table(index='concatenado',
                                  columns='Region',
                                  values='Existencia_Por_Tienda',
                                  aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    columnas_ordenadas = CAMPOS_FIJOS + sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])
    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0
    resultado = resultado.fillna(0)

    return resultado
