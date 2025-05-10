import streamlit as st
import login as login
import re
from bd import query_to_df, create_usuario

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    
    patron_documento = r"^[0-9]+$"
    patron_celular = r"^[0-9]+$"
    
    st.subheader('Información | :orange[Página de Registro de Usuario]')
        
    # Campos de entrada
    nombre_completo = st.text_input("Nombre completo:")
    numero_celular = st.text_input("Número de celular:")
    correo_electronico = st.text_input("Correo electrónico:")
    numero_documento = st.text_input("Número de documento:")

    # Dropdown para seleccionar tipo de documento
    tipos_documento_df = query_to_df("SELECT id_tipo_documento, descripcion FROM tipos_documento WHERE activo='S';")
    tipo_documento_seleccionado = st.selectbox(
        "Tipo de documento:",
        tipos_documento_df["descripcion"].tolist()
    )
    id_tipo_documento = tipos_documento_df.loc[
        tipos_documento_df["descripcion"] == tipo_documento_seleccionado, "id_tipo_documento"
    ].values[0]

    # Dropdown para seleccionar rol
    roles_df = query_to_df("SELECT id_rol, nombre_rol FROM info_roles WHERE activo='S';")
    rol_seleccionado = st.selectbox(
        "Rol del usuario:",
        roles_df["nombre_rol"].tolist()
    )
    id_rol = roles_df.loc[
        roles_df["nombre_rol"] == rol_seleccionado, "id_rol"
    ].values[0]
    


    if re.match(patron_documento, numero_documento):
        st.success(f"Número de documento válido: {numero_documento}")
        # Procesar el número de documento
    else:
        st.error("Por favor, ingrese solo números en el número de documento.")
            
    if re.match(patron_celular, numero_celular):
        st.success(f"Número de celular válido: {numero_celular}")
        # Procesar el número de celular
    else:
        st.error("Por favor, ingrese solo números en el número de celular.")

    # Botón para registrar usuario
    if st.button("Registrar usuario"):
        if nombre_completo and numero_celular and correo_electronico and numero_documento:
            create_usuario(nombre_completo, numero_celular, correo_electronico, numero_documento, int(id_tipo_documento), int(id_rol))
            st.success("Usuario registrado exitosamente.")
            st.balloons()
            st.rerun()
        else:
            st.error("Por favor, completa todos los campos.")