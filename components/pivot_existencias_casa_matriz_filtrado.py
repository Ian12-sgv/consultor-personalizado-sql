import pandas as pd
from components.campofijos import CAMPOS_FIJOS

def pivot_existencias_casa_matriz_filtrado(df):
    columnas_necesarias = CAMPOS_FIJOS + ['Region', 'Existencia_Por_Tienda']
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en el dataframe")

    matriz = df[df['Region'].str.contains('Casa Matriz', na=False)]

    if matriz.empty:
        return pd.DataFrame(columns=CAMPOS_FIJOS + ['Sin datos'])

    df_fijos = matriz[CAMPOS_FIJOS].drop_duplicates()

    df_pivot = matriz.pivot_table(
        index='concatenado',
        columns='Region',
        values='Existencia_Por_Tienda',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    resultado = pd.merge(df_fijos, df_pivot, on='concatenado', how='left')

    casas_matriz_cols = [col for col in df_pivot.columns if col != 'concatenado']
    casas_matriz_cols.sort()

    for col in casas_matriz_cols:
        resultado[col] = resultado[col].fillna(0)

    resultado['Casa_Matriz_Total'] = resultado[casas_matriz_cols].sum(axis=1)

    # 🔥 Calcula el total de TODAS las casa matriz sin filtrar
    total_global_casa_matriz = resultado['Casa_Matriz_Total'].sum()

    # Calcula el porcentaje sobre el total global (aunque después filtres)
    resultado['Porcentaje_CasaMatriz'] = resultado['Casa_Matriz_Total'].apply(
        lambda x: round((x / total_global_casa_matriz) * 100, 2) if total_global_casa_matriz > 0 else 0
    ).astype(str) + '%'

    # Ahora sí, filtras los que tienen existencia > 0
    resultado = resultado[resultado['Casa_Matriz_Total'] > 0].copy()

    columnas_ordenadas = CAMPOS_FIJOS + casas_matriz_cols + ['Casa_Matriz_Total', 'Porcentaje_CasaMatriz']

    resultado = resultado[columnas_ordenadas]

    return resultado
