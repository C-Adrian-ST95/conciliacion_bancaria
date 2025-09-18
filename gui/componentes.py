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
from gui.ventana import listbox, frame_tabla,ventana
import pandas as pd

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
        messagebox.showinfo("Información", "El DataFrame está vacío. No hay datos para mostrar.")
        return
    for widget in frame_tabla.winfo_children(): # Limpiar la tabla antes de mostrar un nuevo DataFrame  
        widget.destroy() # Limpiar los widgets existentes en el frame_tabla 

    columnas = list(df.columns)  # Obtener las columnas del DataFrame para mostrarlas en la tabla   

    scrollbar_y = tk.Scrollbar(frame_tabla, orient="vertical") # Crear una barra de desplazamiento vertical 
    scrollbar_y.pack(side="right", fill="y")   # Añadir la barra de desplazamiento vertical al frame_tabla    
    scrollbar_x = tk.Scrollbar(frame_tabla, orient="horizontal")#Crear una barra de desplazamiento horizontal      
    scrollbar_x.pack(side="bottom", fill="x") # Añadir la barra de desplazamiento horizontal al frame_tabla 

    tabla = ttk.Treeview(
        frame_tabla,
        columns=["Número de fila"] + list(df.columns),
        show='headings', 
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    ) # Crear el Treeview para mostrar los datos del DataFrame  
    tabla.pack(expand=True, fill='both') # Añadir el Treeview al frame_tabla            

    scrollbar_y.config(command=tabla.yview) # Configurar la barra de desplazamiento vertical para controlar el Treeview
    scrollbar_x.config(command=tabla.xview) 

    tabla.heading("Número de fila", text="N°")
    tabla.column("Número de fila", width=30, anchor="center")

    for col in columnas: # Configurar las columnas del Treeview con los nombres del DataFrame
        tabla.heading(col, text=col) # Establecer el encabezado de cada columna 
        tabla.column(col, width=100, anchor="center") # Establecer el ancho de cada columna  

    for i, row in enumerate(df.itertuples(index=False), start=1):  # Enumerar desde 1
        tabla.insert("", "end", values=[i] + list(row))
    # Agregar la tabla al frame
    tabla.pack(fill="both", expand=True)

def mostrar_archivo_seleccionado(): # Mostrar el DataFrame del archivo seleccionado en el Listbox
    """
    Función para mostrar el DataFrame correspondiente al archivo seleccionado en el Listbox.
    Recupera el nombre del archivo seleccionado, accede al DataFrame desde `archivos_cargados`
    y lo muestra utilizando `mostrar_tabla()`.

    Retorna: None
    """
    seleccion = listbox.curselection() # Obtener la selección actual del Listbox    
    if seleccion: # Si hay una selección válida 
        nombre = listbox.get(seleccion[0]) # Obtener el nombre del archivo seleccionado 
        df = archivos_cargados[nombre] # Obtener el DataFrame correspondiente al nombre del archivo seleccionado    
        mostrar_tabla(df) 

    
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
def cargar_pdf(): 
    """
    Función mejorada para cargar y procesar archivos PDF de extractos bancarios.

    Esta función maneja la carga completa de archivos PDF, incluyendo validación
    de formato, procesamiento de datos, manejo de errores detallado y 
    retroalimentación visual para el usuario durante el proceso.

    Características:
    - Validación previa del archivo seleccionado
    - Indicador de progreso durante el procesamiento
    - Manejo detallado de errores con sugerencias específicas
    - Verificación de integridad de datos procesados
    - Actualización automática de la interfaz

    Flujo de procesamiento:
    1. Selección de archivo mediante diálogo
    2. Validación inicial del archivo
    3. Procesamiento del PDF con indicador de progreso
    4. Validación de datos extraídos
    5. Actualización de interfaz y lista de archivos
    6. Visualización de resultados en tabla

    Manejo de errores:
    - Archivos no válidos o dañados
    - Formatos PDF no soportados
    - Extractos sin datos válidos
    - Errores de procesamiento
    - Problemas de memoria con archivos grandes

    Retorna:
    --------
    None
        La función actualiza directamente la interfaz gráfica sin retornar valores.
        Los datos procesados se almacenan en el diccionario global 'archivos_cargados'.
    """

    archivo = filedialog.askopenfilename(
        title="Seleccionar extracto bancario PDF",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        initialdir=os.path.expanduser("~")  # Iniciar en directorio home del usuario
    )
    
    if not archivo:  # Usuario canceló la selección
        return
    
    # Validación inicial del archivo
    try:
        if not os.path.exists(archivo):
            messagebox.showerror("Error", f"El archivo seleccionado no existe:\n{archivo}")
            return
        
        if not archivo.lower().endswith('.pdf'):
            messagebox.showwarning(
                "Formato no válido", 
                f"Se esperaba un archivo PDF.\n\nArchivo seleccionado: {os.path.basename(archivo)}\n\n"
                "Por favor, seleccione un archivo con extensión .pdf"
            )
            return
        
        file_size = os.path.getsize(archivo)
        if file_size == 0:
            messagebox.showerror("Error", "El archivo PDF está vacío (0 bytes).")
            return
            
        if file_size > 50 * 1024 * 1024:  # 50MB
            result = messagebox.askyesno(
                "Archivo grande",
                f"El archivo es grande ({file_size / (1024*1024):.1f}MB).\n\n"
                "El procesamiento puede tomar varios minutos.\n"
                "¿Desea continuar?"
            )
            if not result:
                return
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel(ventana)
        progress_window.title("Procesando PDF...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()  # Modal
        
        # Centrar la ventana de progreso
        progress_window.geometry("+%d+%d" % (
            ventana.winfo_rootx() + 50,
            ventana.winfo_rooty() + 50
        ))
        
        tk.Label(progress_window, text="Procesando extracto bancario PDF...", 
                font=("Arial", 12)).pack(pady=20)
        
        progress_label = tk.Label(progress_window, text=f"Archivo: {os.path.basename(archivo)}")
        progress_label.pack(pady=5)
        
        status_label = tk.Label(progress_window, text="Iniciando procesamiento...")
        status_label.pack(pady=5)
        
        # Actualizar interfaz antes del procesamiento
        progress_window.update()
        
        # Procesar el archivo PDF
        status_label.config(text="Extrayendo datos del PDF...")
        progress_window.update()
        
        df = transformacion_pdf(archivo)
        
        status_label.config(text="Validando datos extraídos...")
        progress_window.update()
        
        # Validaciones adicionales
        if df.empty:
            progress_window.destroy()
            messagebox.showerror(
                "Datos no válidos", 
                "El archivo PDF no contiene transacciones válidas.\n\n"
                "Posibles causas:\n"
                "• El PDF no es un extracto bancario estándar\n"
                "• El archivo contiene solo imágenes escaneadas\n"
                "• El formato no coincide con el esperado\n\n"
                "Sugerencia: Verifique que sea un extracto bancario en formato texto."
            )
            return
        
        # Verificar calidad de los datos
        total_transactions = len(df)
        valid_amounts = df[(df['Cargo'] > 0) | (df['Abono'] > 0)]
        
        if len(valid_amounts) < total_transactions * 0.5:  # Menos del 50% tienen montos válidos
            result = messagebox.askyesno(
                "Calidad de datos cuestionable",
                f"Solo {len(valid_amounts)} de {total_transactions} transacciones "
                f"tienen montos válidos ({len(valid_amounts)/total_transactions*100:.1f}%).\n\n"
                "Esto podría indicar problemas en el formato del PDF.\n"
                "¿Desea continuar de todas formas?"
            )
            if not result:
                progress_window.destroy()
                return
        
        status_label.config(text="Actualizando interfaz...")
        progress_window.update()
        
        # Generar nombre único para el archivo
        nombre_base = obtener_nombre_archivo(archivo)
        nombre_sin_ext = os.path.splitext(nombre_base)[0]
        
        # Si ya existe un archivo con el mismo nombre, agregar número
        contador = 1
        nombre_final = nombre_base
        while nombre_final in archivos_cargados:
            nombre_final = f"{nombre_sin_ext} ({contador}).pdf"
            contador += 1
        
        # Almacenar el DataFrame
        archivos_cargados[nombre_final] = df
        
        # Actualizar interfaz
        actualizar_lista_archivos()
        listbox.selection_clear(0, tk.END)
        
        # Seleccionar el archivo recién cargado
        for i in range(listbox.size()):
            if listbox.get(i) == nombre_final:
                listbox.selection_set(i)
                break
        
        mostrar_tabla(df)
        
        progress_window.destroy()
        
        # Mostrar resumen de carga exitosa
        messagebox.showinfo(
            "PDF cargado exitosamente",
            f"Archivo: {nombre_final}\n"
            f"Transacciones encontradas: {len(df)}\n"
            f"Total cargos: {df['Cargo'].sum():,.2f}\n"
            f"Total abonos: {df['Abono'].sum():,.2f}\n"
            f"Saldo final: {df['Saldo'].iloc[-1]:,.2f}"
        )
        
    except Exception as e:
        # Cerrar ventana de progreso si existe
        try:
            progress_window.destroy()
        except:
            pass
        
        error_details = str(e)
        if "No se encontraron transacciones" in error_details:
            messagebox.showerror(
                "Sin transacciones válidas",
                f"No se pudieron extraer transacciones del PDF.\n\n"
                f"Archivo: {os.path.basename(archivo)}\n\n"
                f"Posibles soluciones:\n"
                f"• Verificar que sea un extracto bancario estándar\n"
                f"• Asegurar que el PDF no sea una imagen escaneada\n"
                f"• Comprobar que el formato coincida con el esperado\n"
                f"• Intentar con un archivo diferente"
            )
        elif "PDF no contiene texto" in error_details:
            messagebox.showerror(
                "PDF sin texto",
                f"El archivo PDF no contiene texto válido.\n\n"
                f"Esto puede ocurrir si:\n"
                f"• El PDF es una imagen escaneada\n"
                f"• El archivo está dañado\n"
                f"• El PDF está protegido\n\n"
                f"Sugerencia: Use un PDF que contenga texto seleccionable."
            )
        else:
            messagebox.showerror(
                "Error al procesar PDF",
                f"No se pudo procesar el archivo PDF.\n\n"
                f"Archivo: {os.path.basename(archivo)}\n"
                f"Error: {error_details}\n\n"
                f"Verifique que el archivo no esté dañado y sea un extracto bancario válido."
            )

def cargar_excel():
    """
    Función mejorada para cargar y procesar archivos Excel de bases de datos contables.

    Esta función proporciona una experiencia completa de carga de archivos Excel,
    incluyendo validación exhaustiva, procesamiento con retroalimentación visual,
    manejo detallado de errores y verificación de integridad de datos.

    Características avanzadas:
    - Validación previa de formato y contenido
    - Indicador de progreso para archivos grandes
    - Verificación de columnas requeridas
    - Análisis de calidad de datos
    - Resumen estadístico post-carga
    - Manejo robusto de errores con sugerencias específicas

    Flujo de procesamiento:
    1. Selección de archivo Excel con filtros apropiados
    2. Validación inicial de formato y accesibilidad
    3. Carga con verificación de estructura
    4. Procesamiento y transformación de datos
    5. Validación de integridad y calidad
    6. Actualización de interfaz con retroalimentación

    Formatos soportados:
    - .xlsx (Excel 2007+)
    - .xls (Excel 97-2003)
    - .xlsm (Excel con macros)

    Columnas requeridas:
    - ANO, MES, DIA (para construcción de fechas)
    - Columnas opcionales: NUM OPERACION, N° DOCUMENTO, NOP, MONEDA, MONTO

    Retorna:
    --------
    None
        La función actualiza directamente la interfaz gráfica.
        Los datos procesados se almacenan en 'archivos_cargados'.
    """

    archivo = filedialog.askopenfilename(
        title="Seleccionar base de datos contable (Excel)",
        filetypes=[
            ("Archivos Excel", "*.xlsx *.xls *.xlsm"),
            ("Excel 2007+", "*.xlsx"),
            ("Excel 97-2003", "*.xls"),
            ("Excel con macros", "*.xlsm"),
            ("Todos los archivos", "*.*")
        ],
        initialdir=os.path.expanduser("~")
    )
    
    if not archivo:  # Usuario canceló la selección
        return
    
    try:
        # Validación inicial
        if not os.path.exists(archivo):
            messagebox.showerror("Error", f"El archivo seleccionado no existe:\n{archivo}")
            return
        
        # Verificar extensión
        valid_extensions = ['.xlsx', '.xls', '.xlsm']
        if not any(archivo.lower().endswith(ext) for ext in valid_extensions):
            messagebox.showwarning(
                "Formato no válido",
                f"Se esperaba un archivo Excel (.xlsx, .xls, .xlsm).\n\n"
                f"Archivo seleccionado: {os.path.basename(archivo)}\n\n"
                "Por favor, seleccione un archivo Excel válido."
            )
            return
        
        file_size = os.path.getsize(archivo)
        if file_size == 0:
            messagebox.showerror("Error", "El archivo Excel está vacío (0 bytes).")
            return
        
        # Advertencia para archivos grandes
        if file_size > 20 * 1024 * 1024:  # 20MB
            result = messagebox.askyesno(
                "Archivo grande",
                f"El archivo Excel es grande ({file_size / (1024*1024):.1f}MB).\n\n"
                "La carga puede tomar tiempo y consumir memoria.\n"
                "¿Desea continuar?"
            )
            if not result:
                return
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel(ventana)
        progress_window.title("Cargando Excel...")
        progress_window.geometry("450x180")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        # Centrar ventana
        progress_window.geometry("+%d+%d" % (
            ventana.winfo_rootx() + 50,
            ventana.winfo_rooty() + 50
        ))
        
        tk.Label(progress_window, text="Cargando base de datos contable...", 
                font=("Arial", 12, "bold")).pack(pady=15)
        
        file_label = tk.Label(progress_window, text=f"Archivo: {os.path.basename(archivo)}")
        file_label.pack(pady=5)
        
        status_label = tk.Label(progress_window, text="Iniciando carga...", fg="blue")
        status_label.pack(pady=5)
        
        size_label = tk.Label(progress_window, text=f"Tamaño: {file_size / 1024:.1f} KB")
        size_label.pack(pady=5)
        
        progress_window.update()
        
        # Intentar abrir archivo para verificar si está en uso
        status_label.config(text="Verificando acceso al archivo...")
        progress_window.update()
        
        try:
            with open(archivo, 'rb') as test_file:
                test_file.read(1)
        except PermissionError:
            progress_window.destroy()
            messagebox.showerror(
                "Archivo en uso",
                f"No se puede abrir el archivo Excel.\n\n"
                f"Posibles causas:\n"
                f"• El archivo está abierto en Excel\n"
                f"• Sin permisos de lectura\n"
                f"• Archivo bloqueado por otra aplicación\n\n"
                f"Cierre Excel y cualquier aplicación que use el archivo, luego intente nuevamente."
            )
            return
        
        # Procesar archivo Excel
        status_label.config(text="Cargando datos desde Excel...")
        progress_window.update()
        
        df = data_base(archivo)
        
        status_label.config(text="Validando estructura de datos...")
        progress_window.update()
        
        # Validaciones adicionales post-carga
        if df.empty:
            progress_window.destroy()
            messagebox.showerror(
                "Datos no válidos",
                "El archivo Excel no contiene datos válidos.\n\n"
                "Verifique que:\n"
                "• El archivo tenga datos en la primera hoja\n"
                "• Las filas no estén completamente vacías\n"
                "• El formato sea compatible con Excel estándar"
            )
            return
        
        # Verificar calidad de fechas
        fechas_validas = df['Fecha'].notna().sum()
        total_registros = len(df)
        
        if fechas_validas < total_registros * 0.8:  # Menos del 80% tienen fechas válidas
            progress_window.destroy()
            result = messagebox.askyesno(
                "Calidad de fechas cuestionable",
                f"Solo {fechas_validas} de {total_registros} registros "
                f"tienen fechas válidas ({fechas_validas/total_registros*100:.1f}%).\n\n"
                "Esto puede causar problemas en la comparación con PDFs.\n"
                "¿Desea continuar de todas formas?"
            )
            if not result:
                return
            
            # Recrear ventana de progreso
            progress_window = tk.Toplevel(ventana)
            progress_window.title("Finalizando carga...")
            progress_window.geometry("400x120")
            progress_window.resizable(False, False)
            progress_window.grab_set()
            status_label = tk.Label(progress_window, text="Finalizando...")
            status_label.pack(pady=20)
        
        status_label.config(text="Actualizando interfaz...")
        progress_window.update()
        
        # Generar nombre único
        nombre_base = obtener_nombre_archivo(archivo)
        nombre_sin_ext = os.path.splitext(nombre_base)[0]
        
        contador = 1
        nombre_final = nombre_base
        while nombre_final in archivos_cargados:
            nombre_final = f"{nombre_sin_ext} ({contador}){os.path.splitext(nombre_base)[1]}"
            contador += 1
        
        # Almacenar datos
        archivos_cargados[nombre_final] = df
        
        # Actualizar interfaz
        actualizar_lista_archivos()
        listbox.selection_clear(0, tk.END)
        
        # Seleccionar archivo recién cargado
        for i in range(listbox.size()):
            if listbox.get(i) == nombre_final:
                listbox.selection_set(i)
                break
        
        mostrar_tabla(df)
        progress_window.destroy()
        
        # Generar estadísticas para el resumen
        monedas_info = ""
        if 'MONEDA' in df.columns:
            monedas_unicas = df['MONEDA'].value_counts()
            monedas_info = f"\nMonedas: {', '.join(monedas_unicas.index.tolist())}"
        
        monto_info = ""
        if 'MONTO' in df.columns:
            monto_total = df['MONTO'].sum()
            monto_info = f"\nMonto total: {monto_total:,.2f}"
        
        # Mostrar resumen de carga exitosa
        messagebox.showinfo(
            "Excel cargado exitosamente",
            f"Archivo: {nombre_final}\n"
            f"Registros cargados: {len(df):,}\n"
            f"Columnas: {len(df.columns)}\n"
            f"Rango de fechas: {df['Fecha'].min()} - {df['Fecha'].max()}"
            f"{monedas_info}"
            f"{monto_info}"
        )
        
    except Exception as e:
        # Cerrar ventana de progreso si existe
        try:
            progress_window.destroy()
        except:
            pass
        
        error_details = str(e)
        
        if "Faltan columnas requeridas" in error_details:
            messagebox.showerror(
                "Estructura incorrecta",
                f"El archivo Excel no tiene la estructura requerida.\n\n"
                f"Error: {error_details}\n\n"
                f"El archivo debe contener al menos las columnas:\n"
                f"• ANO (año de la transacción)\n"
                f"• MES (mes de la transacción)\n"
                f"• DIA (día de la transacción)\n\n"
                f"Verifique la estructura de su archivo Excel."
            )
        elif "archivo está abierto" in error_details.lower() or "permission" in error_details.lower():
            messagebox.showerror(
                "Archivo no disponible",
                f"No se puede acceder al archivo Excel.\n\n"
                f"Posibles soluciones:\n"
                f"• Cierre Excel si el archivo está abierto\n"
                f"• Verifique permisos de lectura\n"
                f"• Intente copiar el archivo a otra ubicación\n"
                f"• Reinicie la aplicación"
            )
        elif "formato" in error_details.lower() or "unsupported" in error_details.lower():
            messagebox.showerror(
                "Formato no soportado",
                f"El formato del archivo Excel no es compatible.\n\n"
                f"Soluciones sugeridas:\n"
                f"• Guarde el archivo como .xlsx desde Excel\n"
                f"• Verifique que no esté dañado\n"
                f"• Use Excel para reparar el archivo\n"
                f"• Pruebe con un archivo diferente"
            )
        else:
            messagebox.showerror(
                "Error al cargar Excel",
                f"No se pudo procesar el archivo Excel.\n\n"
                f"Archivo: {os.path.basename(archivo)}\n"
                f"Error: {error_details}\n\n"
                f"Verifique que el archivo sea un Excel válido con datos contables."
            )

# Función para seleccionar archivos PDF y Excel, y procesarlos
def seleccionar_y_procesar():
    """
    Función integral para comparación avanzada entre extractos bancarios PDF y bases de datos Excel.

    Esta función proporciona un flujo completo de comparación de datos financieros,
    incluyendo selección guiada de archivos, configuración de parámetros de filtrado,
    procesamiento con retroalimentación visual y análisis de resultados detallado.

    Características principales:
    - Selección guiada de archivos con validación previa
    - Configuración de filtros (moneda y año) con valores sugeridos
    - Procesamiento con indicadores de progreso
    - Validación de consistencia entre archivos
    - Análisis de calidad de coincidencias
    - Generación de reportes de diferencias
    - Manejo robusto de errores con sugerencias específicas

    Flujo de procesamiento:
    1. Selección de archivo PDF (extracto bancario)
    2. Selección de archivo Excel (base de datos contable)
    3. Configuración de filtros (moneda y año)
    4. Validación de compatibilidad entre archivos
    5. Procesamiento de comparación
    6. Análisis de resultados y estadísticas
    7. Actualización de interfaz con datos comparados

    Parámetros de filtrado:
    - Moneda: PEN, USD (configurable)
    - Año: 2020-2026 (configurable)

    Tipos de comparación realizados:
    - Coincidencias exactas por fecha y monto
    - Detección de inconsistencias de saldo
    - Identificación de transacciones duplicadas
    - Análisis de diferencias temporales

    Retorna:
    --------
    None
        La función actualiza la interfaz gráfica con los resultados de la comparación.
        Los datos procesados se almacenan en 'archivos_cargados' con un nombre descriptivo.
    """
    
    # Paso 1: Selección de archivo PDF con validación
    pdf_file = filedialog.askopenfilename(
        title="1. Seleccionar extracto bancario (PDF)",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        initialdir=os.path.expanduser("~")
    )
    
    if not pdf_file:
        return  # Usuario canceló
    
    # Validación inicial del PDF
    try:
        if not os.path.exists(pdf_file):
            messagebox.showerror("Error", f"El archivo PDF no existe:\n{pdf_file}")
            return
        
        if not pdf_file.lower().endswith('.pdf'):
            messagebox.showwarning("Formato incorrecto", "El primer archivo debe ser un PDF de extracto bancario.")
            return
        
        pdf_size = os.path.getsize(pdf_file)
        if pdf_size == 0:
            messagebox.showerror("Error", "El archivo PDF está vacío.")
            return
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al validar el archivo PDF:\n{str(e)}")
        return
    
    # Paso 2: Selección de archivo Excel con validación
    excel_file = filedialog.askopenfilename(
        title="2. Seleccionar base de datos contable (Excel)",
        filetypes=[
            ("Archivos Excel", "*.xlsx *.xls *.xlsm"),
            ("Excel 2007+", "*.xlsx"),
            ("Excel 97-2003", "*.xls"),
            ("Todos los archivos", "*.*")
        ],
        initialdir=os.path.dirname(pdf_file)  # Sugerir misma carpeta que PDF
    )
    
    if not excel_file:
        return  # Usuario canceló
    
    # Validación inicial del Excel
    try:
        if not os.path.exists(excel_file):
            messagebox.showerror("Error", f"El archivo Excel no existe:\n{excel_file}")
            return
        
        valid_extensions = ['.xlsx', '.xls', '.xlsm']
        if not any(excel_file.lower().endswith(ext) for ext in valid_extensions):
            messagebox.showwarning("Formato incorrecto", "El segundo archivo debe ser un Excel válido.")
            return
        
        excel_size = os.path.getsize(excel_file)
        if excel_size == 0:
            messagebox.showerror("Error", "El archivo Excel está vacío.")
            return
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al validar el archivo Excel:\n{str(e)}")
        return
    
    # Mostrar resumen de archivos seleccionados
    archivos_info = (
        f"Archivos seleccionados:\n\n"
        f"PDF: {os.path.basename(pdf_file)} ({pdf_size / 1024:.1f} KB)\n"
        f"Excel: {os.path.basename(excel_file)} ({excel_size / 1024:.1f} KB)\n\n"
        f"A continuación configurará los filtros de comparación."
    )
    messagebox.showinfo("Archivos seleccionados", archivos_info)
    
    # Paso 3: Selección de moneda con información contextual
    try:
        moneda = seleccionar_moneda_avanzada()
    except:
        # Fallback a función simple si hay problemas
        moneda = seleccionar_moneda()
    
    if not moneda:
        messagebox.showwarning("Operación cancelada", "Debe seleccionar una moneda para continuar.")
        return
    
    # Paso 4: Selección de año con información contextual
    try:
        anio = seleccionar_anio_avanzado()
    except:
        # Fallback a función simple si hay problemas
        anio = seleccionar_anio()
    
    if not anio:
        messagebox.showwarning("Operación cancelada", "Debe seleccionar un año para continuar.")
        return
    
    # Confirmación final antes del procesamiento
    confirmacion = messagebox.askyesno(
        "Confirmar procesamiento",
        f"¿Proceder con la comparación?\n\n"
        f"PDF: {os.path.basename(pdf_file)}\n"
        f"Excel: {os.path.basename(excel_file)}\n"
        f"Moneda: {moneda}\n"
        f"Año: {anio}\n\n"
        f"Este proceso puede tomar varios minutos dependiendo del tamaño de los archivos."
    )
    
    if not confirmacion:
        return
    
    # Crear ventana de progreso avanzada
    progress_window = tk.Toplevel(ventana)
    progress_window.title("Comparando archivos...")
    progress_window.geometry("500x250")
    progress_window.resizable(False, False)
    progress_window.grab_set()
    
    # Centrar ventana
    progress_window.geometry("+%d+%d" % (
        ventana.winfo_rootx() + 100,
        ventana.winfo_rooty() + 100
    ))
    
    tk.Label(progress_window, text="Comparación de extracto bancario vs base de datos",
            font=("Arial", 12, "bold")).pack(pady=15)
    
    pdf_label = tk.Label(progress_window, text=f"PDF: {os.path.basename(pdf_file)}")
    pdf_label.pack(pady=2)
    
    excel_label = tk.Label(progress_window, text=f"Excel: {os.path.basename(excel_file)}")
    excel_label.pack(pady=2)
    
    filter_label = tk.Label(progress_window, text=f"Filtros: {moneda} - {anio}")
    filter_label.pack(pady=2)
    
    status_label = tk.Label(progress_window, text="Iniciando comparación...", fg="blue", font=("Arial", 10))
    status_label.pack(pady=10)
    
    progress_detail = tk.Label(progress_window, text="", fg="gray")
    progress_detail.pack(pady=5)
    
    try:
        progress_window.update()
        
        # Paso 5: Procesamiento con retroalimentación detallada
        status_label.config(text="Paso 1/4: Cargando y procesando PDF...")
        progress_detail.config(text="Extrayendo transacciones del extracto bancario")
        progress_window.update()
        
        # Verificar que el PDF tenga transacciones antes de continuar
        try:
            df_pdf_test = transformacion_pdf(pdf_file)
            if df_pdf_test.empty:
                progress_window.destroy()
                messagebox.showerror(
                    "PDF sin datos",
                    "El archivo PDF no contiene transacciones válidas.\n\n"
                    "Verifique que sea un extracto bancario estándar con transacciones."
                )
                return
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error en PDF", f"Error al procesar el PDF:\n{str(e)}")
            return
        
        status_label.config(text="Paso 2/4: Cargando y procesando Excel...")
        progress_detail.config(text="Cargando base de datos contable")
        progress_window.update()
        
        # Verificar que el Excel tenga datos antes de continuar
        try:
            df_excel_test = data_base(excel_file)
            if df_excel_test.empty:
                progress_window.destroy()
                messagebox.showerror(
                    "Excel sin datos",
                    "El archivo Excel no contiene datos válidos.\n\n"
                    "Verifique que tenga registros contables y las columnas requeridas."
                )
                return
            
            # Verificar que tenga datos para la moneda seleccionada
            if 'MONEDA' in df_excel_test.columns:
                registros_moneda = df_excel_test[df_excel_test['MONEDA'] == moneda]
                if registros_moneda.empty:
                    progress_window.destroy()
                    result = messagebox.askyesno(
                        "Sin datos para la moneda",
                        f"No se encontraron registros en {moneda} en el archivo Excel.\n\n"
                        f"Monedas disponibles: {list(df_excel_test['MONEDA'].unique())}\n\n"
                        f"¿Desea continuar de todas formas? (La comparación puede no encontrar coincidencias)"
                    )
                    if not result:
                        return
                    
                    # Recrear ventana de progreso
                    progress_window = tk.Toplevel(ventana)
                    progress_window.title("Continuando comparación...")
                    progress_window.geometry("450x200")
                    progress_window.grab_set()
                    status_label = tk.Label(progress_window, text="Continuando...", fg="blue")
                    status_label.pack(pady=20)
                    progress_detail = tk.Label(progress_window, text="", fg="gray")
                    progress_detail.pack(pady=5)
                    
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error en Excel", f"Error al procesar el Excel:\n{str(e)}")
            return
        
        status_label.config(text="Paso 3/4: Realizando comparación...")
        progress_detail.config(text="Buscando coincidencias entre PDF y Excel")
        progress_window.update()
        
        # Realizar la comparación
        df_resultado = procesar_extracto_bancario(pdf_file, excel_file, moneda, anio)
        
        status_label.config(text="Paso 4/4: Analizando resultados...")
        progress_detail.config(text="Generando estadísticas de comparación")
        progress_window.update()
        
        # Análisis de resultados
        total_transacciones = len(df_resultado)
        coincidencias = df_resultado[df_resultado['NOP'] != '---']
        sin_coincidencias = df_resultado[df_resultado['NOP'] == '---']
        
        tasa_coincidencia = len(coincidencias) / total_transacciones * 100 if total_transacciones > 0 else 0
        
        # Generar nombre descriptivo para el resultado
        nombre_pdf = os.path.splitext(os.path.basename(pdf_file))[0]
        timestamp = pd.Timestamp.now().strftime("%H%M")
        nombre_resultado = f"Comparación_{moneda}_{anio}_{nombre_pdf}_{timestamp}"
        
        # Almacenar resultado
        archivos_cargados[nombre_resultado] = df_resultado
        
        # Actualizar interfaz
        actualizar_lista_archivos()
        listbox.selection_clear(0, tk.END)
        
        # Seleccionar el resultado recién creado
        for i in range(listbox.size()):
            if listbox.get(i) == nombre_resultado:
                listbox.selection_set(i)
                break
        
        mostrar_tabla(df_resultado)
        progress_window.destroy()
        
        # Mostrar resumen detallado de resultados
        resumen = (
            f"Comparación completada exitosamente\n\n"
            f"📊 ESTADÍSTICAS:\n"
            f"Total de transacciones procesadas: {total_transacciones:,}\n"
            f"Coincidencias encontradas: {len(coincidencias):,}\n"
            f"Sin coincidencias: {len(sin_coincidencias):,}\n"
            f"Tasa de coincidencia: {tasa_coincidencia:.1f}%\n\n"
            f"🔍 ANÁLISIS:\n"
        )
        
        if tasa_coincidencia >= 80:
            resumen += "✅ Excelente coincidencia entre archivos"
        elif tasa_coincidencia >= 60:
            resumen += "⚠️ Coincidencia moderada - revisar transacciones sin coincidencias"
        elif tasa_coincidencia >= 40:
            resumen += "❌ Baja coincidencia - verificar archivos y filtros"
        else:
            resumen += "⛔ Muy baja coincidencia - posibles problemas en los datos"
        
        resumen += f"\n\n📄 Resultado guardado como: {nombre_resultado}"
        
        messagebox.showinfo("Comparación completada", resumen)
        
        # Sugerir exportar si hay muchas transacciones
        if total_transacciones > 100:
            export_suggestion = messagebox.askyesno(
                "Exportar resultados",
                f"Se procesaron {total_transacciones:,} transacciones.\n\n"
                "¿Desea exportar los resultados a Excel para análisis detallado?"
            )
            if export_suggestion:
                exportar_actual()
        
    except Exception as e:
        # Cerrar ventana de progreso si existe
        try:
            progress_window.destroy()
        except:
            pass
        
        error_details = str(e)
        
        # Categorizar errores y proporcionar soluciones específicas
        if "moneda" in error_details.lower() and "no encontrada" in error_details.lower():
            messagebox.showerror(
                "Error de moneda",
                f"La moneda '{moneda}' no se encontró en los datos Excel.\n\n"
                f"Soluciones:\n"
                f"• Verifique que el Excel contenga registros en {moneda}\n"
                f"• Revise la columna MONEDA en el archivo Excel\n"
                f"• Intente con una moneda diferente\n"
                f"• Verifique la estructura del archivo Excel"
            )
        elif "fecha" in error_details.lower():
            messagebox.showerror(
                "Error de fechas",
                f"Problema al procesar las fechas.\n\n"
                f"Año seleccionado: {anio}\n\n"
                f"Soluciones:\n"
                f"• Verifique que el año {anio} tenga datos en ambos archivos\n"
                f"• Revise las columnas ANO/MES/DIA en el Excel\n"
                f"• Asegúrese de que las fechas del PDF sean del año {anio}\n"
                f"• Intente con un año diferente"
            )
        elif "memoria" in error_details.lower() or "memory" in error_details.lower():
            messagebox.showerror(
                "Error de memoria",
                f"Los archivos son demasiado grandes para procesar.\n\n"
                f"Soluciones:\n"
                f"• Divida los archivos en períodos más pequeños\n"
                f"• Use archivos con menos transacciones\n"
                f"• Cierre otras aplicaciones para liberar memoria\n"
                f"• Reinicie la aplicación"
            )
        else:
            messagebox.showerror(
                "Error en comparación",
                f"No se pudo completar la comparación.\n\n"
                f"Archivos:\n"
                f"PDF: {os.path.basename(pdf_file)}\n"
                f"Excel: {os.path.basename(excel_file)}\n"
                f"Filtros: {moneda}, {anio}\n\n"
                f"Error: {error_details}\n\n"
                f"Verifique que los archivos sean válidos y compatibles."
            )     


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


def seleccionar_moneda_avanzada():
    """
    Función avanzada para seleccionar moneda con información contextual y validación.
    
    Proporciona una interfaz mejorada para la selección de moneda con:
    - Información sobre cada tipo de moneda
    - Valores predeterminados inteligentes
    - Validación de selección
    - Cancelación segura
    
    Retorna:
    --------
    str or None
        Código de moneda seleccionado ('PEN', 'USD') o None si se cancela.
    """
    dialog = tk.Toplevel(ventana)
    dialog.title("Selección de Moneda para Comparación")
    dialog.geometry("450x300")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Centrar ventana
    dialog.geometry("+%d+%d" % (
        ventana.winfo_rootx() + 100,
        ventana.winfo_rooty() + 100
    ))
    
    # Título y descripción
    tk.Label(dialog, text="Seleccionar Moneda para Comparación", 
             font=("Arial", 14, "bold")).pack(pady=15)
    
    tk.Label(dialog, text="Seleccione la moneda que desea usar para filtrar y comparar\nlos datos entre el PDF bancario y el Excel contable.",
             justify="center").pack(pady=10)
    
    # Frame para opciones de moneda
    moneda_frame = tk.Frame(dialog)
    moneda_frame.pack(pady=15)
    
    tk.Label(moneda_frame, text="Monedas disponibles:", font=("Arial", 10, "bold")).pack()
    
    combo = ttk.Combobox(moneda_frame, values=["PEN", "USD"], state="readonly", width=15)
    combo.set("PEN")  # Valor predeterminado
    combo.pack(pady=10)
    
    # Información sobre monedas
    info_frame = tk.Frame(dialog)
    info_frame.pack(pady=10)
    
    tk.Label(info_frame, text="ℹ️ Información:", font=("Arial", 9, "bold")).pack()
    tk.Label(info_frame, text="• PEN: Nuevos Soles Peruanos\n• USD: Dólares Estadounidenses", 
             justify="left", fg="gray").pack()
    
    seleccion = {"moneda": None}
    
    def aceptar():
        if combo.get():
            seleccion["moneda"] = combo.get()
            dialog.destroy()
        else:
            messagebox.showwarning("Selección requerida", "Debe seleccionar una moneda.")
    
    def cancelar():
        dialog.destroy()
    
    # Botones
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Aceptar", command=aceptar, 
              bg="#4CAF50", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancelar", command=cancelar, 
              bg="#f44336", fg="white", width=10).pack(side="left", padx=5)
    
    # Manejo de eventos
    dialog.bind('<Return>', lambda e: aceptar())
    dialog.bind('<Escape>', lambda e: cancelar())
    
    dialog.wait_window(dialog)
    return seleccion["moneda"]

def seleccionar_anio_avanzado():
    """
    Función avanzada para seleccionar año con información contextual y validación.
    
    Proporciona una interfaz mejorada para la selección de año con:
    - Rango de años disponibles con contexto
    - Año predeterminado inteligente (año actual)
    - Información sobre el impacto de la selección
    - Validación de selección
    
    Retorna:
    --------
    str or None
        Año seleccionado como string o None si se cancela.
    """
    dialog = tk.Toplevel(ventana)
    dialog.title("Selección de Año para Filtrado")
    dialog.geometry("450x350")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Centrar ventana
    dialog.geometry("+%d+%d" % (
        ventana.winfo_rootx() + 100,
        ventana.winfo_rooty() + 100
    ))
    
    # Título y descripción
    tk.Label(dialog, text="Seleccionar Año para Filtrado de Fechas", 
             font=("Arial", 14, "bold")).pack(pady=15)
    
    description = tk.Label(dialog, 
                          text="El año seleccionado se usará para:\n"
                               "• Completar las fechas del PDF (que solo tienen día/mes)\n"
                               "• Filtrar los registros del Excel por año\n"
                               "• Realizar la comparación entre ambos archivos",
                          justify="center")
    description.pack(pady=10)
    
    # Frame para selección de año
    year_frame = tk.Frame(dialog)
    year_frame.pack(pady=15)
    
    tk.Label(year_frame, text="Año para procesar:", font=("Arial", 10, "bold")).pack()
    
    # Obtener año actual como predeterminado
    current_year = pd.Timestamp.now().year
    years_list = list(range(2020, 2027))
    
    combo = ttk.Combobox(year_frame, values=years_list, state="readonly", width=15)
    
    # Establecer año predeterminado (actual si está en la lista, sino el más reciente)
    if current_year in years_list:
        combo.set(current_year)
    else:
        combo.set(max(years_list))
    
    combo.pack(pady=10)
    
    # Información contextual
    info_frame = tk.Frame(dialog)
    info_frame.pack(pady=10)
    
    tk.Label(info_frame, text="ℹ️ Información importante:", font=("Arial", 9, "bold")).pack()
    
    info_text = (
        f"• Año actual: {current_year}\n"
        f"• Rango disponible: {min(years_list)} - {max(years_list)}\n"
        f"• Se recomienda usar el año del período que desea analizar\n"
        f"• Verifique que ambos archivos contengan datos del año seleccionado"
    )
    
    tk.Label(info_frame, text=info_text, justify="left", fg="gray").pack()
    
    # Advertencia
    warning_frame = tk.Frame(dialog)
    warning_frame.pack(pady=5)
    
    tk.Label(warning_frame, text="⚠️ Nota:", font=("Arial", 9, "bold"), fg="orange").pack()
    tk.Label(warning_frame, text="Si selecciona un año incorrecto, la comparación\npuede no encontrar coincidencias entre archivos.",
             justify="center", fg="orange").pack()
    
    seleccion = {"anio": None}
    
    def aceptar():
        if combo.get():
            year_selected = combo.get()
            # Confirmación adicional si el año no es el actual
            if int(year_selected) != current_year:
                confirm = messagebox.askyesno(
                    "Confirmar año",
                    f"Ha seleccionado el año {year_selected}.\n"
                    f"El año actual es {current_year}.\n\n"
                    f"¿Está seguro de que sus archivos contienen\n"
                    f"datos del año {year_selected}?"
                )
                if not confirm:
                    return
            
            seleccion["anio"] = year_selected
            dialog.destroy()
        else:
            messagebox.showwarning("Selección requerida", "Debe seleccionar un año.")
    
    def cancelar():
        dialog.destroy()
    
    # Botones
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Aceptar", command=aceptar,
              bg="#4CAF50", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancelar", command=cancelar,
              bg="#f44336", fg="white", width=10).pack(side="left", padx=5)
    
    # Manejo de eventos
    dialog.bind('<Return>', lambda e: aceptar())
    dialog.bind('<Escape>', lambda e: cancelar())
    
    dialog.wait_window(dialog)
    return seleccion["anio"]

# Funciones de respaldo (versiones simples)
def seleccionar_moneda():
    """Función simple de respaldo para seleccionar moneda."""
    dialog = tk.Toplevel(ventana)
    dialog.title("Selecciona la moneda")
    tk.Label(dialog, text="¿Qué moneda deseas comparar?").pack(padx=10, pady=10)
    combo = ttk.Combobox(dialog, values=["PEN", "USD"], state="readonly")
    combo.set("PEN")
    combo.pack(padx=10, pady=10)
    seleccion = {"moneda": None}

    def aceptar():
        seleccion["moneda"] = combo.get()
        dialog.destroy()

    btn = tk.Button(dialog, text="Aceptar", command=aceptar)
    btn.pack(pady=10)
    dialog.grab_set()
    ventana.wait_window(dialog)
    return seleccion["moneda"]

def seleccionar_anio():
    """Función simple de respaldo para seleccionar año."""
    dialog = tk.Toplevel(ventana)
    dialog.title("Selecciona el año")
    tk.Label(dialog, text="¿Qué año deseas filtrar?").pack(padx=10, pady=10)
    combo = ttk.Combobox(dialog, values=[2020, 2021, 2022, 2023, 2024, 2025, 2026], state="readonly")
    combo.set(2026)
    combo.pack(padx=10, pady=10)
    seleccion = {"anio": None}

    def aceptar():
        seleccion["anio"] = combo.get()
        dialog.destroy()

    btn = tk.Button(dialog, text="Aceptar", command=aceptar)
    btn.pack(pady=10)
    dialog.grab_set()
    ventana.wait_window(dialog)
    return seleccion["anio"]

listbox.pack(fill="y", expand=True) # Añadir el Listbox al frame_lista para mostrar los archivos cargados   
listbox.bind('<<ListboxSelect>>', mostrar_archivo_seleccionado)   # Asociar el evento de selección del Listbox con la función para mostrar el DataFrame correspondiente       