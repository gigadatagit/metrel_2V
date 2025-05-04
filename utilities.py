import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
#import os
from PIL import Image, ImageOps
from docx.shared import Cm
from io import BytesIO
from docxtpl import InlineImage

def calcular_Valor_Tension_Nominal(valor_Nominal: float):

    """
    Calcula el valor del Límite Superior e Inferior (+/- 10%) de acuerdo al valor nominal proporcionado.

    Args:
        valor_Nominal (float): Un número de tipo float que representa el valor nominal.

    Returns:
        list[float]: Una lista que contiene dos valores de tipo float, representando el límite superior (+10%) y el límite inferior (-10%).
    """
    var_Limite_Superior = valor_Nominal+(valor_Nominal*0.10)
    var_Limite_Inferior = valor_Nominal-(valor_Nominal*0.10)

    return [var_Limite_Inferior, var_Limite_Superior]

def calcular_Valor_Corriente_Nominal(capacidad_Trafo: float, valor_Nominal: float):

    """
    Realiza el cálculo del valor de corriente nominal recibiendo como parámetros la capacidad del transformador y el valor nominal.

    Args:
        capacidad_Trafo (float): El número que representa el valor de la capacidad del transformador.
        valor_Nominal (float): El número que representa el valor nominal del equipo.

    Returns:
        float: El resultado de la operación realizada con los valores de la capacidad del transformador y el valor nominal.
    """
    var_Corriente_Nominal = capacidad_Trafo/(np.sqrt(3)*valor_Nominal)

    return var_Corriente_Nominal

def renombrar_columnas(dataFrame: pd.DataFrame):
    """Renombra las columnas de un DataFrame para agregar un segundo número,
    manteniendo los caracteres adicionales. Si las columnas ya tienen los nombres
    correctos, no hace nada.

    Args:
        dataFrame: El DataFrame a renombrar.

    Returns:
        El DataFrame con las columnas renombradas (o sin cambios si ya estaban correctas).
    """

    dataFrame = dataFrame.copy()

    # Diccionario de mapeo de nombres de columnas.
    # 'Eptot+(Med)', 'Eptot-(Med)', 'Eqtotind+(Med)', 'Eqtotind-(Med)', 'Eqtotcap+(Med)', 'Eqtotcap-(Med)'
    mapeo_nombres = {
        "THD U1(Max)": "THD U12(Max)",
        "THD U2(Max)": "THD U23(Max)",
        "THD U3(Max)": "THD U31(Max)",
        "U1 a3(Max)": "U12 a3(Max)",
        "U1 a5(Max)": "U12 a5(Max)",
        "U1 a7(Max)": "U12 a7(Max)",
        "U1 a9(Max)": "U12 a9(Max)",
        "U1 a11(Max)": "U12 a11(Max)",
        "U1 a13(Max)": "U12 a13(Max)",
        "U1 a15(Max)": "U12 a15(Max)",
        "U2 a3(Max)": "U23 a3(Max)",
        "U2 a5(Max)": "U23 a5(Max)",
        "U2 a7(Max)": "U23 a7(Max)",
        "U2 a9(Max)": "U23 a9(Max)",
        "U2 a11(Max)": "U23 a11(Max)",
        "U2 a13(Max)": "U23 a13(Max)",
        "U2 a15(Max)": "U23 a15(Max)",
        "U3 a3(Max)": "U31 a3(Max)",
        "U3 a5(Max)": "U31 a5(Max)",
        "U3 a7(Max)": "U31 a7(Max)",
        "U3 a9(Max)": "U31 a9(Max)",
        "U3 a11(Max)": "U31 a11(Max)",
        "U3 a13(Max)": "U31 a13(Max)",
        "U3 a15(Max)": "U31 a15(Max)",
        "Plt12(Min)": "Plt1(Min)",
        "Plt12(Med)": "Plt1(Med)",
        "Plt12(Max)": "Plt1(Max)",
        "Plt23(Min)": "Plt2(Min)",
        "Plt23(Med)": "Plt2(Med)",
        "Plt23(Max)": "Plt2(Max)",
        "Plt31(Min)": "Plt3(Min)",
        "Plt31(Med)": "Plt3(Med)",
        "Plt31(Max)": "Plt3(Max)",
        "Eptot+(Med) [Wh]": "Eptot+(Med) [kWh]",
        "Eptot-(Med) [Wh]": "Eptot-(Med) [kWh]",
        "Eqtotind+(Med) [varh]": "EQtotind+(Med) [kvarh]",
        "Eqtotind-(Med) [varh]": "EQtotind-(Med) [kvarh]",
        "Eqtotcap+(Med) [varh]": "EQtotcap+(Med) [kvarh]",
        "Eqtotcap-(Med) [varh]": "EQtotcap-(Med) [kvarh]"
    }

    # Verificar si las columnas ya tienen los nombres correctos.
    columnas_correctas = all(
        any(re.match(f"{nombre_deseado}.*", col) for col in dataFrame.columns)
        for nombre_deseado in mapeo_nombres.values()
    )

    # Si las columnas ya están correctas, no hacer nada.
    if columnas_correctas:
        print("Las columnas ya tienen los nombres correctos. No se realizarán cambios.")
        return dataFrame

    # Renombrar las columnas usando expresiones regulares.
    nuevos_nombres = {}
    for col in dataFrame.columns:
        for old_name, new_name in mapeo_nombres.items():
            if old_name in col:  # Check if the old name is part of the column name
                nuevos_nombres[col] = col.replace(old_name, new_name)
                break  # Stop searching if a match is found

    dataFrame = dataFrame.rename(columns=nuevos_nombres)

    return dataFrame

def obtener_Columnas_DataFrame(dataFrame: pd.DataFrame, nombres_Fijos_Columnas: list, valores_Corchetes: list):
    """
    Filtra las columnas de un DataFrame que coincidan con los nombres fijos de las columnas y los valores de las unidades de medida dentro de los corchetes.

    Parámetros:
    - dataFrame (pd.DataFrame): DataFrame que contiene las columnas a filtrar.
    - nombres_Fijos_Columnas (list): Lista con los nombres base de las columnas.
    - valores_Corchetes (list): Lista con los valores de las unidades de medida permitidos dentro de los corchetes, incluyendo "" si se quieren corchetes vacíos.

    Retorna:
    - listado_Columnas (list): Listado con los nombres completos de la columna.
    """

    # Copia del DataFrame
    dataFrame_Copy = dataFrame.copy()

    # Construye una expresión regular combinando los nombres fijos con los valores dentro de los corchetes
    patron = "|".join([fr"^{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Fijos_Columnas for valor in valores_Corchetes])

    # Filtra las columnas en base al patrón
    dataFrame_Copy = dataFrame_Copy.filter(regex=patron)

    listado_Columnas = dataFrame_Copy.columns.to_list()

    print(listado_Columnas)

    return listado_Columnas

def convertir_Unidades(dataFrame: pd.DataFrame, columnas_DataFrame: list, unidad_Elegida: str, unidades_Validas: list):
    """
    Solicita al usuario la unidad de medida del conjunto de columnas y, si el input es la primera unidad de medida,
    convierte cada columna de corriente en el listado recibido dividiendo por 1000.

    Parámetros:
      - dataFrame: DataFrame que contiene los datos.
      - columnas_DataFrame: Lista de nombres de columnas que contienen valores a convertir.

    Retorna:
      - dataFrame modificado (operación realizada inplace).
    """
    # Definimos la copia del DataFrame
    finalDataFrame = dataFrame.copy()

    # Definir las unidades válidas
    valid_Units: list = unidades_Validas.copy()

    # Solicitar la unidad y convertir a minúsculas
    #unidad: str = input(f"Seleccione la Unidad de Medida de {nombre_Conjunto_Columnas} ({valid_Units[0]}/{valid_Units[1]}): ").strip().lower()

    # Validar la entrada
    #if unidad not in valid_Units:
        #print(f"Unidad no válida. Por favor, ingrese {valid_Units[0]} o {valid_Units[1]}.")
        #return finalDataFrame  # Se podría implementar un bucle para solicitar nuevamente

    # Si la unidad es igual al primer elemento de las Unidades Válidas, se realiza la conversión dividiendo entre 1000
    if unidad_Elegida == valid_Units[0]:
        for col in columnas_DataFrame:
            if col in finalDataFrame.columns:
                finalDataFrame[col] = finalDataFrame[col] / 1000  # Conversión de valid_Units[0] a valid_Units[1]
                print(f"Conversión realizada en la columna '{col}': {valid_Units[0]} a {valid_Units[1]}")
            else:
                print(f"La columna '{col}' no existe en el DataFrame.")
    else:
        print(f"La unidad ingresada es {valid_Units[1]}. No se requiere conversión.")

    return finalDataFrame

def seleccionar_Energia_Generada(dataFrame: pd.DataFrame, listado_Columnas: list):
    """
    Solicita al usuario una opción numérica y retorna un enlace de plantilla basado en la selección.

    La función solicita al usuario un número entero mediante input, asegurando que
    la entrada sea válida y pertenezca a la lista de opciones permitidas [1, 2].
    Si el usuario ingresa un valor no válido, se le pedirá que ingrese nuevamente
    hasta que se proporcione una opción correcta.

    Returns:
        str: Un enlace para luego descargar el contenido de la plantilla basado en su selección.
    """
    opciones_Plantillas = [1, 2]  # Lista de opciones válidas

    dataFrameFinalEnergias = dataFrame.copy()

    listado_Columnas_Fundamentales = listado_Columnas.copy()

    while True:

        try:

          print("Creando información acerca de las Energías Generadas.")

          dataFrameFinalEnergias[listado_Columnas_Fundamentales]

          dataFrameFinalEnergias['Hora [UTC]'] = dataFrameFinalEnergias['Hora [UTC]'].astype(str)
          dataFrameFinalEnergias['Hora [UTC]'] = pd.to_datetime(dataFrameFinalEnergias['Hora [UTC]'], format='mixed')

          # Lista de nombres de columnas base que deseas buscar
          nombres_Columnas_Energia_Activa = ['Ep1-(Med)', 'Ep2-(Med)', 'Ep3-(Med)']

          # Lista de valores posibles dentro de los corchetes
          valores_Corchetes_Energia_Activa = ['Wh']  # Agrega los valores que necesites

          # Construye una expresión regular combinando nombres y valores
          patron_E_Activa = "|".join([fr"{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Columnas_Energia_Activa for valor in valores_Corchetes_Energia_Activa])

          # Copia del DataFrame para Filtrar Energía Activa
          dataFrameEnergiaActiva = dataFrame.copy()

          # Filtra las columnas que coinciden con el patrón
          dataFrameFiltradoEnergiaActiva = dataFrameEnergiaActiva.filter(regex=patron_E_Activa)

          # Nombre de las Columnas de la Energía Activa
          columnas_Energia_Activa = dataFrameFiltradoEnergiaActiva.columns.to_list()

          print(f'Listado de Columnas de Energía Activa {columnas_Energia_Activa}')

          # Creación del Nombre de la Columna con la unidad de Medida respectiva
          nombre_Columna_Energia_Total_Activa = f'Eptot-(Med) [kWh]'

          print(nombre_Columna_Energia_Total_Activa)

          # Creación de la Columna con el Total de la Energía Activa Total Consumida
          dataFrameFinalEnergias[nombre_Columna_Energia_Total_Activa] = dataFrameFinalEnergias[columnas_Energia_Activa].sum(axis=1)



          # Lista de nombres de columnas base que deseas buscar
          nombres_Columnas_Energia_Capacitiva = ['EQfund1cap-(Med)', 'EQfund2cap-(Med)', 'EQfund3cap-(Med)']

          # Lista de valores posibles dentro de los corchetes
          valores_Corchetes_Energia_Capacitiva = ['varh']  # Agrega los valores que necesites

          # Construye una expresión regular combinando nombres y valores
          patron_E_Capacitiva = "|".join([fr"{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Columnas_Energia_Capacitiva for valor in valores_Corchetes_Energia_Capacitiva])

          # Copia del DataFrame para Filtrar Energía Capacitiva
          dataFrameEnergiaCapacitiva = dataFrame.copy()

          # Filtra las columnas que coinciden con el patrón
          dataFrameFiltradoEnergiaCapacitiva = dataFrameEnergiaCapacitiva.filter(regex=patron_E_Capacitiva)

          # Nombre de las Columnas de la Energía Capacitiva
          columnas_Energia_Capacitiva = dataFrameFiltradoEnergiaCapacitiva.columns.to_list()

          print(f'Listado de Columnas de Energía Capacitiva {columnas_Energia_Capacitiva}')

          # Creación del Nombre de la Columna con la unidad de Medida respectiva
          nombre_Columna_Energia_Total_Capacitiva = f'EQtotcap-(Med) [kvarh]'

          print(nombre_Columna_Energia_Total_Capacitiva)

          # Creación de la Columna con el Total de la Energía Capacitiva Total Consumida
          dataFrameFinalEnergias[nombre_Columna_Energia_Total_Capacitiva] = dataFrameFinalEnergias[columnas_Energia_Capacitiva].sum(axis=1)



          # Lista de nombres de columnas base que deseas buscar
          nombres_Columnas_Energia_Inductiva = ['EQfund1ind-(Med)', 'EQfund2ind-(Med)', 'EQfund3ind-(Med)']

          # Lista de valores posibles dentro de los corchetes
          valores_Corchetes_Energia_Inductiva = ['varh']  # Agrega los valores que necesites

          # Construye una expresión regular combinando nombres y valores
          patron_E_Inductiva = "|".join([fr"{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Columnas_Energia_Inductiva for valor in valores_Corchetes_Energia_Inductiva])

          # Copia del DataFrame para Filtrar Energía Inductiva
          dataFrameEnergiaInductiva = dataFrame.copy()

          # Filtra las columnas que coinciden con el patrón
          dataFrameFiltradoEnergiaInductiva = dataFrameEnergiaInductiva.filter(regex=patron_E_Inductiva)

          # Nombre de las Columnas de la Energía Inductiva
          columnas_Energia_Inductiva = dataFrameFiltradoEnergiaInductiva.columns.to_list()

          print(f'Listado de Columnas de Energía Inductiva {columnas_Energia_Inductiva}')

          # Creación del Nombre de la Columna con la unidad de Medida respectiva
          nombre_Columna_Energia_Total_Inductiva = f'EQtotind-(Med) [kvarh]'

          print(nombre_Columna_Energia_Total_Inductiva)

          # Creación de la Columna con el Total de la Energía Inductiva Total Consumida
          dataFrameFinalEnergias[nombre_Columna_Energia_Total_Inductiva] = dataFrameFinalEnergias[columnas_Energia_Inductiva].sum(axis=1)


          dataFrameFinalEnergias = dataFrameFinalEnergias.round(6)


          print("******"*50)

          listado_Final_Columnas_Energias: list = ['Hora [UTC]', nombre_Columna_Energia_Total_Activa, nombre_Columna_Energia_Total_Inductiva, nombre_Columna_Energia_Total_Capacitiva, 'PFetotcap+(Med) []', 'PFetotind+(Med) []', 'PFetotcap-(Med) []', 'PFetotind-(Med) []']

          dataFrameFinal_Energias_Copy = dataFrameFinalEnergias[listado_Final_Columnas_Energias].copy()



          columnas_FactorPotencia = ['PFetotcap+(Med) []', 'PFetotind+(Med) []', 'PFetotcap-(Med) []', 'PFetotind-(Med) []']

          columnas_A_Sumar = [nombre_Columna_Energia_Total_Activa, nombre_Columna_Energia_Total_Inductiva, nombre_Columna_Energia_Total_Capacitiva]

          dataFrame_H_a_H = dataFrameFinal_Energias_Copy.copy()

          # Listas de columnas
          cols_sumar = columnas_A_Sumar.copy()
          cols_percentil = columnas_FactorPotencia.copy()

          # Crear el diccionario para la función de agregación
          agg_dict = {col: 'sum' for col in cols_sumar}
          agg_dict.update({col: lambda x: x.quantile(0.95) for col in cols_percentil})

          # Ejemplo completo integrando el agrupamiento
          dataFrame_H_a_H['Hora_Corte'] = dataFrame_H_a_H['Hora [UTC]'].dt.floor('h') + pd.Timedelta(hours=1)
          dataFrame_H_a_H_Result = (
              dataFrame_H_a_H.groupby('Hora_Corte')
              .agg(agg_dict)
              .reset_index()
              .rename(columns={'Hora_Corte': 'Hora [UTC]'})
          )

          dataFrame_H_a_H_Result['KWH'] = 100

          dataFrame_H_a_H_Result['KARH_IND'] = np.where(
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Inductiva] != 0) & 
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Activa] != 0), 
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Inductiva] / dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Activa] * 100),
              0
            )

          dataFrame_H_a_H_Result['KVARH_CAP'] = np.where(
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Capacitiva] != 0) &
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Activa] != 0),
              (dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Capacitiva] / dataFrame_H_a_H_Result[nombre_Columna_Energia_Total_Activa] * 100), 
              0
            )

          listado_Final_Columnas_Energias: list = ['Hora [UTC]', nombre_Columna_Energia_Total_Activa, nombre_Columna_Energia_Total_Inductiva, nombre_Columna_Energia_Total_Capacitiva, 'KWH', 'KARH_IND', 'KVARH_CAP', 'PFetotcap+(Med) []', 'PFetotind+(Med) []', 'PFetotcap-(Med) []', 'PFetotind-(Med) []']

          dataFrame_H_a_H_Result = dataFrame_H_a_H_Result[listado_Final_Columnas_Energias]

          dataFrame_Energia_Generada = dataFrame_H_a_H_Result.copy()

          print("#-#-#-#-#-#-#-#-#"*50)

          print("Información sobre el DataFrame de la Energía Generada")

          dataFrame_Energia_Generada.head()

          # Reemplazar valores infinitos por NaN
          dataFrame_Energia_Generada.replace([np.inf, -np.inf], np.nan, inplace=True)

          # Imputar los valores faltantes con la media de cada columna
          dataFrame_Energia_Generada.fillna(dataFrame_Energia_Generada.mean(), inplace=True)

          print("#-#-#-#-#-#-#-#-#"*50)

          return dataFrame_Energia_Generada

        except ValueError:

          print("Error Procesando el DataFrame.")

    #elif opcion == 2:

        #print("Elegiste no crear la información acerca de las Energías Generadas.")
        
def crear_Medidas_DataFrame_Energias(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_Energias: list = listado_Columnas_a_Medir
    #columnas_var_Tabla_Energias: list = ['E.Activa T1', 'E.Capacitiva T1', 'E.Inductiva T1', 'KWH', 'KARH_IND', 'KVARH_CAP', 'F.P. III -', 'F.P. III']

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_Energias] = dataFrame[columnas_var_Tabla_Energias].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Energias].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_Energias].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_Energias].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_Energias].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_Energias].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def filtrar_DataFrame_Columnas(dataFrame: pd.DataFrame, nombres_Fijos_Columnas: list, valores_Corchetes: list):
    """
    Filtra las columnas de un DataFrame que coincidan con los nombres fijos de las columnas y los valores de las unidades de medida dentro de los corchetes.

    Parámetros:
    - dataFrame (pd.DataFrame): DataFrame que contiene las columnas a filtrar.
    - nombres_Fijos_Columnas (list): Lista con los nombres base de las columnas.
    - valores_Corchetes (list): Lista con los valores de las unidades de medida permitidos dentro de los corchetes, incluyendo "" si se quieren corchetes vacíos.

    Retorna:
    - pd.DataFrame: DataFrame con las columnas filtradas.
    """

    # Construye una expresión regular combinando los nombres fijos con los valores dentro de los corchetes
    patron = "|".join([fr"^{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Fijos_Columnas for valor in valores_Corchetes])

    # Filtra las columnas en base al patrón
    dataFrame = dataFrame.filter(regex=patron)

    # Realizamos una copia del DataFrame filtrado con los patrones de búsqueda
    dataFrameFinal = dataFrame.copy()

    return dataFrameFinal

def crear_DataFrame_Tension(dataFrame: pd.DataFrame, var_Lim_Inf_Ten: float, val_Nom: float, var_Lim_Sup_Ten: float):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        var_Lim_Inf_Ten (float): Es el valor del límite inferior de la tensión.
        var_Nom (float): Es el Valor Nominal.
        var_Lim_Sup_Ten (float): Es el valor del límite superior de la tensión.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalTension = dataFrame.copy()

    dataFrameFinalTension['Hora [UTC]'] = dataFrameFinalTension['Hora [UTC]'].astype(str)
    dataFrameFinalTension['Hora [UTC]'] = pd.to_datetime(dataFrameFinalTension['Hora [UTC]'], format='mixed')

    dataFrameFinalTension.loc[:,('var_Limite_Inferior_Tension')] = var_Lim_Inf_Ten
    dataFrameFinalTension.loc[:,('valor_Nominal')] = val_Nom
    dataFrameFinalTension.loc[:,('var_Limite_Superior_Tension')] = var_Lim_Sup_Ten

    return dataFrameFinalTension

def crear_DataFrame_Desbalance_Tension(dataFrame: pd.DataFrame, val_Desb_Ten: float, nombres_Fijos_Columnas: list, valores_Corchetes: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        val_Desb_Ten (float): Es el valor de Referencia del Desbalance de la Tensión.
        nombres_Fijos_Columnas (list): Lista con los nombres base de las columnas.
        valores_Corchetes (list): Lista con los valores de las unidades de medida permitidos dentro de los corchetes, incluyendo "" si se quieren corchetes vacíos.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    # Copia del DataFrame
    dataFrame_Copy = dataFrame.copy()

    # Construye una expresión regular combinando los nombres fijos con los valores dentro de los corchetes
    patron = "|".join([fr"^{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Fijos_Columnas for valor in valores_Corchetes])

    # Filtra las columnas en base al patrón
    dataFrame_Copy = dataFrame_Copy.filter(regex=patron)

    lista_Columnas_a_Promediar = dataFrame_Copy.columns.to_list()

    print(lista_Columnas_a_Promediar)

    dataFrameFinalDesbTension = dataFrame.copy()

    dataFrameFinalDesbTension['Hora [UTC]'] = dataFrameFinalDesbTension['Hora [UTC]'].astype(str)
    dataFrameFinalDesbTension['Hora [UTC]'] = pd.to_datetime(dataFrameFinalDesbTension['Hora [UTC]'], format='mixed')

    dataFrameFinalDesbTension['Promedio'] = dataFrameFinalDesbTension[lista_Columnas_a_Promediar].mean(axis=1)

    dataFrameFinalDesbTension['delta_V1'] = abs(dataFrameFinalDesbTension['Promedio'] - dataFrameFinalDesbTension[lista_Columnas_a_Promediar[0]])
    dataFrameFinalDesbTension['delta_V2'] = abs(dataFrameFinalDesbTension['Promedio'] - dataFrameFinalDesbTension[lista_Columnas_a_Promediar[1]])
    dataFrameFinalDesbTension['delta_V3'] = abs(dataFrameFinalDesbTension['Promedio'] - dataFrameFinalDesbTension[lista_Columnas_a_Promediar[2]])

    listado_Columnas_a_Comparar = ['delta_V1', 'delta_V2', 'delta_V3']

    dataFrameFinalDesbTension['delta_Mayor'] = dataFrameFinalDesbTension[listado_Columnas_a_Comparar].max(axis=1)

    # Realizar el cálculo: valor_mayor / otra_columna
    dataFrameFinalDesbTension['Desbalance'] = dataFrameFinalDesbTension['delta_Mayor'] / dataFrameFinalDesbTension['Promedio'] * 100

    dataFrameFinalDesbTension.loc[:,('var_Ref_Desbalance_Tension')] = val_Desb_Ten

    return dataFrameFinalDesbTension

def crear_DataFrame_Corriente(dataFrame: pd.DataFrame, var_Lim_Corr_Nom: float):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        var_Lim_Corr_Nom (float): Es el valor del límite de corriente nominal.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalCorriente = dataFrame.copy()

    dataFrameFinalCorriente['Hora [UTC]'] = dataFrameFinalCorriente['Hora [UTC]'].astype(str)
    dataFrameFinalCorriente['Hora [UTC]'] = pd.to_datetime(dataFrameFinalCorriente['Hora [UTC]'], format='mixed')

    dataFrameFinalCorriente.loc[:,('var_Limite_Corriente_Nominal')] = var_Lim_Corr_Nom

    return dataFrameFinalCorriente

def crear_DataFrame_Desbalance_Corriente(dataFrame: pd.DataFrame, val_Desb_Corr: float, nombres_Fijos_Columnas: list, valores_Corchetes: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        val_Desb_Corr (float): Es el valor de Referencia del Desbalance de Corriente.
        nombres_Fijos_Columnas (list): Lista con los nombres base de las columnas.
        valores_Corchetes (list): Lista con los valores de las unidades de medida permitidos dentro de los corchetes, incluyendo "" si se quieren corchetes vacíos.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """

    # Copia del DataFrame
    dataFrame_Copy = dataFrame.copy()

    # Construye una expresión regular combinando los nombres fijos con los valores dentro de los corchetes
    patron = "|".join([fr"^{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Fijos_Columnas for valor in valores_Corchetes])

    # Filtra las columnas en base al patrón
    dataFrame_Copy = dataFrame_Copy.filter(regex=patron)

    lista_Columnas_a_Promediar = dataFrame_Copy.columns.to_list()

    listado_Columnas_a_Comparar = dataFrame_Copy.columns.to_list()

    print(lista_Columnas_a_Promediar)

    dataFrameFinalDesbCorr = dataFrame.copy()

    dataFrameFinalDesbCorr['Hora [UTC]'] = dataFrameFinalDesbCorr['Hora [UTC]'].astype(str)
    dataFrameFinalDesbCorr['Hora [UTC]'] = pd.to_datetime(dataFrameFinalDesbCorr['Hora [UTC]'], format='mixed')

    dataFrameFinalDesbCorr['Promedio'] = dataFrameFinalDesbCorr[lista_Columnas_a_Promediar].mean(axis=1)

    dataFrameFinalDesbCorr['max_Corrientes_Medias'] = dataFrameFinalDesbCorr[listado_Columnas_a_Comparar].max(axis=1)

    # Realiza el cálculo: valor_mayor / otra_columna
    dataFrameFinalDesbCorr['Desbalance'] = (dataFrameFinalDesbCorr['max_Corrientes_Medias'] - dataFrameFinalDesbCorr['Promedio']) / dataFrameFinalDesbCorr['Promedio'] * 100

    dataFrameFinalDesbCorr.loc[:,('var_Ref_Desbalance_Corriente')] = val_Desb_Corr

    return dataFrameFinalDesbCorr

def crear_DataFrame_PQS_Potencias(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalPQS = dataFrame.copy()

    dataFrameFinalPQS['Hora [UTC]'] = dataFrameFinalPQS['Hora [UTC]'].astype(str)
    dataFrameFinalPQS['Hora [UTC]'] = pd.to_datetime(dataFrameFinalPQS['Hora [UTC]'], format='mixed')

    return dataFrameFinalPQS

def crear_DataFrame_FactPotencia(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalFactPotencia = dataFrame.copy()

    dataFrameFinalFactPotencia['Hora [UTC]'] = dataFrameFinalFactPotencia['Hora [UTC]'].astype(str)
    dataFrameFinalFactPotencia['Hora [UTC]'] = pd.to_datetime(dataFrameFinalFactPotencia['Hora [UTC]'], format='mixed')

    return dataFrameFinalFactPotencia

def crear_DataFrame_FactPotenciaGrupos(dataFrame: pd.DataFrame, nombres_Fijos_Columnas: list, valores_Corchetes: list):

    """
    Procesa un DataFrame y devuelve un nuevo Diccionario con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        dict: Un nuevo Diccionario con las modificaciones aplicadas para tener subdivididos los Factores de Potencia Inductivos y Capacitivos en su Orden Mínimo, Medio y Máximo.
    """

    # Copia del DataFrame
    dataFrame_Copy = dataFrame.copy()

    # Construye una expresión regular combinando los nombres fijos con los valores dentro de los corchetes
    patron = "|".join([fr"^{re.escape(nombre)} \[{valor}\]" for nombre in nombres_Fijos_Columnas for valor in valores_Corchetes])

    # Filtra las columnas en base al patrón
    dataFrame_Copy = dataFrame_Copy.filter(regex=patron)

    listado_Columnas_FactorPotencia = dataFrame_Copy.columns.to_list()

    print(listado_Columnas_FactorPotencia)

    dataFrameFactPotenciaGrupos = dataFrame.copy()

    #listado_Columnas_FactorPotencia: list = ['F.P. Mn. III', 'F.P. III', 'F.P. Mx. III']

    dataFrameFactPotenciaGrupos['Hora [UTC]'] = dataFrameFactPotenciaGrupos['Hora [UTC]'].astype(str)
    dataFrameFactPotenciaGrupos['Hora [UTC]'] = pd.to_datetime(dataFrameFactPotenciaGrupos['Hora [UTC]'], format='mixed')

    filtro_FactorPotencia_Ind_Min = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[0]] > 0)
    filtro_FactorPotencia_Ind_Med = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[2]] > 0)
    filtro_FactorPotencia_Ind_Max = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[1]] > 0)

    filtro_FactorPotencia_Cap_Min = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[0]] < 0)
    filtro_FactorPotencia_Cap_Med = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[2]] < 0)
    filtro_FactorPotencia_Cap_Max = (dataFrameFactPotenciaGrupos[listado_Columnas_FactorPotencia[1]] < 0)

    serie_FactorPotencia_Ind_Min = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Ind_Min]
    serie_FactorPotencia_Ind_Med = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Ind_Med]
    serie_FactorPotencia_Ind_Max = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Ind_Max]

    serie_FactorPotencia_Cap_Min = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Cap_Min]
    serie_FactorPotencia_Cap_Med = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Cap_Med]
    serie_FactorPotencia_Cap_Max = dataFrameFactPotenciaGrupos[filtro_FactorPotencia_Cap_Max]

    diccionario_Factor_Potencia_General: dict = {
        'PFetotind+(Min) [] - Ind': serie_FactorPotencia_Ind_Min[['Hora [UTC]', listado_Columnas_FactorPotencia[0]]],
        'PFetotind+(Med) [] - Ind': serie_FactorPotencia_Ind_Med[['Hora [UTC]', listado_Columnas_FactorPotencia[2]]],
        'PFetotind+(Max) [] - Ind': serie_FactorPotencia_Ind_Max[['Hora [UTC]', listado_Columnas_FactorPotencia[1]]],
        'PFetotind+(Min) [] - Cap': serie_FactorPotencia_Cap_Min[['Hora [UTC]', listado_Columnas_FactorPotencia[0]]],
        'PFetotind+(Med) [] - Cap': serie_FactorPotencia_Cap_Med[['Hora [UTC]', listado_Columnas_FactorPotencia[2]]],
        'PFetotind+(Max) [] - Cap': serie_FactorPotencia_Cap_Max[['Hora [UTC]', listado_Columnas_FactorPotencia[1]]]
    }

    return diccionario_Factor_Potencia_General

def crear_DataFrame_DistTension(dataFrame: pd.DataFrame, val_Dist_Arm_Tension: float):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        val_Dist_Arm_Tension (float): Es el valor de Referencia de Distorsión Armónica de Tensión.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalDistTension = dataFrame.copy()

    dataFrameFinalDistTension['Hora [UTC]'] = dataFrameFinalDistTension['Hora [UTC]'].astype(str)
    dataFrameFinalDistTension['Hora [UTC]'] = pd.to_datetime(dataFrameFinalDistTension['Hora [UTC]'], format='mixed')

    dataFrameFinalDistTension.loc[:,('var_Ref_Distorsion_Tension')] = val_Dist_Arm_Tension

    return dataFrameFinalDistTension

def crear_DataFrame_Armonicos_DistTension(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalArmonicosDistTension = dataFrame.copy()

    dataFrameFinalArmonicosDistTension['Hora [UTC]'] = dataFrameFinalArmonicosDistTension['Hora [UTC]'].astype(str)
    dataFrameFinalArmonicosDistTension['Hora [UTC]'] = pd.to_datetime(dataFrameFinalArmonicosDistTension['Hora [UTC]'], format='mixed')

    return dataFrameFinalArmonicosDistTension

def crear_DataFrame_DistCorriente(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalDistCorriente = dataFrame.copy()

    dataFrameFinalDistCorriente['Hora [UTC]'] = dataFrameFinalDistCorriente['Hora [UTC]'].astype(str)
    dataFrameFinalDistCorriente['Hora [UTC]'] = pd.to_datetime(dataFrameFinalDistCorriente['Hora [UTC]'], format='mixed')

    return dataFrameFinalDistCorriente

def crear_DataFrame_Armonicos_DistCorriente(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalArmonicosDistCorriente = dataFrame.copy()

    dataFrameFinalArmonicosDistCorriente['Hora [UTC]'] = dataFrameFinalArmonicosDistCorriente['Hora [UTC]'].astype(str)
    dataFrameFinalArmonicosDistCorriente['Hora [UTC]'] = pd.to_datetime(dataFrameFinalArmonicosDistCorriente['Hora [UTC]'], format='mixed')

    return dataFrameFinalArmonicosDistCorriente

def crear_DataFrame_Flicker_Final(dataFrame: pd.DataFrame, val_Lim_Flicker: float):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        val_Lim_Flicker (float): Es el valor de Referencia para el Límite del Flicker.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFlickerFinal = dataFrame.copy()

    dataFrameFlickerFinal['Hora [UTC]'] = dataFrameFlickerFinal['Hora [UTC]'].astype(str)
    dataFrameFlickerFinal['Hora [UTC]'] = pd.to_datetime(dataFrameFlickerFinal['Hora [UTC]'], format='mixed')

    dataFrameFlickerFinal.loc[:,('var_Ref_Limite_Flicker')] = val_Lim_Flicker

    return dataFrameFlickerFinal

def crear_DataFrame_FactorK_Final(dataFrame: pd.DataFrame):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFactorKFinal = dataFrame.copy()

    dataFrameFactorKFinal['Hora [UTC]'] = dataFrameFactorKFinal['Hora [UTC]'].astype(str)
    dataFrameFactorKFinal['Hora [UTC]'] = pd.to_datetime(dataFrameFactorKFinal['Hora [UTC]'], format='mixed')

    return dataFrameFactorKFinal

def calcular_Valor_Corriente_Cortacircuito(corriente_Nominal: float, valor_Impedancia_Cortocircuito: float):

    """
    Realiza el cálculo del valor de corriente cortacircuito recibiendo como parámetros el valor nominal y el valor de la impedancia cortacircuito.

    Args:
        corriente_Nominal (float): El número que representa el valor de la corriente nominal del equipo.
        valor_Impedancia_Cortacircuito (float): El número que representa el valor de la impedancia cortacircuito.

    Returns:
        float: El resultado de la operación realizada con los valores de el valor nominal y el valor de impedancia cortacircuito.
    """

    return (corriente_Nominal/(valor_Impedancia_Cortocircuito/100))/1000

def calcular_Valor_ISC_entre_IL(valor_Corriente_Cortacircuito: float, valor_Max_Corr_Max: float):

    """
    Realiza el cálculo del valor de isc entre il recibiendo como parámetros el valor de corriente cortacircuito y el valor máximo de corrientes máximas.

    Args:
        valor_Corriente_Cortacircuito (float): El número que representa el valor de corriente cortacircuito.
        valor_Max_Corr_Max (float): El número que representa el valor máximo de corrientes máximas.

    Returns:
        float: El resultado de la operación realizada con los valores de el valor de corriente cortacircuito y el valor máximo de corrientes máximas.
    """

    return (valor_Corriente_Cortacircuito/valor_Max_Corr_Max)*1000

def calcular_Valor_Limite_TDD(valor_ISC_sobre_IL: float):

    """
    Realiza el cálculo del valor del límite del TDD según el rango en el que cumpla el parámetro.

    Args:
        valor_ISC_sobre_IL (float): El número que representa el valor de ISC sobre IL.

    Returns:
        float: El resultado de la operación realizada con el valor_ISC_sobre_IL.
    """
    var_ISC: float = valor_ISC_sobre_IL

    if var_ISC < 20:

        var_Limite_TDD: float = 5.0

    elif var_ISC >= 20 and var_ISC < 50:

        var_Limite_TDD: float = 8.0

    elif var_ISC >= 50 and var_ISC < 100:

        var_Limite_TDD: float = 12.0

    elif var_ISC >= 100 and var_ISC < 1000:

        var_Limite_TDD: float = 15.0

    elif var_ISC > 1000:

        var_Limite_TDD: float = 20.0

    return var_Limite_TDD

def calcular_Valores_Limites_Armonicos(value_Limite_TDD: float):

    """
    Realiza el cálculo de los valores de los Límites de Armonicos según el rango que cumpla el parámetro.

    Args:
        value_Limite_TDD (float): El número que representa el valor del limite TDD.

    Returns:
        dict: El resultado de la operación realizada con el valor del Limite TDD determinando los valores de los límites de los armónicos.
    """
    var_TDD: float = value_Limite_TDD

    if var_TDD == 5:

        diccionario_Limites_Armonicos: dict = {
            'ARM_0_10': 4.0,
            'ARM_11_16': 2.0,
            'ARM_17_22': 1.5,
            'ARM_23_34': 0.6,
            'ARM_35': 0.3
        }

    elif var_TDD == 8:

        diccionario_Limites_Armonicos: dict = {
            'ARM_0_10': 7.0,
            'ARM_11_16': 3.5,
            'ARM_17_22': 2.5,
            'ARM_23_34': 1.0,
            'ARM_35': 0.5
        }

    elif var_TDD == 12:

        diccionario_Limites_Armonicos: dict = {
            'ARM_0_10': 10.0,
            'ARM_11_16': 4.5,
            'ARM_17_22': 4.0,
            'ARM_23_34': 1.5,
            'ARM_35': 0.7
        }

    elif var_TDD == 15:

        diccionario_Limites_Armonicos: dict = {
            'ARM_0_10': 12.0,
            'ARM_11_16': 5.5,
            'ARM_17_22': 5.0,
            'ARM_23_34': 2.0,
            'ARM_35': 1.0
        }

    elif var_TDD == 20:

        diccionario_Limites_Armonicos: dict = {
            'ARM_0_10': 15.0,
            'ARM_11_16': 7.0,
            'ARM_17_22': 6.0,
            'ARM_23_34': 2.5,
            'ARM_35': 1.4
        }

    return diccionario_Limites_Armonicos

def crear_DataFrame_CargabilidadTDD_Final(dataFrame: pd.DataFrame, val_Lim_CargTDD: float):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso agregando nuevas columnas de los nuevos parámetros que recibe.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        val_Lim_CargTDD (float): Es el valor de Referencia para el Límite de Cargabilidad TDD.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con las modificaciones aplicadas.
    """
    dataFrameFinalArmonicosCargTDDFinal = dataFrame.copy()

    dataFrameFinalArmonicosCargTDDFinal['Hora [UTC]'] = dataFrameFinalArmonicosCargTDDFinal['Hora [UTC]'].astype(str)
    dataFrameFinalArmonicosCargTDDFinal['Hora [UTC]'] = pd.to_datetime(dataFrameFinalArmonicosCargTDDFinal['Hora [UTC]'], format='mixed')

    dataFrameFinalArmonicosCargTDDFinal.loc[:,('var_Ref_Limite_Cargabilidad_TDD')] = val_Lim_CargTDD

    return dataFrameFinalArmonicosCargTDDFinal

def crear_Medidas_DataFrame_Tension(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_Tensiones: list = listado_Columnas_a_Medir

    dataFrame[columnas_var_Tabla_Tensiones] = dataFrame[columnas_var_Tabla_Tensiones].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Tensiones].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil (MIN, MED y MAX de cada Variable)
    percentiles_95 = dataFrame[columnas_var_Tabla_Tensiones].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo (MIN, MED y MAX de cada Variable)
    maximo = dataFrame[columnas_var_Tabla_Tensiones].max()

    #Aplica a cada columna la función del Promedio (MIN, MED y MAX de cada Variable)
    media = dataFrame[columnas_var_Tabla_Tensiones].mean()

    #Aplica a cada columna la función del Mínimo (MIN, MED y MAX de cada Variable)
    minimo = dataFrame[columnas_var_Tabla_Tensiones].min()

    #Crea un DataFrame que contiene los resultados de las operaciones (MIN, MED y MAX de cada Variable)
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_DesbTension(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_DesbTension_P1 = listado_Columnas_a_Medir

    columnas_var_Tabla_DesbTension_P2: list = ['Promedio', 'delta_V1', 'delta_V2', 'delta_V3', 'Desbalance']

    columnas_var_Tabla_DesbTension_P1.extend(columnas_var_Tabla_DesbTension_P2)

    columnas_var_Tabla_DesbTension: list = columnas_var_Tabla_DesbTension_P1

    dataFrame[columnas_var_Tabla_DesbTension] = dataFrame[columnas_var_Tabla_DesbTension].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_DesbTension].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_DesbTension].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_DesbTension].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_DesbTension].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_DesbTension].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_Corriente(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_Corriente: list = listado_Columnas_a_Medir
    #columnas_var_Tabla_Corriente: list = ['Corriente mn. L1', 'Corriente L1', 'Corriente mx. L1', 'Corriente mn. L2', 'Corriente L2', 'Corriente mx. L2', 'Corriente mn. L3', 'Corriente L3', 'Corriente mx. L3', 'Corriente de neutro mn.', 'Corriente de neutro', 'Corriente de neutro mx.']

    dataFrame[columnas_var_Tabla_Corriente] = dataFrame[columnas_var_Tabla_Corriente].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Corriente].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil (MIN, MED y MAX de cada Variable)
    percentiles_95 = dataFrame[columnas_var_Tabla_Corriente].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo (MIN, MED y MAX de cada Variable)
    maximo = dataFrame[columnas_var_Tabla_Corriente].max()

    #Aplica a cada columna la función del Promedio (MIN, MED y MAX de cada Variable)
    media = dataFrame[columnas_var_Tabla_Corriente].mean()

    #Aplica a cada columna la función del Mínimo (MIN, MED y MAX de cada Variable)
    minimo = dataFrame[columnas_var_Tabla_Corriente].min()

    #Crea un DataFrame que contiene los resultados de las operaciones (MIN, MED y MAX de cada Variable)
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_DesbCorriente(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión

    columnas_var_Tabla_DesbCorriente_P1 = listado_Columnas_a_Medir

    columnas_var_Tabla_DesbCorriente_P2: list = ['Promedio', 'max_Corrientes_Medias', 'Desbalance']

    columnas_var_Tabla_DesbCorriente_P1.extend(columnas_var_Tabla_DesbCorriente_P2)

    columnas_var_Tabla_DesbCorriente: list = columnas_var_Tabla_DesbCorriente_P1

    dataFrame[columnas_var_Tabla_DesbCorriente] = dataFrame[columnas_var_Tabla_DesbCorriente].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_DesbCorriente].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_DesbCorriente].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_DesbCorriente].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_DesbCorriente].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_DesbCorriente].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_PQS(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_PQS: list = listado_Columnas_a_Medir

    dataFrame[columnas_var_Tabla_PQS] = dataFrame[columnas_var_Tabla_PQS].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_PQS].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_PQS].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_PQS].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_PQS].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_PQS].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_FactorPotencia(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    #Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_FactPotencia: list = listado_Columnas_a_Medir

    dataFrame[columnas_var_Tabla_FactPotencia] = dataFrame[columnas_var_Tabla_FactPotencia].fillna(abs(0))

    #Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_FactPotencia].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_FactPotencia].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_FactPotencia].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_FactPotencia].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_FactPotencia].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_FactorPotenciaGeneral(dictFP):

    """
    Procesa un Diccionario y devuelve un nuevo Diccionario con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dictFP (dict): El DataFrame de entrada que se desea procesar.

    Returns:
        dict: Un nuevo Diccionario con las respectivas mediciones aplicadas.
    """
    resultados: dict = {}

    for llave, dataFrame in dictFP.items():
        medidas = {}
        columnas_Numericas = dataFrame.select_dtypes(include=[np.number]).columns

        for columna in columnas_Numericas:
            medidas[columna] = {
                'Percentil': np.nanpercentile(dataFrame[columna], 95),
                'Maximo': dataFrame[columna].max(),
                'Promedio': dataFrame[columna].mean(),
                'Minimo': dataFrame[columna].min()
            }
        resultados[llave] = medidas

    return resultados

def crear_Medidas_DataFrame_Distorsion_Tension(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Tensión
    columnas_var_Tabla_DistorsionTension: list = listado_Columnas_a_Medir

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_DistorsionTension] = dataFrame[columnas_var_Tabla_DistorsionTension].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_DistorsionTension].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_DistorsionTension].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_DistorsionTension].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_DistorsionTension].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_DistorsionTension].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_Armonicos_DistTension(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Armónicos de Distorsión de Tensión
    columnas_var_Tabla_Armonicos_DistorsionTension: list = listado_Columnas_a_Medir

    #columnas_var_Tabla_Armonicos_DistorsionTension: list = ['Arm. tensin 3 L1', 'Arm. tensin 5 L1', 'Arm. tensin 7 L1', 'Arm. tensin 9 L1', 'Arm. tensin 11 L1', 'Arm. tensin 13 L1', 'Arm. tensin 15 L1', 'Arm. tensin 3 L2', 'Arm. tensin 5 L2', 'Arm. tensin 7 L2', 'Arm. tensin 9 L2', 'Arm. tensin 11 L2', 'Arm. tensin 13 L2', 'Arm. tensin 15 L2', 'Arm. tensin 3 L3', 'Arm. tensin 5 L3', 'Arm. tensin 7 L3', 'Arm. tensin 9 L3', 'Arm. tensin 11 L3', 'Arm. tensin 13 L3', 'Arm. tensin 15 L3']

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension] = dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_Armonicos_DistorsionTension].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_Distorsion_Corriente(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Distorsión de Corriente
    columnas_var_Tabla_DistorsionCorriente: list = listado_Columnas_a_Medir

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_DistorsionCorriente] = dataFrame[columnas_var_Tabla_DistorsionCorriente].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_DistorsionCorriente].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_DistorsionCorriente].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_DistorsionCorriente].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_DistorsionCorriente].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_DistorsionCorriente].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_Armonicos_DistCorriente(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Armónicos de Distorsión de Corriente
    columnas_var_Tabla_Armonicos_DistorsionCorriente: list = listado_Columnas_a_Medir

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente] = dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_Armonicos_DistorsionCorriente].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_CargabilidadTDD(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Cargabilidad de TDD
    columnas_var_Tabla_CargabilidadTDD: list = listado_Columnas_a_Medir
    #columnas_var_Tabla_CargabilidadTDD: list = ['resultado_TDD_L1', 'resultado_TDD_L2', 'resultado_TDD_L3']

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_CargabilidadTDD] = dataFrame[columnas_var_Tabla_CargabilidadTDD].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_CargabilidadTDD].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_CargabilidadTDD].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_CargabilidadTDD].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_CargabilidadTDD].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_CargabilidadTDD].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_Flicker(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas del Flicker PLT
    columnas_var_Tabla_Flicker: list = listado_Columnas_a_Medir

    #columnas_var_Tabla_Flicker: list = ['Plt L1', 'Plt L2', 'Plt L3']

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_Flicker] = dataFrame[columnas_var_Tabla_Flicker].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_Flicker].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_Flicker].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_Flicker].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_Flicker].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_Flicker].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T

    return tabla_Con_Medidas_Por_Columna

def crear_Medidas_DataFrame_FactorK(dataFrame: pd.DataFrame, listado_Columnas_a_Medir: list):

    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas, en este caso con las respectivas mediciones de Percentiles, Máximos, Promedios y Mínimos al listado de columnas correspondiente.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada que se desea procesar.
        listado_Columnas_a_Medir (list): El listado con todas las columnas a las que se van a aplicar las medidas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame en su Transpuesta con las respectivas mediciones aplicadas.
    """
    # Selecciona las columnas de la siguiente lista, aplicándolo al DataFrame que contiene TODAS las columnas de Factor K
    columnas_var_Tabla_FactorK: list = listado_Columnas_a_Medir

    #columnas_var_Tabla_FactorK: list = ['Factor K mn. L1', 'Factor K L1', 'Factor K mx. L1', 'Factor K mn. L2', 'Factor K L2', 'Factor K mx. L2', 'Factor K mn. L3', 'Factor K L3', 'Factor K mx. L3']

    # Filtra por todas las columnas el dataFrame del parámetro y además de eso, rellena los datos vacíos con 0 Absoluto
    dataFrame[columnas_var_Tabla_FactorK] = dataFrame[columnas_var_Tabla_FactorK].fillna(abs(0))

    # Convertir dataFrame a tipo Float
    dataFrame[columnas_var_Tabla_FactorK].astype(float)

    for columna in dataFrame.columns:

        print(f"Columna: {columna} - Tipo de Dato: {dataFrame[columna].dtype}")

    #Aplica a cada columna la función del Percentil
    percentiles_95 = dataFrame[columnas_var_Tabla_FactorK].apply(lambda x: np.percentile(x, 95))

    #Aplica a cada columna la función del Máximo
    maximo = dataFrame[columnas_var_Tabla_FactorK].max()

    #Aplica a cada columna la función del Promedio
    media = dataFrame[columnas_var_Tabla_FactorK].mean()

    #Aplica a cada columna la función del Mínimo
    minimo = dataFrame[columnas_var_Tabla_FactorK].min()

    #Crea un DataFrame que contiene los resultados de las operaciones
    tabla_Con_Medidas_Por_Columna = pd.DataFrame({
                                    'Percentil' : percentiles_95,
                                    'Media': media,
                                    'Min': minimo,
                                    'Max': maximo})

    #Crea la Transpuesta de ese DataFrame para poder Visualizarlo a Forma de Título y los Datos
    tabla_Con_Medidas_Por_Columna=tabla_Con_Medidas_Por_Columna.T


    return tabla_Con_Medidas_Por_Columna

def crear_DataFrame_Energias(dataFrame: pd.DataFrame):
    """
    Procesa un DataFrame y devuelve un nuevo DataFrame con modificaciones específicas.

    - Si las columnas base (por ejemplo, 'Ep1+(Med)', 'Ep2+(Med)', 'Ep3+(Med)') existen,
      se suman para crear la columna total (por ejemplo, 'Eptot+(Med) [kWh]').
    - Si la columna total ya existe, se asume que es la columna de interés y no se intenta
      calcularla a partir de las columnas base (ya que estas no están presentes).

    En la agrupación por hora se suman los valores de la columna total, ya sea que se haya
    calculado a partir de las columnas base o que ya existiera en el DataFrame.

    Args:
        dataFrame (pd.DataFrame): El DataFrame de entrada.

    Returns:
        pd.DataFrame: El DataFrame procesado y agrupado por hora.
    """

    dataFrameFinalEnergias = dataFrame.copy()
    dataFrameFinalEnergias['Hora [UTC]'] = pd.to_datetime(dataFrameFinalEnergias['Hora [UTC]'], format='mixed')

    # Diccionario con la información de cada tipo de energía.
    energia_info = {
        "activa": {
            "columnas": ['Ep1+(Med)', 'Ep2+(Med)', 'Ep3+(Med)'],
            "unidad": "Wh",
            "columna_total": "Eptot+(Med) [kWh]",
            "computed": None
        },
        "capacitiva": {
            "columnas": ['EQfund1cap+(Med)', 'EQfund2cap+(Med)', 'EQfund3cap+(Med)'],
            "unidad": "varh",
            "columna_total": "EQtotcap+(Med) [kvarh]",
            "computed": None
        },
        "inductiva": {
            "columnas": ['EQfund1ind+(Med)', 'EQfund2ind+(Med)', 'EQfund3ind+(Med)'],
            "unidad": "varh",
            "columna_total": "EQtotind+(Med) [kvarh]",
            "computed": None
        }
    }

    # Procesar cada tipo de energía
    for tipo, info in energia_info.items():
        columnas_base = info["columnas"]
        unidad = info["unidad"]
        columna_total = info["columna_total"]

        # Si la columna total ya existe en el DataFrame original,
        # se asume que es la columna a usar y no se realiza la suma de las columnas base.
        if columna_total in dataFrame.columns:
            print(f"La columna total '{columna_total}' ya existe. No se realizará la suma de las columnas base para {tipo}.")
            info["computed"] = False
        else:
            # Buscar las columnas base en el DataFrame utilizando regex (buscando la unidad especificada)
            patron_columnas = "|".join([fr"{re.escape(col)} \[{unidad}\]" for col in columnas_base])
            columnas_encontradas = dataFrame.filter(regex=patron_columnas).columns.to_list()
            print(f"Columnas base encontradas para {tipo}: {columnas_encontradas}")

            if columnas_encontradas:
                # Se crea la columna total sumando las columnas base encontradas
                dataFrameFinalEnergias[columna_total] = dataFrameFinalEnergias[columnas_encontradas].sum(axis=1)
                info["computed"] = True
            else:
                print(f"No se encontraron columnas base para {tipo}.")
                info["computed"] = False

    # Redondear los valores
    dataFrameFinalEnergias = dataFrameFinalEnergias.round(6)
    print("*" * 50)

    # Definir las columnas finales a mantener
    listado_Final_Columnas_Energias = ['Hora [UTC]'] + \
        [info["columna_total"] for info in energia_info.values()] + \
        ['PFetotcap+(Med) []', 'PFetotind+(Med) []', 'PFetotcap-(Med) []', 'PFetotind-(Med) []']

    dataFrameFinal_Energias_Copy = dataFrameFinalEnergias[listado_Final_Columnas_Energias].copy()

    # Columnas de factor de potencia (se aplica una función lambda para calcular el percentil 0.95)
    columnas_FactorPotencia = ['PFetotcap+(Med) []', 'PFetotind+(Med) []', 'PFetotcap-(Med) []', 'PFetotind-(Med) []']

    # Armado del diccionario de agregación para la agrupación por hora:
    # En ambos casos (ya sea que la columna total se haya calculado o ya existiera),
    # se suma la columna total.
    agg_dict = {}
    for tipo, info in energia_info.items():
        columna_total = info["columna_total"]
        agg_dict[columna_total] = 'sum'

    agg_dict.update({col: lambda x: x.quantile(0.95) for col in columnas_FactorPotencia})

    # Agrupamos por hora: definimos 'Hora_Corte' como el límite de cada hora (redondeo hacia abajo + 1 hora)
    dataFrame_H_a_H = dataFrameFinal_Energias_Copy.copy()
    dataFrame_H_a_H['Hora_Corte'] = dataFrame_H_a_H['Hora [UTC]'].dt.floor('h') + pd.Timedelta(hours=1)

    dataFrame_H_a_H_Result = (
        dataFrame_H_a_H.groupby('Hora_Corte')
        .agg(agg_dict)
        .reset_index()
        .rename(columns={'Hora_Corte': 'Hora [UTC]'})
    )

    # Ejemplo de columnas adicionales
    dataFrame_H_a_H_Result['KWH'] = 100
    
    dataFrame_H_a_H_Result['KVARH_CAP'] = np.where(
        (dataFrame_H_a_H_Result['EQtotcap+(Med) [kvarh]'] != 0) &
        (dataFrame_H_a_H_Result['Eptot+(Med) [kWh]'] != 0),
        dataFrame_H_a_H_Result['EQtotcap+(Med) [kvarh]'] / dataFrame_H_a_H_Result['Eptot+(Med) [kWh]'] * 100,
        0
    )

    dataFrame_H_a_H_Result['KARH_IND'] = np.where(
        (dataFrame_H_a_H_Result['EQtotind+(Med) [kvarh]'] != 0) &
        (dataFrame_H_a_H_Result['Eptot+(Med) [kWh]'] != 0),
        (dataFrame_H_a_H_Result['EQtotind+(Med) [kvarh]'] / dataFrame_H_a_H_Result['Eptot+(Med) [kWh]']) * 100,
        0
    )

    return dataFrame_H_a_H_Result

def calcular_Variacion_Tension(lista_Percentiles: list, val_Nom: float):
    """
    Realiza la operación: ((valor / divisor) - 100) * 100 para cada elemento de la lista.

    Args:
        lista_Percentiles (list): Lista de valores numéricos.
        val_Nom (float): Valor único por el cual se dividirán los elementos de la lista.

    Returns:
        list: Lista con los resultados de la operación para cada elemento.
    """
    if val_Nom == 0:
        raise ValueError("El divisor no puede ser cero.")

    return [((valor / val_Nom) - 1) * 100 for valor in lista_Percentiles]

def calcular_Valor_Cargabilidad_Disponibilidad(capacidad_Trafo: float, perc_Max_Pot_Apa: float):

    """
    Crea una lista que contiene los valores de la cargabilidad máxima y la disponibilidad de carga.

    Args:
        capacidad_Trafo (float): El número que representa la capacidad del transformador.
        perc_Max_Pot_Apa (float): El número que representa el percentil máximo de la potencia aparente.

    Returns:
        list[float]: Una lista con dos elementos de tipo float, correspondientes a los valores de la cargabilidad máxima y la disponibilidad de carga.
    """
    var_Cargabilidad_Max = perc_Max_Pot_Apa/capacidad_Trafo*100
    var_Disponibilidad = 100-var_Cargabilidad_Max

    return [var_Cargabilidad_Max, var_Disponibilidad]

def calcular_Observacion_Tension(listado_Percentiles_Tension: list, listado_Limites_Tension: list):

    """
    Evalúa si todos los valores de listado_Percentiles_Tension cumplen con la condición de no ser menores ni mayores
    que los valores de listado_Limites_Tension.

    Args:
        listado_Percentiles_Tension (list): Lista de valores numéricos a evaluar (Los Percentiles).
        listado_Limites_Tension (list): Lista con exactamente dos valores para la comparación (Los Límites).

    Returns:
        dict: Diccionario con dos llaves:
            - "valores_no_cumplen": Lista de valores de listado_Percentiles_Tension que no cumplen la condición.
            - "cumple_condicion": "SÍ" si todos los valores cumplen la condición, "NO" de lo contrario.
    """
    if len(listado_Limites_Tension) != 2:
        raise ValueError("La lista listado_Limites_Tension debe contener exactamente 2 valores.")

    menor, mayor = listado_Limites_Tension
    valores_no_cumplen = []
    cumple_condicion = "SÍ"

    for valor in listado_Percentiles_Tension:
        if valor < menor or valor > mayor:
            valores_no_cumplen.append(valor)
            cumple_condicion = "NO"

    if cumple_condicion == "SÍ":

        condicion_2 = "NO"

        condicion_3 = "BUEN"

    else:

        condicion_2 = "SÍ"

        condicion_3 = "MAL"

    resultado_Validacion: dict = {
        "valores_No_Cumplen": valores_no_cumplen,
        "cumple_Condicion": cumple_condicion,
        "cumple_Condicion_2": condicion_2,
        "cumple_Condicion_3": condicion_3
    }

    return resultado_Validacion

def calcular_Observacion_Corriente(diccionario_Percentiles_Corriente: dict, diccionario_Percentiles_CorrienteNeutra: dict, valor_Corriente_Nominal: float):

    """
    Evalúa los valores máximos de dos diccionarios y compara el máximo del Diccionario diccionario_Percentiles_Corriente
    con la variable valor_Corriente_Nominal.

    Args:
        diccionario_Percentiles_Corriente (dict): Primer diccionario con valores numéricos.
        diccionario_Percentiles_CorrienteNeutra (dict): Segundo diccionario con valores numéricos.
        valor_Corriente_Nominal (float): Valor numérico para la comparación.

    Returns:
        list: Lista con tres elementos:
            1. Diccionario con la clave y valor del máximo del Diccionario diccionario_Percentiles_Corriente.
            2. Resultado "FUERA" o "DENTRO" según la comparación del máximo de Diccionario diccionario_Percentiles_Corriente con valor_Corriente_Nominal.
            3. Diccionario con la clave y valor del máximo del Diccionario diccionario_Percentiles_CorrienteNeutra.
    """
    # Obtener el máximo del Diccionario diccionario_Percentiles_Corriente
    clave_Max_Corriente, valor_Max_Corriente = max(diccionario_Percentiles_Corriente.items(), key=lambda item: item[1])
    maximo_Diccionario_Corriente = {clave_Max_Corriente: valor_Max_Corriente}

    # Evaluar si el valor máximo del Diccionario diccionario_Percentiles_Corriente es mayor que la variable valor_Corriente_Nominal
    resultado_Comparacion = "FUERA" if valor_Max_Corriente > valor_Corriente_Nominal else "DENTRO"

    # Obtener el máximo del Diccionario diccionario_Percentiles_CorrienteNeutra
    clave_Max_CorrienteNeutra, valor_Max_CorrienteNeutra = max(diccionario_Percentiles_CorrienteNeutra.items(), key=lambda item: item[1])
    maximo_Diccionario_CorrienteNeutra = {clave_Max_CorrienteNeutra: valor_Max_CorrienteNeutra}

    # Creación de Diccionario con los Resultados
    resultado_Validacion: dict = {
        'val_Maximo_Corriente': maximo_Diccionario_Corriente,
        'resultado_Comparacion_Corriente': resultado_Comparacion,
        'val_Maximo_CorrienteNeutra': maximo_Diccionario_CorrienteNeutra
    }

    # Retornar los resultados
    return resultado_Validacion

def calcular_Observacion_DesbTension(valor_Percentil_DesbTension: float, valor_Referencia_DesbTension: float):

    """
    Evalúa si la variable valor_Percentil_DesbTension es mayor que la variable valor_Referencia_DesbTension y retorna una lista de resultados.

    Args:
        valor_Percentil_DesbTension (float): Primera variable a evaluar.
        valor_Referencia_DesbTension (float): Segunda variable a evaluar.

    Returns:
        list: Una lista con dos elementos:
            - "SÍ", "SÍ SUPERA" y "NO CUMPLE" si valor_Percentil_DesbTension es mayor que valor_Referencia_DesbTension.
            - "NO", "NO SUPERA" y "SÍ CUMPLE" si valor_Percentil_DesbTension no es mayor que valor_Referencia_DesbTension.
    """
    if valor_Percentil_DesbTension > valor_Referencia_DesbTension:

        resultado_Validacion = ["SÍ", "SÍ SUPERA", "NO CUMPLE"]

    else:

        resultado_Validacion = ["NO", "NO SUPERA", "SÍ CUMPLE"]

    return resultado_Validacion

def calcular_Observacion_DesbCorriente(valor_Percentil_DesbCorriente: float, valor_Referencia_DesbCorriente: float):

    """
    Evalúa si la variable valor_Percentil_DesbCorriente es mayor que la variable valor_Referencia_DesbCorriente y retorna una lista de resultados.

    Args:
        valor_Percentil_DesbCorriente (float): Primera variable a evaluar.
        valor_Referencia_DesbCorriente (float): Segunda variable a evaluar.

    Returns:
        list: Una lista con dos elementos:
            - "SÍ", "SÍ SUPERA" y "NO CUMPLE" si valor_Percentil_DesbCorriente es mayor que valor_Referencia_DesbCorriente.
            - "NO", "NO SUPERA" Y "SÍ CUMPLE" si valor_Percentil_DesbCorriente no es mayor que valor_Referencia_DesbCorriente.
    """
    if valor_Percentil_DesbCorriente > valor_Referencia_DesbCorriente:

        resultado_Validacion = ["SÍ", "SÍ SUPERA", "NO CUMPLE"]

    else:

        resultado_Validacion = ["NO", "NO SUPERA", "SÍ CUMPLE"]

    return resultado_Validacion

def calcular_Observacion_THDV(diccionario_Percentiles_THDV: dict, valor_Referencia_THDV: float):

    """
    Evalúa si todos los valores del diccionario diccionario_Percentiles_THDV son menores que la variable valor_Referencia_THDV.

    Args:
        diccionario_Percentiles_THDV (dict): Diccionario con valores de tipo float.
        valor_Referencia_THDV (float): Valor a comparar contra los valores del diccionario.

    Returns:
        str: "NO CUMPLE" si alguno de los valores del diccionario es mayor o igual a valor_Referencia_THDV.
            "SÍ CUMPLE" si todos los valores del diccionario son menores que valor_Referencia_THDV.
    """
    # Evaluar si todos los valores son menores que valor_Referencia_THDV
    if all(valor < valor_Referencia_THDV for valor in diccionario_Percentiles_THDV.values()):

        resultado_Validacion = "SÍ CUMPLE"

    else:

        resultado_Validacion = "NO CUMPLE"

    return resultado_Validacion

def calcular_Observacion_Armonicos_Corriente(diccionario_Percentiles_Arm_3_9: dict, diccionario_Percentiles_Arm_11: dict, listado_Limites_Armonicos_Corriente: list):

    """
    Evalúa si los valores de diccionario diccionario_Percentiles_Arm_3_9 y diccionario diccionario_Percentiles_Arm_11 cumplen ciertas condiciones
    al compararlos con los valores del listado listado_Limites_Armonicos_Corriente.

    Args:
        diccionario_Percentiles_Arm_3_9 (dict): Diccionario con valores numéricos de los Percentiles de los Armónicos del 3 al 9.
        diccionario_Percentiles_Arm_11 (dict): Diccionario con valores numéricos de los Percentiles de los Armónicos #11.
        listado_Limites_Armonicos_Corriente (list): Lista con dos elementos numéricos con los límites de los Armónicos.

    Returns:
        dict: Contiene el resultado de las comparaciones y los valores que no cumplieron.
    """
    # Elementos del listado
    limite1, limite2 = listado_Limites_Armonicos_Corriente

    # Evaluar los valores del Diccionario 1 contra el primer elemento del Listado 1
    no_Cumplen_Diccionario_Armonicos_3_9 = [valor for valor in diccionario_Percentiles_Arm_3_9.values() if valor > limite1]
    resultado_Diccionario_Armonicos_3_9 = "NO CUMPLEN" if no_Cumplen_Diccionario_Armonicos_3_9 else "SÍ CUMPLEN"

    # Evaluar los valores del Diccionario 2 contra el segundo elemento del Listado 1
    no_Cumplen_Diccionario_Armonicos_11 = [valor for valor in diccionario_Percentiles_Arm_11.values() if valor > limite2]
    resultado_Diccionario_Armonicos_11 = "NO CUMPLEN" if no_Cumplen_Diccionario_Armonicos_11 else "SÍ CUMPLEN"

    # Retornar un diccionario con los resultados y los valores que no cumplieron
    resultado_Validacion: dict = {
        "resultado_Arm_3_9": resultado_Diccionario_Armonicos_3_9,
        "no_Cumplen_Arm_3_9": no_Cumplen_Diccionario_Armonicos_3_9,
        "resultado_Arm_11": resultado_Diccionario_Armonicos_11,
        "no_Cumplen_Arm_11": no_Cumplen_Diccionario_Armonicos_11
    }

    return resultado_Validacion

def calcular_Observacion_TDD(diccionario_Percentiles_TDD: dict, valor_Referencia_TDD: float):

    """
    Evalúa si todos los valores del diccionario diccionario_Percentiles_TDD son menores que la variable valor_Referencia_TDD.

    Args:
        diccionario_Percentiles_TDD (dict): Diccionario con valores de tipo float.
        valor_Referencia_TDD (float): Valor a comparar contra los valores del diccionario.

    Returns:
        list: "NO CUMPLE" si alguno de los valores del diccionario es mayor o igual a valor_Referencia_TDD.
            "SÍ CUMPLE" si todos los valores del diccionario son menores que valor_Referencia_TDD.
    """
    # Evaluar si todos los valores son menores que valor_Referencia_THDV
    if all(valor < valor_Referencia_TDD for valor in diccionario_Percentiles_TDD.values()):

        resultado_Validacion = ["SÍ CUMPLEN", "NO SUPERAN"]

    else:

        resultado_Validacion = ["NO CUMPLEN", "SÍ SUPERAN"]

    return resultado_Validacion

def graficar_Timeline_Tension(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limites=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limites (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limites:
        ax.axhline(y=limites[0], color='red', linestyle='-', label=f'Límite Superior ({limites[0]}), [V]')
        ax.axhline(y=limites[1], color='red', linestyle='-', label=f'Límite Inferior ({limites[1]}), [V]')
        ax.set_ylim(-30,limites[0]+100)

    # Configurar etiquetas y títulos
    ax.set_ylabel('Tensión de Línea [V]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_Tension_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_Tension_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_Tension_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_Tension = Image.open(img_buffer_Tension_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_Tension, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_Tension_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_Tension_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_Tension_Con_Borde.seek(0)

    # Mostrar la imagen en Streamlit
    image = Image.open(img_buffer_Tension_Con_Borde)
    st.image(image, caption="Gráfico de Tensión", use_container_width=True)

    return img_buffer_Tension_Con_Borde

def graficar_Timeline_Corriente(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Corriente Nominal ({round(limite, 2)}), [A]')
        ax.set_ylim(-30,limite+500)

    # Configurar etiquetas y títulos
    ax.set_ylabel('Corriente de Línea [A]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_Corriente_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_Corriente_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_Corriente_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_Corriente = Image.open(img_buffer_Corriente_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_Corriente, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_Corriente_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_Corriente_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_Corriente_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_Corriente_Con_Borde)
    st.image(image, caption="Gráfico de Corriente", use_container_width=True)
    
    #display(image)

    return img_buffer_Corriente_Con_Borde

def graficar_Timeline_DesbTension(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), [%]", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Valor de Referencia ({limite}), [%]')

    # Configurar etiquetas y títulos
    ax.set_ylabel('Desbalance de Tensión [%]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_DesbTension = BytesIO()
    plt.savefig(img_buffer_DesbTension, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_DesbTension.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_DesbTension = Image.open(img_buffer_DesbTension)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_DesbTension, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_DesbTension_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_DesbTension_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_DesbTension_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_DesbTension_Con_Borde)
    st.image(image, caption="Gráfico de Desbalance de Tensión", use_container_width=True)
    #display(image)

    return img_buffer_DesbTension_Con_Borde

def graficar_Timeline_DesbCorriente(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), [%]", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Valor de Referencia ({limite}), [%]')

    # Configurar etiquetas y títulos
    ax.set_ylabel('Desbalance de Corriente [%]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_DesbCorriente_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_DesbCorriente_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_DesbCorriente_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_DesbCorriente = Image.open(img_buffer_DesbCorriente_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_DesbCorriente, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_Corriente_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_Corriente_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_Corriente_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_Corriente_Con_Borde)
    st.image(image, caption="Gráfico de Desbalance de Corriente", use_container_width=True)
    #display(image)

    return img_buffer_Corriente_Con_Borde

def graficar_Timeline_PQS_ActApa(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'yellow']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), [kW / kVA]", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Configurar etiquetas y títulos
    ax.set_ylabel('Potencias')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_PQSActApa_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_PQSActApa_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_PQSActApa_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_ActApa = Image.open(img_buffer_PQSActApa_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_ActApa, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_PQSActApa_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_PQSActApa_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_PQSActApa_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_PQSActApa_Con_Borde)
    st.image(image, caption="Gráfico de Potencias (Activa/Aparente)", use_container_width=True)
    #display(image)

    return img_buffer_PQSActApa_Con_Borde

def graficar_Timeline_PQS_CapInd(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'yellow']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), [kVAR]", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Configurar etiquetas y títulos
    ax.set_ylabel('Potencias')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_PQSCapInd_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_PQSCapInd_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_PQSCapInd_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_CapInd = Image.open(img_buffer_PQSCapInd_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_CapInd, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_PQSCapInd_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_PQSCapInd_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_PQSCapInd_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_PQSCapInd_Con_Borde)
    st.image(image, caption="Gráfico de Potencias (Capacitiva/Inductiva)", use_container_width=True)
    #display(image)

    return img_buffer_PQSCapInd_Con_Borde

def graficar_Timeline_FactPotencia(dataFrame: pd.DataFrame, variables: list, percentiles: dict, medidas_dataFrame: dict, fecha_col: str, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        medidas_dataFrame (dict): Un diccionario para agregar a los títulos de las variables la cantidad de valores positivos, ceros o negativos.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['blue', 'red', 'green', 'yellow']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Creamos una lista de Listas y que contiene 2 Listas Individuales con los Valores de cada Factor de Potencia (+ y -) y sus Mediciones (+,0,-)
    list_Mediciones_FP: list = [[medidas_dataFrame.get('CANT_POSITIVOS_FP_POS'), medidas_dataFrame.get('CANT_CEROS_FP_POS')], [medidas_dataFrame.get('CANT_POSITIVOS_FP_NEG'), medidas_dataFrame.get('CANT_CEROS_FP_NEG')]]

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):

        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), + : ( {list_Mediciones_FP[i][0]} ), 0 : ( {list_Mediciones_FP[i][1]} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Configurar etiquetas y títulos
    ax.set_ylabel('Factor de Potencia')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_FactPotencia_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_FactPotencia_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_FactPotencia_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_FactPotencia = Image.open(img_buffer_FactPotencia_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_FactPotencia, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_FactPotencia_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_FactPotencia_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_FactPotencia_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_FactPotencia_Con_Borde)
    st.image(image, caption="Gráfico de Factor de Potencia", use_container_width=True)
    #display(image)

    return img_buffer_FactPotencia_Con_Borde

def graficar_Timeline_Distorsion_Tension(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Distorsión Armónico de Tensión ({round(limite, 2)}), [%]')
        ax.set_ylim(-5,limite+5)

    # Configurar etiquetas y títulos
    ax.set_ylabel('Distorsión Armónica de Tensión [%]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_DistTension_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_DistTension_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_DistTension_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_DistTension = Image.open(img_buffer_DistTension_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_DistTension, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_DistTension_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_DistTension_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_DistTension_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_DistTension_Con_Borde)
    st.image(image, caption="Gráfico de Distorsión de Tensión", use_container_width=True)

    #display(image)

    return img_buffer_DistTension_Con_Borde

def graficar_Timeline_Distorsion_Corriente(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Distorsión Armónica de Corriente ({round(limite, 2)})')

    # Configurar etiquetas y títulos
    ax.set_ylabel('Distorsión Armónica de Corriente [%]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_DistCorriente_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_DistCorriente_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_DistCorriente_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_DistCorriente = Image.open(img_buffer_DistCorriente_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_DistCorriente, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_DistCorriente_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_DistCorriente_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_DistCorriente_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_DistCorriente_Con_Borde)
    st.image(image, caption="Gráfico de Distorsión de Corriente", use_container_width=True)
    
    #display(image)

    return img_buffer_DistCorriente_Con_Borde

def graficar_Timeline_CargabilidadTDD(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valor Máximo del TDD
    copy_dataFrame = dataFrame.copy()
    val_Max_TDD = copy_dataFrame[variables].max().max()
    #print(f"Valor Máximo del TDD {val_Max_TDD}")

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} ), [%]", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Armónicos de Cargabilidad TDD ({round(limite, 2)}), [%]')
        ax.set_ylim(-5,val_Max_TDD+10)

    # Configurar etiquetas y títulos
    ax.set_ylabel('TDD [%]')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_CargTDD_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_CargTDD_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_CargTDD_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_CargTDD = Image.open(img_buffer_CargTDD_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_CargTDD, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_CargTDD_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_CargTDD_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_CargTDD_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_CargTDD_Con_Borde)
    st.image(image, caption="Gráfico de Armónicos de Cargabilidad TDD", use_container_width=True)
    
    #display(image)

    return img_buffer_CargTDD_Con_Borde

def graficar_Timeline_Flicker(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Flicker PLT ({round(limite, 2)})')
        ax.set_ylim(-5,limite+5)

    # Configurar etiquetas y títulos
    ax.set_ylabel('FLICKER PLT')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_Flicker_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_Flicker_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_Flicker_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_Flicker = Image.open(img_buffer_Flicker_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_Flicker, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_Flicker_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_Flicker_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_Flicker_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_Flicker_Con_Borde)
    st.image(image, caption="Gráfico de Flicker", use_container_width=True)
    
    #display(image)

    return img_buffer_Flicker_Con_Borde

def graficar_Timeline_FactorK(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, limite=None, titulo=''):

    """
    Genera un gráfico a partir de los parámetros proporcionados y devuelve un buffer con la imagen en memoria.

    Args:
        dataFrame (pd.DataFrame): El DataFrame que contiene los datos a graficar.
        variables (list): Una lista de valores que se van a visualizar en el gráfico.
        percentiles (dict): Un diccionario para agregar al título los percentiles de forma específica por cada una de las variables.
        fecha_col (str): Identifica el nombre de la columna que contiene la Fecha y Hora a graficar en el eje X.
        limite (list): Una lista utilizada para los datos que contienen los límites en caso de aplicar al gráfico.
        titulo (str): Identifica el nombre que se va a agregar en el gráfico.

    Returns:
        io.BytesIO: Un buffer en memoria que contiene la imagen del gráfico generado.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

    # Colores para la Figura
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Graficar cada variable
    for i, (var, var_Pr) in enumerate(zip(variables, valores_Percentiles)):
        ax.plot(dataFrame[fecha_col], dataFrame[var], label=f"{var}, (PR: {var_Pr} )", alpha=0.45, linewidth=1.2, color=colores[i % len(colores)])

    # Configurar espaciado de etiquetas y formato de fechas
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Formato de fecha
    plt.xticks(rotation=45)  # Rotar etiquetas

    # Agregar límites si se proporcionan
    if limite:
        ax.axhline(y=limite, color='red', linestyle='-', label=f'Límite - Factor K ({round(limite, 2)})')

    # Configurar etiquetas y títulos
    ax.set_ylabel('Factor K')
    ax.set_xlabel('Fechas')
    ax.set_title(titulo)

    # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
    ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

    ax.grid(True)

    # Crear un buffer para la imagen en memoria
    img_buffer_Factork_Sin_Borde = BytesIO()
    plt.savefig(img_buffer_Factork_Sin_Borde, format='png')  # Guardar la imagen en el buffer
    plt.close()
    img_buffer_Factork_Sin_Borde.seek(0)  # Reiniciar el puntero al principio del buffer

    # Cargar la imagen desde el buffer
    imagen_Factork = Image.open(img_buffer_Factork_Sin_Borde)

    # Definir el color y ancho del borde
    color_Borde = (0, 176, 80)  # Verde
    ancho_Borde = 4

    # Agregar el borde a la imagen
    imagen_Con_Borde = ImageOps.expand(imagen_Factork, border=ancho_Borde, fill=color_Borde)

    # Guardar la imagen con borde en un nuevo buffer
    img_buffer_Factork_Con_Borde = BytesIO()
    imagen_Con_Borde.save(img_buffer_Factork_Con_Borde, format='png')

    # Reiniciar el puntero del nuevo buffer
    img_buffer_Factork_Con_Borde.seek(0)

    # Mostrar la imagen en Google Colab
    image = Image.open(img_buffer_Factork_Con_Borde)
    st.image(image, caption="Gráfico de FactorK", use_container_width=True)
    
    #display(image)

    return img_buffer_Factork_Con_Borde


def obtener_nombre_mes(mes):

    """
    Convierte el número entero del mes en una representación de texto con el equivalente al nombre del mes.

    Args:
        mes (int): Un número entero que representa el número del mes.

    Returns:
        str: La representación en cadena del mes para el número proporcionado.
    """
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return meses.get(mes, "Mes inválido")


def generar_Graficos_Barras_Energias(dataFrame: pd.DataFrame, variables: list, percentiles: dict, fecha_col: str, doc):
    """
    Genera gráficos de barras por cada día, mostrando las columnas a lo largo del tiempo (hora).

    :param dataFrame: DataFrame con los datos.
    :param variables: Lista de columnas a graficar (Energías).
    :param fecha_col: Nombre de la columna que contiene las fechas y horas.
    :param doc: Documento de Word para generar los InlineImages.

    :return: Diccionario anidado con gráficos en formato InlineImage.
    """
    # Crear un diccionario para guardar los gráficos
    graficos_dict = {}

    #2024-11-08 10:39:00

    # Valores del Diccionario con los datos de los Percentiles
    valores_Percentiles = percentiles.values()

    # Asegurar que la columna de fecha esté en formato datetime
    dataFrame[fecha_col] = pd.to_datetime(dataFrame[fecha_col], format="%Y/%m/%d %H:%M:%S", errors='coerce')

    # Extraer los días únicos
    dias = dataFrame[fecha_col].dt.date.unique()

    # Iterar por cada día
    for dia in dias:
        dia_data = dataFrame[dataFrame[fecha_col].dt.date == dia]
        graficos_dict[str(dia)] = {}

        year = dia_data[fecha_col].dt.year.iloc[0]
        month = dia_data[fecha_col].dt.month.iloc[0]
        day_number = dia_data[fecha_col].dt.day.iloc[0]
        month_name = obtener_nombre_mes(month)

        # Generar gráficos para las combinaciones de columnas
        # Gráfico 1: Columna 0 y Columna 1
        if len(variables) >= 2:  # Asegurarse de que hay suficientes columnas
            x_values = dia_data[fecha_col].dt.strftime("%d/%m/%y %H:%M:%S")
            bar_width = 0.4
            x_indexes = range(len(x_values))

            # Calcula el valor Máximo de las Barras o Líneas de la Energía Activa - Capacitiva
            max_Value_ActCap = max(
                max(dia_data[variables[0]]),  # Máximo de la Energía Activa
                max(dia_data[variables[1]]),  # Máximo de la Energía Capacitiva
                max(dia_data[variables[3]])   # Máximo del KVARH-CAP
            )

            # Ajustar el límite superior del eje Y dinámicamente con un margen adicional
            y_margin_ActCap = max_Value_ActCap * 0.3  # 30% del valor máximo como margen superior

            fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

            # Agregar las barras de ambas columnas
            ax.bar(x_indexes, dia_data[variables[0]], width=bar_width, label=f"{variables[0]}, (PR: {percentiles.get('PERCENTIL_ENERGIA_ACTIVA_MED')} ), [kWh]", color='#66BB6A', align="center")
            ax.bar([x + bar_width for x in x_indexes], dia_data[variables[1]], width=bar_width, label=f"{variables[1]}, (PR: {percentiles.get('PERCENTIL_ENERGIA_CAPACITIVA_MED')} ), [kVARh]", color='#AB47BC', align="center")

            # Mostrar valores en las barras de la Energía Activa
            for i, v in enumerate(dia_data[variables[0]]):
                ax.text(i, v + y_margin_ActCap * 0.1, f'{v:.1f}', ha='center', fontsize=6.5)

            # Mostrar valores en las barras de la Energía Capacitiva
            for i, v in enumerate(dia_data[variables[1]]):
                ax.text(i + bar_width, v + y_margin_ActCap * 0.1, f'{v:.1f}', ha='center', fontsize=6.5)

            # Agregar la Línea al gráfico de Barras (En este caso es KVARH-CAP)
            line_values = dia_data[variables[3]]
            ax.plot([x + bar_width / 2 for x in x_indexes], line_values, label=f"{variables[3]}, [%]", color='red', linestyle='-', linewidth=1)

            # Mostrar valores en los puntos de la Línea KVARH_CAP
            for i, v in enumerate(line_values):
                ax.text(i + bar_width / 2, v + y_margin_ActCap * 0.4, f'{v:.3f}%', ha='center', fontsize=5.5, rotation=50, color='red')

            # Formatear el eje X
            ax.set_xticks([x + bar_width / 2 for x in x_indexes])
            ax.set_xticklabels(x_values, rotation=45, ha='right')

            # Configurar el resto del gráfico
            ax.set_title(f"REGISTROS DE ENERGÍA ({variables[0]}) Y ENERGÍA ({variables[1]}) - {day_number} de {month_name} del {year}", fontsize=8)
            ax.set_xlabel("Hora del Día", fontsize=10)
            ax.set_ylabel("Valores [kWh - kVARh]", fontsize=10)
            ax.set_ylim(0, max_Value_ActCap + y_margin_ActCap)

            # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
            ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

            ax.grid(True, linestyle="--", alpha=0.7)

            # Guardar el gráfico en un buffer
            buffer_Energia_ActCap_Sin_Borde = BytesIO()
            plt.savefig(buffer_Energia_ActCap_Sin_Borde, format="png", dpi=100)
            buffer_Energia_ActCap_Sin_Borde.seek(0)
            plt.close(fig)

            # Cargar la imagen desde el buffer
            imagen_Energia_ActCap = Image.open(buffer_Energia_ActCap_Sin_Borde)

            # Definir el color y ancho del borde
            color_Borde = (0, 176, 80)  # Verde
            ancho_Borde = 4

            # Agregar el borde a la imagen
            imagen_Con_Borde = ImageOps.expand(imagen_Energia_ActCap, border=ancho_Borde, fill=color_Borde)

            # Guardar la imagen con borde en un nuevo buffer
            img_buffer_Energia_ActCap_Con_Borde = BytesIO()
            imagen_Con_Borde.save(img_buffer_Energia_ActCap_Con_Borde, format='png')

            # Reiniciar el puntero del nuevo buffer
            img_buffer_Energia_ActCap_Con_Borde.seek(0)

            print("******"*50)
            # Mostrar la imagen en Google Colab
            image = Image.open(img_buffer_Energia_ActCap_Con_Borde)
            st.image(image, caption="Gráficos de Energías", use_container_width=True)
            #display(image)
            print("******"*50)

            # Almacenar en el diccionario como InlineImage
            graficos_dict[str(dia)][f"Graf_{variables[0]}_{variables[1]}"] = InlineImage(doc, img_buffer_Energia_ActCap_Con_Borde, Cm(18))

        # Gráfico 2: Columna 0 y Columna 2
        if len(variables) >= 3:  # Asegurarse de que hay suficientes columnas

            fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

            # Calcula el valor Máximo de las Barras o Líneas de la Energía Activa - Capacitiva
            max_Value_ActInd = max(
                max(dia_data[variables[0]]),  # Máximo de la Energía Activa
                max(dia_data[variables[2]]),  # Máximo de la Energía Capacitiva
                max(dia_data[variables[4]])   # Máximo del KVARH-CAP
            )

            # Ajustar el límite superior del eje Y dinámicamente con un margen adicional
            y_margin_ActInd = max_Value_ActInd * 0.3  # 30% del valor máximo como margen superior

            # Agregar las barras de ambas columnas
            ax.bar(x_indexes, dia_data[variables[0]], width=bar_width, label=f"{variables[0]}, (PR: {percentiles.get('PERCENTIL_ENERGIA_ACTIVA_MED')} ), [kWh]", color='#66BB6A', align="center")
            ax.bar([x + bar_width for x in x_indexes], dia_data[variables[2]], width=bar_width, label=f"{variables[2]}, (PR: {percentiles.get('PERCENTIL_ENERGIA_INDUCTIVA_MED')} ), [kVARh]", color='#FFA726', align="center")

            # Mostrar valores en las barras de la Energía Activa
            for i, v in enumerate(dia_data[variables[0]]):
                ax.text(i, v + y_margin_ActInd * 0.1, f'{v:.1f}', ha='center', fontsize=6.5)

            # Mostrar valores en las barras de la Energía Inductiva
            for i, v in enumerate(dia_data[variables[2]]):
                ax.text(i + bar_width, v + y_margin_ActInd * 0.1, f'{v:.1f}', ha='center', fontsize=6.5)

            # Agregar la Línea al gráfico de Barras (En este caso es KARH-IND)
            line_values = dia_data[variables[4]]
            ax.plot([x + bar_width / 2 for x in x_indexes], line_values, label=f"{variables[4]}, [%]", color='red', linestyle='-', linewidth=1)

            # Mostrar valores en los puntos de la Línea KARH_IND
            for i, v in enumerate(line_values):
                ax.text(i + bar_width / 2, v + y_margin_ActInd * 0.4, f'{v:.3f}%', ha='center', fontsize=5.5, rotation=50, color='red')

            # Formatear el eje X
            ax.set_xticks([x + bar_width / 2 for x in x_indexes])
            ax.set_xticklabels(x_values, rotation=45, ha='right')

            # Configurar el resto del gráfico
            ax.set_title(f"REGISTROS DE ENERGÍA ({variables[0]}) Y ENERGÍA ({variables[2]}) - {day_number} de {month_name} del {year}", fontsize=8)
            ax.set_xlabel("Hora del Día", fontsize=10)
            ax.set_ylabel("Valores [kWh - kVARh]", fontsize=10)
            ax.set_ylim(0, max_Value_ActInd + y_margin_ActInd)

            # Ajustar la leyenda (Variables Evaluadas) por fuera del gráfico y ajustar el tamaño del texto
            ax.legend(ncol=1, bbox_to_anchor=(1.02,1.02,0.25,0.25), loc='center', fontsize='x-small')

            ax.grid(True, linestyle="--", alpha=0.7)

            # Guardar el gráfico en un buffer
            buffer_Energia_ActInd_Sin_Borde = BytesIO()
            plt.savefig(buffer_Energia_ActInd_Sin_Borde, format="png", dpi=100)
            buffer_Energia_ActInd_Sin_Borde.seek(0)
            plt.close(fig)

            # Cargar la imagen desde el buffer
            imagen_Energia_ActInd = Image.open(buffer_Energia_ActInd_Sin_Borde)

            # Definir el color y ancho del borde
            color_Borde = (0, 176, 80)  # Verde
            ancho_Borde = 4

            # Agregar el borde a la imagen
            imagen_Con_Borde = ImageOps.expand(imagen_Energia_ActInd, border=ancho_Borde, fill=color_Borde)

            # Guardar la imagen con borde en un nuevo buffer
            img_buffer_Energia_ActInd_Con_Borde = BytesIO()
            imagen_Con_Borde.save(img_buffer_Energia_ActInd_Con_Borde, format='png')

            # Reiniciar el puntero del nuevo buffer
            img_buffer_Energia_ActInd_Con_Borde.seek(0)

            # Mostrar la imagen en Google Colab
            print("******"*50)
            image = Image.open(img_buffer_Energia_ActInd_Con_Borde)
            st.image(image, caption="Gráficos de Energías", use_container_width=True)
            
            #display(image)
            print("******"*50)

            # Almacenar en el diccionario como InlineImage
            graficos_dict[str(dia)][f"Graf_{variables[0]}_{variables[2]}"] = InlineImage(doc, img_buffer_Energia_ActInd_Con_Borde, Cm(18))

    return graficos_dict

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# Funciones para la creación de Gráficos Dinámicos en Plotly

def graficar_Timeline_Tension_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limites=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican únicamente las líneas definidas en 'variables' y se agregan trazas adicionales para representar los límites,
    las cuales aparecen en la leyenda con sus respectivos valores.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limites (list): Lista con dos valores para límites superior e inferior, opcional.
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar trazas para los límites si se proporcionan
    if limites:
        # Calcular el rango del eje X usando los valores mínimos y máximos de la columna de fecha
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()
        
        # Agregar traza para el límite superior
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limites[0], limites[0]],
            mode='lines',
            name=f"Límite Superior ({limites[0]}), [V]",
            line=dict(color='red', dash='solid'),
            showlegend=True
        ))
        # Agregar traza para el límite inferior
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limites[1], limites[1]],
            mode='lines',
            name=f"Límite Inferior ({limites[1]}), [V]",
            line=dict(color='red', dash='solid'),
            showlegend=True
        ))
        fig.update_yaxes(range=[-30, limites[0] + 100])

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Tensión de Línea [V]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas y rotar etiquetas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_Corriente_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de corriente).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite si se proporciona
    if limite is not None:
        # Calcular el rango del eje X a partir de la columna de fechas
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()

        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Corriente Nominal ({round(limite, 2)}), [A]",
            line=dict(color='red', width=1.5),
            showlegend=True
        ))
        # Actualizar el rango del eje Y para que incluya el límite
        fig.update_yaxes(range=[-30, limite + 500])

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Corriente de Línea [A]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_DesbTension_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de referencia).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite si se proporciona
    if limite is not None:
        # Calcular el rango del eje X a partir de la columna de fechas
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()

        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Valor de Referencia ({limite}), [%]",
            line=dict(color='red', width=1.5),
            showlegend=True
        ))

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Desbalance de Tensión [%]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_DesbCorriente_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de referencia).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite, si se proporciona
    if limite is not None:
        # Calcular el rango del eje X a partir de la columna de fechas
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()

        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Valor de Referencia ({limite}), [%]",
            line=dict(color='red', width=1.5),
            showlegend=True
        ))

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Desbalance de Corriente [%]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_PQS_ActApa_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' sin límites, mostrando la evolución a lo largo del tiempo.
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'yellow']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))
    
    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Potencias",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_PQS_CapInd_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables', mostrando la evolución a lo largo del tiempo sin límites.
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'yellow']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=f"{var} [kVAR]",
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))
    
    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Potencias (kVAR)",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')
    
    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_FactPotencia_Plotly(dataFrame: pd.DataFrame, variables: list, medidas_dataFrame: dict, fecha_col: str, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y se incluye en la leyenda información extraída de 'medidas_dataFrame'
    referente a las mediciones de Factor de Potencia (por ejemplo, cantidad de positivos y ceros).
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        medidas_dataFrame (dict): Diccionario con las mediciones del DataFrame (por ejemplo, 'CANT_POSITIVOS_FP_POS', 'CANT_CEROS_FP_POS', 
                                   'CANT_POSITIVOS_FP_NEG' y 'CANT_CEROS_FP_NEG').
        fecha_col (str): Nombre de la columna de fechas (eje X).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['blue', 'red', 'green', 'yellow']

    # Construir una lista de mediciones para cada grupo (+ y -)
    # Se asume que la lista de variables tiene 2 elementos, uno para FP positivo y otro para FP negativo.
    list_Mediciones_FP = [
        [medidas_dataFrame.get('CANT_POSITIVOS_FP_POS'), medidas_dataFrame.get('CANT_CEROS_FP_POS')],
        [medidas_dataFrame.get('CANT_POSITIVOS_FP_NEG'), medidas_dataFrame.get('CANT_CEROS_FP_NEG')]
    ]

    # Graficar cada variable
    for i, var in enumerate(variables):
        # Para cada variable se incluye en el label la información de las mediciones correspondientes.
        label = f"{var}, +: ({list_Mediciones_FP[i][0]}), 0: ({list_Mediciones_FP[i][1]})"
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=label,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Factor de Potencia",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_Distorsion_Tension_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de distorsión).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite, si se proporciona
    if limite is not None:
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Distorsión Armónico de Tensión ({round(limite, 2)}), [%]",
            line=dict(color='red', width=1.5),
            showlegend=True
        ))
        fig.update_yaxes(range=[-5, limite + 5])

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Distorsión Armónica de Tensión [%]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_Distorsion_Corriente_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de distorsión).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite si se proporciona
    if limite is not None:
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Distorsión Armónica de Corriente ({round(limite, 2)})",
            line=dict(color='red', width=1.5),
            showlegend=True
        ))

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Distorsión Armónica de Corriente [%]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_CargabilidadTDD_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de Armónicos de Cargabilidad TDD).
        titulo (str): Título del gráfico.
    """
    # Calcular el valor máximo del TDD en las variables
    val_Max_TDD = dataFrame[variables].max().max()

    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=f"{var} [%]",
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite, si se proporciona
    if limite is not None:
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Armónicos de Cargabilidad TDD ({round(limite, 2)}), [%]",
            line=dict(color='red', width=1.5)
        ))
        fig.update_yaxes(range=[-5, val_Max_TDD + 10])

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="TDD [%]",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    # Formatear el eje X para mostrar fechas
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_Flicker_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' y, si se proporciona un límite, se agrega una línea horizontal.
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (float, opcional): Valor para graficar la línea horizontal (límite de Flicker PLT).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # Agregar línea horizontal para el límite, si se proporciona
    if limite is not None:
        x_min = dataFrame[fecha_col].min()
        x_max = dataFrame[fecha_col].max()
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[limite, limite],
            mode='lines',
            name=f"Límite - Flicker PLT ({round(limite, 2)})",
            line=dict(color='red', width=1.5)
        ))
        fig.update_yaxes(range=[-5, limite + 5])

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="FLICKER PLT",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100),
        xaxis=dict(tickformat='%Y-%m-%d %H:%M')
    )

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def graficar_Timeline_FactorK_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, limite=None, titulo=''):
    """
    Genera un gráfico de Plotly basado en los parámetros proporcionados y lo muestra en Streamlit.
    Se grafican las líneas definidas en 'variables' sin agregar una línea horizontal de límite.

    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos a graficar.
        variables (list): Lista de columnas a visualizar.
        fecha_col (str): Nombre de la columna de fechas (eje X).
        limite (optional): Valor para graficar la línea horizontal (no se utiliza en este caso).
        titulo (str): Título del gráfico.
    """
    # Crear figura de Plotly
    fig = go.Figure()

    # Definir colores para las líneas
    colores = ['#FFD700', 'blue', 'green', 'purple']

    # Agregar trazas para cada variable
    for i, var in enumerate(variables):
        fig.add_trace(go.Scatter(
            x=dataFrame[fecha_col],
            y=dataFrame[var],
            mode='lines',
            name=var,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.45
        ))

    # NOTA: En este caso no se grafica ninguna línea horizontal de límite.

    # Configurar el layout del gráfico
    fig.update_layout(
        title=titulo,
        xaxis_title="Fechas",
        yaxis_title="Factor K",
        legend=dict(orientation="v", x=1.02, y=1),
        margin=dict(r=100)
    )
    
    # Formatear el eje X para mostrar fechas con el formato deseado
    fig.update_xaxes(tickformat='%Y-%m-%d %H:%M')

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
def generar_Graficos_Barras_Energias_Plotly(dataFrame: pd.DataFrame, variables: list, fecha_col: str, titulo=''):
    """
    Genera y muestra en Streamlit gráficos de barras (y líneas) para cada día presente en el DataFrame.
    Se utilizan los siguientes conjuntos de variables:
      - Gráfico 1: variables[0] y variables[1] (barras) y variables[3] (línea)
      - Gráfico 2: variables[0] y variables[2] (barras) y variables[4] (línea)
    
    Args:
        dataFrame (pd.DataFrame): DataFrame con los datos.
        variables (list): Lista de columnas a graficar.
        fecha_col (str): Nombre de la columna con fecha y hora.
        titulo (str): Título base para los gráficos.
    """
    # Asegurarse de que la columna de fecha esté en formato datetime
    dataFrame[fecha_col] = pd.to_datetime(dataFrame[fecha_col], format="%Y/%m/%d %H:%M:%S", errors='coerce')
    
    # Extraer los días únicos
    dias = dataFrame[fecha_col].dt.date.unique()
    
    for dia in dias:
        dia_data = dataFrame[dataFrame[fecha_col].dt.date == dia]
        # Extraer información de la fecha para el título
        year = dia_data[fecha_col].dt.year.iloc[0]
        month_name = dia_data[fecha_col].dt.strftime("%B").iloc[0]
        day_number = dia_data[fecha_col].dt.day.iloc[0]
        
        # Formatear los valores de fecha para el eje X
        x_values = dia_data[fecha_col].dt.strftime("%d/%m/%y %H:%M:%S")
        
        # Gráfico 1: variables[0] y variables[1] (barras) y variables[3] (línea)
        if len(variables) >= 4:
            fig1 = go.Figure()
            
            # Agregar barra para variable[0]
            fig1.add_trace(go.Bar(
                x=x_values,
                y=dia_data[variables[0]],
                name=f"{variables[0]}",
                marker_color='#66BB6A',
                text=dia_data[variables[0]].round(1),
                textposition='auto'
            ))
            
            # Agregar barra para variable[1]
            fig1.add_trace(go.Bar(
                x=x_values,
                y=dia_data[variables[1]],
                name=f"{variables[1]}",
                marker_color='#AB47BC',
                text=dia_data[variables[1]].round(1),
                textposition='auto'
            ))
            
            # Agregar línea para variable[3]
            fig1.add_trace(go.Scatter(
                x=x_values,
                y=dia_data[variables[3]],
                mode='lines+markers+text',
                name=f"{variables[3]}",
                line=dict(color='red', width=1),
                text=dia_data[variables[3]].apply(lambda x: f"{x:.3f}%"),
                textposition='top center'
            ))
            
            fig1.update_layout(
                title=f"REGISTROS DE ENERGÍA ({variables[0]}) Y ENERGÍA ({variables[1]}) - {day_number} de {month_name} del {year}",
                xaxis_title="Hora del Día",
                yaxis_title="Valores [kWh - kVARh]",
                barmode='group',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: variables[0] y variables[2] (barras) y variables[4] (línea)
        if len(variables) >= 5:
            fig2 = go.Figure()
            
            # Agregar barra para variable[0]
            fig2.add_trace(go.Bar(
                x=x_values,
                y=dia_data[variables[0]],
                name=f"{variables[0]}",
                marker_color='#66BB6A',
                text=dia_data[variables[0]].round(1),
                textposition='auto'
            ))
            
            # Agregar barra para variable[2]
            fig2.add_trace(go.Bar(
                x=x_values,
                y=dia_data[variables[2]],
                name=f"{variables[2]}",
                marker_color='#FFA726',
                text=dia_data[variables[2]].round(1),
                textposition='auto'
            ))
            
            # Agregar línea para variable[4]
            fig2.add_trace(go.Scatter(
                x=x_values,
                y=dia_data[variables[4]],
                mode='lines+markers+text',
                name=f"{variables[4]}",
                line=dict(color='red', width=1),
                text=dia_data[variables[4]].apply(lambda x: f"{x:.3f}%"),
                textposition='top center'
            ))
            
            fig2.update_layout(
                title=f"REGISTROS DE ENERGÍA ({variables[0]}) Y ENERGÍA ({variables[2]}) - {day_number} de {month_name} del {year}",
                xaxis_title="Hora del Día",
                yaxis_title="Valores [kWh - kVARh]",
                barmode='group',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        
def crear_grafico(df):
    """
    Crea un gráfico interactivo de líneas a partir del DataFrame.
    - Se asume que la primera columna es la fecha.
    - Permite al usuario seleccionar dinámicamente las columnas a graficar.
    - Retorna un buffer con la imagen del gráfico.
    """
    
    df_total = df.copy()
    
    # Suponemos que la primera columna es la fecha
    fecha_columna = df_total.columns[0]
    
    # Selección dinámica de columnas (excluyendo la columna de fecha)
    columnas_disponibles = df_total.columns[1:].tolist()
    columnas_seleccionadas = st.multiselect("Selecciona las columnas a graficar", 
                                            columnas_disponibles, 
                                            default=columnas_disponibles[:min(3, len(columnas_disponibles))])
    if not columnas_seleccionadas:
        st.warning("Selecciona al menos una columna para graficar.")
        return None

    fig = go.Figure()
    for col in columnas_seleccionadas:
        fig.add_trace(go.Scatter(
            x=df_total[fecha_columna],
            y=df_total[col],
            mode='lines',
            name=col
        ))

    fig.update_layout(
        title='Series Temporales',
        xaxis_title='Fecha y Hora',
        yaxis_title='Valor',
        legend=dict(
            orientation="v",
            x=1.02,
            y=1.02,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=150, t=50, b=50)
    )
    
    st.plotly_chart(fig)