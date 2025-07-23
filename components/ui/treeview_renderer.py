# components/ui/treeview_renderer.py
from utils.treeview_utils import limpiar_treeview, cargar_dataframe_en_treeview
import pandas as pd
from tkinter import ttk

def render(tree: ttk.Treeview, df: pd.DataFrame):
    limpiar_treeview(tree)
    if df is None or df.empty:
        tree["columns"] = ["Sin datos"]
        tree.heading("Sin datos", text="Sin datos disponibles")
    else:
        cargar_dataframe_en_treeview(tree, df)
