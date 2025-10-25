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
    
    resultado[['Concepto', 'CONCEPTO', 'CENTRO COSTO', 'NOP']] = resultado[['Concepto', 'CONCEPTO', 'CENTRO COSTO', 'NOP']].astype(object)    

    df_con_nop = resultado[resultado['NOP'].notna()].copy()
    df_sin_nop = resultado[resultado['NOP'].isna()].copy()

    # Identificar saldos repetidos (aparecen con múltiples NOPs)
    conteo_saldos = df_con_nop.groupby('Saldo')['NOP'].nunique().reset_index(name='Num_NOP')
    saldos_repetidos = conteo_saldos.loc[conteo_saldos['Num_NOP'] > 1, 'Saldo']


    # Separar datos
    filas_saldos_unicos = df_con_nop[~df_con_nop['Saldo'].isin(saldos_repetidos)]
    filas_saldos_repetidos = df_con_nop[df_con_nop['Saldo'].isin(saldos_repetidos)]

    if len(filas_saldos_repetidos) > 0:
        
        # Ordenar por Saldo → NOP → Cargo → Fecha
        cand = filas_saldos_repetidos.sort_values(['Saldo', 'NOP', 'Cargo', 'Fecha'])

        # Conjuntos de control
        usados_nop = set()
        usados_saldo = set()
        sel_rows = []

        print("\n" + "-"*80)

        for idx, row in cand.iterrows():
            nop, saldo, cargo = row['NOP'], row['Saldo'], row['Cargo']

            # Obtener todas las filas con este Saldo
            grupo_saldo = cand[cand['Saldo'] == saldo]
            nops_en_grupo = grupo_saldo['NOP'].unique()
            cargos_en_grupo = grupo_saldo['Cargo'].unique()

            # CASO 1: Mismo NOP repite el mismo Saldo (duplicado exacto o casi exacto)
            # → Solo tomar la primera ocurrencia
            if nop in usados_nop and saldo in usados_saldo:
                continue
            
            # CASO 2: Diferentes NOPs con mismo Saldo
            # → Tomar uno por cada NOP diferente
            if len(nops_en_grupo) > 1 and len(cargos_en_grupo) > 1:
                # Si este NOP no ha sido usado con este Saldo
                if nop not in usados_nop:
                    sel_rows.append(row)
                    usados_nop.add(nop)
                    
                continue
            
            # CASO 3: Primer encuentro de esta combinación
            if nop not in usados_nop and saldo not in usados_saldo:
                sel_rows.append(row)
                usados_nop.add(nop)
                usados_saldo.add(saldo)
            else:
                razones = []
                if nop in usados_nop:
                    razones.append("NOP usado")
                if saldo in usados_saldo:
                    razones.append("Saldo usado")
        filas_seleccionadas = pd.DataFrame(sel_rows)
    else:
        filas_seleccionadas = pd.DataFrame()

    # Resultado final
    if not filas_seleccionadas.empty:
        resultado_final = pd.concat([filas_saldos_unicos, filas_seleccionadas]).sort_index()
    else:
        resultado_final = filas_saldos_unicos

    # Detalle de saldos repetidos procesados
    if not filas_seleccionadas.empty:
        
        for saldo in sorted(filas_seleccionadas['Saldo'].unique()):
            seleccionadas_este_saldo = filas_seleccionadas[filas_seleccionadas['Saldo'] == saldo]
            
            for _, row in seleccionadas_este_saldo.iterrows():
                pass

    resultado_final = pd.concat([resultado_final, df_sin_nop]).sort_index()
    resultado_final = resultado_final[['Fecha', 'Concepto', 'CONCEPTO', 'CENTRO COSTO', 'NOP', 'Abono', 'Cargo', 'Saldo', 'MONEDA']]

    resultado_final.loc[:, ['Concepto', 'CONCEPTO', 'CENTRO COSTO', 'NOP']] = resultado_final.loc[:, ['Concepto', 'CONCEPTO', 'CENTRO COSTO', 'NOP', 'MONEDA']].fillna('---')

    resultado_final = resultado_final.set_axis(['Fecha', 'Movimiento', 'Detalle', 'Tipo de Gasto', 'NOP', 'Debe', 'Haber', 'Saldo', 'Moneda'], axis=1)

    resultado_final['Debe'] = resultado_final['Debe'].astype(float)
    resultado_final['Haber'] = resultado_final['Haber'].astype(float)
    resultado_final['Saldo'] = resultado_final['Saldo'].astype(float)

    return resultado_final