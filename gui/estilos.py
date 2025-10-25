"""
Estilos centralizados para la aplicación
"""

# Colores del tema
COLORES = {
    'primario': '#1f2937',
    'secundario': '#f9fafb',
    'fondo': '#ffffff',
    'texto': '#374151',
    'acento': '#3b82f6',
    'exito': '#10b981',
    'advertencia': '#f59e0b',
    'error': '#ef4444'
}

# Estilos de botones
ESTILO_BOTON_PRINCIPAL = {
    'fg': COLORES['primario'],
    'bg': COLORES['secundario'],
    'activebackground': '#e5e7eb',
    'activeforeground': COLORES['primario'],
    'font': ('Arial', 9),
    'relief': 'flat',
    'cursor': 'hand2',
    'padx': 12,
    'pady': 6
}

ESTILO_BOTON_SECUNDARIO = {
    'fg': COLORES['texto'],
    'bg': COLORES['fondo'],
    'activebackground': COLORES['secundario'],
    'font': ('Arial', 9),
    'relief': 'solid',
    'borderwidth': 1,
    'cursor': 'hand2'
}

# Estilos de etiquetas
ESTILO_TITULO = {
    'font': ('Arial', 12, 'bold'),
    'fg': COLORES['primario']
}

ESTILO_SUBTITULO = {
    'font': ('Arial', 10, 'bold'),
    'fg': COLORES['texto']
}