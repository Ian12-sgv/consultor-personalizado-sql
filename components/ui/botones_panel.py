import customtkinter as ctk
from components.ui.button import Button

class BotonesPanel(ctk.CTkFrame):
    def __init__(self, master, callbacks: dict):
        super().__init__(master)
        self.callbacks = callbacks

        self.grid_columnconfigure((0,1,2,3), weight=1, uniform="btns")

        Button(self, text="Importar Datos", command=self.callbacks.get("importar_datos")).grid(row=0, column=0)
        Button(self, text="Exportar a Excel", command=self.callbacks.get("exportar_excel")).grid(row=0, column=1)
        Button(self, text="Exportar PDF", command=self.callbacks.get("exportar_pdf")).grid(row=0, column=2)
        Button(self, text="Importar Excel", command=self.callbacks.get("importar_excel")).grid(row=0, column=3)
