# view/conection_view.py

import customtkinter as ctk
from utils.db_utils import ConnectionManager
from utils.my_sql_detector import load_history
from tkinter import messagebox

# Importar InicioView para redirección
from view.inicio_view import InicioView

class ConnectionView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Conexión SQL - Instancia y Base")
        self.geometry("400x400")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.conn_manager = ConnectionManager()

        # Cargar historial de instancias
        historial = load_history()
        instancia_values = []

        for item in historial:
            if isinstance(item, dict) and 'instance' in item:
                instancia_values.append(item['instance'])
            elif isinstance(item, str):
                instancia_values.append(item)

        if not instancia_values:
            instancia_values = ["SERVERDOS\\SERVERSQL_DOS"]

        # UI: solo ComboBox
        self.label_instancia = ctk.CTkLabel(self, text="Instancia SQL Server:")
        self.label_instancia.pack(pady=5)

        self.combo_instancias = ctk.CTkComboBox(self, values=instancia_values)
        self.combo_instancias.set(instancia_values[0])
        self.combo_instancias.pack(pady=5)

        # Usuario y contraseña
        self.label_usuario = ctk.CTkLabel(self, text="Usuario:")
        self.label_usuario.pack(pady=5)

        self.entry_usuario = ctk.CTkEntry(self)
        self.entry_usuario.insert(0, "sa")
        self.entry_usuario.pack(pady=5)

        self.label_password = ctk.CTkLabel(self, text="Contraseña:")
        self.label_password.pack(pady=5)

        self.entry_password = ctk.CTkEntry(self, show="*")
        self.entry_password.pack(pady=5)

        # Botón conectar a instancia
        self.button_conectar = ctk.CTkButton(self, text="Conectar a Instancia", command=self.conectar)
        self.button_conectar.pack(pady=10)

        # Combo de bases de datos
        self.combo_bases = ctk.CTkComboBox(self, values=[], state="disabled")
        self.combo_bases.pack(pady=10)

        self.button_base = ctk.CTkButton(self, text="Conectar a Base", command=self.conectar_base, state="disabled")
        self.button_base.pack(pady=10)

    def conectar(self):
        instancia = self.combo_instancias.get()
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()

        success, bases = self.conn_manager.listar_bases(instancia, usuario, password)

        if success:
            self.combo_bases.configure(values=bases, state="normal")
            self.combo_bases.set(bases[0])
            self.button_base.configure(state="normal")
            messagebox.showinfo("Conexión", "Instancia conectada correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la instancia.")

    def conectar_base(self):
        base = self.combo_bases.get()
        success = self.conn_manager.conectar_base(base)

        if success:
            messagebox.showinfo("Conexión", f"Conectado a la base: {base}")

            self.quit()
            self.destroy()

        # Pasar el engine conectado al InicioView
            inicio = InicioView(self.conn_manager.engine)
            inicio.mainloop()

        else:
            messagebox.showerror("Error", "No se pudo conectar a la base seleccionada.")