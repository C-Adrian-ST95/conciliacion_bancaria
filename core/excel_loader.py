import pandas as pd

# Cargar el archivo Excel y procesar los datos  
def data_base(file_path): # Cargar el archivo Excel y procesar los datos 
    """
    Carga un archivo Excel y realiza la transformación de datos necesaria para su análisis.
    Convierte las columnas clave a tipos adecuados, completa valores nulos y
    genera una columna de fecha a partir de las columnas 'ANO', 'MES' y 'DIA'.

    Parámetros:
    file_path : str
        Ruta del archivo Excel a procesar.

    Retorna:
    pandas.DataFrame
        DataFrame transformado con las columnas listas para análisis,
        incluyendo una nueva columna 'Fecha' de tipo fecha.
    """   
    
    df_base = pd.read_excel(file_path, dtype={'N° DOCUMENTO': str}) # Cargar el archivo Excel   
    df_base['NUM OPERACION'] = df_base['NUM OPERACION'].fillna(0).astype(int) # Asegurar que 'NUM OPERACION' sea entero 
    df_base['N° DOCUMENTO'] = df_base['N° DOCUMENTO'].astype(str) # Convertir 'N° DOCUMENTO' a cadena de texto  
    df_base['NOP'] = df_base['NOP'].astype(str)     # Convertir 'NOP' a cadena de texto 
    df_base['Fecha'] = pd.to_datetime(
        df_base.rename(columns={'ANO': 'year', 'MES': 'month', 'DIA': 'day'})[['year', 'month', 'day']]
    ).dt.date # Crear una columna 'fecha' a partir de las columnas 'ANO', 'MES' y 'DIA
    return df_base  

# Procesar el extracto bancario y comparar con los datos de la base 