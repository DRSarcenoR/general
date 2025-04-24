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
# ------------------------------>




class text_management:
    
    def __init__(self) -> None:
        """
        Inicializa una instancia de la clase text_management.
        
        :returns: None
        """
        pass
    
    # APLICADO A CADENAS DE TEXTO
    def eliminar_etiquetas_html(self, texto : str) -> str:
        """
        Elimina las etiquetas HTML de un texto dado.

        :param texto: Cadena de texto con posibles etiquetas HTML.
        :type texto: str
        :returns: El texto limpio sin etiquetas HTML.
        :rtype: str
        :example:
        
        .. code-block:: python

            tm = text_management()
            texto_limpio = tm.eliminar_etiquetas_html("<p>Hola mundo</p>")
            print(texto_limpio)  # Salida: "Hola mundo"
        """
        # Usamos una expresión regular para buscar y eliminar etiquetas HTML
        texto_limpio = re.sub(r'<.*?>', '', texto)
        return texto_limpio

    def limpiar_texto(self, texto : str) -> str:
        """
        Elimina caracteres especiales o no alfanuméricos de un texto.

        :param texto: Cadena de texto a limpiar.
        :type texto: str
        :returns: El texto limpio sin caracteres especiales.
        :rtype: str
        :example:

        .. code-block:: python

            tm = text_management()
            texto_limpio = tm.limpiar_texto("Hola!@# mundo$")
            print(texto_limpio)  # Salida: "Hola mundo"
        """
        # Eliminar caracteres especiales o no alfanuméricos
        return re.sub(r'[^A-Za-z0-9 ]+', '', texto)
    
    def no_imprimibles(self, value : str) -> str:
        """
        Elimina caracteres no imprimibles de una cadena de texto.

        :param value: Cadena de texto que puede contener caracteres no imprimibles.
        :type value: str
        :returns: La cadena de texto sin caracteres no imprimibles.
        :rtype: str
        :example:

        .. code-block:: python

            tm = text_management()
            texto_limpio = tm.no_imprimibles("Hola\x00 mundo")
            print(texto_limpio)  # Salida: "Hola mundo"
        """
        # elimina caracteres no imprimibles
        if isinstance(value, str):
            return ''.join(c for c in value if c.isprintable())
        return value
    
    def remove_unsupported_characters(self, text : str):
        """
        Elimina caracteres no soportados fuera del rango ASCII de 7 bits.

        :param text: Texto con caracteres no soportados.
        :type text: str
        :returns: El texto limpio sin caracteres fuera del rango ASCII.
        :rtype: str
        :example:

        .. code-block:: python

            tm = text_management()
            texto_limpio = tm.remove_unsupported_characters("Hola\x80 mundo")
            print(texto_limpio)  # Salida: "Hola mundo"
        """
        return re.sub(r'[^\x00-\x7F]+', '', text)
    
    def clean_text(self, texto : str) -> str:
        """
        Limpia un texto convirtiéndolo a minúsculas, eliminando tildes, caracteres especiales
        y espacios extra.

        :param texto: Texto a limpiar.
        :type texto: str
        :returns: El texto limpio con minúsculas, sin tildes ni caracteres especiales.
        :rtype: str
        :example:

        .. code-block:: python

            tm = text_management()
            texto_limpio = tm.clean_text("¡Hola Mundo!")
            print(texto_limpio)  # Salida: "hola mundo"
        """
        # minusculas
        texto = texto.lower()

        # eliminar tildes y caracteres espciales
        texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8', 'ignore')

        # eliminar caracteres no alfabeticos
        texto = re.sub(r'[^a-z0-9\s]', '', texto)

        # eliminar espacios extra
        texto = re.sub(r'\s+', ' ', texto).strip()

        return texto
    


class data_text_management:
    def __init__(self) -> None:
        """
        Inicializa una instancia de la clase data_text_management.
        
        :returns: None
        """
        pass

    # APLICANDO A COLUMNAS DE UN DATAFRAME (pandas en su v1)
    # Función para eliminar etiquetas HTML de una columna
    def eliminar_etiquetas_html(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        """
        Elimina las etiquetas HTML de una columna específica en un DataFrame.

        :param df: DataFrame que contiene los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida limpia de etiquetas HTML.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["<p>Hola</p>", "<div>Adiós</div>"]})
            result = dtm.eliminar_etiquetas_html(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ["Hola", "Adiós"]
        """
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'<.*?>', '', x) if isinstance(x, str) else x)
        return df

    # Función para limpiar caracteres especiales de una columna
    def limpiar_texto(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        """
        Limpia caracteres especiales de una columna de texto en un DataFrame.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida limpia de caracteres especiales.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["Hola!", "Adiós#"]})
            result = dtm.limpiar_texto(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ["Hola", "Adiós"]
        """
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'[^\w\s]', '', x) if isinstance(x, str) else x)
        return df
    
    # ------------->
    # correción de funcion para limpiar caracteres especiales
    def caracteres_especiales(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        """
        Limpia los caracteres especiales reemplazándolos por un espacio en blanco.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida limpia de caracteres especiales.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["Hola!", "Adiós#"]})
            result = dtm.caracteres_especiales(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ["Hola", "Adiós"]
        """
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'[^\w\s]', ' ', x) if isinstance(x, str) else x)
        return df

    def espacios_extra(self, df : pd.DataFrame, col_in : str | int, col_out : str | int) -> pd.DataFrame:
        """
        Limpia los caracteres especiales reemplazándolos por un espacio en blanco.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida limpia de caracteres especiales.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["Hola!", "Adiós#"]})
            result = dtm.caracteres_especiales(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ["Hola", "Adiós"]
        """
        df[col_out] = df[col_in].apply(lambda x: re.sub(r'\s+', ' ', x).strip() if isinstance(x, str) else x)
        return df
    # ------------->
    def convertir_minusculas_y_quitar_tildes(self, df: pd.DataFrame, col_in: str | int, col_out: str | int) -> pd.DataFrame:
        """
        Convierte el texto de una columna a minúsculas y elimina las tildes en un DataFrame.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida en minúsculas y sin tildes.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["¡Hola!", "Adiós!"]})
            result = dtm.convertir_minusculas_y_quitar_tildes(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ["hola", "adios"]
        """
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
        """
        Asigna una categoría de "rating" (calificación) basada en los valores de una columna numérica.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna de salida con las categorías de rating.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"rating": [3, 5, 8]})
            result = dtm.rating(df, 'rating', 'rating_categoria')
            print(result)  # Salida: ['Mala', 'Pasable/Normal', 'Buena']
        """
        conditions = [
            (df[col_in] >= 0) & (df[col_in] < 4),
            (df[col_in] >= 4) & (df[col_in] <= 6),
            (df[col_in] > 6) & (df[col_in] <= 10)]
        labels = ['Mala', 'Pasable/Normal', 'Buena']
        df[col_out] = np.select(conditions, labels, default=np.nan)
        return df
    
    def cleaning_pipeline(self, df : pd.DataFrame, col_in : str, col_out : str) -> pd.DataFrame:
        """
        Aplica una serie de transformaciones para limpiar el texto de una columna en un DataFrame.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param col_in: Nombre o índice de la columna de entrada.
        :type col_in: str o int
        :param col_out: Nombre o índice de la columna de salida.
        :type col_out: str o int
        :returns: El DataFrame con la columna limpia.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["<p>Hola</p>", " Adiós! " ]})
            result = dtm.cleaning_pipeline(df, 'texto', 'texto_limpio')
            print(result)  # Salida: ['Hola', 'Adios']
        """
        result = (df
              .pipe(self.eliminar_etiquetas_html, col_in, col_out)
              .pipe(self.caracteres_especiales, col_out, col_out)
              .pipe(self.espacios_extra, col_out, col_out))
        return result
    
    
    def replace_illegal_characters(self, df: pd.DataFrame, replacement=' ') -> pd.DataFrame:
        """
        Reemplaza caracteres ilegales en todo el DataFrame con un valor especificado.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param replacement: El valor con el que reemplazar los caracteres ilegales. Por defecto es un espacio.
        :type replacement: str
        :returns: El DataFrame con los caracteres ilegales reemplazados.
        :rtype: pd.DataFrame
        :example:

        .. code-block:: python

            dtm = data_text_management()
            df = pd.DataFrame({"texto": ["Hola\x00 Mundo", "Adiós\x01 Mundo"]})
            result = dtm.replace_illegal_characters(df)
            print(result)  # Salida: ["Hola Mundo", "Adiós Mundo"]
        """
        # Expresión regular para caracteres ilegales
        illegal_chars_pattern = re.compile(r'[\u0000-\u001f]')

        # Reemplazar en todo el DataFrame
        return df.applymap(lambda x: illegal_chars_pattern.sub(replacement, str(x)) if isinstance(x, str) else x)
