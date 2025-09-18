import tkinter as tk
from gui.componentes import cargar_excel, cargar_pdf, seleccionar_y_procesar, exportar_actual, mostrar_ayuda
from gui.graficos import graficar_dataframe_seleccionado
from gui.ventana import frame_botones, ventana




# Crear botones para cargar archivos Excel y PDF, procesar y exportar           
btn_cargar_excel = tk.Button(frame_botones, text="Cargar Excel", command=cargar_excel) # Cargar archivo Excel
btn_cargar_excel.pack(side="left", padx=10)

btn_cargar_pdf = tk.Button(frame_botones, text="Cargar PDF Bancario", command=cargar_pdf) # Cargar archivo PDF Bancario 
btn_cargar_pdf.pack(side="left", padx=10)

btn_procesar = tk.Button(frame_botones, text="Comparar PDF y Excel", command=seleccionar_y_procesar)# Procesar los archivos cargados    
btn_procesar.pack(side="left", padx=10)

btn_exportar = tk.Button(frame_botones, text="Exportar a Excel", command=exportar_actual)# Exportar el archivo seleccionado a Excel
btn_exportar.pack(side="left", padx=10)


btn_grafica = tk.Button(frame_botones, text="Mostrar Gráfica", command=graficar_dataframe_seleccionado)# Mostrar gráfica de los datos procesados    
btn_grafica.pack(side="left", padx=5)

# Agregar botón de ayuda con diseño destacado
btn_ayuda = tk.Button(frame_botones, text="❓ Ayuda", command=mostrar_ayuda, 
                     bg="#2196F3", fg="white", font=("Arial", 9, "bold"))# Mostrar ayuda completa
btn_ayuda.pack(side="right", padx=10)



ventana.mainloop() # Iniciar el bucle principal de la ventana   

