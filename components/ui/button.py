# components/ui/button.py
import customtkinter as ctk

class Button(ctk.CTkButton):
    """
    Componente reutilizable para botones CTk con estilo moderno y distribución uniforme.

    Parámetros:
    - master: contenedor padre
    - text: texto a mostrar
    - command: función a ejecutar al hacer clic
    - width: ancho fijo del botón (opcional, default=150)
    - height: alto fijo del botón (opcional, default=40)
    - fg_color: color de fondo (por defecto verdiaceo)
    - hover_color: color al pasar el ratón (por defecto más oscuro)
    - corner_radius: radio de las esquinas (opcional, default=8)
    - row, column, padx, pady, sticky: parámetros de grid para posicionar el botón
    """
    DEFAULT_FG = "#2ecc71"
    DEFAULT_HOVER = "#27ae60"
    DEFAULT_WIDTH = 150
    DEFAULT_HEIGHT = 40
    DEFAULT_RADIUS = 8

    def __init__(
        self,
        master,
        text: str,
        command,
        width: int = None,
        height: int = None,
        fg_color: str = None,
        hover_color: str = None,
        corner_radius: int = None,
        row: int = None,
        column: int = None,
        padx: int = 10,
        pady: int = 5,
        sticky: str = "ew",
        **kwargs
    ):
        fg = fg_color or self.DEFAULT_FG
        hover = hover_color or self.DEFAULT_HOVER
        w = width or self.DEFAULT_WIDTH
        h = height or self.DEFAULT_HEIGHT
        radius = corner_radius or self.DEFAULT_RADIUS

        super().__init__(
            master,
            text=text,
            command=command,
            width=w,
            height=h,
            fg_color=fg,
            hover_color=hover,
            corner_radius=radius,
            **kwargs
        )
        # Aplicar sombra suave
        self.configure(border_width=0)

        # Posicionamiento automático en grid con columnas uniformes
        if row is not None and column is not None:
            master.grid_columnconfigure(column, weight=1, uniform="btn")
            self.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
