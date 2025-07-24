# components/exporter.py

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


def export_pdfs_por_sucursal(df, sucursales):
    """
    Genera un PDF por cada sucursal seleccionada. Cada PDF contendrá:
     - Un título con el nombre de la sucursal.
     - Una tabla con las columnas 'Concatenar' y la columna de existencia de esa sucursal.
    Devuelve la ruta de la carpeta donde se guardaron los archivos.
    """
    # Pedir carpeta destino
    carpeta = filedialog.askdirectory(title="Selecciona carpeta para guardar PDFs")
    if not carpeta:
        raise RuntimeError("Exportación cancelada por el usuario.")

    styles = getSampleStyleSheet()
    for suc in sucursales:
        # Nombre de archivo amigable
        nombre_pdf = f"{suc.replace(' ', '_').replace('/', '_')}.pdf"
        ruta_pdf = os.path.join(carpeta, nombre_pdf)

        # Crear documento en horizontal
        doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(letter),
                                title=f"Existencias en {suc}")
        elements = []

        # Título
        titulo = Paragraph(f"Existencias en {suc}", styles["Heading1"])
        elements.append(titulo)
        elements.append(Spacer(1, 12))

        # Construir tabla: encabezados + filas
        tabla_data = [["Concatenar", suc]]
        # Agregar filas
        for _, row in df.iterrows():
            tabla_data.append([row.get("Concatenar", ""), row.get(suc, 0)])

        # Definir estilo de la tabla
        table = Table(tabla_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6aa5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        elements.append(table)

        # Guardar PDF
        doc.build(elements)

    return carpeta
