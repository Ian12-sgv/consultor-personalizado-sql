from tkinter import filedialog, messagebox

def exportar_dataframe_a_excel(df):
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
            messagebox.showinfo("Exportación", f"Datos exportados correctamente a {ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {e}")
