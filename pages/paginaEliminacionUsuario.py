import streamlit as st
import login as login

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    st.header('Información | :orange[Página de Eliminación de Usuario]')
    
    uploaded_file = st.file_uploader("Elige un archivo de Parquet", type=["parquet"])