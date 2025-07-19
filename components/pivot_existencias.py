import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'NombreTienda', 'Existencia_Total']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    df_fijos = df[CAMPOS_FIJOS].drop_duplicates()

    # Crear columna única por tienda detallada
    df['NombreTiendaDetallado'] = df['Region'] + ' - ' + df['NombreTienda']

    # Pivot detallado por tienda y región combinadas
    df_pivot = df.pivot_table(index='concatenado',
                              columns='NombreTiendaDetallado',
                              values='Existencia_Total',
                              aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    # Separar columnas de casa matriz y sucursales
    casas_matriz_cols = [col for col in df_pivot.columns if 'Casa Matriz' in str(col)]
    sucursales_cols = [col for col in df_pivot.columns if 'Sucursales' in str(col)]

    casas_matriz_cols.sort()
    sucursales_cols.sort()

    # Calcular totales por fila
    resultado['Casa_matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)
    resultado['Sucursal_Total'] = resultado[sucursales_cols].sum(axis=1)
    resultado['Total_Existencia'] = resultado['Casa_matriz_Total'] + resultado['Sucursal_Total']

    # Calcular porcentajes
    resultado['Descuento_CasaMatriz'] = resultado.apply(
        lambda row: round((row['Casa_matriz_Total'] / row['Total_Existencia']) * 100, 2) if row['Total_Existencia'] > 0 else 0,
        axis=1
    )

    resultado['Descuento_Sucursales'] = resultado.apply(
        lambda row: round((row['Sucursal_Total'] / row['Total_Existencia']) * 100, 2) if row['Total_Existencia'] > 0 else 0,
        axis=1
    )

    # Formato %
    resultado['Descuento_CasaMatriz'] = resultado['Descuento_CasaMatriz'].astype(str) + '%'
    resultado['Descuento_Sucursales'] = resultado['Descuento_Sucursales'].astype(str) + '%'

    # Ordenar columnas
    columnas_ordenadas = (
    CAMPOS_FIJOS +
    casas_matriz_cols + sucursales_cols +
    ['Sucursal_Total','Casa_matriz_Total'] +
    ['Descuento_CasaMatriz', 'Descuento_Sucursales']
)


    resultado = resultado[columnas_ordenadas]

    # Reemplazar NaN por 0 en existencias
    for col in casas_matriz_cols + sucursales_cols:
        resultado[col] = resultado[col].fillna(0)

    return resultado
