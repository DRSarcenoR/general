# Módulo 1 de Librería de Utilidades
# 
# Funciones de Generales
# 
# Autor: Diego Sarceño
# Contacto: dsarceno68@gmail.com | diego.sarceno@chn.com.gt
# Tel: (+502) 4204 4629
# 
# 
# ------------------------------>
# paquetes necesarios
import json
import pandas as pd
import pyodbc
import warnings
import sqlite3
import locale
from datetime import datetime
import os
from sqlalchemy import create_engine
import importlib.resources as pkg_resources
import time
import importlib.resources
# ------------------------------>


class Connections:
    def __init__(self):
        pass

    def connection(self, query : str, db : int) -> pd.DataFrame:
        '''Selecciona la base de datos 1: Banco, 2: Seguros'''
        warnings.filterwarnings('ignore')

        # seleccionamos la base
        select_db = {1: 'Banco',
        2: 'Seguros'}
        selected_db = select_db.get(db)

        # abrimos el json con las credenciales e informacion
        with open('../credentials.json') as cred:
            credenciales = json.load(cred)
        
        # intentamos hacer la conexion
        try:
            conexion = pyodbc.connect(
                driver = credenciales['DW'][selected_db]['driver'],
                server = credenciales['DW'][selected_db]['server'],
                database = credenciales['DW'][selected_db]['database'],
                port = credenciales['DW'][selected_db]['port'],
                trusted_connection='yes'
            )

            # realizamos la solicitud a la base
            df = pd.read_sql_query(query, conexion)
        except Exception as e:
            print(f'Error: {e}')
            return None
        finally:
            if 'conexion' in locals():
                conexion.close()
        return df



class Scrapping:
    def __init__(self):
        pass



