import pandas as pd
from typing import List, Optional


def apply_filters(
    df: pd.DataFrame,
    opcion: str,
    region: str,
    marca: str,
    referencia: str,
    exclude_marcas: Optional[List[str]] = None,
    solo_promo_1: bool = False
) -> pd.DataFrame:
    """
    Aplica filtros:
      - Filtra por región (solo sucursales si aplica).
      - Filtra por marca exacta.
      - Filtra por referencia exacta (sin distinción de mayúsculas/minúsculas).
      - Excluye las marcas listadas en exclude_marcas.
      - Filtra solo Promoción=1 si solo_promo_1=True.
    """

    if df is None or df.empty:
        return df

    # Región (solo sucursales)
    if opcion == "Solo Sucursales" and region and region != "Todas" and 'Region' in df.columns:
        df = df[df['Region'] == region]

    # Filtrar exacto por marca
    if marca and 'CodigoMarca' in df.columns:
        df = df[df['CodigoMarca'].astype(str) == marca]

    # Filtrar exacto por referencia (case-insensitive)
    if referencia and 'Referencia' in df.columns:
        ref_norm = str(referencia).strip().lower()
        df = df[df['Referencia'].astype(str).str.strip().str.lower() == ref_norm]

    # Excluir marcas personalizadas
    if exclude_marcas and 'CodigoMarca' in df.columns:
        # Normalizar a mayúsculas y sin espacios
        to_exclude = {m.strip().upper() for m in exclude_marcas if m.strip()}
        df = df[~df['CodigoMarca'].astype(str).str.upper().isin(to_exclude)]

    # Solo Promoción = 1
    if solo_promo_1 and 'Promocion' in df.columns:
        promo_num = pd.to_numeric(df['Promocion'], errors='coerce')
        df = df[promo_num.eq(1)]

    return df
