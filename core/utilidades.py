import os

archivos_cargados = {} # Diccionario para almacenar los archivos cargados con su ruta y nombre  

def obtener_nombre_archivo(ruta):  # Obtener el nombre del archivo a partir de su ruta  
    return os.path.basename(ruta)
