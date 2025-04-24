# Módulo 4 de Librería de Utilidades
# 
# Validador de información
# 
# Autor: Diego Sarceño
# Contacto: dsarceno68@gmail.com | diego.sarceno@chn.com.gt
# Tel: (+502) 4204 4629
# 
# 
# ------------------------------>
# <---- paquetes necesarios ---->

# analisis
import pandas as pd
import pandera as pa
import numpy as np
import math
from pandera import Column, DataFrameSchema, Check


# graficas
import matplotlib.pyplot as plt
import seaborn as sns

# apoyo
from datetime import datetime, timedelta
import time
import re
import warnings
import locale
import time
from dotenv import load_dotenv

# archivos del sistema
import os
# ------------------------------>



class Validador:
    def __init__(self) -> None:
        """
        Inicializa una instancia de la clase Validador.
        
        :returns: None
        """
        pass


    def validar_sin_nulos(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
        """
        Valida que no existan valores nulos en las columnas especificadas de un DataFrame.

        :param df: DataFrame que contiene los datos a validar.
        :type df: pd.DataFrame
        :param columnas: Lista de nombres de las columnas a verificar.
        :type columnas: list
        :raises ValueError: Si alguna de las columnas contiene valores nulos.
        :returns: El DataFrame original si no hay valores nulos en las columnas especificadas.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            validador = Validador()
            df = pd.DataFrame({"col1": [1, 2, None], "col2": [3, 4, 5]})
            try:
                validador.validar_sin_nulos(df, ["col1", "col2"])
            except ValueError as e:
                print(e)  # Salida: Columna col1 contiene valores nulos
        """
        for col in columnas:
            if df[col].isnull().any():
                raise ValueError(f"Columna {col} contiene valores nulos")
        
        return df
    
    def validar_esquema_generico(df: pd.DataFrame, columnas: dict) -> pd.DataFrame:
        """
        Valida el esquema de un DataFrame comparando las columnas con sus tipos de datos esperados.

        :param df: DataFrame que contiene los datos a validar.
        :type df: pd.DataFrame
        :param columnas: Diccionario donde las claves son los nombres de las columnas
                         y los valores son los tipos de datos esperados para cada columna.
        :type columnas: dict
        :returns: El DataFrame validado si cumple con el esquema especificado.
        :rtype: pd.DataFrame
        :raises: DataFrameSchemaError: Si el DataFrame no cumple con el esquema.
        :example:

        .. code-block:: python

            from pandas_schema import Column
            validador = Validador()
            df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
            try:
                columnas = {"col1": int, "col2": str}
                validador.validar_esquema_generico(df, columnas)
            except DataFrameSchemaError as e:
                print(e)
        """
        schema_dict = {col: Column(dtype) for col, dtype in columnas.items()}
        schema = DataFrameSchema(schema_dict)
        return schema.validate(df)