# components/filters.py
import streamlit as st

def filter_sidebar(df):
    """
    Aplica filtros de Marca y Región en la barra lateral.
    Si el DataFrame es None, está vacío o no tiene las columnas necesarias,
    retorna df sin modificar.
    """
    # Validación básica
    if df is None or df.empty:
        st.sidebar.warning("No hay datos disponibles para filtrar.")
        return df
    if 'NombreMarca' not in df.columns or 'Region' not in df.columns:
        return df

    # Construcción de filtros
    st.sidebar.header("Filtros")
    marcas = ["Todas"] + sorted(df["NombreMarca"].dropna().unique())
    marca_sel = st.sidebar.selectbox("Marca", marcas)
    if marca_sel != "Todas":
        df = df[df["NombreMarca"] == marca_sel]

    regiones = ["Todas"] + sorted(df["Region"].dropna().unique())
    region_sel = st.sidebar.selectbox("Región", regiones)
    if region_sel != "Todas":
        df = df[df["Region"] == region_sel]

    # Mostrar selección actual
    st.sidebar.markdown(f"**Marca:** {marca_sel} — **Región:** {region_sel}")
    print(f"Applied filters - Marca: {marca_sel}, Region: {region_sel}")
    return df