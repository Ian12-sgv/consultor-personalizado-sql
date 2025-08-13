# components/ui/button.py
import customtkinter as ctk

def _clamp(n, smallest=0, largest=255):
    return max(smallest, min(n, largest))

def _darken(hex_color: str, factor: float = 0.12) -> str:
    """Oscurece un color hex (#RRGGBB) en 'factor' [0..1]."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        return "#000000"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = _clamp(int(r * (1 - factor)))
    g = _clamp(int(g * (1 - factor)))
    b = _clamp(int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

class Button(ctk.CTkButton):
    """
    Botón CTk con estilo moderno.

    ✔ Variantes: 'primary' (default), 'success', 'warning', 'danger', 'neutral',
                 'outline', 'ghost'
    ✔ Tamaños: 'sm', 'md', 'lg'
    ✔ Compatible con tu uso actual (fg_color / hover_color)
    ✔ Opción full_width para ocupar todo el ancho de su celda de grid

    Nota: si NO pasas 'variant' ni 'fg_color',
          el color se autoasigna según el texto común del botón
          (Importar/Exportar/Excel/PDF/Catálogo).
    """

    PALETTE = {
        "primary": {"fg": "#4F46E5", "text": "#FFFFFF"},   # indigo-600
        "success": {"fg": "#10B981", "text": "#FFFFFF"},   # emerald-500
        "warning": {"fg": "#F59E0B", "text": "#111827"},   # amber-500
        "danger":  {"fg": "#EF4444", "text": "#FFFFFF"},   # red-500
        "neutral": {"fg": "#64748B", "text": "#FFFFFF"},   # slate-500
        # para outline/ghost usamos "fg_base" sólo como referencia de borde/texto
        "outline": {"fg": "#4F46E5", "text": "#4F46E5"},
        "ghost":   {"fg": "#4F46E5", "text": "#4F46E5"},
    }

    SIZES = {
        "sm": {"width": 110, "height": 34, "font": ("Segoe UI", 11, "bold"), "radius": 10, "pady": 4},
        "md": {"width": 140, "height": 40, "font": ("Segoe UI", 12, "bold"), "radius": 12, "pady": 6},
        "lg": {"width": 170, "height": 48, "font": ("Segoe UI", 13, "bold"), "radius": 14, "pady": 8},
    }

    # ---- auto-mapeo de colores por texto (si no pasas variant/fg_color) ----
    @staticmethod
    def _auto_variant_from_text(text: str) -> str | None:
        """
        Devuelve una variante sugerida según el texto del botón.
        Sólo se usa cuando NO se pasó fg_color y variant viene por defecto.
        """
        if not text:
            return None
        t = text.strip().lower()

        # normalizamos algunos textos comunes
        if "exportar" in t and "pdf" in t:
            return "warning"   # Exportar PDF -> ámbar
        if "exportar" in t and "excel" in t:
            return "success"   # Exportar Excel -> verde
        if "importar" in t and "excel" in t:
            return "neutral"   # Importar Excel -> gris
        if "importar catálogo" in t or "catálogo" in t or "catalogo" in t:
            return "danger"    # Importar catálogo -> rojo
        if "importar" in t and "datos" in t:
            return "primary"   # Importar Datos -> primario

        # puedes añadir más reglas si lo necesitas
        return None

    def __init__(
        self,
        master,
        text: str,
        command,
        *,
        # nuevos parámetros “bonitos”
        variant: str = "primary",     # primary, success, warning, danger, neutral, outline, ghost
        size: str = "md",             # sm, md, lg
        full_width: bool = True,
        uppercase: bool = False,

        # compatibilidad con proyecto actual
        width: int = None,
        height: int = None,
        fg_color: str = None,
        hover_color: str = None,
        corner_radius: int = None,
        text_color: str = None,

        # grid helpers (opcional)
        row: int = None,
        column: int = None,
        padx: int = 10,
        pady: int = None,
        sticky: str = "ew",
        **kwargs
    ):
        # --- Config base por tamaño ---
        size_cfg = self.SIZES.get(size, self.SIZES["md"])
        w = width or size_cfg["width"]
        h = height or size_cfg["height"]
        radius = corner_radius or size_cfg["radius"]
        pad_y = size_cfg["pady"] if pady is None else pady

        # --- Texto ---
        final_text = text.upper() if uppercase else text

        # --- Paleta y variantes ---
        variant_in = (variant or "primary").lower()

        # Si no pasaste fg_color, podemos autodefinir la variante por el texto
        if fg_color is None:
            sug = self._auto_variant_from_text(final_text)
            if sug:
                variant_in = sug

        pal = self.PALETTE.get(variant_in, self.PALETTE["primary"])

        # Si el usuario pasó fg_color/hover_color, respétalos
        if fg_color:
            base_fg = fg_color
            hov_fg = hover_color or _darken(fg_color, 0.12)
            txt_color = text_color or "#FFFFFF"
            border_w = 0
            border_col = None
        else:
            base_fg = pal["fg"]
            hov_fg = hover_color or _darken(base_fg, 0.12)
            txt_color = text_color or pal["text"]
            border_w = 0
            border_col = None

            # variantes outline/ghost
            if variant_in in ("outline", "ghost"):
                border_col = pal["fg"]
                border_w = 1
                txt_color = pal["text"]
                if variant_in == "outline":
                    base_fg = "transparent"
                    hov_fg = "#eef2ff"
                else:
                    base_fg = "transparent"
                    hov_fg = "#f5f7ff"

        super().__init__(
            master,
            text=final_text,
            command=command,
            width=w,
            height=h,
            fg_color=base_fg,
            hover_color=hov_fg,
            corner_radius=radius,
            text_color=txt_color,
            **kwargs
        )

        # Borde para outline/ghost (o si tú lo pones manualmente)
        if border_col:
            self.configure(border_width=border_w, border_color=border_col)
        else:
            self.configure(border_width=0)

        # Fuente moderna por tamaño (si no la pisaste desde kwargs)
        if "font" not in kwargs:
            self.configure(font=size_cfg["font"])

        # Comportamiento de grid
        if row is not None and column is not None:
            master.grid_columnconfigure(column, weight=1 if full_width else 0, uniform="btns")
            self.grid(row=row, column=column, padx=padx, pady=pad_y, sticky=("ew" if full_width else sticky))
