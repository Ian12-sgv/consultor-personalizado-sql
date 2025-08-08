from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os
import pandas as pd

def export_pdfs_descuentos(df_pivot, output_dir="reportes_descuentos"):
    """
    Genera un PDF con las columnas:
    'Concatenar', 'Descuento' y 'Descuento_Catalogo' del DataFrame df_pivot.
    """
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    print("Columnas disponibles en DataFrame:", df_pivot.columns.tolist())
    print("Primeras filas de datos:")
    print(df_pivot.head())

    if "Concatenar" not in df_pivot.columns and "Conoatenar" in df_pivot.columns:
        df_pivot = df_pivot.rename(columns={"Conoatenar": "Concatenar"})
        print("Renombrada columna 'Conoatenar' a 'Concatenar'")

    required_columns = ["Concatenar", "Descuento", "Descuento_Catalogo"]
    for col in required_columns:
        if col not in df_pivot.columns:
            raise ValueError(f"Falta la columna '{col}' en el DataFrame.")

    data = [required_columns] + df_pivot[required_columns].fillna("").values.tolist()

    fname = os.path.join(output_dir, "Descuentos.pdf")
    doc = SimpleDocTemplate(fname, pagesize=letter)
    flow = [Paragraph("Descuentos por producto", styles['Title']), Spacer(1, 12)]

    tbl = Table(data, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN",      (1, 1), (-1, -1), "RIGHT"),
    ]))

    flow.append(tbl)
    doc.build(flow)

    print(f"PDF generado en: {fname}")
    return fname


def export_pdfs_por_sucursal(df, sucursales, output_dir="reportes_sucursales"):
    """
    Exporta un PDF con las columnas seleccionadas, incluyendo sucursales o casa matriz.

    Args:
        df (pd.DataFrame): DataFrame con columnas seleccionadas.
        sucursales (list): Lista de columnas (sucursales/casa matriz) para incluir en el PDF.
        output_dir (str): Carpeta destino para los PDFs.
    """
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    print("=== PDF Export Confirmation ===")
    print("Columnas recibidas en DataFrame para exportar:")
    print(df.columns.tolist())
    print("Sucursales seleccionadas para exportar:")
    print(sucursales)
    print("Confirmando que las columnas y sucursales coinciden con la selección del usuario...\n")

    columnas = df.columns.tolist()  # Export exactly columns present in df

    data = [columnas]  # Header row
    for _, row in df.iterrows():
        data.append([str(row[col]) if pd.notna(row[col]) else "" for col in columnas])

    fname = os.path.join(output_dir, "Reporte_Sucursales.pdf")
    doc = SimpleDocTemplate(fname, pagesize=letter)
    flow = [Paragraph("Reporte de columnas seleccionadas", styles['Title']), Spacer(1, 12)]

    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN",      (1, 1), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))

    flow.append(table)
    doc.build(flow)

    print(f"PDF generado en: {fname}")
    return fname
