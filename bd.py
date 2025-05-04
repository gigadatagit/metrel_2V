import pandas as pd
import os
import streamlit as st
import datetime as dt
import psycopg2
from sqlalchemy import create_engine, text
from configparser import ConfigParser

DB_USERNAME=st.secrets.database.DB_USERNAME
DB_PASSWORD=st.secrets.database.DB_PASSWORD
DB_URL=st.secrets.database.DB_URL
DB_PORT=st.secrets.database.DB_PORT
DB_NAME=st.secrets.database.DB_NAME

# Definición de la función para obtener la cadena de conexión a la base de datos
def get_engine():
    return create_engine(f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_URL}:{int(DB_PORT)}/{DB_NAME}')

# Función para ejecutar consultas y devolver resultados en un DataFrame usando SQLAlchemy
def query_to_df(query, params=None):
    engine = get_engine()
    # Utilizamos un bloque "with" para asegurar el cierre de la conexión
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df

def execute_query(query, params=None):
    engine = get_engine()
    # Usamos engine.begin() para manejar la transacción automáticamente
    with engine.begin() as connection:
        # La función text() es necesaria para construir una consulta SQL al estilo SQLAlchemy.
        connection.execute(text(query), params or {})
        
        
# Funciones CRUD para la tabla

# CRUD para Usuario
def get_usuarios():
    return query_to_df("SELECT * FROM info_usuario WHERE activo='S';")

def create_usuario(nombre_completo, numero_celular, correo_electronico, numero_documento, id_tipo_documento, id_proyecto, id_rol):
    query = "INSERT INTO info_usuario (nombre_completo, numero_celular, correo_electronico, numero_documento, id_tipo_documento, id_proyecto, id_rol) VALUES (:nombre_completo, :numero_celular, :correo_electronico, :numero_documento, :id_tipo_documento, :id_proyecto, :id_rol)"
    execute_query(query,{"nombre_completo": nombre_completo, "numero_celular": numero_celular, "correo_electronico": correo_electronico, "numero_documento": numero_documento, "id_tipo_documento": id_tipo_documento, "id_proyecto": id_proyecto, "id_rol": id_rol})

def update_usuario(id_usuario, nuevo_nombre_completo, nuevo_numero_celular, nuevo_correo_electronico, nuevo_numero_documento, nuevo_id_tipo_documento, nuevo_id_proyecto, nuevo_id_rol):
    query= "UPDATE info_usuario SET nombre_completo = :nuevo_nombre_completo, numero_celular = :nuevo_numero_celular, correo_electronico = :nuevo_correo_electronico, numero_documento = :nuevo_numero_documento, id_tipo_documento = :nuevo_id_tipo_documento, id_proyecto = :nuevo_id_proyecto, id_rol = :nuevo_id_rol WHERE id_usuario = :id_usuario"
    execute_query(query, {"nuevo_nombre_completo": nuevo_nombre_completo, "nuevo_numero_celular": nuevo_numero_celular, "nuevo_correo_electronico": nuevo_correo_electronico, "nuevo_numero_documento": nuevo_numero_documento, "nuevo_id_tipo_documento": nuevo_id_tipo_documento, "nuevo_id_proyecto": nuevo_id_proyecto, "nuevo_id_rol": nuevo_id_rol, "id_usuario": id_usuario})

def delete_usuario(id_usuario):
    query = "UPDATE info_usuario SET activo = 'N' WHERE id_usuario = :id_usuario"
    execute_query(query, {"id_usuario": id_usuario})