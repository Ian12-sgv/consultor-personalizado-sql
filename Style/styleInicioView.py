# styleInicioView.py
"""
Archivo de estilos para InicioView.
Separa la configuración de CustomTkinter y Treeview.
"""
import customtkinter as ctk
import tkinter.ttk as ttk

def configure_ctk_style(appearance_mode='dark', color_theme='blue'):
    """
    Configura el tema y apariencia de CustomTkinter.
    :param appearance_mode: 'dark', 'light', o 'system'
    :param color_theme: nombre del tema de color (p.ej. 'blue', 'green')
    """
    ctk.set_appearance_mode(appearance_mode)
    ctk.set_default_color_theme(color_theme)

def configure_treeview_style():
    """
    Configura estilos para los Treeview de ttk.
    Encabezados en negrita con fondo azul, filas y selección personalizados.
    """
    style = ttk.Style()
    style.theme_use('default')

    # Encabezados
    style.configure(
        'Treeview.Heading',
        font=('Segoe UI', 10, 'bold'),
        foreground='#ffffff',
        background='#1f6aa5'
    )
    style.map(
        'Treeview.Heading',
        background=[('active', '#18527d')]
    )

    # Filas
    style.configure(
        'Treeview',
        font=('Segoe UI', 10),
        rowheight=22,
        background='#1e1e1e',
        fieldbackground='#1e1e1e',
        foreground='#e5e5e5'
    )
    style.map(
        'Treeview',
        background=[('selected', '#1f6aa5')],
        foreground=[('selected', 'white')]
    )
