import customtkinter as ctk
from components.ui.placeholder_combo import PlaceholderCombo
from components.ui.button import Button

class FilterPanel(ctk.CTkFrame):
    def __init__(self, master, on_filter_change):
        super().__init__(master)
        self.on_filter_change = on_filter_change
        self.filter_mode = None

        # Una sola columna amplia; todo en vertical (label arriba, control abajo)
        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Pivot
        ctk.CTkLabel(self, text="Vista / Pivot").grid(row=row, column=0, sticky="w", padx=6, pady=(6,2))
        row += 1
        self.pivot_selector = ctk.CTkComboBox(
            self,
            values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=lambda _: self._on_change()
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=row, column=0, padx=6, pady=(0,8), sticky="ew")
        row += 1

        # Referencia (solo Enter)
        ctk.CTkLabel(self, text="Referencia").grid(row=row, column=0, sticky="w", padx=6, pady=(0,2))
        row += 1
        self.referencia_entry = PlaceholderCombo(self, placeholder="Referencia", values=[""], state="normal")
        self.referencia_entry.grid(row=row, column=0, padx=6, pady=(0,8), sticky="ew")
        self.referencia_entry.bind("<Return>", lambda e: self._on_change())
        row += 1

        # Excluir año (solo Enter)
        ctk.CTkLabel(self, text="Excluir año").grid(row=row, column=0, sticky="w", padx=6, pady=(0,2))
        row += 1
        self.exclude_year_entry = ctk.CTkEntry(self, placeholder_text="YYYY")
        self.exclude_year_entry.grid(row=row, column=0, padx=6, pady=(0,8), sticky="ew")
        self.exclude_year_entry.bind("<Return>", lambda e: self._on_change())
        row += 1

        # Excluir marcas (solo Enter)
        ctk.CTkLabel(self, text="Marcas a excluir").grid(row=row, column=0, sticky="w", padx=6, pady=(0,2))
        row += 1
        self.exclude_entry = ctk.CTkEntry(self, placeholder_text="Códigos separados por coma")
        self.exclude_entry.grid(row=row, column=0, padx=6, pady=(0,8), sticky="ew")
        self.exclude_entry.bind("<Return>", lambda e: self._on_change())
        row += 1

        # Excluir sublíneas (solo Enter)
        ctk.CTkLabel(self, text="Sublíneas a excluir").grid(row=row, column=0, sticky="w", padx=6, pady=(0,2))
        row += 1
        self.exclude_sublinea_entry = ctk.CTkEntry(self, placeholder_text="Códigos separados por coma")
        self.exclude_sublinea_entry.grid(row=row, column=0, padx=6, pady=(0,8), sticky="ew")
        self.exclude_sublinea_entry.bind("<Return>", lambda e: self._on_change())
        row += 1

        # Opciones
        ctk.CTkLabel(self, text="Opciones").grid(row=row, column=0, sticky="w", padx=6, pady=(8,2))
        row += 1
        self.promo_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Solo Promoción = 1",
            variable=self.promo_var, command=self._on_change
        ).grid(row=row, column=0, padx=6, pady=(0,4), sticky="w")
        row += 1

        # NUEVO: Casa Matriz con existencia 1–11
        self.only_matriz_stock = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self,
            text="Casa Matriz: existencia 1–11",
            variable=self.only_matriz_stock,
            command=self._on_change
        ).grid(row=row, column=0, padx=6, pady=(0,8), sticky="w")
        row += 1

        self.desc_dup_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Resaltar Descuento Duplicados",
            variable=self.desc_dup_var, command=self._on_change
        ).grid(row=row, column=0, padx=6, pady=(0,8), sticky="w")
        row += 1

        # Botones duplicados (aparecen solo si está activo el resaltado)
        self.btn_unique = Button(
            self, text="Solo no duplicados",
            command=lambda: self._set_filter_mode('unique'),
            fg_color="#27ae60", hover_color="#2ecc71",
            row=row, column=0, padx=6, pady=4
        )
        row += 1
        self.btn_dup = Button(
            self, text="Solo duplicados",
            command=lambda: self._set_filter_mode('dup'),
            fg_color="#e74c3c", hover_color="#c0392b",
            row=row, column=0, padx=6, pady=(0,8)
        )
        self.btn_unique.grid_remove()
        self.btn_dup.grid_remove()
        row += 1

        # Coincidencias
        ctk.CTkLabel(self, text="Coincidencias con catálogo").grid(row=row, column=0, sticky="w", padx=6, pady=(8,2))
        row += 1
        self.filter_solo_coincide = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Mostrar solo coincidencias",
            variable=self.filter_solo_coincide, command=self._on_change
        ).grid(row=row, column=0, padx=6, pady=(0,4), sticky="w")
        row += 1
        self.filter_solo_no_coincide = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Mostrar solo no coincidencias",
            variable=self.filter_solo_no_coincide, command=self._on_change
        ).grid(row=row, column=0, padx=6, pady=(0,10), sticky="w")
        row += 1

    # ---- helpers ----
    def _set_filter_mode(self, mode):
        self.filter_mode = None if self.filter_mode == mode else mode
        self._on_change()

    def _on_change(self):
        self.on_filter_change()

    def _get_referencia_safe(self) -> str:
        val = self.referencia_entry.get_value()
        if not val:
            return ""
        val = str(val).strip()
        if val.lower() == "referencia":
            return ""
        return val

    def _get_exclude_year_safe(self):
        raw = (self.exclude_year_entry.get() or "").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    # ---- API pública ----
    def get_filters(self):
        return {
            "pivot": self.pivot_selector.get(),
            "region": None,  # <- ya NO usamos región
            "referencia": self._get_referencia_safe(),
            "exclude_marcas": [m.strip() for m in self.exclude_entry.get().split(',') if m.strip()],
            "exclude_sublineas": [s.strip() for s in self.exclude_sublinea_entry.get().split(',') if s.strip()],
            "solo_promo_1": self.promo_var.get(),
            "solo_matriz_exist_1_11": self.only_matriz_stock.get(),  # <- NUEVO
            "desc_dup": self.desc_dup_var.get(),
            "filter_mode": self.filter_mode,
            "filter_solo_coincide": self.filter_solo_coincide.get(),
            "filter_solo_no_coincide": self.filter_solo_no_coincide.get(),
            "exclude_year": self._get_exclude_year_safe(),
        }

    # setters (compatibles con InicioView; si se llama, no pasa nada)
    def set_region_values(self, values):
        pass

    def set_referencia_values(self, values):
        self.referencia_entry.reset_placeholder(values=values)
