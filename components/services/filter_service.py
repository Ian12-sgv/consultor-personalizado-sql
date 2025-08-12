# components/services/filter_service.py
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
    Aplica filtros al DataFrame sin romper si faltan columnas.

    Reglas:
    - Early return: si TODOS los filtros están "vacíos" (region en 'Todas' o vacío,
      marca vacía, referencia vacía, sin exclude_marcas, y solo_promo_1=False),
      devuelve el DataFrame tal cual (estado "sin cambios").
    - Región: sólo cuando opcion == "Solo Sucursales" y existe 'Region' (match exacto).
    - Marca: exacta si existe 'CodigoMarca'.
    - Referencia: exacta, case-insensitive, si existe 'Referencia'.
    - Excluir marcas: si existe 'CodigoMarca'.
    - Solo Promoción = 1: si existe 'Promocion'.
    """

    if df is None or df.empty:
        return df

    # Normalización de entradas
    ref = (str(referencia).strip() if referencia is not None else "")
    # Evita filtrar por el placeholder accidentalmente
    if ref.lower() == "referencia":
        ref = ""

    cleaned_excludes = [m.strip() for m in (exclude_marcas or []) if m and m.strip()]

    # --- Early return (sin filtros "reales") ---
    if ((not region or region == "Todas")
        and not marca
        and not ref
        and not cleaned_excludes
        and not solo_promo_1):
        return df

    out = df

    # -------------------------
    # Filtro por Región (sólo sucursales)
    # -------------------------
    if (
        opcion == "Solo Sucursales"
        and region
        and region != "Todas"
        and "Region" in out.columns
    ):
        out = out[out["Region"] == region]

    # -------------------------
    # Filtro por Marca exacta
    # -------------------------
    if marca and "CodigoMarca" in out.columns:
        out = out[out["CodigoMarca"].astype(str) == str(marca)]

    # -------------------------
    # Filtro por Referencia (exacto, case-insensitive)
    # -------------------------
    if ref and "Referencia" in out.columns:
        ref_norm = ref.lower()
        out = out[out["Referencia"].astype(str).str.strip().str.lower() == ref_norm]
    # Si no existe 'Referencia', se ignora silenciosamente.

    # -------------------------
    # Excluir Marcas
    # -------------------------
    if cleaned_excludes and "CodigoMarca" in out.columns:
        excluir = {m.upper() for m in cleaned_excludes}
        if excluir:
            out = out[~out["CodigoMarca"].astype(str).str.upper().isin(excluir)]

    # -------------------------
    # Solo Promoción = 1
    # -------------------------
    if solo_promo_1 and "Promocion" in out.columns:
        promo_num = pd.to_numeric(out["Promocion"], errors="coerce")
        out = out[promo_num.eq(1)]

    return out
