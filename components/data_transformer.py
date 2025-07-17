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

    casas_matriz_cols = [col for col in df_pivot.columns if 'Casa Matriz' in str(col)]
    sucursales_cols = [col for col in df_pivot.columns if 'Sucursales' in str(col)]

    casas_matriz_cols.sort()
    sucursales_cols.sort()

    # Totales por fila (referencia)
    resultado['Casa_Matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)
    resultado['Sucursal_Total'] = resultado[sucursales_cols].sum(axis=1)
    resultado['Total_Existencia'] = resultado['Casa_Matriz_Total'] + resultado['Sucursal_Total']

    # Porcentajes por fila
    resultado['Porcentaje_CasaMatriz'] = resultado.apply(
        lambda row: round((row['Casa_Matriz_Total'] / row['Total_Existencia']) * 100, 2) if row['Total_Existencia'] > 0 else 0,
        axis=1
    )

    resultado['Porcentaje_Sucursales'] = resultado.apply(
        lambda row: round((row['Sucursal_Total'] / row['Total_Existencia']) * 100, 2) if row['Total_Existencia'] > 0 else 0,
        axis=1
    )

    # Formato %
    resultado['Porcentaje_CasaMatriz'] = resultado['Porcentaje_CasaMatriz'].astype(str) + '%'
    resultado['Porcentaje_Sucursales'] = resultado['Porcentaje_Sucursales'].astype(str) + '%'

    columnas_ordenadas = (
        CAMPOS_FIJOS +
        casas_matriz_cols + ['Casa_Matriz_Total', 'Porcentaje_CasaMatriz'] +
        sucursales_cols + ['Sucursal_Total', 'Porcentaje_Sucursales']
    )

    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0 en existencias
    for col in casas_matriz_cols + sucursales_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Casa_Matriz_Total'] = resultado['Casa_Matriz_Total'].fillna(0)
    resultado['Sucursal_Total'] = resultado['Sucursal_Total'].fillna(0)

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

    sucursal_cols = sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])

    resultado['Sucursal_Total'] = resultado[sucursal_cols].sum(axis=1)
    resultado['Porcentaje_Sucursales'] = ""

    columnas_ordenadas = CAMPOS_FIJOS + sucursal_cols + ['Sucursal_Total', 'Porcentaje_Sucursales']

    resultado = resultado[columnas_ordenadas]

    for col in sucursal_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Sucursal_Total'] = resultado['Sucursal_Total'].fillna(0)

    return resultado

def pivot_existencias_casa_matriz(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    # Filtrar solo Casa Matriz
    matriz = df[df['Region'].str.contains('Casa Matriz')]

    if matriz.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = matriz[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = matriz.pivot_table(index='concatenado',
                                  columns='Region',
                                  values='Existencia_Por_Tienda',
                                  aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    casas_matriz_cols = sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'concatenado'])

    # Calcular Casa_Matriz_Total sumando las casas matriz por fila
    resultado['Casa_Matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)

    # Filtrar solo las filas donde haya al menos una existencia en Casa Matriz
    resultado = resultado[resultado['Casa_Matriz_Total'] > 0].copy()

    # Calcular total general de Casa Matriz solo con los visibles
    total_general = resultado['Casa_Matriz_Total'].sum()

    if total_general > 0:
        resultado['Porcentaje_CasaMatriz'] = resultado['Casa_Matriz_Total'].apply(
            lambda x: round((x / total_general) * 100, 2)
        ).astype(str) + '%'
    else:
        resultado['Porcentaje_CasaMatriz'] = '0%'

    columnas_ordenadas = CAMPOS_FIJOS + casas_matriz_cols + ['Casa_Matriz_Total', 'Porcentaje_CasaMatriz']

    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0 en existencias
    for col in casas_matriz_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Casa_Matriz_Total'] = resultado['Casa_Matriz_Total'].fillna(0)

    return resultado





