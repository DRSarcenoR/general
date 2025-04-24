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
# <---- paquetes necesarios ---->

# analisis
import pandas as pd
import numpy as np

# conexones dbs
import sqlite3
import pyodbc

# web-scrapping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# graficas
import matplotlib.pyplot as plt
import seaborn as sns

# ML
from sklearn.cluster import KMeans

# apoyo
from datetime import datetime, timedelta
import time
import warnings
import locale
import time
from dotenv import load_dotenv

# archivos del sistema
import os

# APIs o PseudoAPIs
#import win32com.client as win32
# ------------------------------>

load_dotenv()
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
                                    },
                                    "Desarrollo": {
                                        "driver": "{ODBC Driver 17 for SQL Server}",
                                        "server": "172.31.125.11",
                                        "port": "1433",
                                        "database": "kpi_dataw"
                                    }
                                }
                            }
        

    def connection(self, query : str, db : int) -> pd.DataFrame:
        '''Selecciona la base de datos 1: Banco, 2: Seguros'''
        warnings.filterwarnings('ignore')

        # seleccionamos la base
        select_db = {1: 'Banco',
        2: 'Seguros',
        3: 'Desarrollo'}
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

    def genRequest(self, url : str, headers : dict | None = None, timeout : int = 60) -> requests.models.Response:
        return requests.get(
                                url, 
                                headers=headers,
                                proxies={'http': None, 'https': None}, 
                                timeout=timeout,
                                verify=False
                            )   

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
    

    def tipoCambio(self, fecha : str) -> float:
        # url y path al driver
        PATH_TO_DRIVER = 'C:/chromedriver-win32/chromedriver-win32/chromedriver.exe'
        url = 'https://www.banguat.gob.gt/tipo_cambio/'


        # creamos el servicio
        service = Service(PATH_TO_DRIVER)

        # inicializamos el navegador con el servicio
        driver = webdriver.Chrome(service=service)

        # esperamos a que cargue bien
        WebDriverWait(driver, 5)

        try: 
            # navegamos a la página
            driver.get(url)
            print('URL cargado')

            # Calcular la fecha del día anterior
            #fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

            # Esperar que los campos de fecha estén presentes
            campo_fecha_apartir = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "fecha_apartir"))
            )
            campo_fecha_hasta = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "fecha_hasta"))
            )
            print('Campos Cargados')


            # Limpiar y escribir la fecha en los campos
            #campo_fecha_apartir = driver.find_element(By.ID, "icon_fecha_apartir")
            campo_fecha_apartir = driver.find_element(By.ID, "fecha_apartir")
            campo_fecha_apartir.clear()
            campo_fecha_apartir.send_keys(fecha)
            campo_fecha_apartir.send_keys(Keys.RETURN)  # Asegurar el ingreso

            print('Llenamos los campos con las fechas')

            time.sleep(3)

            print("La página cargó correctamente con la fecha ingresada.")


            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            print('información extraida')
        except Exception as e:
            print(f"Ocurrió un error: {e}")

        finally:
            # Cerrar el navegador después de 5 segundos
            time.sleep(5)
            driver.quit()

        # ubicamos tipo de cambio en el html
        rows = soup.select('#table_Data tr')

        for row in rows:
            cells = row.find_all('td')
            if cells and cells[0].get_text(strip=True) == fecha:
                tipo_cambio = float(cells[1].get_text(strip=True))
                break
        
        return tipo_cambio



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

    def notebooks_config(self, precision : int = 5, max_rows : int = 30) -> None:
        # quitamos las warnings
        warnings.filterwarnings('ignore')

        # display options
        pd.options.display.max_columns=50
        pd.options.display.max_rows=max_rows
        pd.options.display.expand_frame_repr=False
        pd.options.display.colheader_justify='center'
        pd.set_option('display.float_format', lambda x: f'{x:.6f}')

        # np options
        np.set_printoptions(
            precision=precision,
            suppress=True,
            linewidth=100,
            threshold=1000
        )

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
    
    '''
    def enviar_correo(destinatario : str, asunto : str, cuerpo : str, ruta_adjunto : str | None = None) -> None:
        """
        Envía un correo electrónico a través de Microsoft Outlook.

        Esta función crea y envía un correo electrónico con el asunto, cuerpo y destinatario especificados.
        Si se proporciona una ruta de archivo válida, se adjuntará el archivo al correo.

        Parámetros:
        destinatario (str): Dirección de correo electrónico del destinatario.
        asunto (str): Asunto del correo electrónico.
        cuerpo (str): Cuerpo del mensaje del correo electrónico.
        ruta_adjunto (str | None, opcional): Ruta completa al archivo que se desea adjuntar al correo. 
            Si no se proporciona o es `None`, no se adjuntará ningún archivo. El valor predeterminado es `None`.

        Excepciones:
        Si ocurre un error al enviar el correo (por ejemplo, Outlook no está configurado o el archivo adjunto no existe), 
        se capturará la excepción y se imprimirá un mensaje de error.

        Ejemplo de uso:
        enviar_correo("destinatario@ejemplo.com", "Asunto del correo", "Este es el cuerpo del correo.", "C:\\ruta\\al\\archivo.pdf")

        """
        try:
            # accedemos a la aplicacion de outlook
            outlook = win32.Dispatch('outlook.application')

            # creamos un objeto de correo
            correo = outlook.CreateItem(0) # 0 es un correo

            # propiedades del correo
            correo.To = destinatario
            correo.Subject = asunto
            correo.Body = cuerpo

            # adjuntar archivo si se proporciona la ruta
            if ruta_adjunto and os.path.exists(ruta_adjunto):
                correo.Attachments.Add(ruta_adjunto)

            # enviamos el correo
            correo.Send()
            print('Correo enviado exitosamente')
        except Exception as e:
            print(f'Error: {e}')
    '''
    
    def verificar_carpeta(self, ruta_base : str, extension_carpeta : str) -> None:
        try:
            # juntamos la ruta base con la carpeta
            ruta = os.path.join(ruta_base, extension_carpeta)

            # verificamos si la carpeta existe
            if not os.path.exists(ruta):
                # la creamos en caso que no este
                os.makedirs(ruta)

                print(f'Carpeta {ruta} creada.')
            return True # todo bien, todo correcto... y yo que me alegro
        except Exception as e:
            print(f'Error: {e}')
            return False # GG
    

    def no_imprimibles(self, value : str) -> str:
        # elimina caracteres no imprimibles
        if isinstance(value, str):
            return ''.join(c for c in value if c.isprintable())
        return value
    

    
    def infoClientes(self, clientes : str | tuple, output : str | None = None) -> tuple | None:
        # creamos el objeto
        conn = Connections()
        
        # comprobamos que sea alguno de los dos tipos de dato que nos interesa
        if isinstance(clientes, str):
            clientes = f" = '{clientes}' "
        elif isinstance(clientes, tuple):
            clientes = f' in {clientes}'
        else:
            return None

        # query en forma lambda
        query = lambda cli: f'''with info_clientes as (
        select
            cli.cliente_Skey,
            cli.cod_cliente,
            cli.nombre,
            convert(varchar, cli.fecha_alta, 23) fecha_alta,
            cli.clase,
            cli.pais,
            cli.profesion,
            cli.direccion_cliente,
            cli.estadoCliente,
            cli.fecha_ultima_actualizacion fecha_ultima_actualizacion,
            cli.agencia_ultima_actualizacion,
            cli.cliente_pep,
            cli.cliente_cpe,
            cli.tipoPersona,
            cli.tipo_sociedad,
            cli.sectorEconomico,
            cli.actividad_economica,
            cli.sector_economico_ive,
            cli.institucion,
            cli.puesto,
            cli.firmante,
            cli.codigo_empleado,
            cli.direcciones_np,
            cli.nombre_notario,
            cli.cod_representante_legal,
            cli.nombre_representante_legal,
            isnull(p.num_productos, 0) as num_productos
        from dim_cliente cli
        left join (
            select cliente_Skey, count(*) as num_productos
            from (
                    select col.cliente_Skey from fac_colocacion col
                    union all
                    select cap.cliente_Skey from fac_captacion cap
                    union all
                    select trj.cliente_Skey from fac_tarjeta trj
                ) as productos_por_cliente
                group by cliente_Skey
        ) p on p.cliente_Skey = cli.cliente_Skey
        where cli.cod_cliente {cli}
    ),
    prods_creds as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            col.cod_col_cartera as cod_prod,
            ce.nombre as estado,
            prod.descripcion as producto,
            sp.descripcion as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'COLOCACION (Credito)'
        from fac_colocacion col
        right join info_clientes ic on ic.cliente_Skey = col.cliente_Skey
            --and (col.col_estado_Skey between 25 and 36 or col.col_estado_Skey between 45 and 48)
        join dim_producto prod on prod.producto_SKey = col.producto_SKey
        join dim_subproducto sp on sp.subproducto_SKey = col.subproducto_SKey
        join dim_sucursal suc on suc.sucursal_Skey = col.sucursal_Skey
        join dim_col_estado ce on ce.col_estado_Skey = col.col_estado_Skey
        --where (col.col_estado_Skey between 25 and 36 or col.col_estado_Skey between 45 and 48) -- no cancelados o anulados
    ),
    prods_cuentas as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            cap.cod_cuenta as cod_prod,
            ec.nombre as estado,
            cp.descripcion as producto,
            cs.descripcion as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'CAPTACION (Cuenta)'
        from fac_captacion cap
        right join info_clientes ic on ic.cliente_Skey = cap.cliente_Skey
            --and cap.estado_cartera_Skey = 2 -- productos activos
        join dim_cap_producto cp on cp.producto_SKey = cap.producto_SKey
        join dim_cap_subproducto cs on cs.subproducto_SKey = cap.subproducto_SKey
        join dim_sucursal suc on suc.sucursal_Skey = cap.sucursal_apertura_skey
        join dim_estado_cartera ec on ec.estado_cartera_SKey = cap.estado_cartera_Skey
        --where cap.estado_cartera_Skey = 2 -- productos activos
    ),
    prods_trj as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            trj.cod_col_cartera as cod_prod,
            ec.nombre as estado,
            producto = 'TARJETA CREDITO',
            tt.nombre as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'TARJETA (T.C.)'
        from fac_tarjeta as trj
        right join info_clientes ic on ic.cliente_Skey = trj.cliente_Skey
            --and trj.estado = 2 -- activa
        join dim_tipotarjeta tt on tt.tipotarjeta_Skey = trj.tipotarjeta_skey
        join dim_sucursal suc on suc.sucursal_Skey = trj.sucursal_skey
        join dim_estado_cartera ec on ec.estado_cartera_SKey = trj.estado
        --where trj.estado = 2 -- activa
    ),
    productos as (
        select * from prods_creds
        union 
        select * from prods_cuentas
        union 
        select * from prods_trj
    ),
    accionistas as (
        select
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            acc.identificacion_accionista,
            acc.nombre_accionista,
            acc.porcentaje_accionista
        from fac_accionista acc
        join info_clientes ic on ic.cliente_Skey = acc.cliente_skey
    ),
    beneficiarios as (
        select
            pc.cliente_Skey,
            pc.cod_cliente,
            pc.nombre,
            pc.cod_prod,
            pc.estado,
            pc.producto,
            pc.subproducto,
            pc.cod_sucursal,
            pc.sucursal,
            ben.nombre_beneficiario,
            ben.porcentaje_beneficiario
        from fac_beneficiario ben
        join prods_cuentas pc on pc.cod_prod = ben.cod_cuenta
    )
    '''
        
        
        # solicitamos la informacion
        infoClienteQ = 'select * from info_clientes'
        productosQ = 'select * from productos'
        accionistasQ = 'select * from accionistas'
        beneficiariosQ = 'select * from beneficiarios'
        infoCliente = conn.connection(query(clientes) + infoClienteQ, 1)
        productos = conn.connection(query(clientes) + productosQ, 1)
        accionistas = conn.connection(query(clientes) + accionistasQ, 1)
        beneficiarios = conn.connection(query(clientes) + beneficiariosQ, 1)

        # limpiamos los caracteres no imprimibles
        infoCliente = self.no_imprimibles(infoCliente)
        productos = self.no_imprimibles(productos)
        accionistas = self.no_imprimibles(accionistas)
        beneficiarios = self.no_imprimibles(beneficiarios)

        # en caso que se desee se exporta en un archivo excel
        if output:
            with pd.ExcelWriter(output, engine='openpyxl') as op:
                infoCliente.to_excel(op, sheet_name='INFOCLIENTE', index=False)
                productos.to_excel(op, sheet_name='PRODUCTOS', index=False)
                accionistas.to_excel(op, sheet_name='ACCIONISTAS', index=False)
                beneficiarios.to_excel(op, sheet_name='BENEFICIARIOS', index=False)

        return infoCliente, productos, accionistas, beneficiarios



class Decorators:
    def __init__(self) -> None:
        pass

    @staticmethod
    def tiempo_ejecucion(func):
        def wrapper(*args, **kwargs):
            global tiempo_global
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            tiempo_global = end - start
            print('Tiempo de ejecución: {:.6f}'.format(tiempo_global))
            return result
        return wrapper
    
    @staticmethod
    def inicio_y_fin(func):
        def wrapper(*args, **kwargs):
            print(f"Inicio de la función: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"Fin de la función: {func.__name__}")
            print()
            return result
        return wrapper

    
    @staticmethod
    def exito(show : bool = True) -> None:
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


class Analysis:
    def __init__(self) -> None:
        pass

    def read_lots_excels(self, path : str) -> list[pd.DataFrame]:
        # dataframes
        dfs = []

        # lectura
        try: 
            # verificar si la carpeta existe
            if not os.path.isdir(path):
                print(f"La carpeta '{path}' no existe.")
                return []
            
            # listamos todos los archivos
            archivos = os.listdir(path)

            # filtrar todos los archivos de excel
            archivos_excel = [archivo for archivo in archivos if archivo.endswith(('.xls', '.xlsx'))]

            if not archivos_excel:
                print("No se encontrar excel en la carpeta.")
                return []
            
            # leer cada archivo de excel y agregarlo a la lista
            for archivo in archivos_excel:
                ruta_archivo = os.path.join(path, archivo)
                print(f"Leyendo el archivo: {ruta_archivo}")
                try: 
                    df = pd.read_excel(ruta_archivo)
                    dfs.append(df)
                except Exception as e:
                    print(f"Error al leer el archivo '{ruta_archivo}': {e}")
        except Exception as e:
            print(f"Error procesando la carpeta: {e}")
        return dfs


    def elbow_test(self, X_scaled: np.ndarray, cluster_range: range = range(1,11), output_name : str | None = None) -> None: 
        # rango de clusters a probar
        rangek = cluster_range
        inertia_values = []

        # aplicamos kmeans varias veces
        for k in rangek:
            kmeans = KMeans(n_clusters=k, random_state=27)
            kmeans.fit(X_scaled)
            inertia_values.append(kmeans.inertia_)


        # 4. Graficar el método del codo
        plt.figure(figsize=(8,6))
        plt.plot(rangek, inertia_values, marker='o', linestyle='--', color='b')
        plt.title('Numero de clusters - Inercia')
        plt.xlabel('Número de Clústeres (k)')
        plt.ylabel('Inercia (Suma de Errores Cuadráticos)')
        plt.grid(True)
        if output_name:
            plt.savefig(output_name + '.pdf')
        plt.show()


    def scatter_cluster(self, df: pd.DataFrame, x_col: str, y_col: str, cluster_col : str = 'Cluster', output_name : str | None = None, title : str = 'Clustering', line : bool = False) -> None: 
        # scatter plot
        sns.scatterplot(
            x=df[x_col],
            y=df[y_col],
            hue=df[cluster_col],
            palette='tab10'
        )

        if line:
            # graficamos la rega y=x
            x_min, x_max = df[x_col].min(), df[x_col].max()
            y_min, y_max = df[x_col].min(), df[x_col].max()
            min_val, max_val = min(x_min, y_min), max(x_max, y_max)
            plt.plot([min_val, max_val], [min_val, max_val], linestyle='--', color='gray', label='y = x')

        plt.title(title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title='Cluster')
        if output_name:
            plt.savefig(output_name + '.pdf')     
        plt.show()
    


    def percentiles(self, df, columna, pasos=1):
        # Generar una lista de percentiles (de 0% a 100%) con el paso especificado
        percentiles = [i / 100 for i in range(0, 101, pasos)]  # Por defecto, pasos=1 (0%, 1%, 2%, ..., 100%)
        
        # Calcular los valores de los percentiles para la columna especificada
        percentiles_values = df[columna].quantile(percentiles)
        
        # Crear un DataFrame con los resultados de los percentiles
        percentiles_table = pd.DataFrame(percentiles_values).reset_index()
        
        # Renombrar las columnas para mayor claridad
        percentiles_table.columns = ['Percentil', 'Valor']
        
        return percentiles_table
    

    def tukey_alternative(self, df: pd.DataFrame, varColumn: str, outputColumn: str, c: float =2.5, low_percentile: float = 0.05, high_percentile: float = 0.95, filter: bool = True) -> pd.DataFrame:
        # quitamos valores faltantes (no se imputan, en caso qeu se requiera, que se haga por fuera)
        data = df[df[varColumn].notna()]

        # filtramos los valores segun percentiles
        low = data[varColumn].quantile(low_percentile)
        high = data[varColumn].quantile(high_percentile)
        if filter:
            data = data[(data[varColumn] >= high) & (data[varColumn] <= low)]


        # medidas estadisticas
        media = data[varColumn].mean()
        mediana = data[varColumn].median()
        mediasup = data[data[varColumn] > mediana][varColumn].mean()
        mediainf = data[data[varColumn] < mediana][varColumn].mean()


        # calcular los limites ajustados por c
        xinf = media - mediainf
        xsup = mediasup - media
        x_sup = media + c*xsup
        x_inf = media - c*xinf

        # marcamos los outliers
        df[outputColumn] = 0
        df.loc[(df[varColumn] < x_inf) | (df[varColumn] > x_sup), outputColumn] = 1
        return df
    


    def tukey(self, df: pd.DataFrame, varColumn: str, outputColumn: str, c: float = 2.5) -> pd.DataFrame:
        # quitamos valores faltantes (no se imputan, en caso qeu se requiera, que se haga por fuera)
        data = df[df[varColumn].notna()]

        # implementacion iqr
        q1 = data[varColumn].quantile(0.25)
        q3 = data[varColumn].quantile(0.75)
        IQR = q3 - q1


        # calcular los limites ajustados por c
        x_inf = q1 - c*IQR
        x_sup = q3 + c*IQR

        # marcamos los outliers
        df[outputColumn] = 0
        df.loc[(df[varColumn] < x_inf) | (df[varColumn] > x_sup), outputColumn] = 1
        return df

    

    def redondear(self, monto : float) -> int:
        # factores de ajuste
        intervalos = [
            (0, 10, 10**0),
            (10, 100, 10**1),
            (100, 1000, 10**1),
            (1000, 10000, 10**2),
            (10000, 100000, 10**2),
            (100000, 1000000, 10**2),
            (1000000, 10000000, 10**3),
            (10000000, 100000000, 10**3),
            (100000000, float('inf'), 10**4)
        ]

        # determinar el factor de ajuste dado el intervalo del monto
        for linf, lsup, f in intervalos:
            if linf <= monto < lsup:
                # aplicamos la formula de redondeo
                monto_redondeado = np.floor(monto / f)*f
                return monto_redondeado

        return monto
    
    def cumsum_with_threshold(self, series : pd.Series, threshold: float, skipna=True) -> pd.Series:
        """
        Realiza una suma acumulativa por partes basada en un umbral definido por el usuario.

        Parameters:
        series (pd.Series): Serie de pandas sobre la que se calcula la suma acumulativa.
        threshold (float): Valor umbral para dividir las sumas acumulativas.
        skipna (bool): Si se deben ignorar valores NaN en los cálculos.

        Returns:
        pd.Series: Una Serie con la suma acumulativa por partes.
        """
        # Convertimos a numpy array para operaciones eficientes
        values = series.values
        result = np.zeros_like(values, dtype=np.float64)
        
        # Inicializamos variables
        acc = 0
        for i, val in enumerate(values):
            acc += val
            if acc > threshold:
                # Si superamos el umbral, marcamos el valor acumulado
                result[i] = acc
                # Calculamos la diferencia para la siguiente celda
                acc -= threshold
            else:
                result[i] = acc
        
        return pd.Series(result, index=series.index, name=series.name)
    

    def describe_categorical(data: pd.DataFrame, column: str) -> None:
        # Obtener conteo de valores únicos y frecuencia
        value_counts = data[column].value_counts()
        
        # Crear tabla con información relevante
        summary = pd.DataFrame({
            'Valor': value_counts.index,
            'Frecuencia': value_counts.values,
            'Porcentaje': value_counts.values / len(data) * 100
        })
        
        # Mostrar tabla
        print(f"Información para la variable '{column}':")
        print(summary)
        print()
        
        # Crear histograma de frecuencias
        plt.figure(figsize=(8, 6))
        plt.bar(summary['Valor'], summary['Frecuencia'], color='skyblue')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')
        plt.title(f'Histograma de frecuencias para la variable {column}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()





