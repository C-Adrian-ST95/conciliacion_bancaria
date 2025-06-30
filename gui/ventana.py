import tkinter as tk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Añadir el directorio padre al path para importar módulos desde allí

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ventana = tk.Tk() # Crear la ventana principal de la aplicación 
ventana.title("Conciliación Bancario (Excel y PDF) - Multiarchivo")  # Título de la ventana
ventana.geometry("1200x700") # Tamaño de la ventana 



ventana.iconbitmap(resource_path("gui/icono_ventana_principal.ico"))
icono = tk.PhotoImage(file=resource_path("accounting.png"))
ventana.iconphoto(True, icono) 

pie_label = tk.Label(ventana, text="C.A.S.T", font=("Arial", 9), fg="gray") # Crear un label para el pie de página  
pie_label.pack(side="bottom", pady=3)  # Coloca el label en la parte inferior



frame_botones = tk.Frame(ventana)   # Crear un frame para los botones de la aplicación  
frame_botones.pack(pady=10)  # Añadir un espacio vertical entre el frame y los botones     
frame_lista = tk.Frame(ventana) # Crear un frame para la lista de archivos cargados 
frame_lista.pack(side="left", fill="y", padx=10, pady=10) # Crear un frame para la lista de archivos cargados   

tk.Label(frame_lista, text="Archivos cargados:").pack() # Etiqueta para la lista de archivos cargados
listbox = tk.Listbox(frame_lista, width=40) # Crear un Listbox para mostrar los archivos cargados           

frame_grafica = tk.Frame(ventana) # Crear un frame para la gráfica
frame_grafica.pack(pady=10)   # Añadir un espacio vertical entre el frame y la gráfica  

frame_tabla = tk.Frame(ventana) # Crear un frame para la tabla de datos procesados  
frame_tabla.pack(side="right", expand=True, fill="both", padx=10, pady=10) # Añadir un espacio vertical entre el frame y la tabla de datos procesados   

