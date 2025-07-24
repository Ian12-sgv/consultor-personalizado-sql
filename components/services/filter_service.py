# components/services/filter_service.py
import pandas as pd

EXCLUDE_CODES = {"GRD", "DNE", "DIE"}

def apply_filters(df: pd.DataFrame,
                  opcion: str,
                  region: str,
                  marca: str,
                  referencia: str,
                  excluir_codigos: bool = False,
                  solo_promo_1: bool = False) -> pd.DataFrame:
    """Aplica filtros comunes + promoción=1 si solo_promo_1=True."""

    if df is None or df.empty:
        return df

    # Región (solo sucursales)
    if opcion == "Solo Sucursales" and region and region != "Todas" and 'Region' in df.columns:
        df = df[df['Region'] == region]

    # Marca exacta
    if marca and 'CodigoMarca' in df.columns:
        df = df[df['CodigoMarca'].astype(str) == marca]

    # Referencia EXACTA (case-insensitive, sin espacios)
    if referencia and 'Referencia' in df.columns:
        ref_norm = str(referencia).strip().lower()
        df = df[df['Referencia'].astype(str).str.strip().str.lower() == ref_norm]

    # Excluir códigos
    if excluir_codigos and 'CodigoMarca' in df.columns:
        df = df[~df['CodigoMarca'].astype(str).str.upper().isin(EXCLUDE_CODES)]

    # Solo Promoción = 1
    if solo_promo_1 and 'Promocion' in df.columns:
        promo_num = pd.to_numeric(df['Promocion'], errors='coerce')
        df = df[promo_num.eq(1)]

    return df
