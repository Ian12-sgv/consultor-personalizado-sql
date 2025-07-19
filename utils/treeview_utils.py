def limpiar_treeview(tree):
    tree.delete(*tree.get_children())

def cargar_dataframe_en_treeview(tree, df):
    tree["columns"] = list(df.columns)
    for col in df.columns:
        tree.heading(col, text=col)
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))
