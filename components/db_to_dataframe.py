import pandas as pd

def cargar_tabla_completa(table_name, engine):
    """
    Carga una tabla completa desde SQL a un DataFrame.
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, con=engine)
