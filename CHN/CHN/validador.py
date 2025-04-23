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
        pass


    def validar_sin_nulos(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
        for col in columnas:
            if df[col].isnull().any():
                raise ValueError(f"Columna {col} contiene valores nulos")
        
        return df
    
    def validar_esquema_generico(df: pd.DataFrame, columnas: dict) -> pd.DataFrame:
        schema_dict = {col: Column(dtype) for col, dtype in columnas.items()}
        schema = DataFrameSchema(schema_dict)
        return schema.validate(df)