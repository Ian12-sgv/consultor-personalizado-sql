# components/filters.py
import streamlit as st
import pandas as pd

# --- Helpers cacheados --------------------------------------------------------
@st.cache_data(show_spinner=False)
def _unique_sorted(series: pd.Series):
    return ["Todas"] + sorted(series.dropna().unique().tolist())

@st.cache_data(show_spinner=False)
def _ensure_ref_lower(df: pd.DataFrame):
    if "Referencia" not in df.columns:
        return None
    return df["Referencia"].astype(str).str.lower()

# ------------------------------------------------------------------------------

EXCLUDE_CODES = {"GRD", "DNE", "DIE"}  # códigos a excluir cuando el check esté activo

def filter_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtros de Marca, Región, Referencia y un check para excluir ciertos códigos de marca.
    """
    if df is None or df.empty:
        st.sidebar.warning("No hay datos disponibles para filtrar.")
        return df

    if not {'NombreMarca', 'Region'}.issubset(df.columns):
        return df

    st.sidebar.header("Filtros")

    # Listas cacheadas
    marcas   = _unique_sorted(df["NombreMarca"])
    regiones = _unique_sorted(df["Region"])
    ref_low  = _ensure_ref_lower(df)

    # Widgets
    marca_sel  = st.sidebar.selectbox("Marca",   marcas,   index=0)
    region_sel = st.sidebar.selectbox("Región",  regiones, index=0)

    ref_text = ""
    if ref_low is not None:
        ref_text = st.sidebar.text_input("Referencia (contiene)", value="", placeholder="Ej: 160PFR").strip().lower()

    excluir_codigos = False
    if "CodigoMarca" in df.columns:
        excluir_codigos = st.sidebar.checkbox("Excluir códigos GRD / DNE / DIE", value=False)

    # Máscara
    mask = pd.Series(True, index=df.index)

    if marca_sel != "Todas":
        mask &= (df["NombreMarca"] == marca_sel)

    if region_sel != "Todas":
        mask &= (df["Region"] == region_sel)

    if ref_low is not None and ref_text:
        mask &= ref_low.str.contains(ref_text, na=False)

    if excluir_codigos and "CodigoMarca" in df.columns:
        mask &= ~df["CodigoMarca"].astype(str).str.upper().isin(EXCLUDE_CODES)

    df_filtrado = df[mask]

    # Resumen
    resumen = f"**Marca:** {marca_sel} — **Región:** {region_sel}"
    if ref_text:
        resumen += f" — **Ref:** '{ref_text}'"
    if excluir_codigos:
        resumen += " — **Excluyendo GRD/DNE/DIE**"
    st.sidebar.markdown(resumen)

    return df_filtrado
