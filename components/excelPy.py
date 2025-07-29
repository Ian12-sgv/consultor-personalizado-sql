# excelPy.py modificado para integración

import pandas as pd
import customtkinter as ctk
from tkinter import filedialog
from tabulate import tabulate

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def detectar_fila_encabezado(df_raw):
    for i, fila in df_raw.iterrows():
        fila_str = fila.astype(str).str.strip().str.lower()
        if any("concatenar" in celda for celda in fila_str) and any("descuento" in celda for celda in fila_str):
            return i
    return None

def seleccionar_fila_gui(df_preview):
    selector = ctk.CTkToplevel()
    selector.title("Seleccionar fila de encabezado")
    selector.geometry("450x130")
    selector.attributes("-topmost", True)

    label = ctk.CTkLabel(selector, text="Selecciona manualmente la fila donde están los encabezados:")
    label.pack(padx=10, pady=5)

    fila_var = ctk.StringVar()
    opciones = [str(i + 1) for i in df_preview.index[:50]]
    combo = ctk.CTkComboBox(selector, values=opciones, variable=fila_var, width=100)
    combo.pack(padx=10, pady=5)
    combo.set(opciones[0])

    def confirmar():
        selector.selected_row = int(fila_var.get()) - 1
        selector.destroy()

    btn_aceptar = ctk.CTkButton(selector, text="Aceptar", command=confirmar)
    btn_aceptar.pack(pady=10)

    selector.grab_set()
    selector.wait_window()

    return getattr(selector, "selected_row", None)

def seleccionar_hoja_gui(hojas):
    selector = ctk.CTkToplevel()
    selector.title("Seleccionar hoja")
    selector.geometry("400x130")
    selector.attributes("-topmost", True)

    label = ctk.CTkLabel(selector, text="Selecciona una hoja:")
    label.pack(padx=10, pady=5)

    hoja_var = ctk.StringVar()
    combo = ctk.CTkComboBox(selector, values=hojas, variable=hoja_var, width=300)
    combo.pack(padx=10, pady=5)
    combo.set(hojas[0])

    def confirmar():
        selector.selected_sheet = hoja_var.get()
        selector.destroy()

    btn_aceptar = ctk.CTkButton(selector, text="Aceptar", command=confirmar)
    btn_aceptar.pack(pady=10)

    selector.grab_set()
    selector.wait_window()

    return getattr(selector, "selected_sheet", None)

def run_excelPy():
    root = ctk.CTk()
    root.withdraw()

    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona un archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not ruta_archivo:
        root.destroy()
        return None

    try:
        hojas = pd.ExcelFile(ruta_archivo).sheet_names
        hoja = seleccionar_hoja_gui(hojas)
        if not hoja:
            root.destroy()
            return None

        df_raw = pd.read_excel(ruta_archivo, sheet_name=hoja, header=None, nrows=50)
        fila_encabezado = detectar_fila_encabezado(df_raw)
        if fila_encabezado is None:
            fila_encabezado = seleccionar_fila_gui(df_raw)

        if fila_encabezado is not None:
            df_full = pd.read_excel(ruta_archivo, sheet_name=hoja, header=fila_encabezado)
            columnas_esperadas = [col for col in df_full.columns if "concatenar" in str(col).lower() or "descuento" in str(col).lower()]
            if len(columnas_esperadas) >= 2:
                df = df_full[columnas_esperadas[:2]]
            else:
                df = df_full.iloc[:, [0, 6]]
            root.destroy()
            return df
        else:
            root.destroy()
            return None
    except Exception as e:
        root.destroy()
        print("Error al procesar el archivo:", e)
        return None

if __name__ == "__main__":
    df = run_excelPy()
    if df is not None:
        print("Dataframe resultante:")
        print(df)
