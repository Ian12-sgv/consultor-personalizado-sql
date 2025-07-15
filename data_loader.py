# data_loader.py
import pandas as pd
import streamlit as st
from utils.db_utils import ConnectionManager
from components.query import INVENTORY_SQL

# Reutilizar el mismo engine creado en app.py
conn_manager = None  # Se inicializa desde app.py

@st.cache_data(ttl=600)
def load_inventory_data():
    if conn_manager is None or conn_manager.engine is None:
        st.error("No hay conexión activa. Por favor, conéctate primero.")
        return pd.DataFrame()

    df = pd.read_sql(INVENTORY_SQL, conn_manager.engine)
    return df
