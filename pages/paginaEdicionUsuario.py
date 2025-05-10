import streamlit as st
import login as login
import re
from bd import query_to_df, update_usuario

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    st.subheader('Información | :orange[Edición de Usuarios]')
    
    # Obtener usuarios
    
    query_Usuarios = """
        SELECT * 
        FROM info_usuario infusr 
        INNER JOIN tipos_documento tdc ON 
            tdc.id_tipo_documento = infusr.id_tipo_documento
        INNER JOIN info_proyecto infpry ON
            infpry.id_proyecto = infusr.id_proyecto
        INNER JOIN info_roles infrol ON
            infrol.id_rol = infusr.id_rol
        WHERE infusr.activo = 'S';
    """
    
    usuarios_df = query_to_df(query_Usuarios)
    nombres_usuarios = usuarios_df["nombre_completo"].tolist()

    usuario_seleccionado = st.selectbox("Selecciona un usuario para editar:", nombres_usuarios)

    # Obtener el ID del usuario seleccionado
    id_usuario_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "id_usuario"
    ].values[0]
    
    # Obtener el Número de Celular del usuario seleccionado
    numero_celular_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "numero_celular"
    ].values[0]
    
    # Obtener el Correo Electrónico del usuario seleccionado
    correo_electronico_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "correo_electronico"
    ].values[0]
    
    # Obtener el Número de Documento del usuario seleccionado
    numero_documento_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "numero_documento"
    ].values[0]
    
    # Obtener el ID del Tipo de Documento del usuario seleccionado
    id_tipo_documento_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "id_tipo_documento"
    ].values[0][0]
    
    # Obtener el ID del Rol del usuario seleccionado
    id_rol_seleccionado = usuarios_df.loc[
        usuarios_df["nombre_completo"] == usuario_seleccionado, "id_rol"
    ].values[0][0]

    # Crear el formulario de edición
    st.subheader(":orange[Editar información del usuario]")
    
    # Campos de entrada con valores actuales
    nuevo_nombre_completo = st.text_input("Nombre completo:", value=usuario_seleccionado)
    nuevo_numero_celular = st.text_input("Número de celular:", value=numero_celular_seleccionado)
    nuevo_correo_electronico = st.text_input("Correo electrónico:", value=correo_electronico_seleccionado)
    nuevo_numero_documento = st.text_input("Número de documento:", value=numero_documento_seleccionado)

    # Validar número de documento y número de celular
    patron_documento = r"^[0-9]+$"
    patron_celular = r"^[0-9]+$"
    
    if not re.match(patron_documento, nuevo_numero_documento):
        st.error("Por favor, ingrese solo números en el número de documento.")
    elif not re.match(patron_celular, nuevo_numero_celular):
        st.error("Por favor, ingrese solo números en el número de celular.")
    else:
        st.success("Datos válidos.")

    # Dropdown para seleccionar tipo de documento
    tipos_documento_df = query_to_df("SELECT id_tipo_documento, descripcion FROM tipos_documento WHERE activo='S';")
    
    
    
    descripcion_tipo_documento_actual = tipos_documento_df.loc[
        tipos_documento_df["id_tipo_documento"] == id_tipo_documento_seleccionado, "descripcion"
    ].values[0]

    tipo_documento_seleccionado = st.selectbox(
        "Tipo de documento:",
        tipos_documento_df["descripcion"].tolist(),
        index=int(tipos_documento_df[tipos_documento_df["descripcion"] == descripcion_tipo_documento_actual].index[0])
    )
    
    nuevo_id_tipo_documento = tipos_documento_df.loc[
        tipos_documento_df["descripcion"] == tipo_documento_seleccionado, "id_tipo_documento"
    ].values[0]



    # Dropdown para seleccionar rol
    roles_df = query_to_df("SELECT id_rol, nombre_rol FROM info_roles WHERE activo='S';")
    
    
    
    nombre_rol_actual = roles_df.loc[
        roles_df["id_rol"] == id_rol_seleccionado, "nombre_rol"
    ].values[0]
    
    rol_seleccionado = st.selectbox(
        "Rol del usuario:",
        roles_df["nombre_rol"].tolist(),
        index=int(roles_df[roles_df["nombre_rol"] == nombre_rol_actual].index[0])
    )
    
    nuevo_id_rol = roles_df.loc[
        roles_df["nombre_rol"] == rol_seleccionado, "id_rol"
    ].values[0]

    # Botón para actualizar usuario
    if st.button("Actualizar usuario"):
        if nuevo_nombre_completo and nuevo_numero_celular and nuevo_correo_electronico and nuevo_numero_documento:
            update_usuario(
                int(id_usuario_seleccionado), 
                nuevo_nombre_completo, 
                nuevo_numero_celular, 
                nuevo_correo_electronico, 
                nuevo_numero_documento,
                int(nuevo_id_tipo_documento), 
                int(nuevo_id_rol)
            )
            st.success("Usuario actualizado correctamente.")
            st.balloons()
            st.rerun()
        else:
            st.error("Por favor, completa todos los campos.")