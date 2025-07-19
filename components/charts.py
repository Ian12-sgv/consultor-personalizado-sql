# components/charts.py
# -----------------
# Chart rendering functions

import streamlit as st


def plot_inventory_by_reference(df):
    st.subheader("Existencia por Referencia")
    chart_data = df.groupby("Referencia")["Existencia_Total"].sum()
    st.bar_chart(chart_data)