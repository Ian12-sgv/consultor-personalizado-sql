# components/ui/placeholder_combo.py
import customtkinter as ctk

PLACEHOLDER_COLOR = ("gray65", "gray45")
NORMAL_COLOR      = ("black", "white")

class PlaceholderCombo(ctk.CTkComboBox):
    def __init__(self, master, placeholder: str, **kwargs):
        super().__init__(master, **kwargs)
        self._placeholder = placeholder
        self._using_placeholder = False
        self._set_placeholder()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _set_placeholder(self):
        self.set(self._placeholder)
        self.configure(text_color=PLACEHOLDER_COLOR)
        self._using_placeholder = True

    def _on_focus_in(self, _):
        if self._using_placeholder:
            self.set("")
            self.configure(text_color=NORMAL_COLOR)
            self._using_placeholder = False

    def _on_focus_out(self, _):
        if not self.get().strip():
            self._set_placeholder()

    def get_value(self):
        """Devuelve '' si hay placeholder, o el valor real."""
        return "" if self._using_placeholder else self.get()

    def reset_placeholder(self, values=None):
        if values is not None:
            self.configure(values=values)
        self._set_placeholder()
