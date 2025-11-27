import streamlit as st
import login as login
import io
from io import BytesIO

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    st.header('Información | :orange[Página Principal]')
    
    st.markdown("""
    # 🚀 **:orange[Plataforma Integral de Gestión de Datos - Metrel 2V]**
    Bienvenid@ a **Plataforma Integral de Gestión de Datos - Metrel 2V**, la herramienta diseñada para **automatizar**, **transformar** y **visualizar** información de manera eficiente. 📊✨  

    ### 🔑 **Características principales**
    - **📥 Procesamiento avanzado de datos:** Carga archivos en formato Parquet y optimiza la transformación y gestión de información.
    - **📄 Generación automatizada de informes:** Convierte datos en documentos Word y Excel estructurados, reduciendo tiempos de elaboración a solo **3 minutos**.
    - **📊 Visualización dinámica:** Explora gráficos interactivos con Plotly para analizar tendencias y tomar decisiones informadas en tiempo real.

    ### 🎯 **Nuestro objetivo**
    Ofrecerte una solución **todo-en-uno** que simplifique la administración de datos, mejore el análisis y potencie la productividad.  

    #### 🔍 **¡Transforma tus datos en conocimiento con eficiencia y precisión!**
    """)
