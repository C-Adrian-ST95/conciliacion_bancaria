import tkinter as tk
from core.utilidades import ToolTip
from gui.estilos import ESTILO_BOTON_PRINCIPAL

def crear_boton(parent, texto, comando, tooltip=None, estilo=None, **kwargs):
    """
    Crea un botón con tooltip y estilo predefinido
    
    Parámetros:
    ----------
    parent : Widget
        Contenedor del botón
    texto : str
        Texto del botón
    comando : function
        Función a ejecutar
    tooltip : str, opcional
        Texto del tooltip
    estilo : dict, opcional
        Diccionario con estilos personalizados
    **kwargs : dict
        Argumentos adicionales para pack()
        
    Retorna:
    -------
    Button : tk.Button
        Botón creado
    """
    # Usar estilo predefinido o personalizado
    btn_config = estilo if estilo else ESTILO_BOTON_PRINCIPAL.copy()
    
    # Crear botón
    btn = tk.Button(parent, text=texto, command=comando, **btn_config)
    
    # Configurar empaquetado
    pack_config = {'side': 'left', 'padx': 10}
    pack_config.update(kwargs)
    btn.pack(**pack_config)
    
    # Añadir tooltip si se proporciona
    if tooltip:
        ToolTip(btn, tooltip)
    
    return btn