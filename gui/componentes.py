import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.utilidades import obtener_nombre_archivo   
from core.pdf_parser import transformacion_pdf     
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from core.utilidades import archivos_cargados
from core.excel_loader import data_base 
from core.comparador import procesar_extracto_bancario 
from gui.ventana import listbox, frame_tabla,ventana,frame_busqueda, frame_estadisticas
import math
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conciliacion.log'),
        logging.StreamHandler()
    ]
)

# Función para mostrar un DataFrame en una tabla dentro de la interfaz gráfica
def mostrar_tabla(df):
    """
    Función para mostrar un DataFrame en una tabla dentro de la interfaz gráfica.

    Parámetros:
    ----------
    df : pandas.DataFrame
        DataFrame que se desea mostrar. Si está vacío, se muestra un mensaje informativo.
        Si contiene datos, se despliega en una tabla con barras de desplazamiento.
        Si no se puede mostrar, se lanza un mensaje de error.

    Retorna:
    -------
    None
    """
    # Verificar si el DataFrame está vacío antes de intentar mostrarlo          
    if df.empty:
        messagebox.showinfo("Información", "El DataFrame está vacío")
        return
    
    # Mostrar estadísticas
    mostrar_estadisticas(df)
    
    for widget in frame_tabla.winfo_children(): # Limpiar la tabla antes de mostrar un nuevo DataFrame  
        widget.destroy() # Limpiar los widgets existentes en el frame_tabla 

    columnas = list(df.columns)  # Obtener las columnas del DataFrame para mostrarlas en la tabla   

    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical") # Crear una barra de desplazamiento vertical 
    scrollbar_y.pack(side="right", fill="y")   # Añadir la barra de desplazamiento vertical al frame_tabla
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal")#Crear una barra de desplazamiento horizontal
    scrollbar_x.pack(side="bottom", fill="x") # Añadir la barra de desplazamiento horizontal al frame_tabla

    # 4) Crear Treeview
    columnas_df = [str(c) for c in list(df.columns)]
    columnas = ["N°"] + columnas_df

    tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show='headings', 
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    ) # Crear el Treeview para mostrar los datos del DataFrame  
    tabla.pack(expand=True, fill='both') # Añadir el Treeview al frame_tabla            

    scrollbar_y.config(command=tabla.yview) # Configurar la barra de desplazamiento vertical para controlar el Treeview
    scrollbar_x.config(command=tabla.xview) 

    tabla.heading("N°", text="N°")
    tabla.column("N°", width=50, anchor="center", stretch=False)

    def ancho_sugerido(serie, minimo=80, maximo=300, padding=20):
            try:
                maxlen = serie.astype(str).map(len).max()
                return max(minimo, min(maximo, maxlen + padding))
            except Exception:
                return minimo
    
    for col in columnas_df:
            tabla.heading(col, text=col)
            # Ancho heurístico por contenido
            try:
                w = ancho_sugerido(df[col])
            except Exception:
                w = 100
            tabla.column(col, width=w, anchor="center")
    
        # 7) Insertar filas (reemplazar NaN por vacío para no mostrar 'nan')
    def clean_value(v):
            try:
                if isinstance(v, float) and math.isnan(v):
                    return ""
            except Exception:
                pass
            return v
    
    for i, row in enumerate(df.itertuples(index=False, name=None), start=1):
            valores = [i] + [clean_value(v) for v in row]
            tabla.insert("", "end", values=valores)
    
        # 8) (Opcional) Zebra striping para legibilidad
    try:
            tabla.tag_configure("evenrow", background="#f5f5f5")
            for idx, item in enumerate(tabla.get_children("")):
                tag = "evenrow" if idx % 2 == 0 else ""
                tabla.item(item, tags=(tag,))
    except Exception:
            pass


def mostrar_archivo_seleccionado(event=None): # Mostrar el DataFrame del archivo seleccionado en el Listbox
    """
    Función para mostrar el DataFrame correspondiente al archivo seleccionado en el Listbox.
    Se puede llamar directamente o a través del evento de selección del Listbox.

    Parámetros:
    ----------
    event : Event, opcional
        Evento de selección del Listbox (por defecto None)

    Retorna: None
    """
    try:
        seleccion = listbox.curselection() # Obtener la selección actual del Listbox    
        if seleccion: # Si hay una selección válida 
            nombre = listbox.get(seleccion[0]) # Obtener el nombre del archivo seleccionado 
            df = archivos_cargados.get(nombre)
            if df is not None:
                mostrar_tabla(df)
            else:
                messagebox.showwarning("Advertencia", f"No se encontró el DataFrame para: {nombre}")
    except Exception as e:
        messagebox.showerror("Error", f"Error mostrando el archivo seleccionado:\n{e}")


def actualizar_lista_archivos(): # Actualizar la lista de archivos cargados en el Listbox
    """
    Función para actualizar el Listbox con los nombres de los archivos actualmente cargados.
    Elimina los elementos existentes del Listbox y agrega los nombres disponibles
    en el diccionario `archivos_cargados`.

    Retorna: None
    """
    listbox.delete(0, tk.END) # Limpiar el Listbox antes de actualizarlo    
    for nombre in archivos_cargados.keys(): # Iterar sobre los nombres de los archivos cargados
        listbox.insert(tk.END, nombre) # Insertar cada nombre de archivo en el Listbox


# Funciones para cargar archivos PDF y Excel
def cargar_pdf(): # Cargar un archivo PDF y procesarlo para extraer datos 

    """
    Función para cargar y procesar un archivo PDF para extraer datos relevantes.

    Abre un cuadro de diálogo para seleccionar un archivo PDF. Si el archivo es válido,
    se transforma en un DataFrame y se muestra. Si no contiene datos válidos,
    se muestra un mensaje de error.

    Retorna: None
    """  

    archivo = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")]) # Abrir un diálogo para seleccionar un archivo PDF
    if archivo: # Si se selecciona un archivo PDF   
        try: # Procesar el archivo PDF y extraer los datos relevantes   
            df = transformacion_pdf(archivo) # Llamar a la función de transformación del PDF para extraer los datos
            if df.empty: # Si el DataFrame resultante está vacío, lanzar una excepción
                raise ValueError("El archivo PDF no contiene datos válidos.")
            nombre = obtener_nombre_archivo(archivo) # Obtener el nombre del archivo sin la ruta completa   
            archivos_cargados[nombre] = df # Almacenar el DataFrame en el diccionario de archivos cargados
            actualizar_lista_archivos() # Actualizar la lista de archivos en el Listbox 
            listbox.selection_clear(0, tk.END) # Limpiar la selección actual del Listbox    
            listbox.selection_set(tk.END) # Seleccionar el último archivo cargado en el Listbox 
            mostrar_tabla(df) # Mostrar el DataFrame en la tabla
            logging.info(f"PDF cargado exitosamente: {nombre}")
        except Exception as e: # Manejar cualquier excepción que ocurra durante el procesamiento del PDF
            logging.error(f"Error al cargar {archivo}: {str(e)}")
            messagebox.showerror("Error", f"No se pudo procesar el PDF:\n{str(e)}")

def cargar_excel(): # Cargar un archivo Excel y procesarlo para extraer datos

    """
    Función para seleccionar un archivo PDF (extracto bancario) y un archivo Excel (base de datos) 
    y procesarlos para realizar una comparación.

    Permite además seleccionar la moneda y el año como filtros.
    Si no se selecciona alguno de los archivos, o la moneda, se muestra un mensaje de error.

    Retorna: None
    """

    archivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")]) # Abrir un diálogo para seleccionar un archivo Excel
    if archivo: # Si se selecciona un archivo Excel
        try: # Procesar el archivo Excel y extraer los datos relevantes         
            df = data_base(archivo) # Llamar a la función de carga del Excel para extraer los datos
            if df.empty:    # Si el DataFrame resultante está vacío, lanzar una excepción           
                raise ValueError("El archivo Excel no contiene datos válidos.")     
            nombre = obtener_nombre_archivo(archivo) # Obtener el nombre del archivo sin la ruta completa   
            archivos_cargados[nombre] = df # Almacenar el DataFrame en el diccionario de archivos cargados  
            actualizar_lista_archivos() # Actualizar la lista de archivos en el Listbox
            listbox.selection_clear(0, tk.END)  # Limpiar la selección actual del Listbox
            listbox.selection_set(tk.END)       # Seleccionar el último archivo cargado en el Listbox       
            mostrar_tabla(df) # Mostrar el DataFrame en la tabla
        except Exception as e: # Manejar cualquier excepción que ocurra durante el procesamiento del Excel          
            logging.error(f"Error al cargar {archivo}: {str(e)}")
            messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{str(e)}")

# Función para seleccionar archivos PDF y Excel, y procesarlos
def seleccionar_y_procesar(): # Seleccionar archivos PDF y Excel, y procesarlos para compararlos    
    """
    Función para seleccionar y procesar un archivo PDF (extracto bancario) y un archivo Excel (base de datos).

    Aplica filtros por moneda y año antes de comparar los datos.
    Si el usuario no selecciona alguno de los archivos o la moneda, se muestra un mensaje de error.

    Retorna:None
    """

    pdf_file = filedialog.askopenfilename(title="Selecciona el PDF bancario", filetypes=[("PDF Files", "*.pdf")]) # Abrir un diálogo para seleccionar un archivo PDF 
    if not pdf_file: # Si no se selecciona un archivo PDF, salir de la función  
        return
    excel_file = filedialog.askopenfilename(title="Selecciona el archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls")]) # Abrir un diálogo para seleccionar un archivo Excel
    if not excel_file: # Si no se selecciona un archivo Excel, salir de la función
        return 

    moneda = seleccionar_moneda() # Seleccionar la moneda para la comparación   
    
    if not moneda: # Si no se selecciona una moneda, mostrar un mensaje de error y salir de la función
        messagebox.showerror("Error", "Debes seleccionar una moneda.") 
        return
    
    anio = seleccionar_anio() # Seleccionar el año para filtrar la columna 'fecha'  
    if not anio:
        messagebox.showerror("Error", "Debes seleccionar un año.")
        return

    try: # Procesar el extracto bancario y comparar con los datos de la base
        df_resultado = procesar_extracto_bancario(pdf_file, excel_file, moneda,anio) # Llamar a la función de procesamiento del extracto bancario para obtener el DataFrame resultante  
        nombre_pdf = pdf_file.split("/")[-1] if "/" in pdf_file else pdf_file.split("\\")[-1]   # Obtener el nombre del archivo PDF sin la ruta completa    
        nombre_sin_ext = nombre_pdf.rsplit('.', 1)[0] # Eliminar la extensión del nombre del archivo PDF    
        nombre = f"Comparación {moneda}_{nombre_sin_ext}" # Crear un nombre para el DataFrame resultante basado en la moneda y el nombre del archivo PDF
        archivos_cargados[nombre] = df_resultado # Almacenar el DataFrame resultante en el diccionario de archivos cargados 
        actualizar_lista_archivos() # Actualizar la lista de archivos en el Listbox 
        listbox.selection_clear(0, tk.END) # Limpiar la selección actual del Listbox    
        listbox.selection_set(tk.END) # Seleccionar el último archivo cargado en el Listbox
        mostrar_tabla(df_resultado) # Mostrar el DataFrame resultante en la tabla           
        
    except Exception as e: # Manejar cualquier excepción que ocurra durante el procesamiento del extracto bancario
        messagebox.showerror("Error", f"No se pudo procesar la comparación:\n{str(e)}")     


# Función para exportar el DataFrame seleccionado a un archivo Excel
def exportar_actual():   # Exportar el DataFrame seleccionado a un archivo Excel 
    """
    Función para exportar el DataFrame actualmente seleccionado en el Listbox a un archivo Excel.

    Si no hay selección, se muestra un mensaje de error.
    Si hay selección, se solicita al usuario un nombre y ubicación para guardar el archivo.
    En caso de error durante la exportación, se muestra un mensaje de advertencia.

    Retorna: None
    """

    seleccion = listbox.curselection() # Obtener la selección actual del Listbox
    if not seleccion: # Si no hay ninguna selección, mostrar un mensaje de error y salir de la función  
        messagebox.showinfo("Exportar", "Selecciona primero un archivo de la lista.")
        return
    
    nombre = listbox.get(seleccion[0]) # Obtener el nombre del archivo seleccionado en el Listbox   
    df = archivos_cargados[nombre]
    # Pedir nombre de archivo al usuario
    nombre_archivo = simpledialog.askstring("Guardar como", "Nombre del archivo Excel (sin extensión):", initialvalue=nombre.replace(" ", "_"))  # Reemplazar espacios por guiones bajos en el nombre del archivo   

    if not nombre_archivo: # Si el usuario no ingresa un nombre, mostrar un mensaje y salir de la función
        return
    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=nombre_archivo + ".xlsx"
    ) # Abrir un diálogo para guardar el archivo Excel con el nombre proporcionado por el usuario
    if ruta: # Si se selecciona una ruta válida para guardar el archivo 
        try:
            df.to_excel(ruta, index=False) # Exportar el DataFrame a un archivo Excel en la ruta seleccionada       
            messagebox.showinfo("Exportar", f"Archivo guardado como:\n{ruta}")
        except Exception as e:  # Manejar cualquier excepción que ocurra durante la exportación del DataFrame a Excel   
            messagebox.showerror("Error", f"No se pudo exportar:\n{str(e)}")


# Función para seleccionar una moneda para filtrar los datos del DataFrame
def seleccionar_moneda(): # Seleccionar una moneda para filtrar los datos del DataFrame
    """
    Función para abrir un cuadro de diálogo y seleccionar una moneda (PEN o USD).

    Retorna:
    -------
    str
        Moneda seleccionada por el usuario ('PEN' o 'USD').
        Si el usuario cierra el cuadro de diálogo sin seleccionar una moneda, retorna None.
    """

    dialog = tk.Toplevel(ventana) # Crear un cuadro de diálogo para seleccionar la moneda   
    dialog.title("Selecciona la moneda") # Título del cuadro de diálogo 
    tk.Label(dialog, text="¿Qué moneda deseas comparar?").pack(padx=10, pady=10) # Etiqueta para indicar al usuario que seleccione una moneda   
    combo = ttk.Combobox(dialog, values=["PEN", "USD"], state="readonly") # Crear un Combobox para seleccionar la moneda
    combo.set("PEN") # Valor predeterminado del Combobox    
    combo.pack(padx=10, pady=10) # Crear el Combobox y añadirlo al cuadro de diálogo    
    seleccion = {"moneda": None} # Diccionario para almacenar la moneda seleccionada por el usuario

    def aceptar(): # Función para aceptar la selección de la moneda 
        seleccion["moneda"] = combo.get() # Obtener la moneda seleccionada por el usuario   
        dialog.destroy() # Cerrar el cuadro de diálogo  

    btn = tk.Button(dialog, text="Aceptar", command=aceptar) # Botón para aceptar la selección de la moneda 
    btn.pack(pady=10) # Añadir el botón al cuadro de diálogo para aceptar la selección de la moneda 
    dialog.grab_set() # Hacer que el cuadro de diálogo sea modal, bloqueando la ventana principal hasta que se cierre
    ventana.wait_window(dialog) # Esperar a que se cierre el cuadro de diálogo antes de continuar con la ejecución del programa 
    return seleccion["moneda"] # Retornar la moneda seleccionada por el usuario

# Función para seleccionar un año para filtrar la columna 'fecha'
def seleccionar_anio():  # Seleccionar un año para filtrar la columna 'fecha'   
    """
    Función para abrir un cuadro de diálogo y seleccionar el año para filtrar la columna 'fecha'.
    
    Retorna:
    int - Año seleccionado por el usuario.
    Si el usuario cierra el cuadro de diálogo sin seleccionar un año, retorna None
    """
    dialog = tk.Toplevel(ventana) # Crear un cuadro de diálogo para seleccionar el año              
    dialog.title("Selecciona el año")  # Título del cuadro de diálogo para seleccionar el  año
    tk.Label(dialog, text="¿Qué año deseas filtrar?").pack(padx=10, pady=10) # Etiqueta para indicar al usuario que seleccione un año
    
    # Crear un Combobox para seleccionar el año
    combo = ttk.Combobox(dialog, values=[2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028], state="readonly") # Crear un Combobox para seleccionar el año    
    combo.set(2026)  # Valor predeterminado
    combo.pack(padx=10, pady=10) # Añadir el Combobox al cuadro de diálogo para seleccionar el año
    
    seleccion = {"anio": None} # Diccionario para almacenar el año seleccionado por el usuario          

    # Función para aceptar la selección del año
    def aceptar():
        seleccion["anio"] = combo.get()  # Obtener el año seleccionado
        dialog.destroy() # Cerrar el cuadro de diálogo      

    # Botón para aceptar la selección
    btn = tk.Button(dialog, text="Aceptar", command=aceptar) # Crear un botón para aceptar la selección del año
    btn.pack(pady=10) # Añadir el botón al cuadro de diálogo para aceptar la selección del año
    
    dialog.grab_set() # Hacer que el cuadro de diálogo sea modal, bloqueando la ventana principal hasta que se cierre
    ventana.wait_window(dialog) # Esperar a que se cierre el cuadro de diálogo antes de continuar con la ejecución del programa
    return seleccion["anio"] # Retornar el año seleccionado por el usuario

# Asegúrate que estas líneas estén al final del archivo:
#listbox.pack(fill="y", expand=True) # Empaquetar el Listbox en la ventana principal
listbox.bind('<<ListboxSelect>>', mostrar_archivo_seleccionado) # Vincular el evento de selección del Listbox a la función mostrar_archivo_seleccionado 


def agregar_buscador():
    """
    Agrega un campo de búsqueda que permite filtrar los datos en la tabla.
    La búsqueda se realiza en tiempo real mientras el usuario escribe.
    """
    # Limpiar el frame de búsqueda antes de agregar nuevos elementos
    for widget in frame_busqueda.winfo_children():
        widget.destroy()
    
    # Agregar etiqueta
    tk.Label(frame_busqueda, text="Buscar:").pack(side="left", padx=(5,2))
    
    entry_buscar = tk.Entry(frame_busqueda)
    entry_buscar.pack(side="left", fill="x", expand=True, padx=5)
    
    def filtrar_datos(*args):
        # Obtener DataFrame actual
        seleccion = listbox.curselection()
        if not seleccion:
            return
            
        nombre = listbox.get(seleccion[0])
        df_original = archivos_cargados.get(nombre)
        
        if df_original is None:
            return
            
        texto = entry_buscar.get().lower().strip()
        
        if not texto:
            # Si no hay texto, mostrar todos los datos
            mostrar_tabla(df_original)
            return
            
        # Filtrar DataFrame
        try:
            mascara = df_original.astype(str).apply(
                lambda x: x.str.lower().str.contains(texto, na=False)
            ).any(axis=1)
            df_filtrado = df_original[mascara]
            mostrar_tabla(df_filtrado)
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {e}")
    
    # Vincular eventos
    entry_buscar.bind('<KeyRelease>', filtrar_datos)
    
    # Botón de búsqueda
    btn_buscar = tk.Button(frame_busqueda, text="🔍", command=filtrar_datos)
    btn_buscar.pack(side="left")
    
    # Botón para limpiar búsqueda
    def limpiar_busqueda():
        entry_buscar.delete(0, tk.END)
        filtrar_datos()
        
    btn_limpiar = tk.Button(frame_busqueda, text="✖", command=limpiar_busqueda)
    btn_limpiar.pack(side="left", padx=(2,5))

def mostrar_estadisticas(df):
    """
    Muestra estadísticas básicas del DataFrame seleccionado.
    
    Parámetros:
    ----------
    df : pandas.DataFrame
        DataFrame del cual se mostrarán las estadísticas
    
    Retorna:
    -------
    None
    """
    # Limpiar el frame de estadísticas antes de agregar nuevos elementos
    for widget in frame_estadisticas.winfo_children():
        widget.destroy()
    
    if df is None or df.empty:
        tk.Label(frame_estadisticas, text="No hay datos para mostrar", 
                font=("Arial", 10), fg="gray").pack(pady=5)
        return
    
    # Obtener estadísticas
    num_filas = len(df)
    num_columnas = len(df.columns)
    sum_haber = sum(df['Haber']) if 'Haber' in df.columns else 0
    sum_debe = sum(df['Debe']) if 'Debe' in df.columns else 0

    # Crear frame contenedor para las estadísticas
    stats_container = tk.Frame(frame_estadisticas, relief="ridge", borderwidth=2)
    stats_container.pack(fill="x", padx=3, pady=3)
    
    # Título
    tk.Label(stats_container, text="📊 Estadísticas del Archivo", 
            font=("Arial", 10, "bold"), fg="#2c3e50").pack(pady=(3,2))
    
    # Separador
    ttk.Separator(stats_container, orient="horizontal").pack(fill="x", padx=8, pady=5)
    
    # Frame para las métricas
    metrics_frame = tk.Frame(stats_container)
    metrics_frame.pack(fill="x", padx=7, pady=5)
    
    # Filas
    fila_frame = tk.Frame(metrics_frame)
    fila_frame.pack(side="left", expand=True, fill="x", padx=5)
    tk.Label(fila_frame, text="Filas:", font=("Arial", 9)).pack(anchor="w")
    tk.Label(fila_frame, text=f"{num_filas:,}", 
            font=("Arial", 11, "bold"), fg="#27ae60").pack(anchor="w")
    
    # Columnas
    tk.Label(fila_frame, text="Columnas:", font=("Arial", 9)).pack(anchor="w")
    tk.Label(fila_frame, text=f"{num_columnas}", 
            font=("Arial", 11, "bold"), fg="#3498db").pack(anchor="w")

    # Total de debe
    total_frame = tk.Frame(metrics_frame)
    total_frame.pack(side="left", expand=True, fill="x", padx=5)
    tk.Label(total_frame, text="Total Debe:", font=("Arial", 9)).pack(anchor="w")
    tk.Label(total_frame, text=f"{sum_debe:,}", 
            font=("Arial", 11, "bold"), fg="#e74c3c").pack(anchor="w")

    # Total Haber
    tk.Label(total_frame, text="Total Haber:", font=("Arial", 9)).pack(anchor="w")
    tk.Label(total_frame, text=f"{sum_haber:,}", 
            font=("Arial", 11, "bold"), fg="#e74c3c").pack(anchor="w")
    
    # Total diferencia
    tk.Label(total_frame, text="Total Diferencia:", font=("Arial", 9)).pack(anchor="w")
    if sum_debe - sum_haber < 0:
        tk.Label(total_frame, text=f"{sum_debe - sum_haber:.3f}", 
                font=("Arial", 11, "bold"), fg="#e74c3c").pack(anchor="w")
    else:
        tk.Label(total_frame, text=f"{sum_debe - sum_haber:.3f}", 
                font=("Arial", 11, "bold"), fg="#27ae60").pack(anchor="w")

    # Espacio final
    tk.Label(stats_container, text="", font=("Arial", 1)).pack(pady=2)