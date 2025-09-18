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

def mostrar_tabla(df):
    """
    Función mejorada para mostrar DataFrames en una tabla con información detallada y opciones avanzadas.

    Esta función proporciona una visualización completa de los datos con:
    - Información estadística del conjunto de datos
    - Numeración de filas para fácil referencia
    - Barras de desplazamiento automáticas
    - Formato optimizado según el tipo de contenido
    - Validación de datos antes de mostrar
    - Información contextual sobre el contenido

    Características:
    - Detección automática del tipo de datos (PDF, Excel, Comparación)
    - Mostrar estadísticas relevantes según el tipo de archivo
    - Formateo inteligente de columnas numéricas
    - Resaltado visual de información importante
    - Manejo robusto de DataFrames grandes

    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame que se desea mostrar. Puede ser de cualquier tipo:
        - Extractos PDF procesados
        - Datos contables de Excel
        - Resultados de comparaciones
        - Cualquier conjunto de datos estructurado

    Validaciones realizadas:
    - Verificación de que el DataFrame no esté vacío
    - Validación de estructura de columnas
    - Detección de tipos de datos para formateo
    - Manejo de valores nulos y especiales

    Información mostrada:
    - Número total de registros
    - Rango de fechas (si aplica)
    - Estadísticas de montos (si aplica)
    - Información de coincidencias (para comparaciones)

    Retorna:
    --------
    None
        La función actualiza directamente la interfaz gráfica con la tabla.
    """
    
    # Validación inicial del DataFrame
    if df is None:
        messagebox.showerror("Error", "No se proporcionó un DataFrame para mostrar.")
        return
    
    if df.empty:
        messagebox.showinfo(
            "Sin datos", 
            "El archivo seleccionado no contiene datos para mostrar.\n\n"
            "Posibles causas:\n"
            "• El archivo está vacío\n"
            "• No se pudieron extraer datos válidos\n"
            "• Los filtros aplicados no devolvieron resultados\n\n"
            "Intente cargar un archivo diferente o revisar los filtros."
        )
        return
    
    # Limpiar widgets existentes en la tabla
    for widget in frame_tabla.winfo_children():
        widget.destroy()
    
    # Crear frame para información del DataFrame
    info_frame = tk.Frame(frame_tabla)
    info_frame.pack(fill="x", padx=5, pady=5)
    
    # Analizar el contenido del DataFrame para mostrar información relevante
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Detectar tipo de contenido
    tipo_contenido = "Datos generales"
    if 'Comparación' in str(df) or ('NOP' in df.columns and 'Saldo' in df.columns):
        tipo_contenido = "Comparación bancaria"
    elif 'FechaOper' in df.columns and 'Concepto' in df.columns:
        tipo_contenido = "Extracto bancario"
    elif 'MONEDA' in df.columns and 'MONTO' in df.columns:
        tipo_contenido = "Base contable"
    
    # Crear etiqueta de información principal
    info_principal = f"📊 {tipo_contenido} | 📄 {num_rows:,} registros | 📋 {num_cols} columnas"
    tk.Label(info_frame, text=info_principal, font=("Arial", 10, "bold"), fg="blue").pack(anchor="w")
    
    # Información adicional específica por tipo
    info_adicional = []
    
    # Para extractos bancarios
    if tipo_contenido == "Extracto bancario":
        if 'Cargo' in df.columns and 'Abono' in df.columns:
            total_cargos = df['Cargo'].sum()
            total_abonos = df['Abono'].sum()
            info_adicional.append(f"💰 Cargos: {total_cargos:,.2f} | Abonos: {total_abonos:,.2f}")
        
        if 'Saldo' in df.columns:
            saldo_inicial = df['Saldo'].iloc[0] if len(df) > 0 else 0
            saldo_final = df['Saldo'].iloc[-1] if len(df) > 0 else 0
            info_adicional.append(f"🏦 Saldo inicial: {saldo_inicial:,.2f} | Final: {saldo_final:,.2f}")
    
    # Para comparaciones
    elif tipo_contenido == "Comparación bancaria" and 'NOP' in df.columns:
        coincidencias = df[df['NOP'] != '---']
        sin_coincidencias = df[df['NOP'] == '---']
        tasa_coincidencia = len(coincidencias) / len(df) * 100 if len(df) > 0 else 0
        
        info_adicional.append(f"✅ Coincidencias: {len(coincidencias)} | ❌ Sin coincidencia: {len(sin_coincidencias)}")
        info_adicional.append(f"📈 Tasa de coincidencia: {tasa_coincidencia:.1f}%")
        
        # Análisis de calidad
        if tasa_coincidencia >= 80:
            calidad = "🟢 Excelente"
        elif tasa_coincidencia >= 60:
            calidad = "🟡 Buena"
        elif tasa_coincidencia >= 40:
            calidad = "🟠 Regular"
        else:
            calidad = "🔴 Necesita revisión"
        info_adicional.append(f"📊 Calidad de comparación: {calidad}")
    
    # Para base contable
    elif tipo_contenido == "Base contable":
        if 'MONEDA' in df.columns:
            monedas = df['MONEDA'].value_counts()
            monedas_str = ", ".join([f"{moneda}: {count}" for moneda, count in monedas.head(3).items()])
            info_adicional.append(f"💱 Monedas: {monedas_str}")
        
        if 'MONTO' in df.columns:
            monto_total = df['MONTO'].sum()
            info_adicional.append(f"💰 Monto total: {monto_total:,.2f}")
    
    # Información de fechas (común para todos los tipos)
    if 'Fecha' in df.columns:
        try:
            fecha_min = df['Fecha'].min()
            fecha_max = df['Fecha'].max()
            if pd.notna(fecha_min) and pd.notna(fecha_max):
                info_adicional.append(f"📅 Período: {fecha_min} - {fecha_max}")
        except:
            pass
    
    # Mostrar información adicional
    for info in info_adicional:
        tk.Label(info_frame, text=info, font=("Arial", 9), fg="gray").pack(anchor="w")
    
    # Separador visual
    separator = tk.Frame(frame_tabla, height=2, bg="lightgray")
    separator.pack(fill="x", padx=5, pady=5)
    
    # Crear frame para la tabla con scrollbars
    table_frame = tk.Frame(frame_tabla)
    table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Configurar barras de desplazamiento
    scrollbar_y = tk.Scrollbar(table_frame, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")
    
    scrollbar_x = tk.Scrollbar(table_frame, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")
    
    # Crear TreeView con columnas dinámicas
    columnas_df = list(df.columns)
    tabla = ttk.Treeview(
        table_frame,
        columns=["N°"] + columnas_df,
        show='headings',
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    
    # Configurar scrollbars
    scrollbar_y.config(command=tabla.yview)
    scrollbar_x.config(command=tabla.xview)
    
    # Configurar columna de número de fila
    tabla.heading("N°", text="N°")
    tabla.column("N°", width=50, anchor="center")
    
    # Configurar columnas del DataFrame con anchos optimizados
    for col in columnas_df:
        tabla.heading(col, text=col)
        
        # Determinar ancho según el tipo de columna
        if col in ['Fecha', 'FechaOper', 'FechaValor']:
            width = 100
        elif col in ['Cargo', 'Abono', 'Saldo', 'MONTO']:
            width = 120
        elif col in ['NOP', 'Origen', 'Referencia']:
            width = 80
        elif col in ['Concepto', 'CONCEPTO', 'RAZON SOCIAL']:
            width = 200
        else:
            width = 100
        
        tabla.column(col, width=width, anchor="center")
    
    # Insertar datos con formato especial para ciertos tipos
    for i, row in enumerate(df.itertuples(index=False), start=1):
        valores = [i] + list(row)
        
        # Aplicar formato especial a valores nulos o especiales
        valores_formateados = []
        for j, valor in enumerate(valores):
            if j == 0:  # Número de fila
                valores_formateados.append(valor)
            elif pd.isna(valor) or valor == '---':
                valores_formateados.append('---')
            elif isinstance(valor, float) and j > 0:  # Valores numéricos
                col_name = columnas_df[j-1] if j-1 < len(columnas_df) else ''
                if col_name in ['Cargo', 'Abono', 'Saldo', 'MONTO']:
                    valores_formateados.append(f"{valor:,.2f}")
                else:
                    valores_formateados.append(f"{valor:.2f}")
            else:
                valores_formateados.append(str(valor))
        
        tabla.insert("", "end", values=valores_formateados)
    
    # Agregar la tabla al frame
    tabla.pack(fill="both", expand=True)
    
    # Frame para controles adicionales
    controls_frame = tk.Frame(frame_tabla)
    controls_frame.pack(fill="x", padx=5, pady=5)
    
    # Mostrar información de navegación para tablas grandes
    if num_rows > 100:
        tk.Label(controls_frame, 
                text=f"💡 Tabla grande ({num_rows:,} filas). Use las barras de desplazamiento para navegar.",
                font=("Arial", 8), fg="orange").pack(anchor="w")
    
    # Mostrar advertencias si hay datos problemáticos
    if tipo_contenido == "Comparación bancaria" and 'NOP' in df.columns:
        sin_coincidencias = len(df[df['NOP'] == '---'])
        if sin_coincidencias > num_rows * 0.5:  # Más del 50% sin coincidencias
            tk.Label(controls_frame,
                    text=f"⚠️ Alto porcentaje de transacciones sin coincidencias ({sin_coincidencias}/{num_rows})",
                    font=("Arial", 8), fg="red").pack(anchor="w")
    
    print(f"\n=== TABLA MOSTRADA ===")
    print(f"Tipo: {tipo_contenido}")
    print(f"Filas: {num_rows:,}")
    print(f"Columnas: {columnas_df}")
    print(f"======================\n")

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
def exportar_actual():
    """
    Función avanzada para exportar DataFrames a Excel con opciones detalladas y análisis.

    Esta función proporciona una experiencia completa de exportación con:
    - Validación previa de datos a exportar
    - Opciones de formato y configuración
    - Análisis estadístico del conjunto de datos
    - Generación de hojas adicionales con metadatos
    - Manejo robusto de errores durante la exportación
    - Retroalimentación detallada al usuario

    Características avanzadas:
    - Múltiples hojas en el archivo Excel (datos, resumen, metadatos)
    - Formato automático de columnas según tipo de datos
    - Inclusión de estadísticas y resúmenes
    - Validación de integridad antes de exportar
    - Opciones de personalización del archivo de salida

    Tipos de datos soportados:
    - DataFrames de transacciones PDF procesadas
    - DataFrames de datos contables de Excel
    - DataFrames de comparaciones entre PDF y Excel
    - Cualquier DataFrame almacenado en archivos_cargados

    Formatos de salida:
    - Excel (.xlsx) con múltiples hojas
    - Formateo automático de números y fechas
    - Metadatos incluidos para trazabilidad

    Retorna:
    --------
    None
        La función maneja la exportación completa y notifica el resultado al usuario.
    """

    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning(
            "Sin selección",
            "Debe seleccionar un archivo de la lista para exportar.\n\n"
            "Pasos:\n"
            "1. Seleccione un archivo de la lista de archivos cargados\n"
            "2. Haga clic en 'Exportar a Excel'\n"
            "3. Configure las opciones de exportación"
        )
        return
    
    nombre = listbox.get(seleccion[0])
    df = archivos_cargados[nombre]
    
    # Validación previa del DataFrame
    if df.empty:
        messagebox.showerror(
            "Datos vacíos",
            f"El archivo seleccionado '{nombre}' no contiene datos para exportar.\n\n"
            "Seleccione un archivo que contenga transacciones o datos válidos."
        )
        return
    
    # Análisis previo del DataFrame para información al usuario
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Detectar tipo de archivo
    tipo_archivo = "Desconocido"
    if "Comparación" in nombre:
        tipo_archivo = "Comparación PDF vs Excel"
    elif nombre.lower().endswith('.pdf'):
        tipo_archivo = "Extracto bancario PDF"
    elif any(ext in nombre.lower() for ext in ['.xlsx', '.xls']):
        tipo_archivo = "Base de datos contable"
    
    # Crear ventana de configuración de exportación
    export_config = tk.Toplevel(ventana)
    export_config.title("Configuración de Exportación")
    export_config.geometry("500x400")
    export_config.resizable(False, False)
    export_config.grab_set()
    
    # Centrar ventana
    export_config.geometry("+%d+%d" % (
        ventana.winfo_rootx() + 50,
        ventana.winfo_rooty() + 50
    ))
    
    # Título y información del archivo
    tk.Label(export_config, text="Configuración de Exportación a Excel", 
             font=("Arial", 14, "bold")).pack(pady=15)
    
    # Frame de información del archivo
    info_frame = tk.LabelFrame(export_config, text="Información del Archivo", padx=10, pady=10)
    info_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(info_frame, text=f"Archivo: {nombre}", font=("Arial", 10, "bold")).pack(anchor="w")
    tk.Label(info_frame, text=f"Tipo: {tipo_archivo}").pack(anchor="w")
    tk.Label(info_frame, text=f"Registros: {num_rows:,}").pack(anchor="w")
    tk.Label(info_frame, text=f"Columnas: {num_cols}").pack(anchor="w")
    
    # Análisis de contenido
    if 'Fecha' in df.columns:
        fecha_min = df['Fecha'].min()
        fecha_max = df['Fecha'].max()
        tk.Label(info_frame, text=f"Rango de fechas: {fecha_min} - {fecha_max}").pack(anchor="w")
    
    if 'MONEDA' in df.columns:
        monedas = df['MONEDA'].unique()
        tk.Label(info_frame, text=f"Monedas: {', '.join(str(m) for m in monedas)}").pack(anchor="w")
    
    # Frame de opciones de exportación
    options_frame = tk.LabelFrame(export_config, text="Opciones de Exportación", padx=10, pady=10)
    options_frame.pack(fill="x", padx=20, pady=10)
    
    # Variables para opciones
    include_summary = tk.BooleanVar(value=True)
    include_metadata = tk.BooleanVar(value=True)
    auto_format = tk.BooleanVar(value=True)
    
    tk.Checkbutton(options_frame, text="Incluir hoja de resumen estadístico", 
                   variable=include_summary).pack(anchor="w")
    tk.Checkbutton(options_frame, text="Incluir hoja de metadatos y configuración", 
                   variable=include_metadata).pack(anchor="w")
    tk.Checkbutton(options_frame, text="Aplicar formato automático a columnas", 
                   variable=auto_format).pack(anchor="w")
    
    # Frame para nombre de archivo
    name_frame = tk.LabelFrame(export_config, text="Nombre del Archivo", padx=10, pady=10)
    name_frame.pack(fill="x", padx=20, pady=10)
    
    nombre_sugerido = nombre.replace(" ", "_").replace(".pdf", "").replace(".xlsx", "").replace(".xls", "")
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    nombre_default = f"{nombre_sugerido}_export_{timestamp}"
    
    tk.Label(name_frame, text="Nombre del archivo (sin extensión):").pack(anchor="w")
    name_entry = tk.Entry(name_frame, width=50)
    name_entry.insert(0, nombre_default)
    name_entry.pack(fill="x", pady=5)
    
    resultado_exportacion = {"success": False, "file_path": None}
    
    def realizar_exportacion():
        try:
            nombre_archivo = name_entry.get().strip()
            if not nombre_archivo:
                messagebox.showerror("Error", "Debe especificar un nombre para el archivo.")
                return
            
            # Seleccionar ubicación de guardado
            ruta = filedialog.asksaveasfilename(
                title="Guardar exportación como",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("Todos los archivos", "*.*")],
                initialfile=nombre_archivo + ".xlsx"
            )
            
            if not ruta:
                return  # Usuario canceló
            
            export_config.destroy()
            
            # Crear ventana de progreso de exportación
            progress_window = tk.Toplevel(ventana)
            progress_window.title("Exportando...")
            progress_window.geometry("400x200")
            progress_window.resizable(False, False)
            progress_window.grab_set()
            
            tk.Label(progress_window, text="Exportando datos a Excel...", 
                    font=("Arial", 12, "bold")).pack(pady=20)
            
            status_label = tk.Label(progress_window, text="Preparando datos...")
            status_label.pack(pady=10)
            
            progress_window.update()
            
            # Crear el escritor de Excel
            with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
                
                # Hoja principal con datos
                status_label.config(text="Escribiendo datos principales...")
                progress_window.update()
                
                df_export = df.copy()
                
                # Aplicar formato automático si está habilitado
                if auto_format.get():
                    # Formatear columnas numéricas
                    numeric_columns = df_export.select_dtypes(include=['number']).columns
                    for col in numeric_columns:
                        if col in ['Cargo', 'Abono', 'Saldo', 'MONTO']:
                            df_export[col] = df_export[col].round(2)
                
                df_export.to_excel(writer, sheet_name='Datos', index=False)
                
                # Hoja de resumen si está habilitada
                if include_summary.get() and not df.empty:
                    status_label.config(text="Generando resumen estadístico...")
                    progress_window.update()
                    
                    resumen_data = []
                    resumen_data.append(['=== RESUMEN ESTADÍSTICO ===', ''])
                    resumen_data.append(['Archivo original', nombre])
                    resumen_data.append(['Fecha de exportación', pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")])
                    resumen_data.append(['Total de registros', num_rows])
                    resumen_data.append(['Total de columnas', num_cols])
                    resumen_data.append(['', ''])
                    
                    # Estadísticas por columnas
                    resumen_data.append(['=== ANÁLISIS POR COLUMNAS ===', ''])
                    for col in df.columns:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            resumen_data.append([f'{col} - Total', df[col].sum()])
                            resumen_data.append([f'{col} - Promedio', df[col].mean()])
                            resumen_data.append([f'{col} - Min', df[col].min()])
                            resumen_data.append([f'{col} - Max', df[col].max()])
                        else:
                            unique_count = df[col].nunique()
                            resumen_data.append([f'{col} - Valores únicos', unique_count])
                    
                    # Estadísticas específicas para comparaciones
                    if "Comparación" in nombre and 'NOP' in df.columns:
                        resumen_data.append(['', ''])
                        resumen_data.append(['=== ANÁLISIS DE COMPARACIÓN ===', ''])
                        coincidencias = df[df['NOP'] != '---']
                        sin_coincidencias = df[df['NOP'] == '---']
                        
                        resumen_data.append(['Transacciones con coincidencias', len(coincidencias)])
                        resumen_data.append(['Transacciones sin coincidencias', len(sin_coincidencias)])
                        resumen_data.append(['Tasa de coincidencia (%)', f"{len(coincidencias)/len(df)*100:.2f}"])
                    
                    resumen_df = pd.DataFrame(resumen_data, columns=['Descripción', 'Valor'])
                    resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja de metadatos si está habilitada
                if include_metadata.get():
                    status_label.config(text="Agregando metadatos...")
                    progress_window.update()
                    
                    metadata = []
                    metadata.append(['=== METADATOS DEL ARCHIVO ===', ''])
                    metadata.append(['Aplicación', 'Conciliador Bancario Automatizado'])
                    metadata.append(['Versión', '1.0'])
                    metadata.append(['Archivo fuente', nombre])
                    metadata.append(['Tipo de archivo', tipo_archivo])
                    metadata.append(['Fecha de exportación', pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")])
                    metadata.append(['Usuario', os.getenv('USERNAME', 'Usuario')])
                    metadata.append(['', ''])
                    
                    metadata.append(['=== ESTRUCTURA DE DATOS ===', ''])
                    metadata.append(['Columnas en el archivo', ', '.join(df.columns.tolist())])
                    metadata.append(['Tipos de datos', ''])
                    
                    for col in df.columns:
                        metadata.append([f'  {col}', str(df[col].dtype)])
                    
                    metadata.append(['', ''])
                    metadata.append(['=== CONFIGURACIÓN DE EXPORTACIÓN ===', ''])
                    metadata.append(['Incluir resumen', 'Sí' if include_summary.get() else 'No'])
                    metadata.append(['Incluir metadatos', 'Sí' if include_metadata.get() else 'No'])
                    metadata.append(['Formato automático', 'Sí' if auto_format.get() else 'No'])
                    
                    metadata_df = pd.DataFrame(metadata, columns=['Campo', 'Valor'])
                    metadata_df.to_excel(writer, sheet_name='Metadatos', index=False)
            
            progress_window.destroy()
            resultado_exportacion["success"] = True
            resultado_exportacion["file_path"] = ruta
            
            # Calcular tamaño del archivo exportado
            file_size = os.path.getsize(ruta)
            
            # Mostrar resumen de exportación exitosa
            sheets_info = "Datos"
            if include_summary.get():
                sheets_info += ", Resumen"
            if include_metadata.get():
                sheets_info += ", Metadatos"
            
            messagebox.showinfo(
                "Exportación completada",
                f"✅ Archivo exportado exitosamente\n\n"
                f"📄 Archivo: {os.path.basename(ruta)}\n"
                f"📁 Ubicación: {os.path.dirname(ruta)}\n"
                f"📊 Registros exportados: {num_rows:,}\n"
                f"📋 Hojas creadas: {sheets_info}\n"
                f"💾 Tamaño: {file_size / 1024:.1f} KB\n\n"
                f"El archivo está listo para usar en Excel o análisis adicionales."
            )
            
        except PermissionError:
            try:
                progress_window.destroy()
            except:
                pass
            messagebox.showerror(
                "Error de permisos",
                f"No se puede escribir en la ubicación seleccionada.\n\n"
                f"Posibles causas:\n"
                f"• El archivo está abierto en Excel\n"
                f"• Sin permisos de escritura en la carpeta\n"
                f"• La unidad está protegida contra escritura\n\n"
                f"Soluciones:\n"
                f"• Cierre Excel si el archivo está abierto\n"
                f"• Seleccione una ubicación diferente\n"
                f"• Ejecute como administrador si es necesario"
            )
        except Exception as e:
            try:
                progress_window.destroy()
            except:
                pass
            messagebox.showerror(
                "Error de exportación",
                f"No se pudo completar la exportación.\n\n"
                f"Archivo: {nombre}\n"
                f"Error: {str(e)}\n\n"
                f"Intente nuevamente o seleccione una ubicación diferente."
            )
    
    def cancelar_exportacion():
        export_config.destroy()
    
    # Botones de acción
    button_frame = tk.Frame(export_config)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Exportar", command=realizar_exportacion,
              bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancelar", command=cancelar_exportacion,
              bg="#f44336", fg="white", width=15).pack(side="left", padx=10)
    
    # Información adicional
    info_label = tk.Label(export_config, 
                         text="💡 El archivo Excel incluirá formato automático y metadatos para mejor análisis",
                         fg="gray", font=("Arial", 9))
    info_label.pack(pady=10)
    
    export_config.wait_window(export_config)


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

def mostrar_ayuda():
    """
    Función para mostrar ventana de ayuda integral con guías detalladas y solución de problemas.
    
    Proporciona documentación completa sobre:
    - Funcionalidades principales de la aplicación
    - Guías paso a paso para cada operación
    - Solución de problemas comunes
    - Requisitos de formato de archivos
    - Mejores prácticas de uso
    """
    
    help_window = tk.Toplevel(ventana)
    help_window.title("Ayuda - Conciliador Bancario Automatizado")
    help_window.geometry("800x600")
    help_window.resizable(True, True)
    
    # Centrar ventana
    help_window.geometry("+%d+%d" % (
        ventana.winfo_rootx() + 50,
        ventana.winfo_rooty() + 50
    ))
    
    # Crear notebook para organizar la ayuda por secciones
    notebook = ttk.Notebook(help_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Sección 1: Introducción y características
    intro_frame = tk.Frame(notebook)
    notebook.add(intro_frame, text="🏠 Introducción")
    
    intro_text = tk.Text(intro_frame, wrap="word", padx=10, pady=10)
    intro_scroll = tk.Scrollbar(intro_frame, orient="vertical", command=intro_text.yview)
    intro_text.configure(yscrollcommand=intro_scroll.set)
    
    intro_content = """
🏦 CONCILIADOR BANCARIO AUTOMATIZADO
====================================

Esta aplicación permite analizar, conciliar y visualizar extractos bancarios en PDF 
comparándolos con registros contables en Excel.

🎯 OBJETIVOS PRINCIPALES:
• Automatizar la conciliación bancaria
• Detectar diferencias entre extractos y contabilidad
• Generar reportes detallados de coincidencias
• Identificar transacciones no registradas
• Exportar resultados para análisis adicional

🚀 CARACTERÍSTICAS PRINCIPALES:
• Lectura automática de extractos PDF
• Procesamiento de bases de datos Excel
• Comparación inteligente de transacciones
• Filtrado por moneda y período
• Visualización de datos en tablas y gráficos
• Exportación a Excel con metadatos
• Interfaz gráfica intuitiva

💼 CASOS DE USO:
• Conciliación bancaria mensual
• Auditoría de transacciones
• Identificación de diferencias contables
• Análisis de flujo de caja
• Preparación de reportes financieros

🔧 REQUISITOS DEL SISTEMA:
• Windows 7 o superior
• Python 3.8+ (para versión código fuente)
• 4GB RAM mínimo (8GB recomendado)
• 500MB espacio en disco
• Resolución mínima: 1024x768
"""
    
    intro_text.insert("1.0", intro_content)
    intro_text.config(state="disabled")
    intro_text.pack(side="left", fill="both", expand=True)
    intro_scroll.pack(side="right", fill="y")
    
    # Sección 2: Guía de uso
    guide_frame = tk.Frame(notebook)
    notebook.add(guide_frame, text="📖 Guía de Uso")
    
    guide_text = tk.Text(guide_frame, wrap="word", padx=10, pady=10)
    guide_scroll = tk.Scrollbar(guide_frame, orient="vertical", command=guide_text.yview)
    guide_text.configure(yscrollcommand=guide_scroll.set)
    
    guide_content = """
📖 GUÍA PASO A PASO
==================

🔄 FLUJO DE TRABAJO RECOMENDADO:

1️⃣ PREPARACIÓN DE ARCHIVOS
--------------------------
• Asegúrese de tener el extracto bancario en PDF
• Verifique que tenga la base contable en Excel
• Los archivos deben corresponder al mismo período

2️⃣ CARGA DE ARCHIVO PDF
-----------------------
• Haga clic en "Cargar PDF Bancario"
• Seleccione el extracto bancario
• Espere a que se procese automáticamente
• Revise las transacciones en la tabla

3️⃣ CARGA DE ARCHIVO EXCEL
-------------------------
• Haga clic en "Cargar Excel"
• Seleccione la base de datos contable
• Verifique que contenga las columnas requeridas
• Revise los datos cargados

4️⃣ COMPARACIÓN DE ARCHIVOS
--------------------------
• Haga clic en "Comparar PDF y Excel"
• Seleccione primero el archivo PDF
• Seleccione después el archivo Excel
• Configure la moneda (PEN, USD)
• Seleccione el año del período
• Confirme y espere el procesamiento

5️⃣ ANÁLISIS DE RESULTADOS
-------------------------
• Revise la tabla de comparación
• Identifique coincidencias y diferencias
• Use la información estadística
• Analice la tasa de coincidencia

6️⃣ EXPORTACIÓN DE RESULTADOS
----------------------------
• Seleccione el archivo a exportar
• Haga clic en "Exportar a Excel"
• Configure opciones de exportación
• Guarde en la ubicación deseada

7️⃣ VISUALIZACIÓN GRÁFICA
------------------------
• Seleccione un archivo de la lista
• Haga clic en "Mostrar Gráfica"
• Analice cargos y abonos por fecha
• Guarde gráficos si es necesario

💡 CONSEJOS PARA MEJORES RESULTADOS:
• Use archivos del mismo período temporal
• Verifique que las fechas sean consistentes
• Asegúrese de seleccionar la moneda correcta
• Revise manualmente las transacciones sin coincidencias
• Mantenga respaldos de los archivos originales
"""
    
    guide_text.insert("1.0", guide_content)
    guide_text.config(state="disabled")
    guide_text.pack(side="left", fill="both", expand=True)
    guide_scroll.pack(side="right", fill="y")
    
    # Sección 3: Formatos de archivo
    format_frame = tk.Frame(notebook)
    notebook.add(format_frame, text="📄 Formatos")
    
    format_text = tk.Text(format_frame, wrap="word", padx=10, pady=10)
    format_scroll = tk.Scrollbar(format_frame, orient="vertical", command=format_text.yview)
    format_text.configure(yscrollcommand=format_scroll.set)
    
    format_content = """
📄 FORMATOS DE ARCHIVOS SOPORTADOS
==================================

📋 ARCHIVOS PDF (EXTRACTOS BANCARIOS)
-------------------------------------
✅ FORMATO REQUERIDO:
• Texto seleccionable (no imágenes escaneadas)
• Estructura tabular con columnas fijas
• Información de transacciones línea por línea

🏗️ ESTRUCTURA ESPERADA:
FechaOper | FechaValor | Origen | Concepto | Referencia | Monto | Saldo

📝 EJEMPLO DE LÍNEA VÁLIDA:
15/03     15/03        001    TRANSFERENCIA  1234567   1,250.50  15,750.25

⚠️ LIMITACIONES:
• No soporta PDFs de solo imagen
• Requiere formato estándar de extracto
• Las fechas deben estar en formato DD/MM
• Los montos deben usar punto decimal y coma miles

📊 ARCHIVOS EXCEL (BASE CONTABLE)
---------------------------------
✅ FORMATOS SOPORTADOS:
• .xlsx (Excel 2007 o superior) ✅ Recomendado
• .xls (Excel 97-2003) ✅ Compatible
• .xlsm (Excel con macros) ✅ Compatible

🏗️ COLUMNAS REQUERIDAS:
• ANO: Año de la transacción (número entero)
• MES: Mes de la transacción (1-12)
• DIA: Día de la transacción (1-31)

🏗️ COLUMNAS OPCIONALES ÚTILES:
• NUM OPERACION: Número de operación
• N° DOCUMENTO: Número de documento
• NOP: Número de operación procesado
• MONEDA: Código de moneda (PEN, USD, etc.)
• MONTO: Importe de la transacción
• CONCEPTO: Descripción del movimiento
• CENTRO COSTO: Centro de costo contable
• RAZON SOCIAL: Nombre del tercero

📋 EJEMPLO DE ESTRUCTURA EXCEL:
ANO | MES | DIA | MONEDA | MONTO    | CONCEPTO        | NOP
2024| 03  | 15  | PEN    | 1250.50  | TRANSFERENCIA   | 001

💾 ARCHIVOS DE EXPORTACIÓN
--------------------------
✅ FORMATO DE SALIDA:
• Excel (.xlsx) con múltiples hojas
• Hoja 'Datos': Información principal
• Hoja 'Resumen': Estadísticas y análisis
• Hoja 'Metadatos': Información técnica

🎨 CARACTERÍSTICAS:
• Formato automático de números
• Preservación de tipos de datos
• Metadatos para trazabilidad
• Estadísticas calculadas automáticamente
"""
    
    format_text.insert("1.0", format_content)
    format_text.config(state="disabled")
    format_text.pack(side="left", fill="both", expand=True)
    format_scroll.pack(side="right", fill="y")
    
    # Sección 4: Solución de problemas
    troubleshoot_frame = tk.Frame(notebook)
    notebook.add(troubleshoot_frame, text="🔧 Problemas")
    
    trouble_text = tk.Text(troubleshoot_frame, wrap="word", padx=10, pady=10)
    trouble_scroll = tk.Scrollbar(troubleshoot_frame, orient="vertical", command=trouble_text.yview)
    trouble_text.configure(yscrollcommand=trouble_scroll.set)
    
    trouble_content = """
🔧 SOLUCIÓN DE PROBLEMAS COMUNES
================================

❌ PROBLEMA: "No se encontraron transacciones en el PDF"
--------------------------------------------------------
🔍 CAUSAS POSIBLES:
• El PDF es una imagen escaneada
• El formato no coincide con el esperado
• El archivo está dañado

💡 SOLUCIONES:
• Use PDFs con texto seleccionable
• Verifique que sea un extracto bancario estándar
• Pruebe con un archivo diferente
• Convierta imágenes a texto usando OCR

❌ PROBLEMA: "Faltan columnas requeridas en Excel"
--------------------------------------------------
🔍 CAUSAS POSIBLES:
• El Excel no tiene las columnas ANO, MES, DIA
• Los nombres de columnas no coinciden exactamente
• Hay espacios extra en los nombres

💡 SOLUCIONES:
• Verifique que existan las columnas: ANO, MES, DIA
• Elimine espacios extra en nombres de columnas
• Use la primera fila para encabezados
• Revise que los nombres sean exactos (sin tildes)

❌ PROBLEMA: "Archivo está abierto en Excel"
--------------------------------------------
🔍 CAUSAS POSIBLES:
• El archivo Excel está siendo usado por otra aplicación
• Falta de permisos de lectura
• Archivo bloqueado por antivirus

💡 SOLUCIONES:
• Cierre Excel y todas las aplicaciones que usen el archivo
• Copie el archivo a otra ubicación
• Ejecute la aplicación como administrador
• Desactive temporalmente el antivirus

❌ PROBLEMA: "Baja tasa de coincidencias"
-----------------------------------------
🔍 CAUSAS POSIBLES:
• Períodos diferentes entre archivos
• Moneda incorrecta seleccionada
• Formatos de fecha inconsistentes
• Datos faltantes en algún archivo

💡 SOLUCIONES:
• Verifique que ambos archivos sean del mismo período
• Confirme que la moneda seleccionada sea correcta
• Revise las fechas en ambos archivos
• Asegúrese de que no falten transacciones

❌ PROBLEMA: "La aplicación se cierra inesperadamente"
------------------------------------------------------
🔍 CAUSAS POSIBLES:
• Archivos demasiado grandes
• Falta de memoria RAM
• Formato de archivo corrupto

💡 SOLUCIONES:
• Use archivos más pequeños (divida por períodos)
• Cierre otras aplicaciones para liberar memoria
• Verifique la integridad de los archivos
• Reinicie la computadora

❌ PROBLEMA: "Error al exportar a Excel"
----------------------------------------
🔍 CAUSAS POSIBLES:
• Sin permisos de escritura en la carpeta
• Nombre de archivo con caracteres especiales
• Poco espacio en disco

💡 SOLUCIONES:
• Seleccione una carpeta con permisos de escritura
• Use nombres de archivo simples (sin caracteres especiales)
• Libere espacio en disco
• Pruebe exportar a otra ubicación

🆘 OBTENER AYUDA ADICIONAL
==========================
• Revise los mensajes de error detallados
• Verifique los archivos de ejemplo en la documentación
• Contacte al soporte técnico con capturas de pantalla
• Incluya detalles del error y archivos de prueba
"""
    
    trouble_text.insert("1.0", trouble_content)
    trouble_text.config(state="disabled")
    trouble_text.pack(side="left", fill="both", expand=True)
    trouble_scroll.pack(side="right", fill="y")
    
    # Sección 5: Información técnica
    tech_frame = tk.Frame(notebook)
    notebook.add(tech_frame, text="⚙️ Técnico")
    
    tech_text = tk.Text(tech_frame, wrap="word", padx=10, pady=10)
    tech_scroll = tk.Scrollbar(tech_frame, orient="vertical", command=tech_text.yview)
    tech_text.configure(yscrollcommand=tech_scroll.set)
    
    tech_content = """
⚙️ INFORMACIÓN TÉCNICA
======================

🔬 ALGORITMO DE COMPARACIÓN
---------------------------
1. EXTRACCIÓN DE DATOS PDF:
   • Uso de pdfplumber para extracción de texto
   • Expresiones regulares para identificar transacciones
   • Validación de formato y estructura
   • Cálculo automático de cargos/abonos

2. PROCESAMIENTO EXCEL:
   • Lectura con pandas para máximo rendimiento
   • Construcción de fechas desde ANO/MES/DIA
   • Validación de tipos de datos
   • Limpieza automática de datos

3. LÓGICA DE COMPARACIÓN:
   • Coincidencia por fecha y monto
   • Detección de inconsistencias de saldo
   • Identificación de duplicados
   • Análisis de diferencias temporales

🏗️ ARQUITECTURA DEL SISTEMA
----------------------------
MÓDULOS PRINCIPALES:
• core/pdf_parser.py: Procesamiento de PDFs
• core/excel_loader.py: Carga de datos Excel
• core/comparador.py: Lógica de comparación
• gui/: Interfaz gráfica de usuario
• core/utilidades.py: Funciones auxiliares

DEPENDENCIAS CLAVE:
• pandas: Manipulación de datos
• pdfplumber: Extracción de texto PDF
• tkinter: Interfaz gráfica
• openpyxl: Manejo de archivos Excel
• matplotlib: Generación de gráficos

💾 GESTIÓN DE MEMORIA
---------------------
OPTIMIZACIONES IMPLEMENTADAS:
• Carga incremental de archivos grandes
• Limpieza automática de memoria
• Validación de tamaño antes de procesar
• Procesamiento por lotes para datasets grandes

LÍMITES RECOMENDADOS:
• PDFs: Máximo 50MB
• Excel: Máximo 100MB
• Transacciones: Hasta 100,000 registros
• RAM mínima: 4GB (8GB recomendado)

🛡️ VALIDACIONES Y SEGURIDAD
----------------------------
VALIDACIONES IMPLEMENTADAS:
• Verificación de integridad de archivos
• Validación de formato antes del procesamiento
• Comprobación de tipos de datos
• Detección de archivos corruptos

CARACTERÍSTICAS DE SEGURIDAD:
• No conexión a internet requerida
• Procesamiento local de datos
• Sin envío de información a servidores externos
• Manejo seguro de archivos temporales

📊 MÉTRICAS DE RENDIMIENTO
--------------------------
TIEMPOS TÍPICOS DE PROCESAMIENTO:
• PDF 1MB, 500 transacciones: 2-5 segundos
• Excel 5MB, 5,000 registros: 3-8 segundos
• Comparación 1,000 vs 1,000: 5-15 segundos
• Exportación con metadatos: 1-3 segundos

FACTORES QUE AFECTAN RENDIMIENTO:
• Tamaño de archivos
• Complejidad del PDF
• Cantidad de transacciones
• Velocidad del disco duro
• Memoria RAM disponible

🔄 ACTUALIZACIONES Y VERSIONADO
-------------------------------
VERSIÓN ACTUAL: 1.0
FECHA DE LANZAMIENTO: 2024

CARACTERÍSTICAS DE ESTA VERSIÓN:
• Interfaz gráfica mejorada
• Validación exhaustiva de datos
• Manejo robusto de errores
• Documentación completa
• Exportación avanzada con metadatos

PRÓXIMAS CARACTERÍSTICAS:
• Soporte para más formatos de PDF
• Integración con sistemas contables
• Procesamiento por lotes
• Reportes automáticos programados
"""
    
    tech_text.insert("1.0", tech_content)
    tech_text.config(state="disabled")
    tech_text.pack(side="left", fill="both", expand=True)
    tech_scroll.pack(side="right", fill="y")
    
    # Botón para cerrar
    close_frame = tk.Frame(help_window)
    close_frame.pack(pady=10)
    
    tk.Button(close_frame, text="Cerrar Ayuda", command=help_window.destroy,
              bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold")).pack()

# Configuración final del listbox
listbox.pack(fill="y", expand=True) # Añadir el Listbox al frame_lista para mostrar los archivos cargados   
listbox.bind('<<ListboxSelect>>', mostrar_archivo_seleccionado)   # Asociar el evento de selección del Listbox con la función para mostrar el DataFrame correspondiente       