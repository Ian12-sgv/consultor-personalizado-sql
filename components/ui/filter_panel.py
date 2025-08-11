import customtkinter as ctk
from components.ui.placeholder_combo import PlaceholderCombo
from components.ui.button import Button

class FilterPanel(ctk.CTkFrame):
    def __init__(self, master, on_filter_change):
        super().__init__(master)
        self.on_filter_change = on_filter_change

        # Pivot selector
        self.pivot_selector = ctk.CTkComboBox(
            self, values=["Todo", "Solo Sucursales", "Solo Casa Matriz"],
            command=lambda _: self._on_change()
        )
        self.pivot_selector.set("Todo")
        self.pivot_selector.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Región selector
        self.region_selector = PlaceholderCombo(
            self, placeholder="Región", values=["Todas"], state="disabled",
            command=lambda _: self._on_change()
        )
        self.region_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Referencia selector
        self.referencia_entry = PlaceholderCombo(
            self, placeholder="Referencia", values=[""], state="normal",
            command=lambda _: self._on_change()
        )
        self.referencia_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Excluir marcas entry
        self.exclude_entry = ctk.CTkEntry(
            self, placeholder_text="Marcas a excluir (separadas por coma)", width=200
        )
        self.exclude_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.exclude_entry.bind("<Return>", lambda e: self._on_change())

        # Checkbox Solo Promoción
        self.promo_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Solo Promoción = 1",
            variable=self.promo_var,
            command=self._on_change
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Checkbox Resaltar Descuento Duplicados
        self.desc_dup_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Resaltar Descuento Duplicados",
            variable=self.desc_dup_var,
            command=self._on_change
        ).grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Botones Solo no duplicados / Solo duplicados (ocultos inicialmente)
        self.btn_unique = Button(
            self,
            text="Solo no duplicados",
            command=lambda: self._set_filter_mode('unique'),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            row=5,
            column=0,
            padx=10,
            pady=5
        )
        self.btn_dup = Button(
            self,
            text="Solo duplicados",
            command=lambda: self._set_filter_mode('dup'),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            row=5,
            column=1,
            padx=10,
            pady=5
        )
        self.btn_unique.grid_remove()
        self.btn_dup.grid_remove()

        # Checkbox Mostrar solo coincidencias
        self.filter_solo_coincide = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self,
            text="Mostrar solo coincidencias",
            variable=self.filter_solo_coincide,
            command=self._on_change
        ).grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Checkbox Mostrar solo no coincidencias
        self.filter_solo_no_coincide = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self,
            text="Mostrar solo no coincidencias",
            variable=self.filter_solo_no_coincide,
            command=self._on_change
        ).grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.filter_mode = None

    def _set_filter_mode(self, mode):
        print(f"[FilterPanel] Cambiando filter_mode: {mode}")
        self.filter_mode = None if self.filter_mode == mode else mode
        self._on_change()

    def _on_change(self):
        print("[FilterPanel] Filtros cambiaron")
        self.on_filter_change()

    def get_filters(self):
        filters = {
            "pivot": self.pivot_selector.get(),
            "region": self.region_selector.get_value(),
            "referencia": self.referencia_entry.get_value(),
            "exclude_marcas": [m.strip() for m in self.exclude_entry.get().split(',') if m.strip()],
            "solo_promo_1": self.promo_var.get(),
            "desc_dup": self.desc_dup_var.get(),
            "filter_mode": self.filter_mode,
            "filter_solo_coincide": self.filter_solo_coincide.get(),
            "filter_solo_no_coincide": self.filter_solo_no_coincide.get(),
        }
        print(f"[FilterPanel] get_filters: {filters}")
        return filters

    def set_region_values(self, values):
        print(f"[FilterPanel] set_region_values: {values}")
        self.region_selector.reset_placeholder(values=values)
        self.region_selector.configure(state="normal")

    def set_referencia_values(self, values):
        print(f"[FilterPanel] set_referencia_values: {values}")
        self.referencia_entry.reset_placeholder(values=values)
