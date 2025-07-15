# components/data_transformer.py

import pandas as pd

def pivot_existencias(df):
    """
    Pivot completo: Casa Matriz y Sucursales como columnas separadas (por región).
    """
    columnas_necesarias = ['Referencia', 'Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    df_pivot = df.pivot_table(index='Referencia',
                              columns='Region',
                              values='Existencia_Por_Tienda',
                              aggfunc='sum').reset_index()

    columnas = ['Referencia'] + sorted([col for col in df_pivot.columns if col != 'Referencia'])
    df_pivot = df_pivot[columnas]
    return df_pivot

def pivot_existencias_sucursales_detallado(df):
    """
    Pivot con todas las sucursales detalladas por tienda (sin agrupar).
    """
    columnas_necesarias = ['Referencia', 'Region', 'NombreTienda', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    sucursales = df[df['Region'].str.contains('Sucursales')]

    if sucursales.empty:
        raise ValueError("No hay datos de sucursales en el dataframe.")

    df_pivot = sucursales.pivot_table(index='Referencia',
                                      columns='NombreTienda',
                                      values='Existencia_Por_Tienda',
                                      aggfunc='sum').reset_index()

    columnas = ['Referencia'] + sorted([col for col in df_pivot.columns if col != 'Referencia'])
    df_pivot = df_pivot[columnas]
    return df_pivot

def pivot_existencias_casa_matriz(df):
    """
    Solo Casa Matriz como columnas (por región).
    """
    columnas_necesarias = ['Referencia', 'Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    matriz = df[df['Region'].str.contains('Casa Matriz')]

    if matriz.empty:
        raise ValueError("No hay datos de Casa Matriz en el dataframe.")

    df_pivot = matriz.pivot_table(index='Referencia',
                                  columns='Region',
                                  values='Existencia_Por_Tienda',
                                  aggfunc='sum').reset_index()

    columnas = ['Referencia'] + sorted([col for col in df_pivot.columns if col != 'Referencia'])
    df_pivot = df_pivot[columnas]
    return df_pivot
