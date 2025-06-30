import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from pdf_parser import transformacion_pdf
from excel_loader import data_base

# Procesar el extracto bancario y comparar con los datos de la base 
def procesar_extracto_bancario(pdf_1, datos_1, moneda, anio): # Procesar el extracto bancario y comparar con los datos de la base
    """
    Función para procesar el extracto bancario y comparar con los datos de la base.
    Permite modificar el año en la columna 'fecha' si se especifica.

    Parámetros:
    pdf_1: DataFrame - Datos extraídos del PDF.
    datos_1: DataFrame - Datos de la base.
    moneda: str - Moneda para la comparación.
    nuevo_anio: int - Año que se desea establecer en la columna 'fecha'. (Opcional)

    Retorna:
    DataFrame - DataFrame procesado con las comparaciones realizadas.
    """
    df_pdf = transformacion_pdf(pdf_1) # Procesar el PDF y extraer los datos relevantes 
    df_base = data_base(datos_1) # Cargar el archivo Excel y procesar los datos
    df_pdf = pd.DataFrame(df_pdf)   # Asegurar que df_pdf sea un DataFrame  
    anios = anio
    df_pdf['Fecha'] = pd.to_datetime(df_pdf['FechaOper'].astype(str) + '/'+ anios , format='%d/%m/%Y', errors='coerce') # Convertir la columna 'FechaOper' a tipo datetime  
    df_pdf['Fecha'] = df_pdf['Fecha'].dt.date 

    df_acc2 = df_base.query(f'MONEDA == "{moneda}"') # Filtrar el DataFrame base por la moneda seleccionada 
    resultado = pd.merge(
        df_pdf[['Fecha','Concepto', 'Cargo','Abono','Saldo']],
        df_acc2[['Fecha','NOP','MONEDA','RAZON SOCIAL','CONCEPTO','MONTO','CENTRO COSTO']],
        left_on=['Fecha', 'Cargo'],
        right_on=['Fecha', 'MONTO'],
        how='left',
    ) # Realizar un merge entre el DataFrame del PDF y el DataFrame base filtrado por moneda    
    resultado.fillna('---', inplace=True) # Reemplazar los valores NaN con '---' para facilitar la 
    filtro = resultado[resultado["NOP"] != "---"]

# Paso 1: Coincidencias exactas de Saldo con NOP diferentes
    bloques_1 = []
    for i in range(len(filtro) - 1):
        if filtro['Saldo'].iloc[i] == filtro['Saldo'].iloc[i + 1]:
            if filtro['NOP'].iloc[i] != filtro['NOP'].iloc[i + 1]:
                fila = filtro[filtro['Saldo'] == filtro['Saldo'].iloc[i]]
                bloques_1.append(fila)

    total = pd.concat(bloques_1)

    # Reasignar total como el nuevo total filtrad

    # Paso 2: Agrupar por coincidencias exactas de Saldo y NOP diferentes (bloques repetidos)
    bloques_2 = []
    for i in range(len(total) - 1):
        if total['Saldo'].iloc[i] == total['Saldo'].iloc[i + 1]:
            if total['NOP'].iloc[i] != total['NOP'].iloc[i + 1]:
                mask = (total['NOP'] == total['NOP'].iloc[i]) & (total['Saldo'] == total['Saldo'].iloc[i])
                bloques_2.append(total[mask])

    combine = pd.concat(bloques_2).drop_duplicates(subset=["Saldo", "NOP"], keep="first") \
                                            .drop_duplicates(subset=["NOP"], keep="first")
    cambios_saldo = []
    for i in range(len(total) - 2):
        if total['Saldo'].iloc[i] != total['Saldo'].iloc[i + 1]:
            if total['NOP'].iloc[i] != total['NOP'].iloc[i + 1]:
                if i + 2 < len(total):
                    mask = (total['NOP'] == total['NOP'].iloc[i]) & (total['Saldo'] ==
                                                                    total['Saldo'].iloc[i + 2])
                cambios_saldo.append(total[mask])

    combined_dfa = pd.concat(cambios_saldo).drop_duplicates(subset=["Saldo", "NOP"], keep="first")

    # Paso 4: Unión final y orden
    tabla_unica = pd.concat([combine, combined_dfa]).sort_index()
    
    tabla_repetidas = resultado.drop(index=total.index)
    total_final = pd.concat([tabla_repetidas,tabla_unica]).sort_index()
    total_final = total_final[['Fecha', 'Concepto','CONCEPTO','CENTRO COSTO', 'NOP', 'Abono', 'Cargo', 'Saldo','MONEDA']] 

    return total_final