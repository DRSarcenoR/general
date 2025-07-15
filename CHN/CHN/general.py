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
import re
import calendar

# archivos del sistema
import os

# APIs o PseudoAPIs
#import win32com.client as win32
# ------------------------------>

load_dotenv()
class Connections:
    """
    Clase para gestionar conexiones a distintas bases de datos mediante ODBC.

    Esta clase contiene credenciales internas y permite ejecutar consultas SQL
    sobre diferentes entornos como Banco, Seguros y Desarrollo.
    """


    def __init__(self):
        """
        Inicializa la clase Connections con las credenciales predefinidas
        para múltiples entornos de base de datos.
        """
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
        """
        Ejecuta una consulta SQL sobre la base de datos seleccionada y devuelve los resultados.

        Parameters:
            query (str): Cadena con la consulta SQL a ejecutar.
            db (int): Código numérico de la base de datos a utilizar:
                - 1: Banco
                - 2: Seguros
                - 3: Desarrollo

        Returns:
            pd.DataFrame: Un DataFrame con los resultados de la consulta SQL.
                          Si ocurre un error durante la conexión o ejecución, retorna None.
        """
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
    """
    Clase para realizar scrapping del tipo de cambio desde el sitio del Banco de Guatemala.
    Contiene métodos para obtener el tipo de cambio del día actual o de una fecha específica.
    """

    def __init__(self) -> None:
        """
        Inicializa la clase Scrapping con la URL de consulta del tipo de cambio.
        """
        # url para tipo de cambio
        self.urlTC = 'https://www.banguat.gob.gt/tipo_cambio/'



    def genRequest(self, url : str, headers : dict | None = None, timeout : int = 60) -> requests.models.Response:
        """
        Realiza una solicitud HTTP GET a una URL específica con parámetros opcionales.

        Parameters:
            url (str): URL de destino.
            headers (dict, optional): Encabezados HTTP personalizados.
            timeout (int): Tiempo máximo de espera en segundos. Por defecto es 60.

        Returns:
            requests.Response: Objeto de respuesta de la petición.
        """
        return requests.get(
                                url, 
                                headers=headers,
                                proxies={'http': None, 'https': None}, 
                                timeout=timeout,
                                verify=False
                            )   
    


    def tipoCambioHoy(self) -> float:
        """
        Obtiene el tipo de cambio actual desde la página del Banco de Guatemala.

        Returns:
            float: Valor del tipo de cambio actual. Si ocurre un error, se imprime el mensaje y no retorna nada.
        """
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
        """
        Obtiene el tipo de cambio para una fecha específica mediante automatización del navegador.

        Parameters:
            fecha (str): Fecha en formato 'dd/mm/yyyy' para la cual se desea obtener el tipo de cambio.

        Returns:
            float: Valor del tipo de cambio correspondiente a la fecha dada.
        """
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

    def notebooks_config(self, precision : int = 5, max_rows : int = 30, max_cols : int = 50) -> None:
        """
        Configura las opciones de visualización de pandas y numpy para mejorar la legibilidad en notebooks.

        Parameters:
            precision (int): Precisión de números decimales para numpy. Por defecto 5.
            max_rows (int): Máximo de filas que pandas muestra por defecto. Por defecto 30.
        """
        # quitamos las warnings
        warnings.filterwarnings('ignore')

        # display options
        pd.options.display.max_columns=max_cols
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
        """
        Lista la estructura de directorios y archivos de una ruta base y la guarda como árbol en un archivo de texto.

        Parameters:
            base_path (str): Ruta base del sistema de archivos a listar.
            archivo_salida (str): Nombre del archivo de salida.
            nivel (int): Nivel de indentación inicial para el árbol (usado internamente).
        """
        # Abre el archivo para escribir con codificación UTF-8
        with open(archivo_salida, 'w', encoding='utf-8') as archivo:
            archivo.write("```markdown\n")
            archivo.write(f"{base_path}/\n")
            self._listar_directorios_recursivo(base_path, archivo, nivel)
            archivo.write("```\n")

    def _listar_directorios_recursivo(self, base_path, archivo, nivel):
        """
        Método auxiliar recursivo para listar los directorios y escribirlos con indentación jerárquica.

        Parameters:
            base_path (str): Ruta actual a listar.
            archivo (TextIO): Archivo de escritura abierto.
            nivel (int): Nivel actual de profundidad en el árbol.
        """
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
        """
        Verifica si una carpeta existe en la ruta especificada. Si no existe, la crea.

        :param ruta_base: Ruta base donde se quiere verificar/crear la carpeta.
        :type ruta_base: str
        :param extension_carpeta: Nombre o extensión de la carpeta a verificar/crear.
        :type extension_carpeta: str
        :return: True si la carpeta ya existía o fue creada exitosamente, False en caso de error.
        :rtype: bool
        :example:

        .. code-block:: python

            other = Other()
            other.verificar_carpeta("C:/Users/Admin", "nueva_carpeta")
        """
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
        """
        Elimina caracteres no imprimibles de una cadena de texto.

        :param value: Cadena de texto a limpiar.
        :type value: str
        :return: Cadena sin caracteres no imprimibles.
        :rtype: str
        :example:

        .. code-block:: python

            texto_limpio = other.no_imprimibles("Hola\x00Mundo")
        """
        # elimina caracteres no imprimibles
        if isinstance(value, str):
            return ''.join(c for c in value if c.isprintable())
        return value
    
    def clean_dataframe(self, df):
        # Define una expresión regular para caracteres no imprimibles
        non_printable = re.compile(r'[\x00-\x1F\x7F-\x9F]')
        
        # Aplica la limpieza a cada celda del DataFrame
        df_clean = df.applymap(lambda x: non_printable.sub('', str(x)) if isinstance(x, str) else x)
    
        return df_clean
    
    def infoClientes(self, clientes : str | tuple, output : str | None = None, time_lapse : int = 6) -> tuple | None:
        """
        Recupera información detallada de uno o varios clientes, incluyendo sus productos,
        accionistas y beneficiarios. Puede exportar los resultados a un archivo Excel.

        :param clientes: Código(s) de cliente(s). Puede ser un string o una tupla de strings.
        :type clientes: str | tuple
        :param output: Ruta del archivo Excel para exportar los resultados. Opcional.
        :type output: str | None
        :return: Tupla con los DataFrames (infoCliente, productos, accionistas, beneficiarios).
                Retorna None si el parámetro `clientes` no es válido.
        :rtype: tuple | None
        :example:

        .. code-block:: python

            clientes_data = other.infoClientes(("C123", "C456"), output="clientes.xlsx")
        """
        # creamos el objeto
        conn = Connections()
        
        # comprobamos que sea alguno de los dos tipos de dato que nos interesa
        if isinstance(clientes, str):
            clientes = f" = '{clientes}' "
        elif isinstance(clientes, tuple):
            clientes = f' in {clientes}'
        else:
            return None
        
        # tomamos el rango de fechas segun el lapso de meses indicado
        hoy = datetime.today()
        # ultimo día del mes anterior
        primer_dia_mes_actual = hoy.replace(day=1)
        ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
        # calcular el primer dia n meses atras
        anio = ultimo_dia_mes_anterior.year
        mes = ultimo_dia_mes_anterior.month - time_lapse
        # ajustar el mes y anio
        while mes <= 0:
            mes += 12
            anio -= 1
        meses_atras = ultimo_dia_mes_anterior.replace(year=anio, month=mes, day=1)
        # renombrando por facilidad
        fecha_inicio = int(meses_atras.strftime('%Y%m%d'))
        fecha_fin = int(ultimo_dia_mes_anterior.strftime('%Y%m%d'))

        # query en forma lambda
        query = lambda cli: f'''
        declare @fecha_inicio int = {fecha_inicio};
        declare @fecha_fin int = {fecha_fin};

        with info_clientes as (
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
                    cli.tel1,
                    cli.tel2,
                    cli.cliente_pep,
                    cli.cliente_cpe,
                    cli.tipoPersona,
                    cli.tipo_sociedad,
                    cli.sectorEconomico,
                    cli.actividad_economica,
                    cli.sector_economico_ive,
                    cli.nacionalidad,
                    cli.lugar_nacimiento_extranjero,
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
                    col.fac_colocacion_Skey as prod_key,
                    col.cod_col_cartera as cod_prod,
                    ce.nombre as estado,
                    col.monto_desembolsado as saldo,
                    col.monto_capital_total as deuda,
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
                    cap.fac_captacion_skey as prod_key,
                    cap.cod_cuenta as cod_prod,
                    ec.nombre as estado,
                    cap.saldo_disponible as saldo,
                    NULL as deuda,
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
                    trj.tarjeta_skey as prod_key,
                    trj.cod_col_cartera as cod_prod,
                    ec.nombre as estado,
                    trj.limite_credito as saldo,
                    trj.monto_capital as deuda,
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
            prom_capt as (
                select
                    smcap.fac_captacion_Skey,
                    avg(smcap.cantidad_creditos) as cantidad_creditos,
                    avg(smcap.creditos) as creditos,
                    avg(smcap.cantidad_debitos) as cantidad_debitos,
                    avg(smcap.debitos) as debitos
                from (
                    select
                            mov.fac_captacion_Skey,
                            left(cast(mov.fecha_operacion as varchar), 6) as mes,
                            count(case when trx.tipo_movimiento = 'CREDITO' then 1 else null end) as cantidad_creditos,
                            sum(case when trx.tipo_movimiento = 'CREDITO' then mov.valor_operacion else 0 end) as creditos,
                            count(case when trx.tipo_movimiento = 'DEBITO' then 1 else null end) as cantidad_debitos,
                            sum(case when trx.tipo_movimiento = 'DEBITO' then mov.valor_operacion else 0 end) as debitos
                        from fac_movimientos mov
                        join info_clientes ic on ic.cliente_Skey = mov.cliente_Skey
                        join dim_transacciones trx on trx.trx_Skey = mov.trx_Skey and trx.relacion_cuenta = 'RELACIONADA'
                        where mov.estado_trx_Skey = 1 and mov.fecha_operacion between @fecha_inicio and @fecha_fin --and cliente_Skey is not null and cliente_Skey <> -1
                        group by mov.fac_captacion_Skey, 
                            left(cast(fecha_operacion as varchar), 6)
                    ) as smcap
                    group by smcap.fac_captacion_Skey
            ),
            prom_trj as (
                select
                    smtrj.tarjeta_skey,
                    avg(smtrj.cantidad_creditos) as cantidad_creditos,
                    -1*avg(smtrj.creditos) as creditos,
                    avg(smtrj.cantidad_debitos) as cantidad_debitos,
                    avg(smtrj.debitos) as debitos
                from (
                    select	
                        movt.tarjeta_skey,
                        left(cast(movt.fecha_trx as varchar), 6) as mes,
                        count(case when movt.monto <> 0 and movt.cod_trx in (2,11,13,15,30,511,513,730,732,848) then 1 else null end) as cantidad_creditos,
                        sum(case when movt.monto <> 0 and movt.cod_trx in (2,11,13,15,30,511,513,730,732,848) then movt.monto else null end) as creditos,
                        count(case when movt.monto <> 0 and movt.cod_trx not in (2,11,13,15,30,511,513,730,732,848) then 1 else null end) as cantidad_debitos,
                        sum(case when movt.monto <> 0 and movt.cod_trx not in (2,11,13,15,30,511,513,730,732,848) then movt.monto else null end) as debitos
                    from fac_movimientos_tarjeta movt
                    join fac_tarjeta trj on trj.tarjeta_skey = movt.tarjeta_skey
                    join info_clientes ic on ic.cliente_Skey = trj.cliente_Skey
                    where movt.cod_trx not in (5,8,9,10,19,21,22,29,32,41,50,104,451,453,553,554,637,665,671,689,701,715,717,731,733,747,751,754,821,849,851)
                        and movt.fecha_trx between @fecha_inicio and @fecha_fin
                    group by movt.tarjeta_skey,
                        left(cast(movt.fecha_trx as varchar), 6)
                ) as smtrj
                group by smtrj.tarjeta_skey
            ),
            prom_col as (
                select
                    smcol.fac_colocacion_skey,
                    null as cantidad_creditos,
                    null as creditos, 
                    avg(smcol.cantidad_debitos) as cantidad_debitos,
                    avg(smcol.debitos) as debitos
                from (
                    select
                        movc.fac_colocacion_skey,
                        left(cast(movc.fecha_trx as varchar), 6) as mes,
                        count(case when movc.total <> 0 then 1 else null end) as cantidad_debitos,
                        sum(case when movc.total <> 0 then movc.total else null end) as debitos
                    from fac_movimientos_colocacion movc
                    join fac_colocacion col on col.fac_colocacion_Skey = movc.fac_colocacion_skey
                    join info_clientes ic on ic.cliente_Skey = col.cliente_Skey
                    where movc.trx_col_skey in (1,3) and movc.fecha_trx between @fecha_inicio and @fecha_fin
                    group by movc.fac_colocacion_skey,
                        left(cast(movc.fecha_trx as varchar), 6)
                ) as smcol
                group by smcol.fac_colocacion_skey
            ),
            creditos as (
                select 
                    pcr.cliente_Skey,
                    pcr.cod_cliente,
                    pcr.nombre,
                    pcr.cod_prod,
                    pcr.estado,
                    pcr.saldo,
                    pcr.deuda,
                    pcr.producto,
                    pcr.subproducto,
                    pco.cantidad_creditos,
                    pco.creditos,
                    pco.cantidad_debitos,
                    pco.debitos,
                    pcr.cod_sucursal,
                    pcr.sucursal,
                    pcr.origen
                from prods_creds pcr 
                left join prom_col pco on pco.fac_colocacion_skey = pcr.prod_key
            ), 
            cuentas as (
                select 
                    pcu.cliente_Skey,
                    pcu.cod_cliente,
                    pcu.nombre,
                    pcu.cod_prod,
                    pcu.estado,
                    pcu.saldo,
                    pcu.deuda,
                    pcu.producto,
                    pcu.subproducto,
                    pct.cantidad_creditos,
                    pct.creditos,
                    pct.cantidad_debitos,
                    pct.debitos,
                    pcu.cod_sucursal,
                    pcu.sucursal,
                    pcu.origen
                from prods_cuentas pcu
                left join prom_capt pct on pct.fac_captacion_Skey = pcu.prod_key
            ), 
            tarjeta as (
                select 
                    ptr.cliente_Skey,
                    ptr.cod_cliente,
                    ptr.nombre,
                    ptr.cod_prod,
                    ptr.estado,
                    ptr.saldo,
                    ptr.deuda,
                    ptr.producto,
                    ptr.subproducto,
                    ptrj.cantidad_creditos,
                    ptrj.creditos,
                    ptrj.cantidad_debitos,
                    ptrj.debitos,
                    ptr.cod_sucursal,
                    ptr.sucursal,
                    ptr.origen
                from prods_trj ptr 
                left join prom_trj ptrj on ptrj.tarjeta_skey = ptr.prod_key
            ), 
            productos as (
                select * from creditos
                union 
                select * from cuentas
                union 
                select * from tarjeta
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

        # quitamos caracteres ilegales
        infoCliente = self.clean_dataframe(infoCliente)
        productos = self.clean_dataframe(productos)
        accionistas = self.clean_dataframe(accionistas)
        beneficiarios = self.clean_dataframe(beneficiarios)

        # en caso que se desee se exporta en un archivo excel
        if output:
            with pd.ExcelWriter(output, engine='openpyxl') as op:
                infoCliente.to_excel(op, sheet_name='INFOCLIENTE', index=False)
                productos.to_excel(op, sheet_name='PRODUCTOS', index=False)
                accionistas.to_excel(op, sheet_name='ACCIONISTAS', index=False)
                beneficiarios.to_excel(op, sheet_name='BENEFICIARIOS', index=False)

        return infoCliente, productos, accionistas, beneficiarios
    

    # Funcion para dividir en tuplas
    def dividir_en_tuplas(self, tupla : tuple, max_size : int = 1000) -> list[tuple]:
        return [tupla[i:i + max_size] for i in range(0, len(tupla), max_size)]


    # Función para procesar los clientes en partes manejables
    def procesar_clientes(self, clientes : tuple) -> list[pd.DataFrame]:
        # Dividimos la lista de clientes en sublistas de tamaño máximo 1000
        sublistas = self.dividir_en_tuplas(clientes)
        
        # Inicializamos las listas para concatenar los resultados
        ic_total = []
        prods_total = []
        acc_total = []
        ben_total = []

        # Iteramos sobre las sublistas
        for sublista in sublistas:
            ic, prods, acc, ben = self.infoClientes(tuple(sublista))  # Llamamos a la función en cada sublista
            
            # Concatenamos los resultados de esta sublista
            ic_total.append(ic)
            prods_total.append(prods)
            acc_total.append(acc)
            ben_total.append(ben)

        # Concatenamos todos los resultados en un solo DataFrame
        ic_final = pd.concat(ic_total, ignore_index=True)
        prods_final = pd.concat(prods_total, ignore_index=True)
        acc_final = pd.concat(acc_total, ignore_index=True)
        ben_final = pd.concat(ben_total, ignore_index=True)
        
        return ic_final, prods_final, acc_final, ben_final



class Decorators:
    def __init__(self) -> None:
        """
        Clase que contiene decoradores y utilidades para funciones.
        """
        pass

    @staticmethod
    def tiempo_ejecucion(func):
        """
        Decorador que mide el tiempo de ejecución de una función y lo imprime.

        :param func: Función a decorar.
        :return: Función decorada.
        """
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
        """
        Decorador que imprime el inicio y el fin de una función.
        """
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
    """
    Clase que agrupa funciones para análisis de datos como lectura de múltiples archivos Excel,
    pruebas estadísticas y visualizaciones.
    """
    def __init__(self) -> None:
        pass

    def read_lots_excels(self, path : str) -> list[pd.DataFrame]:
        """
        Lee múltiples archivos Excel de una carpeta dada.

        :param path: Ruta a la carpeta que contiene archivos Excel.
        :return: Lista de DataFrames leídos desde los archivos.
        """
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
        """
        Realiza el método del codo para determinar el número óptimo de clústeres.

        :param X_scaled: Matriz de datos escalados.
        :param cluster_range: Rango de valores para k en KMeans.
        :param output_name: Nombre del archivo PDF para guardar el gráfico.
        """
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
        """
        Genera un gráfico de dispersión con los clusters asignados.

        :param df: DataFrame con los datos.
        :param x_col: Nombre de la columna para el eje x.
        :param y_col: Nombre de la columna para el eje y.
        :param cluster_col: Columna con los clusters asignados.
        :param output_name: Nombre del archivo PDF para guardar el gráfico.
        :param title: Título del gráfico.
        :param line: Si se desea graficar la línea y = x.
        """ 
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
    


    def percentiles(self, df: pd.DataFrame, columna: str, pasos: int = 1) -> pd.DataFrame:
        """
        Calcula los percentiles de una columna.

        :param df: DataFrame de entrada.
        :param columna: Columna sobre la cual calcular los percentiles.
        :param pasos: Intervalo entre percentiles a calcular.
        :return: DataFrame con percentiles y valores.
        """
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
        """
        Alternativa al método de Tukey para detección de outliers usando percentiles y diferencias relativas a la media.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param varColumn: Columna a analizar.
        :type varColumn: str
        :param outputColumn: Columna donde marcará los outliers.
        :type outputColumn: str
        :param c: Factor de multiplicación para los límites.
        :type c: float
        :param low_percentile: Percentil inferior para filtrar datos.
        :type low_percentile: float
        :param high_percentile: Percentil superior para filtrar datos.
        :type high_percentile: float
        :param filter: Si se desea filtrar por percentiles antes del análisis.
        :type filter: bool
        :return: DataFrame con columna de outliers marcada.
        :rtype: pd.DataFrame
        """
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
        """
        Aplica el método clásico de Tukey (basado en IQR) para detectar outliers.

        :param df: DataFrame con los datos.
        :type df: pd.DataFrame
        :param varColumn: Columna a evaluar.
        :type varColumn: str
        :param outputColumn: Nombre de la columna a crear para marcar los outliers.
        :type outputColumn: str
        :param c: Coeficiente para determinar los límites.
        :type c: float
        :return: DataFrame con columna de outliers marcada.
        :rtype: pd.DataFrame
        """
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
        """
        Redondea un monto hacia abajo al múltiplo más cercano según un factor definido por intervalos.

        :param monto: Monto a redondear.
        :type monto: float
        :return: Monto redondeado.
        :rtype: int
        """
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
        Realiza una suma acumulativa por bloques, reiniciando cuando se alcanza un umbral.

        :param series: Serie sobre la que se aplicará el cálculo.
        :type series: pd.Series
        :param threshold: Umbral máximo antes de reiniciar acumulación.
        :type threshold: float
        :param skipna: Si se deben omitir valores NaN.
        :type skipna: bool
        :return: Serie con suma acumulativa parcial.
        :rtype: pd.Series
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
        """
        Muestra un resumen de frecuencias para una columna categórica.

        :param data: DataFrame con los datos.
        :type data: pd.DataFrame
        :param column: Nombre de la columna categórica.
        :type column: str
        :return: None
        """
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





