import os
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter, landscape
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


def export_pdfs_por_sucursal(df, selected_columns, nombre_archivo=None):
    """
    Exporta un solo PDF con todas las columnas seleccionadas por el usuario.

    Args:
        df (pd.DataFrame): DataFrame con los datos completos.
        selected_columns (list): Lista con las columnas que el usuario seleccionó para exportar.
        nombre_archivo (str, optional): Nombre sugerido para el archivo PDF. Si no se pasa, se usará diálogo para pedir ruta.
    """
    if df is None or df.empty:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
        return

    if nombre_archivo:
        carpeta = filedialog.askdirectory(title="Selecciona carpeta para guardar PDF")
        if not carpeta:
            messagebox.showwarning("Exportación cancelada", "No se seleccionó carpeta para guardar PDF.")
            return
        ruta_pdf = os.path.join(carpeta, nombre_archivo)
    else:
        ruta_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar PDF como"
        )
        if not ruta_pdf:
            messagebox.showwarning("Exportación cancelada", "No se seleccionó archivo para guardar PDF.")
            return

    print("=== Exportador: columnas para exportar ===")
    print(selected_columns)
    print("Primeras filas de datos:")
    print(df[selected_columns].head())

    styles = getSampleStyleSheet()
    data = [selected_columns]  # encabezados

    for _, row in df[selected_columns].iterrows():
        fila = [str(row[col]) if row[col] is not None else "" for col in selected_columns]
        data.append(fila)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(letter))
    flow = [Paragraph("Reporte PDF - Columnas seleccionadas", styles['Title']), Spacer(1, 12)]

    table = Table(data, hAlign="LEFT")

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    flow.append(table)
    doc.build(flow)

    messagebox.showinfo("Exportación PDF", f"PDF generado correctamente en:\n{ruta_pdf}")
    return ruta_pdf
