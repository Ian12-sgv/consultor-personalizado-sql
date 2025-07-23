import pandas as pd
import customtkinter as ctk
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from tkinter import messagebox
from utils.my_sql_detector import load_history

class InstanciaSQLModal(ctk.CTkToplevel):
    """
    Modal para capturar conexión a SQL Server dinámicamente,
    con historial, prellenado y botón Conectar.
    """
    def __init__(self, master, callback, instancia_default="", base_default="", usuario_default="", password_default=""):
        super().__init__(master)
        self.callback = callback
        self.title("Conexión a SQL Server")
        self.geometry("400x400")
        self.resizable(False, False)

        # Historial de instancias
        historial = load_history()
        instancia_values = []

        for item in historial:
            if isinstance(item, dict) and 'instance' in item:
                instancia_values.append(item['instance'])
            elif isinstance(item, str):
                instancia_values.append(item)

        if not instancia_values:
            instancia_values = [instancia_default] if instancia_default else ["SERVERSQL\\SQL"]

        # Widgets UI
        ctk.CTkLabel(self, text="Instancia SQL Server:").pack(pady=5)
        self.instancia_entry = ctk.CTkComboBox(self, values=instancia_values)
        self.instancia_entry.set(instancia_default or instancia_values[0])
        self.instancia_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Base de Datos:").pack(pady=5)
        self.base_entry = ctk.CTkEntry(self)
        self.base_entry.insert(0, base_default)
        self.base_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Usuario:").pack(pady=5)
        self.usuario_entry = ctk.CTkEntry(self)
        self.usuario_entry.insert(0, usuario_default)
        self.usuario_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Contraseña:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.insert(0, password_default)
        self.password_entry.pack(pady=5)

        # Botón conectar
        self.button_conectar = ctk.CTkButton(self, text="Conectar", command=self.enviar_datos)
        self.button_conectar.pack(pady=15)

    def enviar_datos(self):
        instancia = self.instancia_entry.get().strip()
        base = self.base_entry.get().strip()
        usuario = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()

        if not instancia or not base or not usuario or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        self.callback(instancia, base, usuario, password)
        self.destroy()


def cargar_excel_a_sql_dinamico(file_path, instancia, base, usuario, password, tabla_destino):
    """
    Carga un Excel a SQL Server en una tabla existente, limpiando basura y garantizando calidad de datos.
    """
    try:
        # Leer el Excel completo sin usecols ni skiprows para evitar perder datos
        df = pd.read_excel(file_path)

        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.upper()

        # Verificar que estén las columnas necesarias
        columnas_validas = ["CONCATENAR", "% DESCUENTO"]
        if not set(columnas_validas).issubset(set(df.columns)):
            raise ValueError(f"El Excel debe tener las columnas: {columnas_validas}")

        # Renombrar columnas
        df = df[["CONCATENAR", "% DESCUENTO"]]
        df.columns = ["Concatenar", "Descuento"]

        # Limpiar datos
        df["Concatenar"] = df["Concatenar"].astype(str).str.strip()
        df["Descuento"] = df["Descuento"].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and not pd.isna(x) else str(x)).str.strip()

        # Eliminar filas basura o comentarios
        basura = ["CREACION", "FECHA", "MARGARITA", "VALENCIA", "MARACAIBO", "NAN", ""]
        df = df[~df["Concatenar"].str.upper().isin(basura)]

        # Eliminar filas con valores nulos o vacíos
        df = df.dropna(subset=["Concatenar", "Descuento"])
        df = df[df["Concatenar"] != ""]

        # Eliminar duplicados
        df = df.drop_duplicates(subset=["Concatenar"])

        if df.empty:
            messagebox.showerror("Error", "El Excel no tiene datos válidos para cargar.")
            return

        # Conexión a SQL Server
        password_enc = quote_plus(password)
        conn_str = f"mssql+pyodbc://{usuario}:{password_enc}@{instancia}/{base}?driver=SQL+Server"
        engine = create_engine(conn_str, fast_executemany=True)

        with engine.begin() as conn:
            # Vaciar tabla sin eliminar la estructura
            conn.execute(text(f"TRUNCATE TABLE {tabla_destino};"))

            # Insertar datos
            data = df.to_dict(orient="records")
            insert_sql = text(f"""
                INSERT INTO {tabla_destino} (Concatenar, Descuento)
                VALUES (:Concatenar, :Descuento)
            """)
            conn.execute(insert_sql, data)

        messagebox.showinfo("Éxito", f"Se cargó el Excel a {base}.{tabla_destino}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el Excel a SQL Server:\n{e}")
