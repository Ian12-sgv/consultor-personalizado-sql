import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias_casa_matriz(df, total_casa_matriz_global=None):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'Existencia_Total']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    matriz = df[df['Region'].str.contains('Casa Matriz')]

    if matriz.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = matriz[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = matriz.pivot_table(index='Concatenar',
                                  columns='Region',
                                  values='Existencia_Total',
                                  aggfunc='sum').reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='Concatenar', how='left')

    casas_matriz_cols = sorted([col for col in resultado.columns if col not in CAMPOS_FIJOS and col != 'Concatenar'])

    resultado['Casa_matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)

    total_general = total_casa_matriz_global if total_casa_matriz_global is not None else resultado['Casa_matriz_Total'].sum()

    resultado['Descuento_CasaMatriz'] = resultado['Casa_matriz_Total'].apply(
        lambda x: round((x / total_general) * 100, 2) if total_general > 0 else 0
    ).astype(str) + '%'

    columnas_ordenadas = CAMPOS_FIJOS + casas_matriz_cols + ['Casa_matriz_Total', 'Descuento_CasaMatriz']

    resultado = resultado[columnas_ordenadas]

    for col in casas_matriz_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Casa_matriz_Total'] = resultado['Casa_matriz_Total'].fillna(0)

    return resultado
