import os
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def exportar_dataframe_a_excel(df):
    """
    Guarda el DataFrame completo en un archivo .xlsx.
    """
    if df is None or df.empty:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
        return

    try:
        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar como"
        )
        if ruta:
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Exportación", f"Datos exportados correctamente a:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{e}")


def export_pdfs_por_sucursal(df, selected_columns):
    """
    Exporta un solo PDF con todas las columnas seleccionadas por el usuario.

    Args:
        df (pd.DataFrame): DataFrame con los datos completos.
        selected_columns (list): Lista con las columnas que el usuario seleccionó para exportar.
    """
    if df is None or df.empty:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
        return

    carpeta = filedialog.askdirectory(title="Selecciona carpeta para guardar PDF")
    if not carpeta:
        messagebox.showwarning("Exportación cancelada", "No se seleccionó carpeta para guardar PDF.")
        return

    styles = getSampleStyleSheet()
    data = [selected_columns]  # encabezados

    for _, row in df[selected_columns].iterrows():
        fila = [str(row[col]) if row[col] is not None else "" for col in selected_columns]
        data.append(fila)

    nombre_pdf = "Reporte_Seleccionado.pdf"
    ruta_pdf = os.path.join(carpeta, nombre_pdf)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
    flow = [Paragraph("Reporte PDF - Columnas seleccionadas", styles['Title']), Spacer(1, 12)]

    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    flow.append(table)
    doc.build(flow)

    messagebox.showinfo("Exportación PDF", f"PDF generado correctamente en:\n{ruta_pdf}")
    return ruta_pdf
