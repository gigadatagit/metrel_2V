# Importamos las librerías necesarias
import streamlit as st  # Librería para crear aplicaciones web interactivas. Instalación: pip install streamlit
import pandas as pd  # Librería para manipulación y análisis de datos. Instalación: pip install pandas
import os
import random
from bd import query_to_df
from mailjet_rest import Client
#from streamlit_cookies_controller import CookieController # Librería para manejar cookies en Streamlit. Instalación: pip install streamlit-cookies-controller

# Creamos una instancia de CookieController
#controller = CookieController()

# Validación simple de usuario y clave con un archivo csv

# Función para enviar el correo con el código de verificación vía Mailjet 
def enviar_codigo_mailjet(destinatario, nombre_destinatario, codigo_verificacion): 
    """ 
    Envía un correo utilizando Mailjet, mostrando el código de verificación en un formato HTML. 
    """ 
    # Configuración de Mailjet desde los secretos 
    api_key = st.secrets.mailjet.apikeyPublic 
    api_secret = st.secrets.mailjet.apikeyPrivate 
    mailjet = Client(auth=(api_key, api_secret), version='v3.1') 
     
    mensaje = "Estimad@ Usuari@, en el siguiente correo encontrará el código de acceso para la App." 
    # Si el código es una cadena de 6 dígitos, lo convertimos en lista para mostrar cada dígito en una caja 
    listado_Codigo = [d for d in codigo_verificacion] 
     
    mensaje_HTML = f""" 
    <html> 
    <head> 
        <style> 
            body {{ 
                font-family: Arial, sans-serif; 
                background-color: #f2f2f2; 
                padding: 20px; 
                margin: 0; 
            }} 
            .container {{ 
                max-width: 500px; 
                margin: auto; 
                background: #fff; 
                padding: 30px; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); 
                text-align: center; 
            }} 
            h1 {{ 
                margin-bottom: 20px; 
                font-size: 24px; 
                color: #333; 
            }} 
            .verification-boxes {{ 
                display: inline-flex; 
                gap: 10px; 
            }} 
            .box {{ 
                width: 40px; 
                height: 40px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 24px; 
                font-weight: bold; 
                color: #333; 
                border: 2px solid #ddd; 
                border-radius: 4px; 
                background-color: #f9f9f9; 
            }} 
        </style> 
    </head> 
    <body> 
        <div class="container"> 
          <h1>Código de Verificación</h1> 
          <div class="verification-boxes"> 
              <div class="box">{listado_Codigo[0]}</div> 
              <div class="box">{listado_Codigo[1]}</div> 
              <div class="box">{listado_Codigo[2]}</div> 
              <div class="box">{listado_Codigo[3]}</div> 
              <div class="box">{listado_Codigo[4]}</div> 
              <div class="box">{listado_Codigo[5]}</div> 
          </div> 
        </div> 
    </body> 
    </html> 
    """ 
     
    data = { 
      'Messages': [ 
                    { 
                        "From": { 
                            "Email": "juan.vergara@mejiaacevedo.com.co", 
                            "Name": "Juan Daniel Vergara" 
                        }, 
                        "To": [ 
                                { 
                                    "Email": destinatario, 
                                    "Name": nombre_destinatario 
                                } 
                        ], 
                        "Subject": "Código de Autenticación | Tableros Power BI App", 
                        "TextPart": mensaje, 
                        "HTMLPart": mensaje_HTML 
                    } 
            ] 
    } 
 
    result = mailjet.send.create(data=data) 
    if result.status_code in [200, 201]: 
        st.info("Correo enviado exitosamente.") 
    else: 
        st.error("Fallo al enviar el correo.")

def validarUsuario(usuario,clave):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """    
    # Leemos la tabla con los usuarios y claves
    dfusuarios = query_to_df("SELECT * FROM viewinfousuarios;")
    
    # Filtramos el dataframe para buscar el usuario y la clave
    if len(dfusuarios[(dfusuarios['correo_electronico']==usuario) & (dfusuarios['numero_documento']==clave)])>0:
        # Si el usuario y la clave existen, retornamos True
        return True
    else:
        # Si el usuario o la clave no existen, retornamos False
        return False

# Generación de menú según el usuario y el rol se maneja desde el código
def generarMenu(usuario):
    """Genera el menú dependiendo del usuario y el rol

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar: # Creamos una barra lateral para el menú
        
        # Cargamos la tabla de usuarios
        dfusuarios = query_to_df("SELECT * FROM viewinfousuarios;")
        # Filtramos la tabla de usuarios por el usuario actual
        dfUsuario =dfusuarios[(dfusuarios['correo_electronico']==usuario)]
        # Cargamos el nombre del usuario
        nombre= dfUsuario['nombre_completo'].values[0]
        
        # Cargamos el rol
        rol= dfUsuario['rol'].values[0]
        #Mostramos el nombre del usuario
        st.write(f"Bienvenid@ **:blue-background[{nombre}]**") # Mostramos el nombre del usuario con formato
        st.caption(f"Rol: **:red-background[{rol}]**") # Mostramos el rol del usuario
        # Mostramos los enlaces de páginas
        st.page_link("home.py", label="Inicio", icon=":material/home:") # Enlace a la página de inicio
        st.subheader("Menú de Navegación - **:red-background[Metrel 2V]**") # Subtítulo para los tableros
        # Mostramos los enlaces a las páginas según el rol del usuario
        if rol in ['admin','informes']:
            st.page_link("pages/paginaCalidadEnergia.py", label="Informes | Calidad de Energía", icon=":material/add_notes:") # Enlace a la página de ventas        
        if rol in ['admin','informes']:
            st.page_link("pages/paginaCargabilidad.py", label="Informes | Cargabilidad", icon=":material/add_notes:") # Enlace a la página de compras
        if rol in ['admin','informes']:
            st.page_link("pages/paginaGraficosDinamicos.py", label="Informes | Gráficos Dinámicos", icon=":material/monitoring:") # Enlace a la página de personal   
        
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir") # Creamos un botón para salir
        if btnSalir: # Si se presiona el botón

            st.session_state.clear() # Limpiamos las variables de sesión
            
            # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            st.rerun() # Reiniciamos la aplicación


# Validación de acceso a la página según los roles del usuario
def validarPagina(pagina,usuario):
    """Valida si el usuario tiene permiso para acceder a la página

    Args:
        pagina (str): página a validar
        usuario (str): usuario a validar

    Returns:
        bool: True si tiene permiso, False si no tiene permiso
    """
    # Cargamos la información de usuarios y roles
    dfusuarios = query_to_df("SELECT * FROM viewinfousuarios;")
    
    dfPaginas = query_to_df("SELECT * FROM info_paginas_metrel;")
    
    dfUsuario = dfusuarios[(dfusuarios['correo_electronico']==usuario)]

    rol = dfUsuario['nombre_rol'].values[0]
    dfPagina = dfPaginas[(dfPaginas['pagina'].str.contains(pagina))]
    
    # Validamos si el rol del usuario tiene acceso a la página
    if len(dfPagina)>0:
        if rol in dfPagina['roles'].values[0] or rol == "Administrador" or st.secrets.permisos.tipoPermiso=="rol":
            return True # El usuario tiene permiso
        else:
            return False # El usuario no tiene permiso
    else:
        return False # La página no existe en el archivo de permisos

# Generación de menú según el usuario y el rol se maneja desde un archivo csv
def generarMenuRoles(usuario):
    """Genera el menú dependiendo del usuario y el rol asociado a la página

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar: # Menú lateral
        # Cargamos la tabla de usuarios y páginas
        dfusuarios = query_to_df("SELECT * FROM viewinfousuarios;")
        dfPaginas = query_to_df("SELECT * FROM info_paginas_metrel ORDER BY id_pagina ASC;")

        # Filtramos la tabla de usuarios por el usuario actual
        dfUsuario =dfusuarios[(dfusuarios['correo_electronico']==usuario)]
        # Obtenemos el nombre y rol del usuario
        nombre = dfUsuario['nombre_completo'].values[0]
        rol = dfUsuario['nombre_rol'].values[0]
    
        #Mostramos el nombre del usuario
        st.write(f"Bienvenid@ **:blue-background[{nombre}]** ")
        st.caption(f"Rol: **:red-background[{rol}]**")
        # Mostramos los enlaces de páginas        
        st.subheader("Opciones")
        # Verificamos si se deben ocultar o deshabilitar las opciones del menú
        if st.secrets.permisos.ocultarOpciones=="True": # Verificamos el valor del secreto "ocultarOpciones"
            if rol!='Administrador': # Si el rol no es admin
                # Filtramos la tabla de páginas por el rol actual
                dfPaginas = dfPaginas[dfPaginas['roles'].apply(lambda roles_str: rol in roles_str.split('|'))]

            # Ocultamos las páginas que no tiene permiso
            for index, row in dfPaginas.iterrows():
                icono=row['icono']            
                st.page_link(row['pagina'], label=row['nombre'], icon=f":material/{icono}:")  # Mostramos la página  
        else: # Si no se ocultan las opciones
            # Deshabilitamo las páginas que no tiene permiso            
            for index, row in dfPaginas.iterrows():
                deshabilitarOpcion = True  # Valor por defecto para deshabilitar las opciones
                if rol in row["roles"] or rol == "Administrador": # Verificamos el rol
                    deshabilitarOpcion = False # Habilitamos la página si el usuario tiene permiso
                
                icono=row['icono']            
                # Mostramos el enlace de la página, deshabilitado o no según el permiso.
                st.page_link(row['pagina'], label=row['nombre'], icon=f":material/{icono}:",disabled=deshabilitarOpcion)         
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir")
        if btnSalir:
            st.session_state.clear()
            # controller.remove('correo_electronico')
            st.rerun()

# Generación de la ventana de login y carga de menú
def generarLogin(archivo):
    """
    Flujo de login con dos pasos:
    1. Validación de usuario y contraseña.
    2. Verificación del código enviado vía correo.
    """
    # Si ya se ha completado la verificación, se carga el menú y la página
    if 'correo_electronico' in st.session_state:

        if st.secrets.permisos.tipoPermiso == "rolpagina":

            generarMenuRoles(st.session_state['correo_electronico'])

        else:

            generarMenu(st.session_state['correo_electronico'])

        if not validarPagina(archivo, st.session_state['correo_electronico']):

            st.error(f"No tiene permisos para acceder a esta página {archivo}")
            st.stop()

    else:

    # Si ya se enviaron las credenciales y el código al correo, mostramos el campo para verificarlos.
        if 'pending_user' in st.session_state:

            st.info("Hemos enviado un correo con el código de verificación. Ingresa el código a continuación:")
            codigo_ingresado = st.text_input("Código de Verificación:")

            if st.button("Verificar código"):

                if codigo_ingresado == st.session_state.get('verification_code'):

                    # El código es correcto: finalizamos el login
                    st.session_state['correo_electronico'] = st.session_state.pop('pending_user')
                    st.success("¡Código verificado exitosamente! Ahora puedes acceder a las páginas.")
                    st.rerun()

                else:

                    st.error("Código incorrecto. Por favor, intenta nuevamente.")

            return # Finalizamos aquí para que no se muestre el formulario de usuario/clave.
    
        # Formulario inicial de login: se solicitan usuario y contraseña.
        with st.form('frmLogin'):

            parUsuario = st.text_input('Usuario (Correo electrónico)')
            parPassword = st.text_input('Password (Nro. Documento)', type='password')
            btnLogin = st.form_submit_button('Ingresar', type='primary')
    
            if btnLogin:

                if validarUsuario(parUsuario, parPassword):

                    # Credenciales correctas: generamos el código de verificación
                    codigo_verificacion = ''.join(random.choices("0123456789", k=6))
                    
                    st.session_state['pending_user'] = parUsuario
                    st.session_state['verification_code'] = codigo_verificacion
                    # Envío del correo mediante Mailjet:
                    # Aquí usamos el correo ingresado como destinatario y, en este ejemplo, el nombre será el mismo;
                    # puedes adaptar esto si cuentas con el nombre real del usuario.
                    enviar_codigo_mailjet(parUsuario, parUsuario, codigo_verificacion)

                    st.info("Se ha enviado un código de verificación a tu correo. Ingresa el código en el campo superior.")

                    st.rerun()

            else:

                st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")
