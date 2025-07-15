# components/data_transformer.py

import pandas as pd

def pivot_existencias(df):
    """
    Transforma el dataframe largo a formato ancho: Referencia vs Casa Matriz y Sucursales.
    """

    # Tomamos las columnas necesarias
    columnas = ['Referencia', 'Existencia_CasaMatriz', 'Existencia_Sucursales']

    # Verifica si las columnas existen para evitar errores
    for col in columnas:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    # Genera el nuevo dataframe
    df_pivot = df[columnas].drop_duplicates()

    # Renombrar para visualización limpia (opcional)
    df_pivot = df_pivot.rename(columns={
        'Existencia_CasaMatriz': 'Casa Matriz',
        'Existencia_Sucursales': 'Sucursales'
    })

    return df_pivot
