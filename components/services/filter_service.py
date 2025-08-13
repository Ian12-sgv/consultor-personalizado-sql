# components/services/filter_service.py
import pandas as pd
from typing import List, Optional


def _find_col_case_insensitive(df: pd.DataFrame, candidates_lower: List[str]) -> Optional[str]:
    """
    Devuelve el nombre REAL de la primera columna cuyo nombre (lower) coincide
    con alguno de los candidates_lower. Si no encuentra, retorna None.
    """
    cols_lower = df.columns.str.strip().str.lower()
    for idx, real_name in enumerate(df.columns):
        if cols_lower[idx] in candidates_lower:
            return real_name
    return None


def apply_filters(
    df: pd.DataFrame,
    opcion: str,
    region: str,
    marca: str,
    referencia: str,
    exclude_marcas: Optional[List[str]] = None,
    solo_promo_1: bool = False,
    exclude_sublineas: Optional[List[str]] = None,  # <--- NUEVO parámetro
) -> pd.DataFrame:
    """
    Aplica filtros al DataFrame sin romper si faltan columnas.

    Reglas:
    - Early return: si TODOS los filtros están "vacíos" (region en 'Todas' o vacío,
      marca vacía, referencia vacía, sin exclude_marcas, sin exclude_sublineas
      y solo_promo_1=False), devuelve el DataFrame tal cual (estado "sin cambios").
    - Región: sólo cuando opcion == "Solo Sucursales" y existe 'Region' (match exacto).
    - Marca: exacta si existe 'CodigoMarca'.
    - Referencia: exacta, case-insensitive, si existe 'Referencia'.
    - Excluir marcas: si existe 'CodigoMarca'.
    - Excluir sublíneas: si existe la columna de sublínea (CodigoSubLinea/CodSubLinea/SubLinea).
    - Solo Promoción = 1: si existe 'Promocion'.
    """
    if df is None or df.empty:
        return df

    # Normalización de entradas
    ref = (str(referencia).strip() if referencia is not None else "")
    if ref.lower() == "referencia":  # evita filtrar por placeholder
        ref = ""

    cleaned_excludes_marcas = [m.strip() for m in (exclude_marcas or []) if m and m.strip()]
    cleaned_excludes_subs   = [s.strip() for s in (exclude_sublineas or []) if s and s.strip()]

    # --- Early return (sin filtros "reales") ---
    if ((not region or region == "Todas")
        and not marca
        and not ref
        and not cleaned_excludes_marcas
        and not cleaned_excludes_subs
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
    # Si no existe 'Referencia', se ignora.

    # -------------------------
    # Excluir Marcas
    # -------------------------
    if cleaned_excludes_marcas and "CodigoMarca" in out.columns:
        excluir_m = {m.upper() for m in cleaned_excludes_marcas}
        if excluir_m:
            out = out[~out["CodigoMarca"].astype(str).str.upper().isin(excluir_m)]

    # -------------------------
    # Excluir Sublíneas (flexible en nombre de columna)
    # -------------------------
    if cleaned_excludes_subs:
        # Buscar columna candidata de sublínea de forma case-insensitive
        cand_lower = {"codigosublinea", "codsublinea", "sublinea", "codigo_sublinea"}
        sub_col = _find_col_case_insensitive(out, list(cand_lower))
        if sub_col is not None:
            excluir_s = {s.upper() for s in cleaned_excludes_subs}
            out = out[~out[sub_col].astype(str).str.upper().isin(excluir_s)]
        # Si no hay columna compatible, se ignora silenciosamente.

    # -------------------------
    # Solo Promoción = 1
    # -------------------------
    if solo_promo_1 and "Promocion" in out.columns:
        promo_num = pd.to_numeric(out["Promocion"], errors="coerce")
        out = out[promo_num.eq(1)]

    return out
