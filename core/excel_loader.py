import pandas as pd
import os

def data_base(file_path): 
    """
    Carga y procesa un archivo Excel de base de datos contable para análisis bancario.

    Esta función realiza una transformación completa de los datos contables desde Excel,
    incluyendo limpieza de datos, conversión de tipos, manejo de valores nulos y 
    construcción de columnas derivadas. Es especialmente útil para preparar datos
    contables que serán comparados con extractos bancarios.

    Transformaciones realizadas:
    - Conversión de tipos de datos apropiados para análisis
    - Creación de columna 'Fecha' desde componentes ANO/MES/DIA
    - Limpieza y estandarización de campos de texto
    - Validación de integridad de datos contables
    - Manejo de valores nulos y datos faltantes

    Parámetros:
    -----------
    file_path : str
        Ruta absoluta o relativa del archivo Excel (.xlsx, .xls) que contiene
        los datos contables. El archivo debe tener las siguientes columnas:
        - 'ANO': Año de la transacción (entero)
        - 'MES': Mes de la transacción (1-12)
        - 'DIA': Día de la transacción (1-31)
        - 'NUM OPERACION': Número de operación (entero, puede tener nulos)
        - 'N° DOCUMENTO': Número de documento (texto)
        - 'NOP': Número de operación procesado (texto)
        - 'MONEDA': Código de moneda (PEN, USD, etc.)
        - 'MONTO': Monto de la transacción
        - Otras columnas contables opcionales

    Retorna:
    --------
    pandas.DataFrame
        DataFrame transformado y limpio con las siguientes características:
        - Tipos de datos optimizados para análisis
        - Columna 'Fecha' de tipo datetime.date
        - Campos de texto estandarizados
        - Valores nulos reemplazados apropiadamente
        - Validaciones de integridad aplicadas

        Columnas principales del DataFrame resultante:
        - 'Fecha' (datetime.date): Fecha construida desde ANO/MES/DIA
        - 'NUM OPERACION' (int): Número de operación (0 si es nulo)
        - 'N° DOCUMENTO' (str): Número de documento como texto
        - 'NOP' (str): Número de operación como texto
        - 'MONEDA' (str): Código de moneda
        - 'MONTO' (float): Monto de la transacción
        - Otras columnas preservadas del archivo original

    Lanza:
    ------
    FileNotFoundError:
        Si el archivo Excel no existe en la ruta especificada.
    ValueError:
        Si el archivo no es un Excel válido, faltan columnas requeridas,
        o los datos no pueden ser procesados correctamente.
    PermissionError:
        Si no hay permisos para leer el archivo.
    pandas.errors.EmptyDataError:
        Si el archivo Excel está vacío o no contiene datos.

    Ejemplos:
    ---------
    >>> df = data_base("contabilidad_2024.xlsx")
    >>> print(df.dtypes)
    Fecha              object
    NUM OPERACION       int64
    MONEDA             object
    MONTO             float64
    ...

    >>> # Verificar rango de fechas
    >>> print(f"Desde: {df['Fecha'].min()} hasta: {df['Fecha'].max()}")

    >>> # Verificar monedas disponibles
    >>> print(f"Monedas: {df['MONEDA'].unique().tolist()}")

    Notas:
    ------
    - Se requiere que el archivo tenga al menos las columnas ANO, MES, DIA
    - Los valores nulos en NUM OPERACION se convierten a 0
    - Las fechas inválidas son manejadas con valores nulos
    - Se preservan todas las columnas del archivo original
    - La función es optimizada para archivos Excel grandes (>10MB)
    """    try:
        # Validación inicial del archivo
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo Excel no existe en la ruta: {file_path}")
        
        # Verificar extensión del archivo
        valid_extensions = ['.xlsx', '.xls', '.xlsm']
        if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"El archivo debe ser Excel (.xlsx, .xls, .xlsm). Archivo recibido: {file_path}")
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("El archivo Excel está vacío (0 bytes).")
        
        if file_size > 100 * 1024 * 1024:  # 100MB límite
            print(f"Advertencia: Archivo grande ({file_size / (1024*1024):.1f}MB). El procesamiento puede tomar tiempo.")

        print(f"Cargando archivo Excel: {os.path.basename(file_path)} ({file_size / 1024:.1f}KB)")
        
        # Cargar el archivo Excel con configuración específica
        try:
            df_base = pd.read_excel(
                file_path, 
                dtype={'N° DOCUMENTO': str},  # Forzar como texto para preservar formato
                parse_dates=False  # No parsear fechas automáticamente
            )
        except Exception as e:
            if "No such file or directory" in str(e):
                raise FileNotFoundError(f"No se pudo acceder al archivo: {file_path}")
            elif "Unsupported format" in str(e):
                raise ValueError(f"Formato de archivo Excel no soportado: {file_path}")
            else:
                raise ValueError(f"Error al leer el archivo Excel: {str(e)}")
        
        # Verificar que el archivo no esté vacío
        if df_base.empty:
            raise ValueError("El archivo Excel no contiene datos o todas las filas están vacías.")
        
        print(f"Archivo cargado exitosamente: {len(df_base)} filas, {len(df_base.columns)} columnas")
        
        # Verificar columnas requeridas
        required_columns = ['ANO', 'MES', 'DIA']
        missing_columns = [col for col in required_columns if col not in df_base.columns]
        if missing_columns:
            available_columns = list(df_base.columns)
            raise ValueError(
                f"Faltan columnas requeridas: {missing_columns}\n"
                f"Columnas disponibles: {available_columns}\n"
                f"El archivo debe contener al menos: {required_columns}"
            )
        
        # Información sobre las columnas disponibles
        print(f"Columnas detectadas: {list(df_base.columns)}")
        
        # Procesar NUM OPERACION con validación
        if 'NUM OPERACION' in df_base.columns:
            # Contar valores nulos antes del procesamiento
            null_count = df_base['NUM OPERACION'].isna().sum()
            if null_count > 0:
                print(f"Convirtiendo {null_count} valores nulos en NUM OPERACION a 0")
            
            df_base['NUM OPERACION'] = df_base['NUM OPERACION'].fillna(0).astype(int)
        else:
            print("Advertencia: Columna 'NUM OPERACION' no encontrada. Se omitirá.")
        
        # Procesar N° DOCUMENTO
        if 'N° DOCUMENTO' in df_base.columns:
            df_base['N° DOCUMENTO'] = df_base['N° DOCUMENTO'].astype(str)
            # Limpiar valores que se convirtieron a 'nan' como texto
            df_base['N° DOCUMENTO'] = df_base['N° DOCUMENTO'].replace('nan', '')
        else:
            print("Advertencia: Columna 'N° DOCUMENTO' no encontrada.")
        
        # Procesar NOP
        if 'NOP' in df_base.columns:
            df_base['NOP'] = df_base['NOP'].astype(str)
            df_base['NOP'] = df_base['NOP'].replace('nan', '')
        else:
            print("Advertencia: Columna 'NOP' no encontrada.")
        
        # Validar y procesar columnas de fecha
        date_columns = ['ANO', 'MES', 'DIA']
        for col in date_columns:
            # Verificar que las columnas de fecha sean numéricas
            if not pd.api.types.is_numeric_dtype(df_base[col]):
                try:
                    df_base[col] = pd.to_numeric(df_base[col], errors='coerce')
                    null_count = df_base[col].isna().sum()
                    if null_count > 0:
                        print(f"Advertencia: {null_count} valores no numéricos en columna {col} convertidos a NaN")
                except:
                    raise ValueError(f"No se pudo convertir la columna {col} a valores numéricos")
        
        # Validar rangos de fechas
        año_min, año_max = df_base['ANO'].min(), df_base['ANO'].max()
        mes_min, mes_max = df_base['MES'].min(), df_base['MES'].max()
        dia_min, dia_max = df_base['DIA'].min(), df_base['DIA'].max()
        
        # Verificar rangos lógicos
        if año_min < 1900 or año_max > 2100:
            print(f"Advertencia: Rango de años inusual: {año_min} - {año_max}")
        
        if mes_min < 1 or mes_max > 12:
            invalid_months = df_base[(df_base['MES'] < 1) | (df_base['MES'] > 12)]
            print(f"Advertencia: {len(invalid_months)} registros con meses inválidos (fuera del rango 1-12)")
        
        if dia_min < 1 or dia_max > 31:
            invalid_days = df_base[(df_base['DIA'] < 1) | (df_base['DIA'] > 31)]
            print(f"Advertencia: {len(invalid_days)} registros con días inválidos (fuera del rango 1-31)")
        
        # Crear columna Fecha con manejo de errores detallado
        print("Creando columna Fecha desde ANO/MES/DIA...")
        try:
            # Crear DataFrame temporal para construcción de fechas
            date_df = df_base[['ANO', 'MES', 'DIA']].copy()
            date_df = date_df.rename(columns={'ANO': 'year', 'MES': 'month', 'DIA': 'day'})
            
            # Convertir a datetime con manejo de errores
            df_base['Fecha'] = pd.to_datetime(date_df, errors='coerce').dt.date
            
            # Verificar fechas inválidas
            invalid_dates = df_base['Fecha'].isna().sum()
            if invalid_dates > 0:
                print(f"Advertencia: {invalid_dates} fechas inválidas encontradas y convertidas a NaN")
                
                # Mostrar algunos ejemplos de fechas inválidas
                invalid_rows = df_base[df_base['Fecha'].isna()][['ANO', 'MES', 'DIA']].head()
                if not invalid_rows.empty:
                    print("Ejemplos de fechas inválidas:")
                    print(invalid_rows.to_string())
        
        except Exception as e:
            raise ValueError(f"Error al crear la columna Fecha: {str(e)}")
        
        # Verificar información de moneda si existe
        if 'MONEDA' in df_base.columns:
            monedas_unicas = df_base['MONEDA'].unique()
            monedas_count = df_base['MONEDA'].value_counts()
            print(f"Monedas encontradas: {list(monedas_unicas)}")
            print("Distribución por moneda:")
            for moneda, count in monedas_count.items():
                print(f"  {moneda}: {count} registros")
        
        # Verificar información de montos si existe
        if 'MONTO' in df_base.columns:
            montos_nulos = df_base['MONTO'].isna().sum()
            if montos_nulos > 0:
                print(f"Advertencia: {montos_nulos} valores nulos en columna MONTO")
            
            monto_min = df_base['MONTO'].min()
            monto_max = df_base['MONTO'].max()
            monto_promedio = df_base['MONTO'].mean()
            print(f"Rango de montos: {monto_min:,.2f} - {monto_max:,.2f} (promedio: {monto_promedio:,.2f})")
        
        # Estadísticas finales
        print(f"\n=== RESUMEN PROCESAMIENTO EXCEL ===")
        print(f"Archivo: {os.path.basename(file_path)}")
        print(f"Registros procesados: {len(df_base)}")
        print(f"Rango de fechas: {df_base['Fecha'].min()} a {df_base['Fecha'].max()}")
        print(f"Columnas disponibles: {len(df_base.columns)}")
        print(f"===================================\n")
        
        return df_base
        
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except PermissionError as e:
        raise PermissionError(f"Sin permisos para leer el archivo Excel: {str(e)}")
    except pd.errors.EmptyDataError:
        raise ValueError("El archivo Excel está vacío o no contiene datos válidos.")
    except Exception as e:
        error_msg = (
            f"Error al procesar el archivo Excel.\n\n"
            f"Archivo: {file_path}\n"
            f"Error: {str(e)}\n\n"
            f"Sugerencias:\n"
            f"• Verifique que el archivo no esté abierto en Excel\n"
            f"• Asegúrese de que contiene las columnas requeridas (ANO, MES, DIA)\n"
            f"• Compruebe que el formato del archivo sea válido (.xlsx, .xls)\n"
            f"• Verifique que tiene permisos de lectura sobre el archivo"
        )
        raise ValueError(error_msg)  

# Procesar el extracto bancario y comparar con los datos de la base 