import customtkinter as ctk
from components.ui.button import Button

class BotonesPanel(ctk.CTkFrame):
    def __init__(self, master, callbacks: dict):
        super().__init__(master)
        self.callbacks = callbacks

        # Distribución de columnas uniforme
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="btns")

        # Botones
        Button(self, text="Importar Datos",
               command=self._cb("importar_datos")).grid(row=0, column=0)
        Button(self, text="Exportar a Excel",
               command=self._cb("exportar_excel")).grid(row=0, column=1)
        Button(self, text="Exportar PDF",
               command=self._cb("exportar_pdf")).grid(row=0, column=2)
        Button(self, text="Importar Catálogo Desc",
               command=self._cb("importar_catalogo_descuento")).grid(row=0, column=3)

    def _cb(self, name: str):
        """Wrapper con print de tester y manejo seguro si falta el callback."""
        def _wrapped():
            print(f"[BotonesPanel] Click en botón: {name}")
            cb = self.callbacks.get(name)
            if cb is None:
                print(f"[BotonesPanel][WARN] No hay callback registrado para '{name}'")
                return
            try:
                cb()
            except Exception as e:
                print(f"[BotonesPanel][ERROR] Falló '{name}': {e}")
        return _wrapped
