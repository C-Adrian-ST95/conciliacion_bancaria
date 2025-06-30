import pdfplumber
import re
import pandas as pd

def transformacion_pdf(pdf_path):              
    """
    Procesa un archivo PDF de extracto bancario y retorna los datos estructurados en un DataFrame.

    Extrae texto desde todas las páginas del PDF, aplica expresiones regulares para identificar
    los campos relevantes (fechas, origen, concepto, referencia, monto, saldo), y construye un 
    DataFrame con columnas como Cargo, Abono y Saldo calculadas en base a la lógica contable.

    Parámetros:
    pdf_path : str
        Ruta del archivo PDF que contiene el extracto bancario.

    Retorna:
    pandas.DataFrame
        DataFrame con las columnas:
        ['FechaOper', 'FechaValor', 'Origen', 'Concepto', 'Referencia', 'Cargo', 'Abono', 'Saldo']

    Lanza:
    FileNotFoundError:
        Si el archivo no se encuentra en la ruta especificada.
    ValueError:
        Si el archivo no contiene texto, no se identifican transacciones válidas, 
        o si ocurre algún error durante el procesamiento.
    """
    
    try: # Abrir el PDF y extraer el texto  
        with pdfplumber.open(pdf_path) as pdf: # Verificar si el PDF tiene páginas  
            text = "\n".join([page.extract_text() for page in pdf.pages]) # Extraer texto de todas las páginas del PDF
        if not text: # Si no se pudo extraer texto, lanzar una excepción    
            raise ValueError("El PDF no contiene texto o no se pudo extraer.")

        pattern = re.compile(
            r"(?P<FechaOper>\d{2}/\d{2})\s+"
            r"(?P<FechaValor>\d{2}/\d{2})\s+"
            r"(?P<Origen>\d{3})\s+"
            r"(?P<Concepto>.+?)\s+"
            r"(?P<Referencia>\d{7,}|0000)?\s*"
            r"(?P<Monto>\d{1,3}(?:,\d{3})*\.\d{2})?\s*"
            r"(?P<Saldo>\d{1,3}(?:,\d{3})*\.\d{2})"
        ) # Expresión regular para extraer los datos del texto del PDF

        rows = [] # Lista para almacenar las filas extraídas del PDF
        saldo_anterior = None # Variable para almacenar el saldo anterior 

        for line in text.splitlines(): # Iterar sobre cada línea del texto extraído 
            match = pattern.search(line) # Buscar coincidencias con la expresión regular
            if match: # Si se encuentra una coincidencia, extraer los datos 

                d = match.groupdict() # Extraer los datos de la coincidencia 
                concepto = d["Concepto"].strip() # Limpiar el concepto de espacios en blanco
                referencia = d["Referencia"] or "--" # Si no hay referencia, asignar un valor por defecto 
                saldo = float(d["Saldo"].replace(',', '')) # Convertir el saldo a float, eliminando comas

                montos = []# Lista para almacenar los montos extraídos
                if d["Monto"]: # Si hay un monto, convertirlo a float y eliminar comas  
                    montos.append(float(d["Monto"].replace(',', ''))) # Si hay un monto, agregarlo a la lista de montos 

                cargo, abono = 0.0, 0.0 
                if len(montos) == 1:  
                    if saldo_anterior is not None: # Si hay un saldo anterior, comparar con el saldo actual 
                        if saldo > saldo_anterior: # Si el saldo actual es mayor que el anterior, es un abono
                            abono = montos[0]
                        else:
                            cargo = montos[0]
                    else:
                        cargo = montos[0]

                rows.append({ 
                    "FechaOper": d["FechaOper"],
                    "FechaValor": d["FechaValor"],
                    "Origen": d["Origen"],
                    "Concepto": concepto,
                    "Referencia": referencia,
                    "Cargo": round(cargo, 2),
                    "Abono": round(abono, 2),
                    "Saldo": round(saldo, 2)
                }) # Añadir la fila extraída a la lista de filas        

                saldo_anterior = saldo # Actualizar el saldo anterior para la siguiente iteración   

        if not rows: # Si no se encontraron filas, lanzar una excepción 
            raise ValueError("No se encontraron transacciones en el documento.")

        df = pd.DataFrame(rows) 
        #if 'FechaOper' in df.columns: # Convertir la columna 'FechaOper' a tipo datetime    
            #df['fecha'] = pd.to_datetime(df['FechaOper'].astype(str) + '/2024', format='%d/%m/%Y', errors='coerce')
        return df

    except FileNotFoundError: # Manejar el caso en que el archivo PDF no se encuentra   
        raise FileNotFoundError(f"El archivo {pdf_path} no fue encontrado.")
    except Exception as e: # Manejar cualquier otro error que ocurra durante el procesamiento del PDF
        raise ValueError(f"Error al procesar el extracto bancario: {str(e)}")