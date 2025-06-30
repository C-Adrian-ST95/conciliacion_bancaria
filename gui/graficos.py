import tkinter as tk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from core.utilidades import archivos_cargados
from gui.ventana import listbox, ventana, resource_path

def abrir_ventana_grafica(df_cargo,df_abono, col_fecha, col_cargo, col_abono):
    """
    Crea una ventana emergente con gráficos de barras horizontales de cargos y abonos por fecha.
    Verifica que los DataFrames no estén vacíos y que contengan las columnas necesarias.
    Luego genera dos gráficos en una ventana nueva: uno para los cargos y otro para los abonos.

    Parámetros:
    df_cargo : pandas.DataFrame
        DataFrame que contiene los montos de cargo por fecha.
    df_abono : pandas.DataFrame
        DataFrame que contiene los montos de abono por fecha.
    col_fecha : str
        Nombre de la columna que contiene las fechas.
    col_cargo : str
        Nombre de la columna que contiene los valores de cargo.
    col_abono : str
        Nombre de la columna que contiene los valores de abono.

    Retorna:None
    """
    if df_cargo.empty:
        messagebox.showinfo("Información", "El DataFrame está vacío.")
        return

    if col_fecha not in df_cargo.columns or col_cargo not in df_cargo.columns:
        messagebox.showerror("Error", f"El DataFrame no tiene las columnas '{col_fecha}' y/o '{col_cargo}'.")
        return
    if col_fecha not in df_abono.columns or col_abono not in df_abono.columns:
        messagebox.showerror("Error", f"El DataFrame no tiene las columnas '{col_fecha}' y/o '{col_abono}'.")
        return

    # Crear una nueva ventana
    ventana_grafica = tk.Toplevel(ventana) # Crear una ventana emergente para mostrar la gráfica    
    ventana_grafica.title('Gráfica') # Título de la ventana gráfica
    ventana_grafica.geometry("900x700") # Tamaño de la ventana gráfica 
    
    ventana_grafica.resizable(True, True) # Permitir que la ventana gráfica sea redimensionable 
    ventana_grafica.iconbitmap(resource_path("gui/icono_grafica.ico"))
    df_cargo = df_cargo     
    df_abono = df_abono      
    # Crear la figura y el eje
    fig, axs = plt.subplots(1, 2, figsize=(12, 6)) # Crear una figura con dos subgráficos (uno para cargos y otro para abonos)

# Primer gráfico: Cargos
    bars = axs[0].barh(df_cargo[col_fecha], df_cargo[col_cargo]) # Gráfico de barras horizontales para cargos       
    axs[0].set_title('Cargos vs Fecha') # Título del gráfico de cargos
    axs[0].set_xlabel('') # Etiqueta del eje X
    axs[0].set_ylabel('') # Etiqueta del eje Y  
    axs[0].spines['top'].set_visible(False) # Ocultar el borde superior del gráfico
    axs[0].spines['right'].set_visible(False) # Ocultar el borde derecho del gráfico    
    axs[0].tick_params(axis='y', labelsize=7)  # Tamaño de los valores (eje Y)
    axs[0].set_xticks([])  # Oculta etiquetas del eje X
    axs[0].set_yticks([]) # Oculta etiquetas del eje Y

    # Agregar texto al final de cada barra
    for i, bar in enumerate(bars):
        width = bar.get_width()  # longitud de la barra
        y_pos = bar.get_y() + bar.get_height() / 2 # posición vertical de la barra
        fecha = df_cargo[col_fecha].iloc[i] # fecha correspondiente a la barra  
        axs[0].text(width-df_cargo[col_cargo].iloc[i], y_pos, fecha, 
                    ha='right', va='center', fontsize=7, rotation=0, color='black') # texto de la fecha
        axs[0].text(width , y_pos , f'{width:.2f}',
                    ha='left', va='center', fontsize=7, rotation=0, color='black') # texto del valor de la barra    
    
    # Segundo gráfico: Abonos
    bara = axs[1].barh(df_abono[col_fecha], df_abono[col_abono], color='orange') # Gráfico de barras horizontales para abonos
    axs[1].set_title('Abonos vs Fecha') # Título del gráfico de abonos
    axs[1].set_xlabel('') # Etiqueta del eje X 
    axs[1].set_ylabel('', fontsize=5) # Etiqueta del eje Y
    axs[1].spines['top'].set_visible(False) # Ocultar el borde superior del gráfico
    axs[1].spines['right'].set_visible(False) # Ocultar el borde derecho del gráfico
    axs[1].tick_params(axis='x', labelsize=7)  # Tamaño de las fechas (eje X)
    axs[1].tick_params(axis='y', labelsize=7)  # Tamaño de los valores (eje Y)
    axs[1].set_xticks([]) # Oculta etiquetas del eje X
    axs[1].set_yticks([]) # Oculta etiquetas del eje Y

    # Agregar texto al final de cada barra
    for i, bar in enumerate(bara): # Iterar sobre cada barra del gráfico de abonos  
        width = bar.get_width() # longitud de la barra
        y_pos = bar.get_y() + bar.get_height() / 2  # posición vertical de la barra
        fecha = df_abono[col_fecha].iloc[i] # fecha correspondiente a la barra          
        axs[1].text(width-df_abono[col_abono].iloc[i], y_pos, fecha,
                    ha='right', va='center', fontsize=7, rotation=0, color='black') # texto de la fecha
        axs[1].text(width , y_pos , f'{width:.2f}',
                    ha='left', va='center', fontsize=7, rotation=0, color='black') # texto del valor de la barra


    # Ajustar diseño
    plt.tight_layout() 
    # Mostrar la figura en la nueva ventana
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafica) # Crear un canvas para mostrar la figura
    canvas.draw() # Dibujar la figura en el canvas  
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True) # Añadir el canvas a la ventana gráfica

    # Función para guardar imagen
    def guardar_grafica(): 
        archivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("Todos los archivos", "*.*")]
        ) # Abrir un diálogo para guardar la imagen 
        if archivo:
            try:
                fig.savefig(archivo) # Guardar la figura en el archivo seleccionado 
                messagebox.showinfo("Guardado", f"Gráfica guardada exitosamente en:\n{archivo}")
            except Exception as e: # Manejar cualquier error al guardar la gráfica      
                messagebox.showerror("Error", f"No se pudo guardar la gráfica:\n{str(e)}")

    # Botón para guardar
    btn_guardar = tk.Button(ventana_grafica, text="Guardar imagen", command=guardar_grafica) # Crear un botón para guardar la gráfica como imagen  
    btn_guardar.pack(pady=10) # Añadir un espacio vertical entre el botón y la gráfica  


def graficar_dataframe_seleccionado():
    """
    Genera una gráfica de los datos 'Cargo' y 'Abono' agrupados por fecha desde el archivo seleccionado.
    Verifica que el usuario haya seleccionado un archivo desde el Listbox. Luego agrupa 
    los valores por fecha y genera las sumas correspondientes para 'Cargo' y 'Abono'.
    Si faltan las columnas necesarias, muestra un mensaje de error.
    Llama a la función `abrir_ventana_grafica()` para mostrar la visualización.

    Requiere:
        - Un widget Listbox llamado `listbox`.
        - Un diccionario `archivos_cargados` con los DataFrames cargados.
        - La función `abrir_ventana_grafica(df1, df2, x_col, y1_col, y2_col)`.

    Retorna: None
    """
    seleccion = listbox.curselection() # Obtener la selección del Listbox
    if not seleccion: # Verificar si hay una selección en el Listbox    
        messagebox.showinfo("Información", "Selecciona primero un archivo para graficar.")
        return

    nombre = listbox.get(seleccion[0]) # Obtener el nombre del archivo seleccionado     
    df = archivos_cargados[nombre] # Obtener el DataFrame correspondiente al archivo seleccionado               
    df_cargo = df.groupby('Fecha')['Cargo'].sum().reset_index()
    df_cargo = df_cargo.query('Cargo > 0') # Agrupar de 'Cargo' por fecha y filtrar los que son mayores a 

    df_abono = df.groupby('Fecha')['Abono'].sum().reset_index()
    df_abono = df_abono.query('Abono > 0') # Agrupar de 'Abono' por fecha y filtrar los que son mayores a 0
    if 'Cargo' not in df.columns or 'Fecha' not in df.columns:
        messagebox.showerror("Error", "El DataFrame no tiene las columnas necesarias para graficar ('Fecha', 'Cargo','Abono').")
        return

    abrir_ventana_grafica(df_cargo,df_abono, 'Fecha', 'Cargo','Abono')

