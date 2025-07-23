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
    """Aplica filtros comunes + promocion=1 si solo_promo_1=True."""

    if opcion == "Solo Sucursales" and region and region != "Todas" and 'Region' in df.columns:
        df = df[df['Region'] == region]

    if marca and 'CodigoMarca' in df.columns:
        df = df[df['CodigoMarca'].astype(str) == marca]

    if referencia and 'Referencia' in df.columns:
        df = df[df['Referencia'].astype(str).str.contains(referencia, case=False, na=False)]

    if excluir_codigos and 'CodigoMarca' in df.columns:
        df = df[~df['CodigoMarca'].astype(str).str.upper().isin(EXCLUDE_CODES)]

    if solo_promo_1 and 'Promocion' in df.columns:
        df = df[df['Promocion'].astype(str).str.strip() == "1"]

    return df
