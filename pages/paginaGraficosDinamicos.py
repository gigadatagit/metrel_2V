import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io
import plotly.graph_objects as go
import requests
import zipfile
import login as login
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm
from docx.shared import Mm
from io import BytesIO
from utilities import calcular_Valor_Tension_Nominal, calcular_Valor_Corriente_Nominal, renombrar_columnas, obtener_Columnas_DataFrame, convertir_Unidades, seleccionar_Energia_Generada, crear_Medidas_DataFrame_Energias, filtrar_DataFrame_Columnas, crear_DataFrame_Tension, crear_DataFrame_Desbalance_Tension, crear_DataFrame_Corriente, crear_DataFrame_Desbalance_Corriente, crear_DataFrame_PQS_Potencias, crear_DataFrame_FactPotencia, crear_DataFrame_DistTension, crear_DataFrame_Armonicos_DistTension, crear_DataFrame_DistCorriente, crear_DataFrame_Armonicos_DistCorriente, crear_DataFrame_Flicker_Final, crear_DataFrame_FactorK_Final, calcular_Valor_Corriente_Cortacircuito, calcular_Valor_ISC_entre_IL, calcular_Valor_Limite_TDD, calcular_Valores_Limites_Armonicos, crear_DataFrame_CargabilidadTDD_Final, crear_Medidas_DataFrame_Tension, crear_Medidas_DataFrame_DesbTension, crear_Medidas_DataFrame_Corriente, crear_Medidas_DataFrame_DesbCorriente, crear_Medidas_DataFrame_PQS, crear_Medidas_DataFrame_FactorPotencia, crear_Medidas_DataFrame_Distorsion_Tension, crear_Medidas_DataFrame_Armonicos_DistTension, crear_Medidas_DataFrame_Distorsion_Corriente, crear_Medidas_DataFrame_Armonicos_DistCorriente, crear_Medidas_DataFrame_CargabilidadTDD, crear_Medidas_DataFrame_Flicker, crear_Medidas_DataFrame_FactorK, crear_DataFrame_Energias, calcular_Variacion_Tension, calcular_Valor_Cargabilidad_Disponibilidad, calcular_Observacion_Tension, calcular_Observacion_Corriente, calcular_Observacion_DesbTension, calcular_Observacion_DesbCorriente, calcular_Observacion_THDV, calcular_Observacion_Armonicos_Corriente, calcular_Observacion_TDD, graficar_Timeline_Tension, graficar_Timeline_Corriente, graficar_Timeline_DesbTension, graficar_Timeline_DesbCorriente, graficar_Timeline_PQS_ActApa, graficar_Timeline_PQS_CapInd, graficar_Timeline_FactPotencia, graficar_Timeline_Distorsion_Tension, graficar_Timeline_Distorsion_Corriente, graficar_Timeline_CargabilidadTDD, graficar_Timeline_Flicker, graficar_Timeline_FactorK, generar_Graficos_Barras_Energias, graficar_Timeline_Tension_Plotly, graficar_Timeline_Corriente_Plotly, graficar_Timeline_DesbTension_Plotly, graficar_Timeline_DesbCorriente_Plotly, graficar_Timeline_PQS_ActApa_Plotly, graficar_Timeline_PQS_CapInd_Plotly, graficar_Timeline_FactPotencia_Plotly, graficar_Timeline_Distorsion_Tension_Plotly, graficar_Timeline_Distorsion_Corriente_Plotly, graficar_Timeline_CargabilidadTDD_Plotly, graficar_Timeline_Flicker_Plotly, graficar_Timeline_FactorK_Plotly, generar_Graficos_Barras_Energias_Plotly, crear_grafico

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    st.header('Información | :orange[Página de Gráficos Dinámicos]')
    
    uploaded_file = st.file_uploader("Elige un archivo de Parquet", type=["parquet"])
    if uploaded_file:
        try:
            
            #temp_db_path = "energyiea.db"
    
            # Guardamos el archivo subido en disco
            #with open(temp_db_path, "wb") as f:
                #f.write(uploaded_file.getbuffer())
            
            st.success("Archivo subido correctamente.")
            
            # Conexión a la base de datos SQLite
            #conn_sqlite = sqlite3.connect(temp_db_path)  # Reemplaza con el nombre de tu archivo SQLite

            # Leer la vista 'energy_view' en un DataFrame de pandas
            df = pd.read_parquet(uploaded_file)

            #st.markdown("""
            #---
            #
            #> ## Elige la plantilla para generar el informe.
            #
            #---
            #""")

            #plantillaSeleccionada = st.selectbox("Selecciona una Plantilla:", ["Vatia", "GIGA"])
            
            st.markdown("""
            ---
            
            > ## Elige si vas a visualizar o no las energías generadas.
            
            ---
            """)
            
            energiaGenerada = st.selectbox("Seleccione si quiere visualizar o no la Energía Generada:", ["Sí", "No"], index=1)
            
            st.markdown("""
            ---
            
            > ## Elige las respectivas unidades de medida para las siguientes variables.
            
            ---
            """)
            
            unidadMedidaVoltaje = st.selectbox("Seleccione la Unidad de Medida de Voltajes:", ["mV", "V"])
            unidadMedidaCorriente = st.selectbox("Seleccione la Unidad de Medida de Corrientes:", ["mA", "A"])
            unidadMedidaPotenciaActiva = st.selectbox("Seleccione la Unidad de Medida de Potencias (Activa):", ["W", "kW"])
            unidadMedidaPotenciaAparente = st.selectbox("Seleccione la Unidad de Medida de Potencias (Aparente):", ["VA", "kVA"])
            unidadMedidaPotenciaCapacitiva = st.selectbox("Seleccione la Unidad de Medida de Potencias (Capacitiva):", ["VAR", "kVAR"])
            unidadMedidaPotenciaInductiva = st.selectbox("Seleccione la Unidad de Medida de Potencias (Inductiva):", ["VAR", "kVAR"])
            unidadMedidaEnergiaActiva = st.selectbox("Seleccione la Unidad de Medida de Energías (Activa):", ["Wh", "kWh"])
            unidadMedidaEnergiaInductiva = st.selectbox("Seleccione la Unidad de Medida de Energías (Inductiva):", ["VARh", "kVARh"])
            unidadMedidaEnergiaCapacitiva = st.selectbox("Seleccione la Unidad de Medida de Energías (Capacitiva):", ["VARh", "kVARh"])
            
            
            st.markdown("""
            ---
            
            > ## Ingresa el valor de cada variable y dale click al botón para generar el informe.
            
            ---
            """)
            
            var1 = st.number_input("Ingrese el Valor Nominal de Tensión:", min_value=0.0, max_value=1000.0, step=0.1, format="%.1f")
            var2 = st.number_input("Ingrese el Valor de la Capacidad del Transformador [kVA]:", min_value=0.0, max_value=1000000.0, step=0.1, format="%.1f")
            var3 = st.number_input("Ingrese el Valor de Referencia - Desbalance de Tensión [%]:", min_value=0.0, max_value=2.0, step=0.1, format="%.1f")
            var4 = st.number_input("Ingrese el Valor de Referencia - Desbalance de Corriente [%]:", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
            var5 = st.number_input("Ingrese el Valor de Límite Máximo de Distorsión Armónica de Tensión:", min_value=0.0, max_value=1000.0, step=0.1, format="%.1f")
            var6 = st.number_input("Ingrese el Valor de Impedancia de Cortocircuito (Transformador):", min_value=0.0, max_value=1000.0, step=0.1, format="%.1f")
            var7 = st.number_input("Ingrese el Valor de Referencia - PLT (Flicker):", min_value=0.0, max_value=5.0, step=0.1, format="%.1f")
            
            st.markdown("""
            ---
            
            > ## Visualización de Gráfico Interactivo para Comparación de Variables.
        
            ---
            """)
                    
            crear_grafico(df.copy())
            
            if st.button("Generar Gráficos Dinámicos", type="primary"):
                
                try:
                    
                    var_Limite_Inferior_Tension = calcular_Valor_Tension_Nominal(var1)[0]
                    var_Limite_Superior_Tension = calcular_Valor_Tension_Nominal(var1)[1]
                    
                    print(f"Limites de Tensión - Inferior ({var_Limite_Inferior_Tension}) y Superior({var_Limite_Superior_Tension})")

                    var_Corriente_Nominal_Value = calcular_Valor_Corriente_Nominal((var2 * 1000), var1)
                    
                    print(f"Valor de Corriente Nominal {var_Corriente_Nominal_Value}")

                    df_Read_Final = renombrar_columnas(dataFrame=df)

                    df = df_Read_Final.copy()

                    print("¿Quedan valores NaN en el DataFrame de Minuto a Minuto?", df.isna().any().any())

                    print("*****"*50)
                    print(df.head(5))
                    
                    print("*****"*50)
                    print(df.index)
                    
                    print("*****"*50)
                    print(df.shape)
                    
                    print("*****"*50)
                    
                    # Lista de columnas de Tensión a convertir
                    columnas_Tension_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['U12(Min)', 'U12(Med)', 'U12(Max)', 'U23(Min)', 'U23(Med)', 'U23(Max)', 'U31(Min)', 'U31(Med)', 'U31(Max)'], valores_Corchetes=['V'])

                    # Llamada a la función
                    df_Cambios_Tension = convertir_Unidades(dataFrame=df, columnas_DataFrame=columnas_Tension_Unidades, unidad_Elegida=unidadMedidaVoltaje, unidades_Validas=['mV', 'V'])
                    
                    #st.dataframe(df_Cambios_Tension.head(5))
                    

                    # Lista de columnas de Corriente a convertir
                    columnas_Corriente_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['I1(Min)', 'I1(Med)', 'I1(Max)', 'I2(Min)', 'I2(Med)', 'I2(Max)', 'I3(Min)', 'I3(Med)', 'I3(Max)'], valores_Corchetes=['A'])

                    # Llamada a la función
                    df_Cambios_Corriente = convertir_Unidades(dataFrame=df_Cambios_Tension, columnas_DataFrame=columnas_Corriente_Unidades, unidad_Elegida=unidadMedidaCorriente, unidades_Validas=['mA', 'A'])
                    
                    #st.dataframe(df_Cambios_Corriente.head(5))

                    #print("******"*50)

                    # Lista de columnas de PQS - Activa a convertir
                    columnas_PQS_Activa_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ptot+(Min)', 'Ptot+(Med)', 'Ptot+(Max)'], valores_Corchetes=['W'])

                    # Llamada a la función
                    df_Cambios_PQS_Activa = convertir_Unidades(dataFrame=df_Cambios_Corriente, columnas_DataFrame=columnas_PQS_Activa_Unidades, unidad_Elegida=unidadMedidaPotenciaActiva, unidades_Validas=['W', 'kW'])
                    
                    #st.dataframe(df_Cambios_PQS_Activa.head(5))

                    #print("******"*50)

                    # Lista de columnas de PQS - Aparente a convertir
                    columnas_PQS_Aparente_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Setot+(Min)', 'Setot+(Med)', 'Setot+(Max)'], valores_Corchetes=['VA'])

                    # Llamada a la función
                    df_Cambios_PQS_Aparente = convertir_Unidades(dataFrame=df_Cambios_PQS_Activa, columnas_DataFrame=columnas_PQS_Aparente_Unidades, unidad_Elegida=unidadMedidaPotenciaAparente, unidades_Validas=['VA', 'kVA'])

                    #st.dataframe(df_Cambios_PQS_Aparente.head(5))

                    #print("******"*50)

                    # Lista de columnas de PQS - Capacitiva a convertir
                    columnas_PQS_Capacitiva_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ntotcap-(Min)', 'Ntotcap-(Med)', 'Ntotcap-(Max)'], valores_Corchetes=['var'])

                    # Llamada a la función
                    df_Cambios_PQS_Capacitiva = convertir_Unidades(dataFrame=df_Cambios_PQS_Aparente, columnas_DataFrame=columnas_PQS_Capacitiva_Unidades, unidad_Elegida=unidadMedidaPotenciaCapacitiva, unidades_Validas=['VAR', 'kVAR'])

                    #st.dataframe(df_Cambios_PQS_Capacitiva.head(5))

                    #print("******"*50)

                    # Lista de columnas de PQS - Inductiva a convertir
                    columnas_PQS_Inductiva_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ntotind+(Min)', 'Ntotind+(Med)', 'Ntotind+(Max)'], valores_Corchetes=['var'])

                    # Llamada a la función
                    df_Cambios_PQS_Inductiva = convertir_Unidades(dataFrame=df_Cambios_PQS_Capacitiva, columnas_DataFrame=columnas_PQS_Inductiva_Unidades, unidad_Elegida=unidadMedidaPotenciaInductiva, unidades_Validas=['VAR', 'kVAR'])

                    #st.dataframe(df_Cambios_PQS_Inductiva.head(5))

                    #print("******"*50)

                    # Lista de columnas de Energía - Activa a convertir
                    columnas_Energia_Activa_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Eptot+(Med)', 'Eptot-(Med)', 'Ep1-(Med)', 'Ep2-(Med)', 'Ep3-(Med)', 'Ep1+(Med)', 'Ep2+(Med)', 'Ep3+(Med)'], valores_Corchetes=['kWh', 'Wh'])

                    # Llamada a la función
                    df_Cambios_Energia_Activa = convertir_Unidades(dataFrame=df_Cambios_PQS_Inductiva, columnas_DataFrame=columnas_Energia_Activa_Unidades, unidad_Elegida=unidadMedidaEnergiaActiva, unidades_Validas=['Wh', 'kWh'])

                    #st.dataframe(df_Cambios_Energia_Activa.head(5))

                    #print("******"*50)

                    # Lista de columnas de Energía - Inductiva a convertir
                    columnas_Energia_Inductiva_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['EQtotind+(Med)', 'EQtotind-(Med)', 'EQfund1ind+(Med)', 'EQfund2ind+(Med)', 'EQfund3ind+(Med)', 'EQfund1ind-(Med)', 'EQfund2ind-(Med)', 'EQfund3ind-(Med)'], valores_Corchetes=['kVARh', 'varh'])

                    # Llamada a la función
                    df_Cambios_Energia_Inductiva = convertir_Unidades(dataFrame=df_Cambios_Energia_Activa, columnas_DataFrame=columnas_Energia_Inductiva_Unidades, unidad_Elegida=unidadMedidaEnergiaInductiva, unidades_Validas=['VARh', 'kVARh'])

                    #st.dataframe(df_Cambios_Energia_Inductiva.head(5))

                    #print("******"*50)

                    # Lista de columnas de Energía - Capacitiva a convertir
                    columnas_Energia_Capacitiva_Unidades = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['EQtotcap+(Med)', 'EQtotcap-(Med)', 'EQfund1cap+(Med)', 'EQfund2cap+(Med)', 'EQfund3cap+(Med)', 'EQfund1cap-(Med)', 'EQfund2cap-(Med)', 'EQfund3cap-(Med)'], valores_Corchetes=['kVARh', 'varh'])

                    # Llamada a la función
                    df_Cambios_Energia_Capacitiva = convertir_Unidades(dataFrame=df_Cambios_Energia_Inductiva, columnas_DataFrame=columnas_Energia_Capacitiva_Unidades, unidad_Elegida=unidadMedidaEnergiaCapacitiva, unidades_Validas=['VARh', 'kVARh'])

                    

                    print("******"*50)

                    # Declaración del DataFrame Final con los cambios de las Unidades de Medida
                    df = df_Cambios_Energia_Capacitiva.copy()

                    #print("DataFrame final con los cambios de Unidades de Medida")

                    st.dataframe(df.head(10))

                    #print("******"*50)
                    
                    listado_Columnas_Energia_Generada = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ep1-(Med)', 'Ep2-(Med)', 'Ep3-(Med)', 'EQfund1ind-(Med)', 'EQfund2ind-(Med)', 'EQfund3ind-(Med)', 'EQfund1cap-(Med)', 'EQfund2cap-(Med)', 'EQfund3cap-(Med)', 'PFetotcap+(Med)', 'PFetotind+(Med)', 'PFetotcap-(Med)', 'PFetotind-(Med)'], valores_Corchetes=['Wh', 'varh', ''])

                    if energiaGenerada == "Sí":

                        #df_Read = pd.read_parquet(filename1)

                        df_Energia_Generada = seleccionar_Energia_Generada(dataFrame=df, listado_Columnas=listado_Columnas_Energia_Generada)

                        print(df_Energia_Generada.head())

                        listado_Columnas_Energias_Generada_Final: list = df_Energia_Generada.columns.to_list()

                        print(f"Columnas: {listado_Columnas_Energias_Generada_Final}")

                        print(f'Listado de Columnas de Energías Generadas {listado_Columnas_Energias_Generada_Final}')

                        df_Tabla_Calculos_Energias_Generadas = crear_Medidas_DataFrame_Energias(dataFrame=df_Energia_Generada, listado_Columnas_a_Medir=listado_Columnas_Energias_Generada_Final[1:])

                        print(df_Tabla_Calculos_Energias_Generadas.head())

                        print("******"*50)

                        table_Data_Energy_Generated = df_Energia_Generada.copy()

                        table_Data_Energy_Generated_Info = table_Data_Energy_Generated.to_dict(orient="records")

                        listado_Columnas_PR_Energia_Generada_P1: list = df_Energia_Generada.columns.to_list()
                        listado_Columnas_PR_Energia_Generada: list = listado_Columnas_PR_Energia_Generada_P1[1:4]

                        print(f"Prueba de Columnas Energía Generada {listado_Columnas_PR_Energia_Generada}")

                        #print("###########"*50)
                        #print(f"Columnas PR - Energías (Generadas) {list_Columns_Graficos_Consolidado_Energia_Generada}")
                        #print("###########"*50)

                        data_Percentiles_Energia_Generada: dict = {
                            'PERCENTIL_ENERGIA_ACTIVA_MED': round(df_Tabla_Calculos_Energias_Generadas[listado_Columnas_PR_Energia_Generada[0]].iloc[0], 2),
                            'PERCENTIL_ENERGIA_CAPACITIVA_MED': round(df_Tabla_Calculos_Energias_Generadas[listado_Columnas_PR_Energia_Generada[2]].iloc[0], 2),
                            'PERCENTIL_ENERGIA_INDUCTIVA_MED': round(df_Tabla_Calculos_Energias_Generadas[listado_Columnas_PR_Energia_Generada[1]].iloc[0], 2)
                        }

                        print(data_Percentiles_Energia_Generada)

                        visualizacion_Generada = True

                    else:
                        
                        visualizacion_Generada = False

                        var_Enlace_Plantilla = "https://github.com/gigadatagit/GIGA_Data/blob/365a61d9e72f3e175c39d5fa6cb1c189e0c70ffa/vars_Template_ETV_Metrel_VATIA5.docx?raw=true"

                        #print(f"Has elegido no visualizar la información de la Energía Generada {e}")
                        #return  # Salir del menú

                    # Enlace a la Plantilla del Documento de Word que contiene toda la información del Informe
                    #url = var_Enlace_Plantilla

                    # Petición para Traer la información de esa URL con la Plantilla
                    #response = requests.get(url)

                    # Guardado de contenido de la Plantilla de Word en un el Almacenamiento de Memoria
                    #template_data = BytesIO(response.content)

                    # Crear una instancia de DocxTemplate - Carga el contenido de la Plantilla del Documento de Word
                    #doc = DocxTemplate(template_data)



                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para la tensión
                    list_Columns_Grafico_Tension: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['U12(Med)', 'U23(Med)', 'U31(Med)'], valores_Corchetes=['V'])
                    #print(f"Listado de Columnas Tensión: {list_Columns_Grafico_Tension}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Desbalance de Tensión
                    list_Columns_Grafico_DesbTension: list = ['Desbalance']

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para la corriente
                    list_Columns_Grafico_Corriente: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['I1(Max)', 'I2(Max)', 'I3(Max)', 'IN(Med)'], valores_Corchetes=['A'])
                    #print(f"Listado de Columnas Corriente: {list_Columns_Grafico_Corriente}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Desbalance de Tensión
                    list_Columns_Grafico_DesbCorriente: list = ['Desbalance']



                    # Declaración de todos los DataFrames filtrando por las columnas que se van a Utilizar para generar el Documento y Realizar los Cálculos o Gráficos

                    df_Tabla_Tension = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'U12(Min)', 'U12(Med)', 'U12(Max)', 'U23(Min)', 'U23(Med)', 'U23(Max)', 'U31(Min)', 'U31(Med)', 'U31(Max)'], valores_Corchetes=['UTC', 'V'])

                    df_Tabla_Corriente = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'I1(Min)', 'I1(Med)', 'I1(Max)', 'I2(Min)', 'I2(Med)', 'I2(Max)', 'I3(Min)', 'I3(Med)', 'I3(Max)', 'IN(Min)', 'IN(Med)', 'IN(Max)'], valores_Corchetes=['UTC', 'A'])

                    df_Tabla_Desbalance_Tension = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'U12(Med)', 'U23(Med)', 'U31(Med)'], valores_Corchetes=['UTC', 'V'])

                    df_Tabla_Desbalance_Corriente = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'I1(Med)', 'I2(Med)', 'I3(Med)'], valores_Corchetes=['UTC', 'A'])

                    df_Tabla_PQS_Potencias = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'Ptot+(Min)', 'Ptot+(Med)', 'Ptot+(Max)', 'Ntotcap-(Min)', 'Ntotcap-(Min)', 'Ntotcap-(Med)', 'Ntotcap-(Max)', 'Ntotind+(Min)', 'Ntotind+(Med)', 'Ntotind+(Max)', 'Setot+(Min)', 'Setot+(Med)', 'Setot+(Max)'], valores_Corchetes=['UTC', 'W', 'var', 'VA'])

                    df_Tabla_FactorPotencia = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'PFetotcap+(Min)', 'PFetotcap+(Med)', 'PFetotcap+(Max)', 'PFetotind+(Min)', 'PFetotind+(Med)', 'PFetotind+(Max)', 'PFetotcap-(Min)', 'PFetotcap-(Med)', 'PFetotcap-(Max)', 'PFetotind-(Min)', 'PFetotind-(Med)', 'PFetotind-(Max)'], valores_Corchetes=['UTC', ''])

                    df_Tabla_Distorsion_Tension = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'THD U12(Max)', 'THD U23(Max)', 'THD U31(Max)'], valores_Corchetes=['UTC', '%'])

                    df_Tabla_Armonicos_Distorsion_Tension = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'U12 a3(Max)', 'U12 a5(Max)', 'U12 a7(Max)', 'U12 a9(Max)', 'U12 a11(Max)', 'U12 a13(Max)', 'U12 a15(Max)', 'U23 a3(Max)', 'U23 a5(Max)', 'U23 a7(Max)', 'U23 a9(Max)', 'U23 a11(Max)', 'U23 a13(Max)', 'U23 a15(Max)', 'U31 a3(Max)', 'U31 a5(Max)', 'U31 a7(Max)', 'U31 a9(Max)', 'U31 a11(Max)', 'U31 a13(Max)', 'U31 a15(Max)'], valores_Corchetes=['UTC', '%'])

                    df_Tabla_Distorsion_Corriente = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'THD I1(Max)', 'THD I2(Max)', 'THD I3(Max)'], valores_Corchetes=['UTC', '%'])

                    df_Tabla_Armonicos_Distorsion_Corriente = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'I1 a3(Max)', 'I1 a5(Max)', 'I1 a7(Max)', 'I1 a9(Max)', 'I1 a11(Max)', 'I1 a13(Max)', 'I1 a15(Max)', 'I2 a3(Max)', 'I2 a5(Max)', 'I2 a7(Max)', 'I2 a9(Max)', 'I2 a11(Max)', 'I2 a13(Max)', 'I2 a15(Max)', 'I3 a3(Max)', 'I3 a5(Max)', 'I3 a7(Max)', 'I3 a9(Max)', 'I3 a11(Max)', 'I3 a13(Max)', 'I3 a15(Max)'], valores_Corchetes=['UTC', '%'])

                    df_Tabla_Armonicos_Cargabilidad_TDD = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'TDD I1(ProAct)', 'TDD I2(ProAct)', 'TDD I3(ProAct)'], valores_Corchetes=['UTC', '%'])

                    df_Tabla_Flicker = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'Plt1(Min)', 'Plt1(Med)', 'Plt1(Max)', 'Plt2(Min)', 'Plt2(Med)', 'Plt2(Max)', 'Plt3(Min)', 'Plt3(Med)', 'Plt3(Max)'], valores_Corchetes=['UTC', ''])

                    df_Tabla_FactorK = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'Ki1(Min)', 'Ki1(Med)', 'Ki1(Max)', 'Ki2(Min)', 'Ki2(Med)', 'Ki2(Max)', 'Ki3(Min)', 'Ki3(Med)', 'Ki3(Max)'], valores_Corchetes=['UTC', ''])

                    df_Tabla_FactorPotencia_Grupos = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'PFetotind+(Min)', 'PFetotind+(Med)', 'PFetotind+(Max)'], valores_Corchetes=['UTC', ''])

                    df_Tabla_Energias = filtrar_DataFrame_Columnas(dataFrame=df, nombres_Fijos_Columnas=['Hora', 'Ep1+(Med)', 'Ep2+(Med)', 'Ep3+(Med)', 'Ep1-(Med)', 'Ep2-(Med)', 'Ep3-(Med)', 'EQfund1cap+(Med)', 'EQfund2cap+(Med)', 'EQfund3cap+(Med)', 'EQfund1cap-(Med)', 'EQfund2cap-(Med)', 'EQfund3cap-(Med)', 'EQfund1ind+(Med)', 'EQfund2ind+(Med)', 'EQfund3ind+(Med)', 'EQfund1ind-(Med)', 'EQfund2ind-(Med)', 'EQfund3ind-(Med)'], valores_Corchetes=['UTC', 'Wh', 'varh'])

                    #print("******"*50)

                    # En este paso se realizan los pasos adicionales como cálculos de nuevas columnas u operaciones entre columnas

                    df_Tabla_Tension_Final = crear_DataFrame_Tension(dataFrame=df_Tabla_Tension, var_Lim_Inf_Ten=var_Limite_Inferior_Tension, val_Nom=var1, var_Lim_Sup_Ten=var_Limite_Superior_Tension)

                    #st.dataframe(df_Tabla_Tension_Final.head(5))
                    #print("******"*50)

                    df_Tabla_Desb_Tension = crear_DataFrame_Desbalance_Tension(dataFrame=df_Tabla_Desbalance_Tension, val_Desb_Ten=var3, nombres_Fijos_Columnas=['U12(Med)', 'U23(Med)', 'U31(Med)'], valores_Corchetes=['V'])

                    #st.dataframe(df_Tabla_Desb_Tension.head(5))
                    #print("******"*50)

                    df_Tabla_Corriente_Final = crear_DataFrame_Corriente(dataFrame=df_Tabla_Corriente, var_Lim_Corr_Nom=var_Corriente_Nominal_Value)

                    #st.dataframe(df_Tabla_Corriente_Final.head(5))
                    #print("******"*50)

                    df_Tabla_Desb_Corriente = crear_DataFrame_Desbalance_Corriente(dataFrame=df_Tabla_Desbalance_Corriente, val_Desb_Corr=var4, nombres_Fijos_Columnas=['I1(Med)', 'I2(Med)', 'I3(Med)'], valores_Corchetes=['A'])

                    #st.dataframe(df_Tabla_Desb_Corriente.head(5))
                    #print("******"*50)

                    df_Tabla_PQS_Final = crear_DataFrame_PQS_Potencias(dataFrame=df_Tabla_PQS_Potencias)

                    #st.dataframe(df_Tabla_PQS_Final.head(5))
                    #print("******"*50)

                    df_Tabla_FactPotenciaFinal = crear_DataFrame_FactPotencia(dataFrame=df_Tabla_FactorPotencia)

                    #st.dataframe(df_Tabla_FactPotenciaFinal.head(5))
                    #print("******"*50)

                    #df_Tabla_FactorPotencia_GruposFinal = crear_DataFrame_FactPotenciaGrupos(dataFrame=df_Tabla_FactorPotencia_Grupos, nombres_Fijos_Columnas=['PFetotind+(Min)', 'PFetotind+(Med)', 'PFetotind+(Max)'], valores_Corchetes=[''])

                    #print(df_Tabla_FactorPotencia_GruposFinal)
                    #print("******"*50)

                    df_Tabla_Distorsion_TensionFinal = crear_DataFrame_DistTension(dataFrame=df_Tabla_Distorsion_Tension, val_Dist_Arm_Tension=var5)

                    #st.dataframe(df_Tabla_Distorsion_TensionFinal.head(5))
                    #print("******"*50)

                    df_Tabla_Armonicos_Distorsion_Tension_Final = crear_DataFrame_Armonicos_DistTension(dataFrame=df_Tabla_Armonicos_Distorsion_Tension)

                    #st.dataframe(df_Tabla_Armonicos_Distorsion_Tension_Final.head(5))
                    #print("******"*50)

                    df_Tabla_Distorsion_CorrienteFinal = crear_DataFrame_DistCorriente(dataFrame=df_Tabla_Distorsion_Corriente)

                    #st.dataframe(df_Tabla_Distorsion_CorrienteFinal.head(5))
                    #print("******"*50)

                    df_Tabla_Armonicos_Distorsion_Corriente_Final = crear_DataFrame_Armonicos_DistCorriente(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente)

                    #st.dataframe(df_Tabla_Armonicos_Distorsion_Corriente_Final.head(5))
                    #print("******"*50)

                    df_Tabla_FlickerFinal = crear_DataFrame_Flicker_Final(dataFrame=df_Tabla_Flicker, val_Lim_Flicker=var7)

                    #st.dataframe(df_Tabla_FlickerFinal.head(5))
                    #print("******"*50)

                    df_Tabla_FactorKFinal = crear_DataFrame_FactorK_Final(dataFrame=df_Tabla_FactorK)

                    #st.dataframe(df_Tabla_FactorKFinal.head(5))
                    #print("******"*50)



                    print("******"*50)

                    valor_Maximo_Corrientes = df[list_Columns_Grafico_Corriente[0:3]].max().max()

                    print(f"Valor Máximo de de las Corrientes: {valor_Maximo_Corrientes}")

                    valor_Corriente_Cortacircuito = calcular_Valor_Corriente_Cortacircuito(var_Corriente_Nominal_Value, var6)

                    print(f"Valor de Corriente Cortacircuito {valor_Corriente_Cortacircuito}")

                    valor_ISC_sobre_IL = calcular_Valor_ISC_entre_IL(valor_Corriente_Cortacircuito, valor_Maximo_Corrientes)

                    print(f"Valor de ISC/IL {valor_ISC_sobre_IL}")

                    valor_Limite_TDD: float = calcular_Valor_Limite_TDD(valor_ISC_sobre_IL)

                    print(f"Valor del Limite del TDD {valor_Limite_TDD}")

                    valores_Limites_Armonicos = calcular_Valores_Limites_Armonicos(valor_Limite_TDD)

                    print(f"Valores de los Límites de los Armónicos {valores_Limites_Armonicos.values()}")

                    df_Tabla_Armonicos_Cargabilidad_TDDFinal = crear_DataFrame_CargabilidadTDD_Final(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDD, val_Lim_CargTDD=valor_Limite_TDD)

                    ##st.dataframe(df_Tabla_Armonicos_Cargabilidad_TDDFinal.head(5))



                    print("******"*50)



                    # En este paso se están realizando los cálculos de las tablas con Percentiles, Máximos, Promedios y Mínimos.

                    df_Tabla_Calculos_Tension = crear_Medidas_DataFrame_Tension(dataFrame=df_Tabla_Tension_Final, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Tension_Final, nombres_Fijos_Columnas=['U12(Min)', 'U12(Med)', 'U12(Max)', 'U23(Min)', 'U23(Med)', 'U23(Max)', 'U31(Min)', 'U31(Med)', 'U31(Max)'], valores_Corchetes=['V']))

                    #st.markdown("""
                    #Medidas - DataFrame Tensión
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Tension)
                    #print("******"*50)

                    df_Tabla_Calculos_Desb_Tension = crear_Medidas_DataFrame_DesbTension(dataFrame=df_Tabla_Desb_Tension, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Desb_Tension, nombres_Fijos_Columnas=['U12(Med)', 'U23(Med)', 'U31(Med)'], valores_Corchetes=['V']))

                    #st.markdown("""
                    #Medidas - DataFrame Desbalance de Tensión
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Desb_Tension)
                    #print("******"*50)

                    df_Tabla_Calculos_Corriente = crear_Medidas_DataFrame_Corriente(dataFrame=df_Tabla_Corriente_Final, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Corriente_Final, nombres_Fijos_Columnas=['I1(Min)', 'I1(Med)', 'I1(Max)', 'I2(Min)', 'I2(Med)', 'I2(Max)', 'I3(Min)', 'I3(Med)', 'I3(Max)', 'IN(Min)', 'IN(Med)', 'IN(Max)'], valores_Corchetes=['A']))

                    #st.markdown("""
                    #Medidas - DataFrame Corriente
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Corriente)
                    #print("******"*50)

                    df_Tabla_Calculos_Desb_Corriente = crear_Medidas_DataFrame_DesbCorriente(dataFrame=df_Tabla_Desb_Corriente, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Desb_Corriente, nombres_Fijos_Columnas=['I1(Med)', 'I2(Med)', 'I3(Med)'], valores_Corchetes=['A']))

                    #st.markdown("""
                    #Medidas - DataFrame Desbalance de Corriente
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Desb_Corriente)
                    #print("******"*50)

                    df_Tabla_Calculos_PQS_Potencias = crear_Medidas_DataFrame_PQS(dataFrame=df_Tabla_PQS_Final, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_PQS_Final, nombres_Fijos_Columnas=['Ptot+(Min)', 'Ptot+(Med)', 'Ptot+(Max)', 'Ntotcap-(Min)', 'Ntotcap-(Med)', 'Ntotcap-(Max)', 'Ntotind+(Min)', 'Ntotind+(Med)', 'Ntotind+(Max)', 'Setot+(Min)', 'Setot+(Med)', 'Setot+(Max)'], valores_Corchetes=['W', 'var', 'VA']))

                    #st.markdown("""
                    #Medidas - DataFrame PQS Potencias
                    #""")

                    #st.dataframe(df_Tabla_Calculos_PQS_Potencias)
                    #print("******"*50)

                    df_Tabla_Calculos_FactorPotencia_Consumido = crear_Medidas_DataFrame_FactorPotencia(dataFrame=df_Tabla_FactPotenciaFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactPotenciaFinal, nombres_Fijos_Columnas=['PFetotcap+(Min)', 'PFetotcap+(Med)', 'PFetotcap+(Max)', 'PFetotind+(Min)', 'PFetotind+(Med)', 'PFetotind+(Max)'], valores_Corchetes=['']))

                    #st.markdown("""
                    #Medidas - DataFrame Factor de Potencia (Consumido)
                    #""")

                    #st.dataframe(df_Tabla_Calculos_FactorPotencia_Consumido)
                    #print("******"*50)

                    df_Tabla_Calculos_FactorPotencia_Generado = crear_Medidas_DataFrame_FactorPotencia(dataFrame=df_Tabla_FactPotenciaFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactPotenciaFinal, nombres_Fijos_Columnas=['PFetotcap-(Min)', 'PFetotcap-(Med)', 'PFetotcap-(Max)', 'PFetotind-(Min)', 'PFetotind-(Med)', 'PFetotind-(Max)'], valores_Corchetes=['']))

                    #st.markdown("""
                    #Medidas - DataFrame Factor de Potencia (Generado)
                    #""")

                    #st.dataframe(df_Tabla_Calculos_FactorPotencia_Generado)
                    #print("******"*50)

                    #df_Tabla_Calculos_FactorPotenciaGeneral = crear_Medidas_DataFrame_FactorPotenciaGeneral(dictFP=df_Tabla_FactorPotencia_GruposFinal)

                    #print(df_Tabla_Calculos_FactorPotenciaGeneral)
                    #print("******"*50)

                    df_Tabla_Calculos_DistTension = crear_Medidas_DataFrame_Distorsion_Tension(dataFrame=df_Tabla_Distorsion_TensionFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Distorsion_TensionFinal, nombres_Fijos_Columnas=['THD U12(Max)', 'THD U23(Max)', 'THD U31(Max)'], valores_Corchetes=['%']))

                    #st.markdown("""
                    #Medidas - DataFrame Distorsión de Tensión
                    #""")

                    #st.dataframe(df_Tabla_Calculos_DistTension)
                    #print("******"*50)

                    df_Tabla_Calculos_Armonicos_DistTension = crear_Medidas_DataFrame_Armonicos_DistTension(dataFrame=df_Tabla_Armonicos_Distorsion_Tension_Final, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Distorsion_Tension_Final, nombres_Fijos_Columnas=['U12 a3(Max)', 'U12 a5(Max)', 'U12 a7(Max)', 'U12 a9(Max)', 'U12 a11(Max)', 'U12 a13(Max)', 'U12 a15(Max)', 'U23 a3(Max)', 'U23 a5(Max)', 'U23 a7(Max)', 'U23 a9(Max)', 'U23 a11(Max)', 'U23 a13(Max)', 'U23 a15(Max)', 'U31 a3(Max)', 'U31 a5(Max)', 'U31 a7(Max)', 'U31 a9(Max)', 'U31 a11(Max)', 'U31 a13(Max)', 'U31 a15(Max)'], valores_Corchetes=['%']))

                    #st.markdown("""
                    #Medidas - DataFrame Armónicos de Distorsión de Tensión
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Armonicos_DistTension.head())
                    #print("******"*50)

                    df_Tabla_Calculos_DistCorriente = crear_Medidas_DataFrame_Distorsion_Corriente(dataFrame=df_Tabla_Distorsion_CorrienteFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Distorsion_CorrienteFinal, nombres_Fijos_Columnas=['THD I1(Max)', 'THD I2(Max)', 'THD I3(Max)'], valores_Corchetes=['%']))

                    #st.markdown("""
                    #Medidas - DataFrame Distorsión de Corriente
                    #""")

                    #st.dataframe(df_Tabla_Calculos_DistCorriente)
                    #print("******"*50)

                    df_Tabla_Calculos_Armonicos_DistCorriente = crear_Medidas_DataFrame_Armonicos_DistCorriente(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente_Final, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente_Final, nombres_Fijos_Columnas=['I1 a3(Max)', 'I1 a5(Max)', 'I1 a7(Max)', 'I1 a9(Max)', 'I1 a11(Max)', 'I1 a13(Max)', 'I1 a15(Max)', 'I2 a3(Max)', 'I2 a5(Max)', 'I2 a7(Max)', 'I2 a9(Max)', 'I2 a11(Max)', 'I2 a13(Max)', 'I2 a15(Max)', 'I3 a3(Max)', 'I3 a5(Max)', 'I3 a7(Max)', 'I3 a9(Max)', 'I3 a11(Max)', 'I3 a13(Max)', 'I3 a15(Max)'], valores_Corchetes=['%']))

                    #st.markdown("""
                    #Medidas - DataFrame Armónicos de Distorsión de Corriente
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Armonicos_DistCorriente)
                    #print("******"*50)

                    df_Tabla_Calculos_CargabilidadTDD = crear_Medidas_DataFrame_CargabilidadTDD(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDDFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDDFinal, nombres_Fijos_Columnas=['TDD I1(ProAct)', 'TDD I2(ProAct)', 'TDD I3(ProAct)'], valores_Corchetes=['%']))

                    #st.markdown("""
                    #Medidas - DataFrame Armónicos de Cargabilidad TDD
                    #""")

                    #st.dataframe(df_Tabla_Calculos_CargabilidadTDD)
                    #print("******"*50)

                    df_Tabla_Calculos_Flicker = crear_Medidas_DataFrame_Flicker(dataFrame=df_Tabla_FlickerFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_FlickerFinal, nombres_Fijos_Columnas=['Plt1(Med)', 'Plt2(Med)', 'Plt3(Med)'], valores_Corchetes=['']))

                    #st.markdown("""
                    #Medidas - DataFrame Flicker
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Flicker)
                    #print("******"*50)

                    df_Tabla_Calculos_FactorK = crear_Medidas_DataFrame_FactorK(dataFrame=df_Tabla_FactorKFinal, listado_Columnas_a_Medir=obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactorKFinal, nombres_Fijos_Columnas=['Ki1(Min)', 'Ki1(Med)', 'Ki1(Max)', 'Ki2(Min)', 'Ki2(Med)', 'Ki2(Max)', 'Ki3(Min)', 'Ki3(Med)', 'Ki3(Max)'], valores_Corchetes=['']))

                    #st.markdown("""
                    #Medidas - DataFrame FactorK
                    #""")

                    #st.dataframe(df_Tabla_Calculos_FactorK)
                    #print("******"*50)


                    # Separamos esta sección ya que es importante distinguir el uso del DataFrame que está compuesto por los datos del .TXT que va de Hora a Hora

                    print("Información sobre el DataFrame de Energías")
                    
                    #st.markdown("""
                    #---
                    #
                    #DataFrame Energías
                    #
                    #--- 
                    #""")

                    dataFrame_Energias = crear_DataFrame_Energias(dataFrame=df)

                    #st.dataframe(dataFrame_Energias.head(5))

                    listado_Columnas_Energias: list = dataFrame_Energias.columns.to_list()

                    print(f'Listado de Columnas de Energías {listado_Columnas_Energias}')

                    df_Tabla_Calculos_Energias = crear_Medidas_DataFrame_Energias(dataFrame_Energias, listado_Columnas_a_Medir=listado_Columnas_Energias[1:])

                    #st.markdown("""
                    #Medidas - DataFrame Energías
                    #""")

                    #st.dataframe(df_Tabla_Calculos_Energias.head(5))
                    #print("******"*50)



                    #df_Tabla

                    # Convertimos la información del DataFrame que contiene las energías para luego convertirlo en un diccionario con los registros de cada una de las columnas y poder mostrarlos en una tabla de Word

                    table_Data_Energy_Info = dataFrame_Energias.to_dict(orient="records")
                    
                    # Separamos esta sección ya que es importante distinguir el uso del DataFrame del Factor de Potencia, para aplicarle Filtros de Medición a los Datos

                    listado_Columnas_FactorPotencia_Consumido: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['PFetotcap+(Min)', 'PFetotcap+(Med)', 'PFetotcap+(Max)', 'PFetotind+(Min)', 'PFetotind+(Med)', 'PFetotind+(Max)'], valores_Corchetes=[''])

                    print(f'Listado de Columnas de Factor de Potencia (Consumido) {listado_Columnas_FactorPotencia_Consumido}')



                    filtro_FP_Cons_POS_CANTPOS = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Consumido[5]] > 0)

                    filtro_FP_Cons_POS_CANTZeros = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Consumido[5]] == abs(0))

                    filtro_FP_Cons_NEG_CANTPOS = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Consumido[2]] > 0)

                    filtro_FP_Cons_NEG_CANTZeros = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Consumido[2]] == abs(0))



                    # Separamos esta sección ya que es importante distinguir el uso del DataFrame del Factor de Potencia, para aplicarle Filtros de Medición a los Datos

                    listado_Columnas_FactorPotencia_Generado: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['PFetotcap-(Min)', 'PFetotcap-(Med)', 'PFetotcap-(Max)', 'PFetotind-(Min)', 'PFetotind-(Med)', 'PFetotind-(Max)'], valores_Corchetes=[''])

                    print(f'Listado de Columnas de Factor de Potencia (Generado) {listado_Columnas_FactorPotencia_Generado}')



                    filtro_FP_Gene_POS_CANTPOS = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Generado[5]] > 0)

                    filtro_FP_Gene_POS_CANTZeros = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Generado[5]] == abs(0))

                    filtro_FP_Gene_NEG_CANTPOS = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Generado[2]] > 0)

                    filtro_FP_Gene_NEG_CANTZeros = (df_Tabla_FactPotenciaFinal[listado_Columnas_FactorPotencia_Generado[2]] == abs(0))


                    print("******"*50)

                    # En este lugar declaramos un diccionario con los Valores negativos, ceros y positivos del Factor de Potencia Consumido

                    data_Cantidad_NEG_POS_FactorPotencia_Consumido: dict = {
                        'CANT_POSITIVOS_FP_POS': len(df_Tabla_FactPotenciaFinal[filtro_FP_Cons_POS_CANTPOS]),
                        'CANT_CEROS_FP_POS': len(df_Tabla_FactPotenciaFinal[filtro_FP_Cons_POS_CANTZeros]),
                        'CANT_POSITIVOS_FP_NEG': len(df_Tabla_FactPotenciaFinal[filtro_FP_Cons_NEG_CANTPOS]),
                        'CANT_CEROS_FP_NEG': len(df_Tabla_FactPotenciaFinal[filtro_FP_Cons_NEG_CANTZeros])
                    }

                    print(data_Cantidad_NEG_POS_FactorPotencia_Consumido)


                    print("******"*50)

                    # En este lugar declaramos un diccionario con los Valores negativos, ceros y positivos del Factor de Potencia Consumido

                    data_Cantidad_NEG_POS_FactorPotencia_Generado: dict = {
                        'CANT_POSITIVOS_FP_POS': len(df_Tabla_FactPotenciaFinal[filtro_FP_Gene_POS_CANTPOS]),
                        'CANT_CEROS_FP_POS': len(df_Tabla_FactPotenciaFinal[filtro_FP_Gene_POS_CANTZeros]),
                        'CANT_POSITIVOS_FP_NEG': len(df_Tabla_FactPotenciaFinal[filtro_FP_Gene_NEG_CANTPOS]),
                        'CANT_CEROS_FP_NEG': len(df_Tabla_FactPotenciaFinal[filtro_FP_Gene_NEG_CANTZeros])
                    }

                    print(data_Cantidad_NEG_POS_FactorPotencia_Generado)


                    print("******"*50)

                    # En este lugar declaramos diccionarios con los percentiles para utilizarlos luego en gráficos o en otras partes del código

                    listado_Columnas_PR_Tension: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['U12(Med)', 'U23(Med)', 'U31(Med)'], valores_Corchetes=['V'])

                    print(f"Columnas PR - Tension {listado_Columnas_PR_Tension}")

                    data_Percentiles_Tension: dict = {
                        'PERCENTIL_TENSIN_L12': round(df_Tabla_Calculos_Tension[listado_Columnas_PR_Tension[0]].iloc[0], 2),
                        'PERCENTIL_TENSIN_L23': round(df_Tabla_Calculos_Tension[listado_Columnas_PR_Tension[1]].iloc[0], 2),
                        'PERCENTIL_TENSIN_L31': round(df_Tabla_Calculos_Tension[listado_Columnas_PR_Tension[2]].iloc[0], 2)
                    }

                    print(data_Percentiles_Tension)

                    print("******"*50)

                    listado_Columnas_PR_Corriente: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['I1(Max)', 'I2(Max)', 'I3(Max)', 'IN(Med)'], valores_Corchetes=['A'])

                    print(f"Columnas PR - Corriente {listado_Columnas_PR_Corriente}")

                    data_Percentiles_Corriente: dict = {
                        'PERCENTIL_CORR_MAX_L1': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente[0]].iloc[0], 2),
                        'PERCENTIL_CORR_MAX_L2': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente[1]].iloc[0], 2),
                        'PERCENTIL_CORR_MAX_L3': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente[2]].iloc[0], 2),
                        'PERCENTIL_CORR_MED_LN': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente[3]].iloc[0], 2)
                    }

                    print(data_Percentiles_Corriente)

                    print("******"*50)

                    listado_Columnas_PR_Corriente_Maximos: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['I1(Max)', 'I2(Max)', 'I3(Max)'], valores_Corchetes=['A'])

                    print(f"Columnas PR - Corrientes Máximas {listado_Columnas_PR_Corriente_Maximos}")

                    data_Percentiles_Corriente_Maximos: dict = {
                        'PERCENTIL_CORR_MAX_L1': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente_Maximos[0]].iloc[0], 2),
                        'PERCENTIL_CORR_MAX_L2': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente_Maximos[1]].iloc[0], 2),
                        'PERCENTIL_CORR_MAX_L3': round(df_Tabla_Calculos_Corriente[listado_Columnas_PR_Corriente_Maximos[2]].iloc[0], 2)
                    }

                    print(data_Percentiles_Corriente_Maximos)

                    print("******"*50)

                    listado_Columnas_PR_DesbTension: list = ['Desbalance']

                    print(f"Columnas PR - Desbalance de Tensión {listado_Columnas_PR_DesbTension}")

                    data_Percentiles_DesbTension: dict = {
                        'PERCENTIL_DESBALANCE_DESBTEN': round(df_Tabla_Calculos_Desb_Tension[listado_Columnas_PR_DesbTension[0]].iloc[0], 2)
                    }

                    print(data_Percentiles_DesbTension)

                    print("******"*50)

                    listado_Columnas_PR_DesbCorriente: list = ['Desbalance']

                    print(f"Columnas PR - Desbalance de Corriente {listado_Columnas_PR_DesbCorriente}")

                    data_Percentiles_DesbCorriente: dict = {
                        'PERCENTIL_DESBALANCE_DESBCORR': round(df_Tabla_Calculos_Desb_Corriente[listado_Columnas_PR_DesbCorriente[0]].iloc[0], 2)
                    }

                    print(data_Percentiles_DesbCorriente)

                    print("******"*50)

                    listado_Columnas_PR_PQS_ActApa: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ptot+(Med)', 'Setot+(Med)'], valores_Corchetes=['W', 'VA', 'kVA'])

                    print(f"Columnas PR - PQS Activa/Aparente {listado_Columnas_PR_PQS_ActApa}")

                    data_Percentiles_PQS_ActApa: dict = {
                        'PERCENTIL_PQS_ACT': round(df_Tabla_Calculos_PQS_Potencias[listado_Columnas_PR_PQS_ActApa[0]].iloc[0], 2),
                        'PERCENTIL_PQS_APA': round(df_Tabla_Calculos_PQS_Potencias[listado_Columnas_PR_PQS_ActApa[1]].iloc[0], 2)
                    }

                    print(data_Percentiles_PQS_ActApa)

                    print("******"*50)

                    listado_Columnas_PR_PQS_CapInd: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ntotcap-(Med)', 'Ntotind+(Med)'], valores_Corchetes=['var'])

                    print(f"Columnas PR - PQS Capacitiva/Inductiva {listado_Columnas_PR_PQS_CapInd}")

                    data_Percentiles_PQS_CapInd: dict = {
                        'PERCENTIL_PQS_CAP': round(df_Tabla_Calculos_PQS_Potencias[listado_Columnas_PR_PQS_CapInd[0]].iloc[0], 2),
                        'PERCENTIL_PQS_IND': round(df_Tabla_Calculos_PQS_Potencias[listado_Columnas_PR_PQS_CapInd[1]].iloc[0], 2)
                    }

                    print(data_Percentiles_PQS_CapInd)

                    print("******"*50)

                    listado_Columnas_PR_FactorPotencia_Consumido: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['PFetotcap+(Med)', 'PFetotind+(Med)'], valores_Corchetes=[''])

                    print(f"Columnas PR - Factor de Potencia Consumido {listado_Columnas_PR_FactorPotencia_Consumido}")

                    data_Percentiles_FactorPotencia_Consumido: dict = {
                        'PERCENTIL_FACTOR_POTENCIA_NEG': round(df_Tabla_Calculos_FactorPotencia_Consumido[listado_Columnas_PR_FactorPotencia_Consumido[1]].iloc[0], 2),
                        'PERCENTIL_FACTOR_POTENCIA_POS': round(df_Tabla_Calculos_FactorPotencia_Consumido[listado_Columnas_PR_FactorPotencia_Consumido[0]].iloc[0], 2)
                    }

                    print(data_Percentiles_FactorPotencia_Consumido)

                    print("******"*50)

                    listado_Columnas_PR_FactorPotencia_Generado: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['PFetotcap-(Med)', 'PFetotind-(Med)'], valores_Corchetes=[''])

                    print(f"Columnas PR - Factor de Potencia Generado {listado_Columnas_PR_FactorPotencia_Generado}")

                    data_Percentiles_FactorPotencia_Generado: dict = {
                        'PERCENTIL_FACTOR_POTENCIA_NEG': round(df_Tabla_Calculos_FactorPotencia_Generado[listado_Columnas_PR_FactorPotencia_Generado[1]].iloc[0], 2),
                        'PERCENTIL_FACTOR_POTENCIA_POS': round(df_Tabla_Calculos_FactorPotencia_Generado[listado_Columnas_PR_FactorPotencia_Generado[0]].iloc[0], 2)
                    }

                    print(data_Percentiles_FactorPotencia_Generado)

                    print("******"*50)

                    listado_Columnas_PR_Energia_P1: list = dataFrame_Energias.columns.to_list()
                    listado_Columnas_PR_Energia: list = listado_Columnas_PR_Energia_P1[1:4]

                    print(f"Columnas PR - Energías (Consumidas) {listado_Columnas_PR_Energia}")

                    data_Percentiles_Energia: dict = {
                        'PERCENTIL_ENERGIA_ACTIVA_MED': round(df_Tabla_Calculos_Energias[listado_Columnas_PR_Energia[0]].iloc[0], 2),
                        'PERCENTIL_ENERGIA_CAPACITIVA_MED': round(df_Tabla_Calculos_Energias[listado_Columnas_PR_Energia[2]].iloc[0], 2),
                        'PERCENTIL_ENERGIA_INDUCTIVA_MED': round(df_Tabla_Calculos_Energias[listado_Columnas_PR_Energia[1]].iloc[0], 2)
                    }

                    print(data_Percentiles_Energia)
                    
                    listado_Columnas_PR_DistorsionTension: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['THD U12(Max)', 'THD U23(Max)', 'THD U31(Max)'], valores_Corchetes=['%'])

                    print(f"Columnas PR - Distorsión de Tensión {listado_Columnas_PR_DistorsionTension}")

                    data_Percentiles_DistorsionTension: dict = {
                        'PERCENTIL_THDV_MAX_L1': round(df_Tabla_Calculos_DistTension[listado_Columnas_PR_DistorsionTension[0]].iloc[0],2),
                        'PERCENTIL_THDV_MAX_L2': round(df_Tabla_Calculos_DistTension[listado_Columnas_PR_DistorsionTension[1]].iloc[0],2),
                        'PERCENTIL_THDV_MAX_L3': round(df_Tabla_Calculos_DistTension[listado_Columnas_PR_DistorsionTension[2]].iloc[0],2)
                    }

                    print(data_Percentiles_DistorsionTension)

                    print("******"*50)

                    listado_Columnas_PR_DistorsionCorriente: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['THD I1(Max)', 'THD I2(Max)', 'THD I3(Max)'], valores_Corchetes=['%'])

                    print(f"Columnas PR - Distorsión de Corriente {listado_Columnas_PR_DistorsionCorriente}")

                    data_Percentiles_DistorsionCorriente: dict = {
                        'PERCENTIL_THDI_MAX_L1': round(df_Tabla_Calculos_DistCorriente[listado_Columnas_PR_DistorsionCorriente[0]].iloc[0],2),
                        'PERCENTIL_THDI_MAX_L2': round(df_Tabla_Calculos_DistCorriente[listado_Columnas_PR_DistorsionCorriente[1]].iloc[0],2),
                        'PERCENTIL_THDI_MAX_L3': round(df_Tabla_Calculos_DistCorriente[listado_Columnas_PR_DistorsionCorriente[2]].iloc[0],2)
                    }

                    print(data_Percentiles_DistorsionCorriente)

                    print("******"*50)

                    listado_Columnas_PR_CargabilidadTDD: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['TDD I1(ProAct)', 'TDD I2(ProAct)', 'TDD I3(ProAct)'], valores_Corchetes=['%'])

                    print(f"Columnas PR - Cargabilidad TDD {listado_Columnas_PR_CargabilidadTDD}")

                    data_Percentiles_CargabilidadTDD: dict = {
                        'PERCENTIL_TDD_L1': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_PR_CargabilidadTDD[0]].iloc[0],2),
                        'PERCENTIL_TDD_L2': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_PR_CargabilidadTDD[1]].iloc[0],2),
                        'PERCENTIL_TDD_L3': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_PR_CargabilidadTDD[2]].iloc[0],2)
                    }

                    print(data_Percentiles_CargabilidadTDD)

                    print("******"*50)

                    listado_Columnas_PR_Flicker: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Plt1(Med)', 'Plt2(Med)', 'Plt3(Med)'], valores_Corchetes=[''])

                    print(f"Columnas PR - Flicker {listado_Columnas_PR_Flicker}")

                    data_Percentiles_Flicker: dict = {
                        'PERCENTIL_FLICKER_PLT_L1_MED': round(df_Tabla_Calculos_Flicker[listado_Columnas_PR_Flicker[0]].iloc[0],2),
                        'PERCENTIL_FLICKER_PLT_L2_MED': round(df_Tabla_Calculos_Flicker[listado_Columnas_PR_Flicker[1]].iloc[0],2),
                        'PERCENTIL_FLICKER_PLT_L3_MED': round(df_Tabla_Calculos_Flicker[listado_Columnas_PR_Flicker[2]].iloc[0],2)
                    }

                    print(data_Percentiles_Flicker)

                    print("******"*50)

                    listado_Columnas_PR_FactorK: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Ki1(Med)', 'Ki2(Med)', 'Ki3(Med)'], valores_Corchetes=[''])

                    print(f"Columnas PR - FactorK {listado_Columnas_PR_FactorK}")

                    data_Percentiles_FactorK: dict = {
                        'PERCENTIL_FACTORK_L1_MED': round(df_Tabla_Calculos_FactorK[listado_Columnas_PR_FactorK[0]].iloc[0], 2),
                        'PERCENTIL_FACTORK_L2_MED': round(df_Tabla_Calculos_FactorK[listado_Columnas_PR_FactorK[1]].iloc[0], 2),
                        'PERCENTIL_FACTORK_L3_MED': round(df_Tabla_Calculos_FactorK[listado_Columnas_PR_FactorK[2]].iloc[0], 2)
                    }

                    print(data_Percentiles_FactorK)

                    print("******"*50)

                    # Creación del código que nos permite tener todos los DataFrames que estamos utilizando en su versión final, convirtiéndolos a un Excel que contiene distintas hojas
                    # En estas hojas veremos en una hoja con todas las columnas de los DataFrames y de resto, hojas individuales que contienen la información de cada uno de ellos (Minuto a Minuto)

                    # Creamos una copia de cada uno de los DataFrames Finales

                    df_Tabla_Tension_Copy = df_Tabla_Tension_Final.copy()

                    df_Tabla_Desb_Tension_Copy = df_Tabla_Desb_Tension.copy()

                    df_Tabla_Corriente_Copy = df_Tabla_Corriente_Final.copy()

                    df_Tabla_Desb_Corriente_Copy = df_Tabla_Desb_Corriente.copy()

                    df_Tabla_PQS_Final_Copy = df_Tabla_PQS_Final.copy()

                    df_Tabla_FactPotenciaFinal_Copy = df_Tabla_FactPotenciaFinal.copy()

                    df_Tabla_Distorsion_TensionFinal_Copy = df_Tabla_Distorsion_TensionFinal.copy()

                    df_Tabla_Armonicos_Distorsion_Tension_Final_Copy = df_Tabla_Armonicos_Distorsion_Tension_Final.copy()

                    df_Tabla_Distorsion_CorrienteFinal_Copy = df_Tabla_Distorsion_CorrienteFinal.copy()

                    df_Tabla_Armonicos_Distorsion_Corriente_Final_Copy = df_Tabla_Armonicos_Distorsion_Corriente_Final.copy()

                    df_Tabla_Armonicos_Cargabilidad_TDDFinal_Copy = df_Tabla_Armonicos_Cargabilidad_TDDFinal.copy()

                    df_Tabla_FlickerFinal_Copy = df_Tabla_FlickerFinal.copy()

                    df_Tabla_FactorKFinal_Copy = df_Tabla_FactorKFinal.copy()

                    df_Tabla_Energias_Copy = dataFrame_Energias.copy()

                    #df_Tabla_Energias_Generadas_Copy = df_Energia_Generada.copy()

                    print("******"*50)

                    # Creamos la variable donde se almacenará

                    registros = []
                    
                    # Aquí hay una lista que almacena cada uno de los valores de la Variación para cada Percentil de las Tensiones

                    listado_Variaciones_Tension_Minima_y_Maxima: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Tension_Final, nombres_Fijos_Columnas=['U12(Min)', 'U23(Min)', 'U31(Min)', 'U12(Max)', 'U23(Max)', 'U31(Max)'], valores_Corchetes=['V'])

                    print(f'Listado de Columnas - Variaciones {listado_Variaciones_Tension_Minima_y_Maxima}')

                    var_Lista_Variaciones = calcular_Variacion_Tension(lista_Percentiles=[df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[0]].iloc[0], df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[2]].iloc[0], df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[4]].iloc[0], df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[1]].iloc[0], df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[3]].iloc[0], df_Tabla_Calculos_Tension[listado_Variaciones_Tension_Minima_y_Maxima[5]].iloc[0]], val_Nom=var1)

                    listado_PQS_Maxima_Aparente: list = obtener_Columnas_DataFrame(dataFrame=df, nombres_Fijos_Columnas=['Setot+(Max)'], valores_Corchetes=['VA'])

                    print(f'Listado - PQS Aparente (Max) {listado_PQS_Maxima_Aparente}')

                    var_Lista_PQS_Carg_Disp = [calcular_Valor_Cargabilidad_Disponibilidad(var2, df_Tabla_Calculos_PQS_Potencias[listado_PQS_Maxima_Aparente[0]].iloc[0])[0], calcular_Valor_Cargabilidad_Disponibilidad(var2, df_Tabla_Calculos_PQS_Potencias[listado_PQS_Maxima_Aparente[0]].iloc[0])[1]]

                    print(f"Listado de Variaciones: {var_Lista_Variaciones}")

                    print(f'Listado de Cargabilidad Disponible: {var_Lista_PQS_Carg_Disp}')



                    # Aquí vamos a determinar los resultados de cada una de las Observaciones

                    print("******"*50)

                    listado_Columnas_Percentiles_Tension: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Tension_Final, nombres_Fijos_Columnas=['U12(Min)', 'U23(Min)', 'U31(Min)', 'U12(Med)', 'U23(Med)', 'U31(Med)', 'U12(Max)', 'U23(Max)', 'U31(Max)'], valores_Corchetes=['V'])

                    print(f'Listado de Columnas de Tensión para Percentiles: {listado_Columnas_Percentiles_Tension}')

                    listado_Percentiles_Tension: list = [round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[0]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[2]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[1]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[3]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[5]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[4]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[6]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[8]].iloc[0], 2), round(df_Tabla_Calculos_Tension[listado_Columnas_Percentiles_Tension[7]].iloc[0], 2),]

                    listado_Limites_Tension: list = [var_Limite_Inferior_Tension, var_Limite_Superior_Tension]

                    observaciones_Tension = calcular_Observacion_Tension(listado_Percentiles_Tension, listado_Limites_Tension)

                    print(f"Observaciones de Tensión: {observaciones_Tension}")

                    print("******"*50)

                    listado_Columnas_Percentiles_Corriente: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Corriente_Final, nombres_Fijos_Columnas=['I1(Min)', 'I1(Med)', 'I1(Max)', 'I2(Min)', 'I2(Med)', 'I2(Max)', 'I3(Min)', 'I3(Med)', 'I3(Max)', 'IN(Min)', 'IN(Med)', 'IN(Max)'], valores_Corchetes=['A'])

                    print(f'Listado de Columnas de Corriente para Percentiles: {listado_Columnas_Percentiles_Corriente}')

                    diccionario_Percentiles_Corriente: dict = {
                        'CORRIENTE_L1_MIN': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[0]].iloc[0], 2),
                        'CORRIENTE_L1_MED': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[2]].iloc[0], 2),
                        'CORRIENTE_L1_MAX': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[1]].iloc[0], 2),
                        'CORRIENTE_L2_MIN': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[3]].iloc[0], 2),
                        'CORRIENTE_L2_MED': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[5]].iloc[0], 2),
                        'CORRIENTE_L2_MAX': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[4]].iloc[0], 2),
                        'CORRIENTE_L3_MIN': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[6]].iloc[0], 2),
                        'CORRIENTE_L3_MED': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[8]].iloc[0], 2),
                        'CORRIENTE_L3_MAX': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[7]].iloc[0], 2)
                    }

                    diccionario_Percentiles_CorrienteNeutra: dict = {
                        'CORRIENTE_NEUTRA_MIN': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[9]].iloc[0], 2),
                        'CORRIENTE_NEUTRA_MED': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[11]].iloc[0], 2),
                        'CORRIENTE_NEUTRA_MAX': round(df_Tabla_Calculos_Corriente[listado_Columnas_Percentiles_Corriente[10]].iloc[0], 2)
                    }

                    valor_Corriente_Nominal = var_Corriente_Nominal_Value

                    observaciones_Corriente = calcular_Observacion_Corriente(diccionario_Percentiles_Corriente, diccionario_Percentiles_CorrienteNeutra, valor_Corriente_Nominal)

                    print(f"Observaciones de Corriente: {observaciones_Corriente}")

                    print("******"*50)

                    valor_Percentil_DesbTension = round(df_Tabla_Calculos_Desb_Tension['Desbalance'].iloc[0], 2)

                    valor_Referencia_DesbTension = var3

                    observaciones_DesbTension = calcular_Observacion_DesbTension(valor_Percentil_DesbTension, valor_Referencia_DesbTension)

                    print(f"Observaciones del Desbalance de Tensión: {observaciones_DesbTension}")

                    print("******"*50)

                    valor_Percentil_DesbCorriente = round(df_Tabla_Calculos_Desb_Corriente['Desbalance'].iloc[0], 2)

                    valor_Referencia_DesbCorriente = var4

                    observaciones_DesbCorriente = calcular_Observacion_DesbCorriente(valor_Percentil_DesbCorriente, valor_Referencia_DesbCorriente)

                    print(f"Observaciones del Desbalance de Corriente: {observaciones_DesbCorriente}")

                    print("******"*50)

                    listado_Columnas_Percentiles_DistorsionTension: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Distorsion_TensionFinal, nombres_Fijos_Columnas=['THD U12(Max)', 'THD U23(Max)', 'THD U31(Max)'], valores_Corchetes=['%'])

                    print(f'Listado de Columnas de Distorsión de Tensión para Percentiles {listado_Columnas_Percentiles_DistorsionTension}')

                    diccionario_Percentiles_THDV: dict = {
                        'THDV_DISTTENSION_L1': round(df_Tabla_Calculos_DistTension[listado_Columnas_Percentiles_DistorsionTension[0]].iloc[0], 2),
                        'THDV_DISTTENSION_L2': round(df_Tabla_Calculos_DistTension[listado_Columnas_Percentiles_DistorsionTension[1]].iloc[0], 2),
                        'THDV_DISTTENSION_L3': round(df_Tabla_Calculos_DistTension[listado_Columnas_Percentiles_DistorsionTension[2]].iloc[0], 2)
                    }

                    valor_Referencia_THDV = var5

                    observaciones_THDV = calcular_Observacion_THDV(diccionario_Percentiles_THDV, valor_Referencia_THDV)

                    print(f"Observaciones del THDV: {observaciones_THDV}")

                    print("******"*50)

                    listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente_Final, nombres_Fijos_Columnas=['I1 a3(Max)', 'I1 a5(Max)', 'I1 a7(Max)', 'I1 a9(Max)', 'I1 a11(Max)'], valores_Corchetes=['%'])

                    print(f'Listado de Columnas de Armónicos de Distorsión de Corriente para Percentiles (L1): {listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1}')

                    listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente_Final, nombres_Fijos_Columnas=['I2 a3(Max)', 'I2 a5(Max)', 'I2 a7(Max)', 'I2 a9(Max)', 'I2 a11(Max)'], valores_Corchetes=['%'])

                    print(f'Listado de Columnas de Armónicos de Distorsión de Corriente para Percentiles (L2): {listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2}')

                    listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Distorsion_Corriente_Final, nombres_Fijos_Columnas=['I3 a3(Max)', 'I3 a5(Max)', 'I3 a7(Max)', 'I3 a9(Max)', 'I3 a11(Max)'], valores_Corchetes=['%'])

                    print(f'Listado de Columnas de Armónicos de Distorsión de Corriente para Percentiles (L3): {listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3}')

                    diccionario_Percentiles_Armonicos_3_9: dict = {
                        'ARMONICO_3_L1': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1[0]].iloc[0], 2),
                        'ARMONICO_3_L2': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2[0]].iloc[0], 2),
                        'ARMONICO_3_L3': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3[0]].iloc[0], 2),
                        'ARMONICO_5_L1': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1[1]].iloc[0], 2),
                        'ARMONICO_5_L2': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2[1]].iloc[0], 2),
                        'ARMONICO_5_L3': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3[1]].iloc[0], 2),
                        'ARMONICO_7_L1': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1[2]].iloc[0], 2),
                        'ARMONICO_7_L2': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2[2]].iloc[0], 2),
                        'ARMONICO_7_L3': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3[2]].iloc[0], 2),
                        'ARMONICO_9_L1': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1[3]].iloc[0], 2),
                        'ARMONICO_9_L2': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2[3]].iloc[0], 2),
                        'ARMONICO_9_L3': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3[3]].iloc[0], 2)
                    }

                    diccionario_Percentiles_Armonicos_11: dict = {
                        'ARMONICO_11_L1': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L1[4]].iloc[0], 2),
                        'ARMONICO_11_L2': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L2[4]].iloc[0], 2),
                        'ARMONICO_11_L3': round(df_Tabla_Calculos_Armonicos_DistCorriente[listado_Columnas_Percentiles_Armonicos_DistorsionCorriente_L3[4]].iloc[0], 2)
                    }

                    listado_Limites_Armonicos_Corriente: list = list(valores_Limites_Armonicos.values())[:2]

                    observaciones_ArmonicosCorriente = calcular_Observacion_Armonicos_Corriente(diccionario_Percentiles_Armonicos_3_9, diccionario_Percentiles_Armonicos_11, listado_Limites_Armonicos_Corriente)

                    print(f"Listado de Límites de los Armónicos de Corriente: {listado_Limites_Armonicos_Corriente}")

                    print(f"Observaciones de los Armónicos de Corriente: {observaciones_ArmonicosCorriente}")

                    print("******"*50)

                    listado_Columnas_Percentiles_TDD: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDDFinal, nombres_Fijos_Columnas=['TDD I1(ProAct)', 'TDD I2(ProAct)', 'TDD I3(ProAct)'], valores_Corchetes=['%'])

                    print(f'Listado de Columnas de Cargabilidad TDD para Percentiles {listado_Columnas_Percentiles_TDD}')

                    diccionario_Percentiles_TDD: dict = {
                        'TDD_PERCENTIL_L1': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_Percentiles_TDD[0]].iloc[0], 2),
                        'TDD_PERCENTIL_L2': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_Percentiles_TDD[1]].iloc[0], 2),
                        'TDD_PERCENTIL_L3': round(df_Tabla_Calculos_CargabilidadTDD[listado_Columnas_Percentiles_TDD[2]].iloc[0], 2)
                    }

                    valor_Referencia_TDD = valor_Limite_TDD

                    observaciones_TDD = calcular_Observacion_TDD(diccionario_Percentiles_TDD, valor_Referencia_TDD)

                    print(f"Observaciones del TDD: {observaciones_TDD}")

                    print("******"*50)



                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el PQS - N1
                    list_Columns_Grafico_DesbCorriente_ActApa: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_PQS_Final, nombres_Fijos_Columnas=['Ptot+(Med)', 'Setot+(Med)'], valores_Corchetes=['W', 'VA'])
                    print(f"Listado de Columnas PQS Activa/Aparente: {list_Columns_Grafico_DesbCorriente_ActApa}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el PQS - N2
                    list_Columns_Grafico_DesbCorriente_CapInd: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_PQS_Final, nombres_Fijos_Columnas=['Ntotcap-(Med)', 'Ntotind+(Med)'], valores_Corchetes=['var'])
                    print(f"Listado de Columnas PQS Capacitiva/Inductiva: {list_Columns_Grafico_DesbCorriente_ActApa}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Factor de Potencia
                    list_Columns_Grafico_FactorPot_Consumido: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactorPotencia, nombres_Fijos_Columnas=['PFetotcap+(Med)', 'PFetotind+(Med)'], valores_Corchetes=[''])
                    print(f"Listado de Columnas Factor de Potencia (Consumido): {list_Columns_Grafico_FactorPot_Consumido}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Factor de Potencia
                    list_Columns_Grafico_FactorPot_Generado: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactorPotencia, nombres_Fijos_Columnas=['PFetotcap-(Med)', 'PFetotind-(Med)'], valores_Corchetes=[''])
                    print(f"Listado de Columnas Factor de Potencia (Generado): {list_Columns_Grafico_FactorPot_Generado}")

                    list_Columns_Graficos_Consolidado_Energia: list = ['Eptot+(Med) [kWh]', 'EQtotind+(Med) [kvarh]', 'EQtotcap+(Med) [kvarh]', 'KARH_IND', 'KVARH_CAP']
                    print(f"Listado de Columnas de Energías: {list_Columns_Graficos_Consolidado_Energia}")

                    list_Columns_Graficos_Consolidado_Energia_Generada: list = ['Eptot-(Med) [kWh]', 'EQtotind-(Med) [kvarh]', 'EQtotcap-(Med) [kvarh]', 'KARH_IND', 'KVARH_CAP']
                    print(f"Listado de Columnas de Energías Generadas: {list_Columns_Graficos_Consolidado_Energia_Generada}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Análisis de Distorsión de Tensión
                    list_Columns_Distorsion_Tension: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Distorsion_TensionFinal, nombres_Fijos_Columnas=['THD U12(Max)', 'THD U23(Max)', 'THD U31(Max)'], valores_Corchetes=['%'])
                    print(f"Listado de Columnas Distorsión de Tensión: {list_Columns_Distorsion_Tension}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Análisis de Distorsión de Corriente
                    list_Columns_Distorsion_Corriente: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Distorsion_CorrienteFinal, nombres_Fijos_Columnas=['THD I1(Max)', 'THD I2(Max)', 'THD I3(Max)'], valores_Corchetes=['%'])
                    print(f"Listado de Columnas Distorsión de Corriente: {list_Columns_Distorsion_Corriente}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Análisis del Listado de Armónicos de Cargabilidad TDD
                    list_Columns_Armonicos_Cargabilidad_TDD: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDDFinal, nombres_Fijos_Columnas=['TDD I1(ProAct)', 'TDD I2(ProAct)', 'TDD I3(ProAct)'], valores_Corchetes=['%'])
                    print(f"Listado de Columnas Cargabilidad TDD: {list_Columns_Armonicos_Cargabilidad_TDD}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Análisis del Flicker
                    list_Columns_Flicker: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_FlickerFinal, nombres_Fijos_Columnas=['Plt1(Med)', 'Plt2(Med)', 'Plt3(Med)'], valores_Corchetes=[''])
                    print(f"Listado de Columnas Flicker: {list_Columns_Flicker}")

                    # Aquí tenemos una lista de las columnas que se van a graficar a través del tiempo para el Análisis del Factor K
                    list_Columns_FactorK: list = obtener_Columnas_DataFrame(dataFrame=df_Tabla_FactorKFinal, nombres_Fijos_Columnas=['Ki1(Med)', 'Ki2(Med)', 'Ki3(Med)'], valores_Corchetes=[''])
                    print(f"Listado de Columnas FactorK: {list_Columns_FactorK}")
                    
                    
                    
                    graficar_Timeline_Tension_Plotly(dataFrame=df_Tabla_Tension_Final, variables=list_Columns_Grafico_Tension, fecha_col='Hora [UTC]', limites=[df_Tabla_Tension_Final['var_Limite_Inferior_Tension'].iloc[0], df_Tabla_Tension_Final['var_Limite_Superior_Tension'].iloc[0]], titulo='REGISTROS DE TENSIÓN')

                    graficar_Timeline_Corriente_Plotly(dataFrame=df_Tabla_Corriente_Final, variables=list_Columns_Grafico_Corriente, fecha_col='Hora [UTC]', limite=df_Tabla_Corriente_Final['var_Limite_Corriente_Nominal'].iloc[0], titulo='REGISTROS DE CORRIENTE')

                    graficar_Timeline_DesbTension_Plotly(dataFrame=df_Tabla_Desb_Tension, variables=list_Columns_Grafico_DesbTension, fecha_col='Hora [UTC]', limite=df_Tabla_Desb_Tension['var_Ref_Desbalance_Tension'].iloc[0], titulo='REGISTROS DESBALANCE DE TENSIÓN')
                    
                    graficar_Timeline_DesbCorriente_Plotly(dataFrame=df_Tabla_Desb_Corriente, variables=list_Columns_Grafico_DesbCorriente, fecha_col='Hora [UTC]', limite=df_Tabla_Desb_Corriente['var_Ref_Desbalance_Corriente'].iloc[0], titulo='REGISTROS DESBALANCE DE CORRIENTE')
                    
                    graficar_Timeline_PQS_ActApa_Plotly(dataFrame=df_Tabla_PQS_Final, variables=list_Columns_Grafico_DesbCorriente_ActApa, fecha_col='Hora [UTC]', titulo='REGISTROS DE POTENCIA - Activa / Aparente (kW / kVA)')
                    
                    graficar_Timeline_PQS_CapInd_Plotly(dataFrame=df_Tabla_PQS_Final, variables=list_Columns_Grafico_DesbCorriente_CapInd[::-1], fecha_col='Hora [UTC]', titulo='REGISTROS DE POTENCIA - Capacitiva / Inductiva (kVAR)')
                    
                    graficar_Timeline_FactPotencia_Plotly(dataFrame=df_Tabla_FactPotenciaFinal, variables=list_Columns_Grafico_FactorPot_Consumido[::-1], medidas_dataFrame=data_Cantidad_NEG_POS_FactorPotencia_Consumido, fecha_col='Hora [UTC]', titulo='REGISTROS DE POTENCIA - Factor de Potencia / Consumido')
                    
                    graficar_Timeline_FactPotencia_Plotly(dataFrame=df_Tabla_FactPotenciaFinal, variables=list_Columns_Grafico_FactorPot_Generado[::-1], medidas_dataFrame=data_Cantidad_NEG_POS_FactorPotencia_Generado, fecha_col='Hora [UTC]', titulo='REGISTROS DE POTENCIA - Factor de Potencia / Generado')
                    
                    graficar_Timeline_Distorsion_Tension_Plotly(dataFrame=df_Tabla_Distorsion_TensionFinal, variables=list_Columns_Distorsion_Tension, fecha_col='Hora [UTC]', limite=df_Tabla_Distorsion_TensionFinal['var_Ref_Distorsion_Tension'].iloc[0], titulo='REGISTROS DISTORSIÓN ARMÓNICA DE TENSIÓN - THDV')
                    
                    graficar_Timeline_Distorsion_Corriente_Plotly(dataFrame=df_Tabla_Distorsion_CorrienteFinal, variables=list_Columns_Distorsion_Corriente, fecha_col='Hora [UTC]', limite=None, titulo='REGISTROS DISTORSIÓN ARMÓNICA DE CORRIENTE - THDI')
                    
                    graficar_Timeline_CargabilidadTDD_Plotly(dataFrame=df_Tabla_Armonicos_Cargabilidad_TDDFinal, variables=list_Columns_Armonicos_Cargabilidad_TDD, fecha_col='Hora [UTC]', limite=valor_Limite_TDD, titulo='REGISTROS DISTORSIÓN TOTAL DE DEMANDA')
                    
                    graficar_Timeline_Flicker_Plotly(dataFrame=df_Tabla_FlickerFinal, variables=list_Columns_Flicker, fecha_col='Hora [UTC]', limite=var7, titulo='REGISTRO DE FLICKER')
                    
                    graficar_Timeline_FactorK_Plotly(dataFrame=df_Tabla_FactorKFinal, variables=list_Columns_FactorK, fecha_col='Hora [UTC]', limite=None, titulo='REGISTROS DE FACTOR K')
                    
                    generar_Graficos_Barras_Energias_Plotly(dataFrame=dataFrame_Energias, variables=list_Columns_Graficos_Consolidado_Energia, fecha_col='Hora [UTC]')
                    
                    st.markdown("""
                    > ## Gráficos Interactivos de Energías Generadas            
                    """)
                    
                    generar_Graficos_Barras_Energias_Plotly(dataFrame=df_Energia_Generada, variables=list_Columns_Graficos_Consolidado_Energia_Generada, fecha_col='Hora [UTC]')

                    
                except Exception as e:
                    
                    print(f"Hubo un error al generar el informe: {e}")

            
        except Exception as e:
            st.error(f"Error al cargar el archivo .parquet o procesar los datos: {e}")
    else:
        st.write("Por favor, sube un archivo .parquet para comenzar.")
