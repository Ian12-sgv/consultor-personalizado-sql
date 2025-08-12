# components/ui/selector_pdf.py
import customtkinter as ctk
from tkinter import messagebox


class SelectorPDF(ctk.CTkToplevel):
    """
    Modal en dos pasos:
      1) Seleccionar columnas de datos (no sucursales).
      2) Seleccionar columnas de sucursales/casa matriz.
    Al finalizar, llama on_export(selected_data_cols, selected_branch_cols).
    """

    BRANCH_KEYWORDS = ("Casa Matriz", "Sucursal")

    def __init__(self, master, df, on_export):
        super().__init__(master)
        self.title("Exportar a PDF")
        self.geometry("380x460")
        self.transient(master)
        self.grab_set()

        self.df = df
        self.on_export = on_export

        # Partición de columnas
        all_cols = list(self.df.columns)
        self.data_columns = [c for c in all_cols if not any(kw in c for kw in self.BRANCH_KEYWORDS)]
        self.branch_columns = [c for c in all_cols if any(kw in c for kw in self.BRANCH_KEYWORDS)]

        if not self.data_columns:
            messagebox.showinfo("Sin columnas de datos", "No hay columnas de datos para exportar.")
            self.destroy()
            return
        if not self.branch_columns:
            messagebox.showinfo("Sin sucursales", "No hay columnas de sucursales/casa matriz para exportar.")
            self.destroy()
            return

        # Estado
        self.selected_data_cols = []
        self.selected_branch_cols = []

        # Contenedores de pasos
        self.step_frame = ctk.CTkFrame(self)
        self.step_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Render paso 1
        self._render_step1()

    # -----------------------
    # Paso 1: columnas de datos
    # -----------------------
    def _render_step1(self):
        for w in self.step_frame.winfo_children():
            w.destroy()

        title = ctk.CTkLabel(self.step_frame, text="1) Selecciona columnas de DATOS", font=("Arial", 14, "bold"))
        title.pack(pady=(5, 8))

        self.scroll_1 = ctk.CTkScrollableFrame(self.step_frame, width=340, height=300)
        self.scroll_1.pack(fill="both", expand=True)

        self.vars_step1 = {}
        for c in self.data_columns:
            var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(self.scroll_1, text=c, variable=var)
            chk.pack(anchor="w", pady=2)
            self.vars_step1[c] = var

        btns = ctk.CTkFrame(self.step_frame)
        btns.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(btns, text="Cancelar", command=self.destroy).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkButton(btns, text="Siguiente", command=self._go_step2).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    def _go_step2(self):
        self.selected_data_cols = [c for c, v in self.vars_step1.items() if v.get()]
        if not self.selected_data_cols:
            messagebox.showwarning("Selección requerida", "Selecciona al menos una columna de datos.")
            return
        self._render_step2()

    # -----------------------------
    # Paso 2: columnas de sucursales
    # -----------------------------
    def _render_step2(self):
        for w in self.step_frame.winfo_children():
            w.destroy()

        title = ctk.CTkLabel(self.step_frame, text="2) Selecciona sucursales / casa matriz", font=("Arial", 14, "bold"))
        title.pack(pady=(5, 8))

        self.scroll_2 = ctk.CTkScrollableFrame(self.step_frame, width=340, height=300)
        self.scroll_2.pack(fill="both", expand=True)

        self.vars_step2 = {}
        for c in self.branch_columns:
            var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(self.scroll_2, text=c, variable=var)
            chk.pack(anchor="w", pady=2)
            self.vars_step2[c] = var

        btns = ctk.CTkFrame(self.step_frame)
        btns.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(btns, text="Volver", command=self._render_step1).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btns, text="Exportar", command=self._confirm_export).grid(row=0, column=1, padx=5, pady=5)

    def _confirm_export(self):
        self.selected_branch_cols = [c for c, v in self.vars_step2.items() if v.get()]
        if not self.selected_branch_cols:
            messagebox.showwarning("Selección requerida", "Selecciona al menos una sucursal o casa matriz.")
            return
        try:
            # Delega al callback del padre
            self.on_export(self.selected_data_cols, self.selected_branch_cols)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar PDFs: {e}")
