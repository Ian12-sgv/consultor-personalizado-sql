import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'NombreTienda', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    df_fijos = df[CAMPOS_FIJOS].drop_duplicates()

    # Crear columna única por tienda detallada
    df['NombreTiendaDetallado'] = df['Region'] + ' - ' + df['NombreTienda']

    # Pivot detallado por tienda y región combinadas
    df_pivot = df.pivot_table(index='concatenado',
                              columns='NombreTiendaDetallado',
                              values='Existencia_Por_Tienda',
                              aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    # Separar columnas de casa matriz y sucursales
    casas_matriz_cols = [col for col in df_pivot.columns if 'Casa Matriz' in str(col)]
    sucursales_cols = [col for col in df_pivot.columns if 'Sucursales' in str(col)]

    casas_matriz_cols.sort()
    sucursales_cols.sort()

    # Calcular totales por fila
    resultado['Casa_Matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)
    resultado['Sucursal_Total'] = resultado[sucursales_cols].sum(axis=1)
    resultado['Total_Existencia'] = resultado['Casa_Matriz_Total'] + resultado['Sucursal_Total']

    # Calcular porcentajes
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

    # Ordenar columnas
    columnas_ordenadas = (
        CAMPOS_FIJOS +
        casas_matriz_cols + ['Casa_Matriz_Total', 'Porcentaje_CasaMatriz'] +
        sucursales_cols + ['Sucursal_Total', 'Porcentaje_Sucursales']
    )

    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0 en existencias
    for col in casas_matriz_cols + sucursales_cols:
        resultado[col] = resultado[col].fillna(0)

    return resultado
