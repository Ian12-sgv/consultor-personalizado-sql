import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
from tabulate import tabulate

def detectar_fila_encabezado(df_raw):
    print("🔍 Buscando fila de encabezado...")
    for i, fila in df_raw.iterrows():
        fila_str = fila.astype(str).str.strip().str.lower()
        if any("concatenar" in celda for celda in fila_str) and any("descuento" in celda for celda in fila_str):
            print(f"✅ Encabezado encontrado en fila {i + 1}")
            return i
    print("❌ No se encontró fila con encabezados esperados.")
    return None

def seleccionar_fila_gui(df_preview):
    selector = tk.Toplevel()
    selector.title("Seleccionar fila de encabezado")
    selector.geometry("450x130")
    selector.attributes("-topmost", True)

    tk.Label(selector, text="Selecciona manualmente la fila donde están los encabezados:").pack(padx=10, pady=5)

    fila_var = tk.StringVar()
    opciones = [str(i + 1) for i in df_preview.index[:50]]
    combo = ttk.Combobox(selector, textvariable=fila_var, values=opciones, state="readonly", width=10)
    combo.pack(padx=10, pady=5)
    combo.current(0)

    def confirmar():
        selector.selected_row = int(fila_var.get()) - 1
        selector.destroy()

    tk.Button(selector, text="Aceptar", command=confirmar).pack(pady=10)
    selector.grab_set()
    selector.wait_window()

    return getattr(selector, "selected_row", None)

def seleccionar_hoja_gui(hojas):
    selector = tk.Toplevel()
    selector.title("Seleccionar hoja")
    selector.geometry("400x130")
    selector.attributes("-topmost", True)

    tk.Label(selector, text="Selecciona una hoja:").pack(padx=10, pady=5)

    hoja_var = tk.StringVar()
    combo = ttk.Combobox(selector, textvariable=hoja_var, values=hojas, state="readonly", width=50)
    combo.pack(padx=10, pady=5)
    combo.current(0)

    def confirmar():
        selector.selected_sheet = hoja_var.get()
        selector.destroy()

    tk.Button(selector, text="Aceptar", command=confirmar).pack(pady=10)
    selector.grab_set()
    selector.wait_window()

    return getattr(selector, "selected_sheet", None)

# Iniciar ventana raíz (solo una vez)
root = tk.Tk()
root.withdraw()

print("📂 Selecciona un archivo...")
ruta_archivo = filedialog.askopenfilename(
    title="Selecciona un archivo Excel",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)

if ruta_archivo:
    try:
        print(f"\n📁 Archivo seleccionado: {ruta_archivo}")

        # Obtener lista de hojas
        hojas = pd.ExcelFile(ruta_archivo).sheet_names
        print("\n🗂 Hojas disponibles:")
        for hoja in hojas:
            print(f"- {hoja}")

        # Seleccionar hoja desde GUI
        hoja = seleccionar_hoja_gui(hojas)

        if not hoja:
            print("❌ No se seleccionó ninguna hoja.")
            exit()

        print(f"\n📝 Hoja seleccionada: {hoja}")

        # Leer primeras 50 filas sin encabezado
        df_raw = pd.read_excel(ruta_archivo, sheet_name=hoja, header=None, nrows=50)

        fila_encabezado = detectar_fila_encabezado(df_raw)

        if fila_encabezado is None:
            print("\n🧐 Vista previa del archivo (primeras 20 filas):")
            print(tabulate(df_raw.fillna("").astype(str).head(20), headers="keys", tablefmt="pretty"))
            fila_encabezado = seleccionar_fila_gui(df_raw)

        if fila_encabezado is not None:
            print(f"\n📊 Leyendo datos definitivos desde fila {fila_encabezado + 1} como encabezado...")
            df = pd.read_excel(ruta_archivo, sheet_name=hoja, header=fila_encabezado, usecols="A,G")

            print("\n✅ Columnas seleccionadas:")
            print(df.columns.tolist())

            print("\n🔹 Primeras 10 filas:")
            print(df.head(10))
        else:
            print("❌ No se pudo determinar la fila del encabezado.")
    except Exception as e:
        print("❌ Error al procesar el archivo:")
        print(str(e))
else:
    print("❌ No se seleccionó archivo.")
