import pdfplumber
import re
import pandas as pd
import os

def transformacion_pdf(pdf_path):              
    """
    Procesa un archivo PDF de extracto bancario y retorna los datos estructurados en un DataFrame.

    Esta función analiza cada página del PDF, extrae el texto usando pdfplumber, y aplica 
    expresiones regulares específicas para identificar transacciones bancarias. Cada línea
    es procesada para extraer:
    - Fechas de operación y valor
    - Código de origen (3 dígitos)
    - Concepto de la transacción
    - Número de referencia (opcional)
    - Monto de la transacción (opcional)
    - Saldo resultante

    La lógica contable determina si cada transacción es un cargo o abono comparando
    el saldo actual con el anterior:
    - Si saldo_actual > saldo_anterior → es un ABONO
    - Si saldo_actual < saldo_anterior → es un CARGO

    Parámetros:
    -----------
    pdf_path : str
        Ruta absoluta o relativa del archivo PDF que contiene el extracto bancario.
        El archivo debe tener un formato estándar de extracto bancario con columnas
        organizadas en el siguiente orden:
        FechaOper | FechaValor | Origen | Concepto | Referencia | Monto | Saldo

    Retorna:
    --------
    pandas.DataFrame
        DataFrame estructurado con las siguientes columnas:
        - 'FechaOper' (str): Fecha de operación en formato DD/MM
        - 'FechaValor' (str): Fecha valor en formato DD/MM  
        - 'Origen' (str): Código de 3 dígitos del origen de la transacción
        - 'Concepto' (str): Descripción de la transacción
        - 'Referencia' (str): Número de referencia (7+ dígitos) o '--' si no existe
        - 'Cargo' (float): Monto del cargo (0.0 si es abono)
        - 'Abono' (float): Monto del abono (0.0 si es cargo)
        - 'Saldo' (float): Saldo resultante después de la transacción

    Lanza:
    ------
    FileNotFoundError:
        Si el archivo PDF no se encuentra en la ruta especificada.
    ValueError:
        Si el archivo no contiene texto válido, está dañado, no se pueden
        identificar transacciones, o el formato no coincide con el esperado.
    PermissionError:
        Si no hay permisos para leer el archivo PDF.
    
    Ejemplos:
    ---------
    >>> df = transformacion_pdf("extracto_enero_2024.pdf")
    >>> print(df.columns.tolist())
    ['FechaOper', 'FechaValor', 'Origen', 'Concepto', 'Referencia', 'Cargo', 'Abono', 'Saldo']
    
    >>> # Verificar total de transacciones procesadas
    >>> print(f"Transacciones encontradas: {len(df)}")
    
    Notas:
    ------
    - El PDF debe estar en formato texto, no imagen escaneada
    - Se requiere que las transacciones sigan el patrón de expresión regular definido
    - Los montos deben usar punto como separador decimal y coma como separador de miles
    - La primera transacción se considera cargo por defecto si no hay saldo anterior
    """
    
    try: 
        # Validación inicial del archivo
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe en la ruta: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"El archivo debe ser un PDF. Archivo recibido: {pdf_path}")
        
        # Verificar tamaño del archivo (opcional: evitar archivos demasiado grandes)
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            raise ValueError("El archivo PDF está vacío (0 bytes).")
        
        if file_size > 50 * 1024 * 1024:  # 50MB límite
            raise ValueError(f"El archivo PDF es demasiado grande ({file_size / (1024*1024):.1f}MB). Máximo permitido: 50MB.")

        # Abrir el PDF y extraer el texto  
        with pdfplumber.open(pdf_path) as pdf: 
            if len(pdf.pages) == 0:
                raise ValueError("El archivo PDF no contiene páginas.")
            
            # Extraer texto de todas las páginas con manejo de errores por página
            pages_text = []
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                except Exception as e:
                    print(f"Advertencia: Error al extraer texto de la página {i+1}: {str(e)}")
                    continue
            
            if not pages_text:
                raise ValueError("No se pudo extraer texto de ninguna página del PDF. El archivo podría estar dañado o contener solo imágenes.")
            
            text = "\n".join(pages_text)
        
        if not text or len(text.strip()) < 50:  # Verificar contenido mínimo
            raise ValueError(f"El PDF contiene muy poco texto ({len(text)} caracteres). Verifique que sea un extracto bancario válido.")

        # Patrón de expresión regular mejorado con comentarios detallados
        pattern = re.compile(
            r"(?P<FechaOper>\d{2}/\d{2})\s+"      # Fecha operación: DD/MM
            r"(?P<FechaValor>\d{2}/\d{2})\s+"     # Fecha valor: DD/MM  
            r"(?P<Origen>\d{3})\s+"               # Código origen: 3 dígitos
            r"(?P<Concepto>.+?)\s+"               # Concepto: texto variable
            r"(?P<Referencia>\d{7,}|0000)?\s*"    # Referencia: 7+ dígitos o 0000 (opcional)
            r"(?P<Monto>\d{1,3}(?:,\d{3})*\.\d{2})?\s*"  # Monto: formato #,###.## (opcional)
            r"(?P<Saldo>\d{1,3}(?:,\d{3})*\.\d{2})"      # Saldo: formato #,###.## (obligatorio)
        ) # Expresión regular para extraer los datos del texto del PDF

        rows = [] # Lista para almacenar las filas extraídas del PDF
        saldo_anterior = None # Variable para almacenar el saldo anterior 
        lineas_procesadas = 0
        lineas_validas = 0

        for line_num, line in enumerate(text.splitlines(), 1): # Iterar sobre cada línea del texto extraído 
            lineas_procesadas += 1
            line = line.strip()  # Limpiar espacios
            
            if not line:  # Saltar líneas vacías
                continue
                
            match = pattern.search(line) # Buscar coincidencias con la expresión regular
            if match: # Si se encuentra una coincidencia, extraer los datos 
                lineas_validas += 1
                try:
                    d = match.groupdict() # Extraer los datos de la coincidencia 
                    
                    # Validación y limpieza de datos
                    concepto = d["Concepto"].strip() # Limpiar el concepto de espacios en blanco
                    if len(concepto) > 100:  # Limitar longitud del concepto
                        concepto = concepto[:97] + "..."
                    
                    referencia = d["Referencia"] or "--" # Si no hay referencia, asignar un valor por defecto
                    
                    # Convertir saldo con validación
                    try:
                        saldo = float(d["Saldo"].replace(',', '')) # Convertir el saldo a float, eliminando comas
                        if saldo < 0:
                            print(f"Advertencia línea {line_num}: Saldo negativo encontrado: {saldo}")
                    except ValueError:
                        print(f"Error línea {line_num}: No se pudo convertir saldo: {d['Saldo']}")
                        continue

                    # Procesar monto con validación
                    montos = []# Lista para almacenar los montos extraídos
                    if d["Monto"]: # Si hay un monto, convertirlo a float y eliminar comas  
                        try:
                            monto_value = float(d["Monto"].replace(',', ''))
                            if monto_value >= 0:  # Validar que el monto no sea negativo
                                montos.append(monto_value) # Si hay un monto, agregarlo a la lista de montos 
                            else:
                                print(f"Advertencia línea {line_num}: Monto negativo ignorado: {monto_value}")
                        except ValueError:
                            print(f"Error línea {line_num}: No se pudo convertir monto: {d['Monto']}")

                    # Lógica contable mejorada para determinar cargo/abono
                    cargo, abono = 0.0, 0.0 
                    if len(montos) == 1:  
                        if saldo_anterior is not None: # Si hay un saldo anterior, comparar con el saldo actual 
                            diferencia_saldo = saldo - saldo_anterior
                            
                            # Verificar consistencia entre monto y cambio de saldo
                            if abs(abs(diferencia_saldo) - montos[0]) > 0.01:  # Tolerancia de 1 centavo
                                print(f"Advertencia línea {line_num}: Inconsistencia entre monto ({montos[0]}) y cambio de saldo ({diferencia_saldo})")
                            
                            if saldo > saldo_anterior: # Si el saldo actual es mayor que el anterior, es un abono
                                abono = montos[0]
                            else:
                                cargo = montos[0]
                        else:
                            # Primera transacción: asumir que es cargo por defecto
                            cargo = montos[0]

                    # Validación de fechas
                    try:
                        fecha_oper_parts = d["FechaOper"].split('/')
                        fecha_valor_parts = d["FechaValor"].split('/')
                        
                        if len(fecha_oper_parts) != 2 or len(fecha_valor_parts) != 2:
                            raise ValueError("Formato de fecha inválido")
                        
                        dia_oper, mes_oper = int(fecha_oper_parts[0]), int(fecha_oper_parts[1])
                        dia_valor, mes_valor = int(fecha_valor_parts[0]), int(fecha_valor_parts[1])
                        
                        if not (1 <= dia_oper <= 31 and 1 <= mes_oper <= 12):
                            raise ValueError(f"Fecha operación inválida: {d['FechaOper']}")
                        if not (1 <= dia_valor <= 31 and 1 <= mes_valor <= 12):
                            raise ValueError(f"Fecha valor inválida: {d['FechaValor']}")
                            
                    except ValueError as ve:
                        print(f"Error línea {line_num}: {str(ve)}")
                        continue

                    # Crear registro de transacción
                    row_data = { 
                        "FechaOper": d["FechaOper"],
                        "FechaValor": d["FechaValor"],
                        "Origen": d["Origen"],
                        "Concepto": concepto,
                        "Referencia": referencia,
                        "Cargo": round(cargo, 2),
                        "Abono": round(abono, 2),
                        "Saldo": round(saldo, 2)
                    }
                    
                    rows.append(row_data) # Añadir la fila extraída a la lista de filas        
                    saldo_anterior = saldo # Actualizar el saldo anterior para la siguiente iteración   
                    
                except Exception as e:
                    print(f"Error procesando línea {line_num}: {str(e)}")
                    continue   

        # Validación final de resultados con estadísticas detalladas
        if not rows: # Si no se encontraron filas, lanzar una excepción con detalles
            error_details = (
                f"No se encontraron transacciones válidas en el documento.\n"
                f"Líneas procesadas: {lineas_procesadas}\n"
                f"Líneas que coinciden con el patrón: {lineas_validas}\n"
                f"Transacciones válidas: {len(rows)}\n\n"
                f"Posibles causas:\n"
                f"• El PDF no es un extracto bancario estándar\n"
                f"• El formato de las columnas no coincide con el esperado\n"
                f"• El archivo contiene solo imágenes escaneadas\n"
                f"• Los datos están en un formato no reconocido"
            )
            raise ValueError(error_details)
        
        # Crear DataFrame con validación adicional
        df = pd.DataFrame(rows)
        
        # Validaciones finales del DataFrame
        if df.empty:
            raise ValueError("El DataFrame resultante está vacío después del procesamiento.")
        
        # Verificar que las columnas esperadas existen
        expected_columns = ['FechaOper', 'FechaValor', 'Origen', 'Concepto', 'Referencia', 'Cargo', 'Abono', 'Saldo']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Faltan columnas esperadas: {missing_columns}")
        
        # Validaciones de integridad de datos
        if df['Saldo'].isna().any():
            raise ValueError("Se encontraron valores nulos en la columna Saldo.")
        
        if (df['Cargo'] < 0).any() or (df['Abono'] < 0).any():
            raise ValueError("Se encontraron valores negativos en Cargo o Abono.")
        
        # Verificar que no hay transacciones donde tanto Cargo como Abono sean > 0
        invalid_transactions = df[(df['Cargo'] > 0) & (df['Abono'] > 0)]
        if not invalid_transactions.empty:
            print(f"Advertencia: {len(invalid_transactions)} transacciones tienen tanto cargo como abono > 0")
        
        # Estadísticas del procesamiento para información del usuario
        total_cargos = df['Cargo'].sum()
        total_abonos = df['Abono'].sum()
        saldo_inicial = df['Saldo'].iloc[0] - (df['Abono'].iloc[0] - df['Cargo'].iloc[0]) if len(df) > 0 else 0
        saldo_final = df['Saldo'].iloc[-1] if len(df) > 0 else 0
        
        print(f"\n=== RESUMEN DEL PROCESAMIENTO PDF ===")
        print(f"Archivo procesado: {os.path.basename(pdf_path)}")
        print(f"Páginas procesadas: {len(pages_text)}")
        print(f"Líneas analizadas: {lineas_procesadas}")
        print(f"Transacciones encontradas: {len(df)}")
        print(f"Total cargos: {total_cargos:,.2f}")
        print(f"Total abonos: {total_abonos:,.2f}")
        print(f"Saldo inicial estimado: {saldo_inicial:,.2f}")
        print(f"Saldo final: {saldo_final:,.2f}")
        print(f"=====================================\n")
        
        return df

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Archivo no encontrado: {str(e)}")
    except PermissionError as e:
        raise PermissionError(f"Sin permisos para leer el archivo: {str(e)}")
    except Exception as e: # Manejar cualquier otro error que ocurra durante el procesamiento del PDF
        error_msg = (
            f"Error al procesar el extracto bancario PDF.\n\n"
            f"Archivo: {pdf_path}\n"
            f"Error: {str(e)}\n\n"
            f"Sugerencias:\n"
            f"• Verifique que el archivo no esté dañado\n"
            f"• Asegúrese de que sea un extracto bancario en formato texto\n"
            f"• Compruebe que el formato coincida con el esperado\n"
            f"• Intente con un archivo PDF diferente"
        )
        raise ValueError(error_msg)