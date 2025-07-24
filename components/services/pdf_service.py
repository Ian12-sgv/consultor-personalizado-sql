# components/services/pdf_service.py

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os

def export_pdfs_por_sucursal(df_pivot, sucursales=None, output_dir="reportes_sucursales"):
    """
    Para cada sucursal en 'sucursales' (o todas si es None),
    genera un PDF con Concatenar y existencias.
    """
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()
    # determina la lista de columnas a exportar
    if sucursales is None:
        suc_list = [c for c in df_pivot.columns if "Sucursales" in c]
    else:
        suc_list = sucursales

    for suc in suc_list:
        fname = os.path.join(output_dir, f"{suc.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(fname, pagesize=letter)
        flow = [Paragraph(f"Existencias en <b>{suc}</b>", styles['Title']), Spacer(1,12)]
        data = [["Concatenar", suc]] + df_pivot[["Concatenar", suc]].values.tolist()
        tbl = Table(data, hAlign="LEFT")
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f6aa5")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN",      (1,1), (-1,-1), "RIGHT"),
        ]))
        flow.append(tbl)
        doc.build(flow)

    return output_dir
