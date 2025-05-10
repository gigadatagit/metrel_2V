import streamlit as st
import login as login
import time
from bd import query_to_df, delete_usuario

archivo = __file__.split("/")[-1]
login.generarLogin(archivo)
if 'correo_electronico' in st.session_state:
    
    st.subheader('Información | :orange[Eliminación de Usuario]')

    df_Listado_Usuarios = query_to_df("SELECT * FROM info_usuario WHERE activo = 'S';")

    nombres_usuarios = df_Listado_Usuarios["nombre_completo"].tolist()

    usuario_seleccionado = st.selectbox("Seleccione un usuario para eliminar:", nombres_usuarios)

    # Obtener el ID del asunto seleccionado
    id_usuario_seleccionado = df_Listado_Usuarios.loc[
        df_Listado_Usuarios["nombre_completo"] == usuario_seleccionado, "id_usuario"
    ].values[0]

    if st.button("Eliminar usuario"):
        delete_usuario(int(id_usuario_seleccionado))
        st.success(f"El usuario '{usuario_seleccionado}' ha sido eliminado correctamente.")
        st.balloons()
        
        time.sleep(3)
        st.rerun()