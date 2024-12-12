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
import requests
from bs4 import BeautifulSoup
#from importlib.resources import pkg_resources
import time
from datetime import datetime
import os
# ------------------------------>


class Connections:
    def __init__(self):
        self.__credentials = {
                                "DW": {
                                    "Banco": {
                                        "driver": "{ODBC Driver 17 for SQL Server}",
                                        "server": "172.31.100.37",
                                        "port": "1433",
                                        "database": "kpi_dataw"
                                    },
                                    "Seguros": {
                                        "driver": "{ODBC Driver 17 for SQL Server}",
                                        "server": "172.31.100.67",
                                        "port": "1433",
                                        "database": "DW"
                                    }
                                }
                            }

    def connection(self, query : str, db : int) -> pd.DataFrame:
        '''Selecciona la base de datos 1: Banco, 2: Seguros'''
        warnings.filterwarnings('ignore')

        # seleccionamos la base
        select_db = {1: 'Banco',
        2: 'Seguros'}
        selected_db = select_db.get(db)

        # abrimos el json con las credenciales e informacion
        #with pkg_resources.open_text('CHN', 'credenciales.json', encoding='UTF-8') as cred:
        #    credenciales = json.load(cred)
        
        # intentamos hacer la conexion
        try:
            conexion = pyodbc.connect(
                driver = self.__credentials['DW'][selected_db]['driver'],
                server = self.__credentials['DW'][selected_db]['server'],
                database = self.__credentials['DW'][selected_db]['database'],
                port = self.__credentials['DW'][selected_db]['port'],
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
    def __init__(self) -> None:
        # url para tipo de cambio
        self.urlTC = 'https://www.banguat.gob.gt/tipo_cambio/'

    def tipoCambioHoy(self) -> float:
        # solicitamos la información a la url
        response = requests.get(self.urlTC, proxies={'https': None, 'http': None})

        # si la respuesta es positiva, i.e. status_code = 200
        if response.status_code == 200:
            # parseamos el contenido a html
            soup = BeautifulSoup(response.content, 'html.parser')

            # empezamos a navegar por el archivo en busca de la data
            try:
                # buscamos la etiqueta tr filtrada por la clase dada
                detalle = soup.find('tr', class_="detalle_banguat")
                if detalle is None:
                    raise ValueError("No se encontró el elemento 'tr' con la clase 'detalle_banguat'.")
                
                # en caso de encontrarla buscamos la etiqueta td dentro de la tr
                td = detalle.find('td') 
                if td is None:
                    raise ValueError("No se encontró un elemento 'td' dentro del 'tr' especificado.")

                # en caso de encontrarla, extraemos el valor de esta misma
                valor = td.text.strip()
                
                # Intentamos convertir el valor extraído a float
                valor = float(valor)
                return valor
            except ValueError as e:
                print("Error de valor:", e)

            except Exception as e:
                print("Ocurrió un error inesperado:", e)
        else:
            print('En caso de buscar un día distitno al día de hoy, esperar a que se agregue esta opción al codigo fuente.')



class Other:
    """
    Clase que contiene métodos auxiliares para registrar eventos y mostrar mensajes.

    Métodos:
        record(script_name: str, exec_time: str) -> None:
            Registra el nombre del script y el tiempo de ejecución en un archivo.
        
        exito(show: bool = True) -> None:
            Imprime un mensaje ASCII de éxito en la consola.
    """
        
    def __init__(self):
        """
        Inicializa la clase Other. No recibe parámetros ni realiza ninguna acción durante la inicialización.
        """
                
        pass

    def record(self, script_name : str, exec_time : str) -> None:
        """
        Registra el nombre del script, la fecha y hora, y el tiempo de ejecución en el archivo 'record.txt'.

        :param script_name: Nombre del script que se está ejecutando.
        :type script_name: str
        :param exec_time: Tiempo de ejecución del script.
        :type exec_time: str
        :returns: None
        :example:

        .. code-block:: python

            logger = Other()
            logger.record("mi_script.py", "1452 segundos")
        """
        #locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        locale.setlocale(locale.LC_TIME, "Spanish")
        current_datetime = datetime.now()
        format_current_datetime = current_datetime.strftime("%A, %d de %B de %Y, %H:%M:%S")
        with open("record.txt", 'a') as f:
            f.write(script_name + ', ' + format_current_datetime + ', ' + exec_time + "\n")
        f.close()


    def listar_directorios(self, base_path, archivo_salida, nivel=0):
        """Lista los directorios y archivos en formato de árbol y los guarda en un archivo."""
        # Abre el archivo para escribir con codificación UTF-8
        with open(archivo_salida, 'w', encoding='utf-8') as archivo:
            archivo.write("```markdown\n")
            archivo.write(f"{base_path}/\n")
            self._listar_directorios_recursivo(base_path, archivo, nivel)
            archivo.write("```\n")

    def _listar_directorios_recursivo(self, base_path, archivo, nivel):
        """Función recursiva para listar directorios y archivos."""
        espacios = '    ' * nivel  # Espacio para el nivel
        items = os.listdir(base_path)  # Lista de elementos en el directorio
        items.sort()  # Ordena alfabéticamente
        
        for index, item in enumerate(items):
            ruta_completa = os.path.join(base_path, item)
            # Comprobar si es el último elemento para la visualización correcta del árbol
            if os.path.isdir(ruta_completa):
                if index == len(items) - 1:
                    archivo.write(f"{espacios}└── {item}/\n")
                else:
                    archivo.write(f"{espacios}├── {item}/\n")
                self._listar_directorios_recursivo(ruta_completa, archivo, nivel + 1)
            else:
                if index == len(items) - 1:
                    archivo.write(f"{espacios}└── {item}\n")
                else:
                    archivo.write(f"{espacios}├── {item}\n")



class Decorators:
    def __init__(self) -> None:
        pass


    def tiempo_ejecucion(self, func):
        def wrapper(*args, **kwargs):
            global tiempo_global
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            tiempo_global = end - start
            print('Tiempo de ejecución: {:.6f}'.format(tiempo_global))
            return result
        return wrapper
    

    def inicio_y_fin(self, func):
        def wrapper(*args, **kwargs):
            print(f"Inicio de la función: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"Fin de la función: {func.__name__}")
            print()
            return result
        return wrapper

    

    def exito(self, show : bool = True) -> None:
        """
        Muestra un mensaje ASCII en la consola indicando el éxito de una operación.

        :param show: Si es True, imprime el mensaje ASCII. Por defecto es True.
        :type show: bool
        :returns: None
        :example:

        .. code-block:: python

            notifier = Other()
            notifier.exito()
        """

        if show:
            print("         _nnnn_")
            print('        dGGGGMMb     ,""""""""".')
            print("       @p~qp~~qMb    | ¡Éxito! |")
            print("       M|@||@) M|   _;.........'")
            print("       @,----.JM| -'")
            print("      JS^\__/  qKL")
            print("     dZP        qKRb")
            print("    dZP          qKKb")
            print("   fZP            SMMb")
            print("   HZM            MMMM")
            print("   FqM            MMMM")
            print(' __| ".        |\dS"qML')
            print(" |    `.       | `' \Zq")
            print("_)      \.___.,|     .'")
            print("\____   )MMMMMM|   .'")
            print("     `-'       `--' ")
            return None




