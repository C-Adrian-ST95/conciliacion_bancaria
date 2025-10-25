import tkinter as tk
import sys
import os
from tkinter import ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Añadir el directorio padre al path para importar módulos desde allí

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ventana = tk.Tk() # Crear la ventana principal de la aplicación 
ventana.title("Conciliación Bancario - Multiarchivo")  # Título de la ventana
ventana.geometry("1200x700") # Tamaño de la ventana 

ventana.minsize(1000, 650)

ventana.iconbitmap(resource_path("gui/icono_ventana_principal.ico"))
icono = tk.PhotoImage(file=resource_path("accounting.png"))
ventana.iconphoto(True, icono) 

pie_label = tk.Label(ventana, text="C.A.S.T", font=("Arial", 9), fg="gray") # Crear un label para el pie de página  
pie_label.pack(side="bottom", pady=3)  # Coloca el label en la parte inferior
frame_botones = tk.Frame(ventana)   # Crear un frame para los botones de la aplicación 
frame_botones.pack(side="top", pady=10)  # Añadir un espacio vertical entre el frame y los botones

frame_grafica = tk.Frame(ventana) # Crear un frame para la gráfica
frame_grafica.pack(pady=10)   # Añadir un espacio vertical entre el frame y la gráfica  

 

# Crear frame para la búsqueda (agregar antes del frame_tabla)
frame_busqueda = tk.Frame(ventana)
frame_busqueda.pack(fill="y", padx=10, pady=(0, 5))

# Crear frame para estadísticas (después del frame_busqueda)
frame_estadisticas = tk.Frame(ventana)
frame_estadisticas.pack(fill="x", padx=8, pady=(0, 5))

# Crear un contenedor principal que divida la ventana en dos partes
main_container = tk.Frame(ventana)
main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# Frame izquierdo (lista de archivos) con ancho fijo
frame_izquierdo = tk.Frame(main_container, width=250)
frame_izquierdo.pack(side="left", fill="y", padx=(0, 5))
frame_izquierdo.pack_propagate(True)

# Frame derecho (búsqueda, estadísticas y tabla)
frame_derecho = tk.Frame(main_container)
frame_derecho.pack(side="right", fill="both", expand=True)
frame_derecho.update()  # Actualizar para obtener dimensiones
frame_derecho.config(width=600, height=400)  # Tamaño mínimo inicial
frame_derecho.pack_propagate(True)  # Permitir que se expanda

# Mover frame_busqueda al frame_derecho
frame_busqueda = tk.Frame(frame_izquierdo)
frame_busqueda.pack(fill="x", pady=(0, 5))

# Mover frame_lista al frame_izquierdo
frame_lista = tk.Frame(frame_izquierdo) 
frame_lista.pack(fill="both", expand=True)


tk.Label(frame_lista, text="📁 Archivos cargados:", font=("Arial", 10, "bold")).pack(pady=(0,5))
listbox = tk.Listbox(frame_lista, width=30, font=("Arial", 9))
listbox.pack(side="left", fill="both", expand=True)

# Scrollbar para el listbox
scrollbar_lista = ttk.Scrollbar(frame_lista, orient="vertical", command=listbox.yview)
scrollbar_lista.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar_lista.set)

# Separador vertical
ttk.Separator(main_container, orient="vertical").pack(side="left", fill="y", padx=5)


# Mover frame_estadisticas al frame_derecho
frame_estadisticas = tk.Frame(frame_izquierdo)
frame_estadisticas.pack(fill="x", pady=(0, 5))
# Frame gráfica (si lo necesitas, va abajo de todo)

frame_grafica = tk.Frame(ventana)
# frame_grafica.pack(fill="x", padx=10, pady=(0, 10))  # Descomenta si lo usas

frame_tabla = tk.Frame(frame_derecho) # Crear un frame para la tabla de datos procesados  
frame_tabla.pack(side="bottom", expand=True, fill="both", padx=10, pady=10) # Añadir un espacio vertical entre el frame y la tabla de datos procesados  

# Mover frame_tabla al frame_derecho
#frame_tabla = tk.Frame()
#frame_tabla.pack(fill="both", expand=True)