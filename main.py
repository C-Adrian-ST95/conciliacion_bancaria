import tkinter as tk
from gui.componentes import (
    cargar_excel, 
    cargar_pdf, 
    seleccionar_y_procesar, 
    exportar_actual, 
    agregar_buscador
)
from gui.graficos import graficar_dataframe_seleccionado
from gui.ventana import frame_botones, ventana, frame_busqueda
from gui.helpers import crear_boton

def configurar_interfaz():
    """Configura todos los elementos de la interfaz"""
    
    # Botones principales
    botones_config = [
        {
            'texto': '📚 Libro de Empresa',
            'comando': cargar_excel,
            'tooltip': 'Carga archivos Excel con el libro de bancos de tu empresa'
        },
        {
            'texto': '🏦 Extracto Bancario',
            'comando': cargar_pdf,
            'tooltip': 'Carga extractos bancarios en formato PDF'
        },
        {
            'texto': '⚖️ Conciliar',
            'comando': seleccionar_y_procesar,
            'tooltip': 'Compara y concilia el libro de bancos con el extracto bancario'
        },
        {
            'texto': '📊 Exportar Reporte',
            'comando': exportar_actual,
            'tooltip': 'Exporta el archivo seleccionado a formato Excel'
        },
        {
            'texto': '📈 Gráfico',
            'comando': graficar_dataframe_seleccionado,
            'tooltip': 'Muestra gráficos estadísticos de los datos procesados',
            'padx': 5
        }
    ]
    
    # Crear botones principales
    for config in botones_config:
        crear_boton(
            frame_botones,
            config['texto'],
            config['comando'],
            config['tooltip'],
            padx=config.get('padx', 9)
        )
    
    # Botón de búsqueda
    crear_boton(
        frame_busqueda,
        '🔍 Buscar',
        agregar_buscador,
        'Activa el campo de búsqueda para filtrar datos en la tabla',
        padx=5
    )

if __name__ == "__main__":
    configurar_interfaz()
    ventana.mainloop()

