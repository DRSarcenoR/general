# Módulo 1 de Librería de Utilidades
# 
# Funciones de manejo y manipulacion de texto
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
import numpy as np

# apoyo
from datetime import datetime, timedelta
import time
import warnings
import locale
import time

# manipulacion y manejo de texto
import re
import unicodedata

# archivos del sistema
import os

# APIs o PseudoAPIs
import win32com.client as win32
# ------------------------------>




class text_management:
    def __init__(self) -> None:
        pass
    
    # APLICADO A CADENAS DE TEXTO
    def eliminar_etiquetas_html(self, texto : str) -> str:
        # Usamos una expresión regular para buscar y eliminar etiquetas HTML
        texto_limpio = re.sub(r'<.*?>', '', texto)
        return texto_limpio

    def limpiar_texto(self, texto : str) -> str:
        # Eliminar caracteres especiales o no alfanuméricos
        return re.sub(r'[^A-Za-z0-9 ]+', '', texto)
    
    def no_imprimibles(self, value : str) -> str:
        # elimina caracteres no imprimibles
        if isinstance(value, str):
            return ''.join(c for c in value if c.isprintable())
        return value
    
    def remove_unsupported_characters(self, text : str):
        return re.sub(r'[^\x00-\x7F]+', '', text)
    


class data_text_management:
    def __init__(self) -> None:
        pass

    # APLICANDO A COLUMNAS DE UN DATAFRAME (pandas en su v1)
    # Función para eliminar etiquetas HTML de una columna
    def eliminar_etiquetas_html(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'<.*?>', '', x) if isinstance(x, str) else x)
        return df

    # Función para limpiar caracteres especiales de una columna
    def limpiar_texto(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'[^\w\s]', '', x) if isinstance(x, str) else x)
        return df
    
    # ------------->
    # correción de funcion para limpiar caracteres especiales
    def caracteres_especiales(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'[^\w\s]', ' ', x) if isinstance(x, str) else x)
        return df

    def espacios_extra(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'\s+', ' ', x).strip() if isinstance(x, str) else x)
        return df
    # ------------->
    def convertir_minusculas_y_quitar_tildes(self, df: pd.DataFrame, col_in: str | int, col_out: str | int) -> pd.DataFrame:
        def normalizar(texto):
            if isinstance(texto, str):
                # Elimina las tildes
                texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
                # Convierte a minúsculas
                texto = texto.lower()
                return texto
            return texto

        df[col_out] = df[col_in].apply(normalizar)
        return df
    # ------------->

    def rating(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        conditions = [
            (df[col_in] >= 0) & (df[col_in] < 4),
            (df[col_in] >= 4) & (df[col_in] <= 6),
            (df[col_in] > 6) & (df[col_in] <= 10)]
        labels = ['Mala', 'Pasable/Normal', 'Buena']
        df[col_out] = np.select(conditions, labels, default=np.nan)
        return df
    
    def cleaning_pipeline(self, df : pd.DataFrame, col_in : str, col_out : str) -> pd.DataFrame:
        result = (df
              .pipe(self.eliminar_etiquetas_html, col_in, col_out)
              .pipe(self.caracteres_especiales, col_out, col_out)
              .pipe(self.espacios_extra, col_out, col_out))
        return result
