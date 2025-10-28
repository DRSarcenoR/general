# Módulo 3 de Librería de la Metodología.
# 
# Metodología de Parametrización de Banderas
# 
# Autor: Gerencia de Innovación
# Modificado: Diego Sarceño
# Contacto: dsarceno68@gmail.com | diego.sarceno@chn.com.gt
# Tel: (+502) 4204 4629
# 
# 
# ------------------------------>
# <---- paquetes necesarios ---->

# analisis
import pandas as pd
import numpy as np
import math


# conexones dbs
import sqlite3
import pyodbc


# graficas
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# ML
from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor

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


class Metodologia:
    def __init__(self, cliente: str, fecha: str, analisis: str) -> None:
        # Creamos un dataframe donde se estará guardando toda la información
        # Nombres de las columnas
        columns = ['Parámetro', 'Clientes totales', 'Monto total transado en el periodo', 'Monto total monitoreado (%)', 'Alertas generadas',
                'Clientes monitoreados (%)', 'Rendimiento (%)', 'Potenciales alertas generadas por mes']

        # Creamos el dataframe
        self.resultados = pd.DataFrame(columns=columns)

        # definimos para toda la clase los nombres de las columnas
        self.cliente = cliente
        self.fecha = fecha
        self.analisis = analisis

    
    def estats_base(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_cliente : str = 'cliente_Skey') -> tuple[float, int]:
        """
        Calculates the total sum of the specified amounts and the count of clients to analyze.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: 'cliente_Skey' and 'AMOUNT'.
        col_analisis (str, optional): The name of a column in the DataFrame that contains the amounts to be analyzed. If not provided, the default 'AMOUNT' column will be used.

        Returns:
        tuple: A tuple containing:
            - mt (float): The sum of the specified amounts.
            - ct (int): The count of unique clients based on the 'cliente_Skey' column.
        """
        # Monto total
        mt  = dataframe[col_analisis].sum()

        # Clientes totales
        ct = dataframe[col_cliente].nunique()

        return mt, ct

    def validar_formato_fecha(self, fecha : str) -> bool:
        # Expresión regular para el formato MM-DD (mes y día válidos)
        if re.match(r'^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', fecha):
            return True
        return False


    def plot_total_amount_by_transaction_date(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_date : str ='TRANSACTION DATE',  horizontal_line_value : bool | None = None) -> matplotlib.figure.Figure:
        """'
        Creates and returns a bar chart of total amounts by transaction date.

        Parameters:
        dataframe (DataFrame): A DataFrame with 'TRANSACTION DATE' and 'AMOUNT' columns.
        horizontal_line_value (float, optional): The y-value at which to draw a horizontal line.

        Returns:
        fig (Figure): The matplotlib figure object containing the plot.
        """
        # Group by transaction date and sum amounts
        dataframe['FORMAT'] = dataframe[col_date].astype(str).apply(self.validar_formato_fecha)
        if dataframe['FORMAT'].all():
            dataframe[col_date] = '2000-' + dataframe[col_date]  # Añadir el año 2000
            dataframe[col_date] = pd.to_datetime(dataframe[col_date], format='%Y-%m-%d')

        dataframe[col_date] =pd.to_datetime(dataframe[col_date]) #dataframe[col_date].astype(str)
        transaction_date_amounts = dataframe.groupby(col_date)[col_analisis].sum().reset_index()
        transaction_date_amounts[col_analisis] = pd.to_numeric(transaction_date_amounts[col_analisis], errors='coerce')
        
        # Convert Period to Timestamp (if applicable)
        if isinstance(transaction_date_amounts[col_date].dtype, pd.core.dtypes.dtypes.PeriodDtype):
            transaction_date_amounts[col_date] = transaction_date_amounts[col_date].dt.to_timestamp()

        # Plotting
        fig, ax = plt.subplots(figsize=(10,5)) 
        ax.plot(transaction_date_amounts[col_date], transaction_date_amounts[col_analisis], 'go', color = '#00008B')
        ax.set_title('Monto total por fecha de transacción', loc = 'left', fontdict = {'size': 25})
        ax.grid(False)
        
        
        # Set xticks for unique months
        #unique_months = transaction_date_amounts['TRANSACTION DATE'].dt.to_period('M').unique()
        #ax.set_xticks(unique_months.start_time)
        #ax.set_xticklabels(unique_months.astype(str), rotation=45)

        # Add horizontal line if specified
        if horizontal_line_value is not None:
            ax.axhline(y=horizontal_line_value, color='r', linestyle='--', label='Percentil')
            ax.legend()

        return fig


    def plot_total_amount_by_customer_cluster(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_id_cliente : str = 'cliente_Skey',horizontal_line_value : bool | None = None) -> matplotlib.figure.Figure:
        """'
        Creates and returns a scatter plot of total amounts by customer, grouped by cluster or quantile.

        Parameters:
        dataframe (DataFrame): A DataFrame with 'cliente_Skey' and 'Cluster' columns.
        col_analisis (str, optional): The name of a column in the DataFrame that contains the amounts to be analyzed. If not provided, the default 'AMOUNT' column will be used.
        horizontal_line_value (float, optional): The y-value at which to draw a horizontal line.

        Returns:
        fig (Figure): The matplotlib figure object containing the plot.
        """
        # Scatter plot for customers vs amount with figsize=(20, 12)
        fig = plt.figure(figsize=(20, 12))
        sns.scatterplot(x=col_id_cliente, y=col_analisis, hue='Cluster', palette='muted', data=dataframe)
        plt.title('Montos por clientes', loc = 'left', fontdict = {'size': 25})
        plt.grid(False)
        plt.ylabel('')
        # Optional horizontal line
        if horizontal_line_value is not None:
            plt.axhline(y=horizontal_line_value, color='r', linestyle='--', label='Percentil')
            plt.legend()

        return fig


    def plot_total_amount_by_transaction_date_cluster(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_date : str = 'TRANSACTION FECHA', horizontal_line_value : bool | None  = None,) -> matplotlib.figure.Figure:
        """
        Creates and returns a scatter plot of total amounts by transaction date, grouped by cluster or quantile.

        Parameters:
        dataframe (DataFrame): A DataFrame with 'Cluster' column.
        col_analisis (str, optional): The name of a column in the DataFrame that contains the amounts to be analyzed. If not provided, the default 'AMOUNT' column will be used.
        col_date (str, optional): The name of a column in the DataFrame that contains dates to be analyzed. If not provided, the default 'TRANSACTION FECHA' column will be used.
        horizontal_line_value (float, optional): The y-value at which to draw a horizontal line.

        Returns:
        plt (Figure): The matplotlib figure object containing the plot.
        """
        dataframe['FORMAT'] = dataframe[col_date].astype(str).apply(self.validar_formato_fecha)
        if dataframe['FORMAT'].all():
            dataframe[col_date] = '2000-' + dataframe[col_date]  # Añadir el año 2000
            dataframe[col_date] = pd.to_datetime(dataframe[col_date], format='%Y-%m-%d')
        dataframe[col_date] = pd.to_datetime(dataframe[col_date])
        # Scatter plot for transaction date vs amount with figsize=(20, 12)
        fig = plt.figure(figsize=(20, 12))
        sns.scatterplot(x=col_date, y= col_analisis, hue='Cluster', palette='muted', data=dataframe)
        plt.title('Montos por fecha de transacción',  loc = 'left', fontdict = {'size': 25})
        plt.grid(False)
        plt.xlabel('')
        plt.ylabel('')
        

        # Optional horizontal line
        if horizontal_line_value is not None:
            plt.axhline(y=horizontal_line_value, color='r', linestyle='--', label='Percentil')
            plt.legend()

        return fig


    def plot_total_amount_by_customer(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_id_cliente : str ='cliente_Skey', horizontal_line_value : bool | None = None) -> matplotlib.figure.Figure:
        """
        Creates and returns a bar chart of total amounts by customer.

        Parameters:
        dataframe (DataFrame): A DataFrame with 'cliente_Skey' and 'AMOUNT' columns.
        col_analisis (str, optional): The name of a column in the DataFrame that contains the amounts to be analyzed. If not provided, the default 'AMOUNT' column will be used.
        horizontal_line_value (float, optional): The y-value at which to draw a horizontal line.

        Returns:
        fig (Figure): The matplotlib figure object containing the plot.
        """
        print(col_id_cliente)
        customer_amounts = dataframe.groupby(col_id_cliente)[col_analisis].sum().reset_index()
        customer_amounts[col_analisis] = pd.to_numeric(customer_amounts[col_analisis], errors='coerce')
        customer_amounts[col_id_cliente] = customer_amounts[col_id_cliente].astype(str)

        fig, ax = plt.subplots(figsize=(10, 5))
        bar_container = ax.bar(customer_amounts[col_id_cliente], customer_amounts[col_analisis], color = '#00008B')
        ax.set_title('Monto total por cliente',loc = 'left', fontdict = {'size': 25})
        ax.set_xticks(range(len(customer_amounts[col_id_cliente])))
        ax.set_xticklabels(customer_amounts[col_id_cliente])
        #ax.bar_label(bar_container, fmt = 'Q{:,.0f}')
        ax.grid(False)

        # Add horizontal line if specified
        if horizontal_line_value is not None:
            ax.axhline(y=horizontal_line_value, color='r', linestyle='--', label='Percentil')
            ax.legend()

        return fig


    # Función para creación de tablas de quantiles
    def quantile_table(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT') -> pd.DataFrame:
        """
        Generates quantile values from the 75th percentile to the 100th percentile in steps of 1%.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing a column with numerical values, typically 'AMOUNT'.
        col_analisis (str, optional): The name of the column containing the values to be analyzed. Defaults to 'AMOUNT' if not provided.

        Returns:
        DataFrame: A DataFrame containing the quantiles from the 75th to the 100th percentile in 1% increments.
            The DataFrame has the quantile values as indices and the corresponding amount values.
        """
        # Creamos los valores de quantiles desde 75% hasta 100% por incrementos de 1%
        quantiles = dataframe[col_analisis].quantile([i/100 for i in range(75, 101)])

        # Guardamos la información para mejor representación
        quantile_df = pd.DataFrame({
            'Percentil': quantiles.index * 100,  # Converting to percentage
            'Monto': quantiles.values
        })
        quantile_df.style.hide()

        # Realizamos una modificación para mostrar todos los dígitos
        pd.set_option('display.float_format', '{:.2f}'.format)

        # Mostramos la tabla con la información
        return quantile_df





    # ---------------------------- STEPS --------------------------------------------- >
    def first_step(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_id_cliente : str = 'cliente_Skey') -> tuple[float, int]: # Mostrar monto y clientes totales
        """
        Calls the 'estats_base' function to calculate the total sum of amounts and the count of unique clients.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing a column with numerical values, typically 'AMOUNT', and a column identifying unique clients (e.g., 'cliente_Skey').
        col_analisis (str, optional): The name of the column containing the values to be analyzed. Defaults to 'AMOUNT' if not provided.

        Returns:
        tuple: A tuple containing:
            - mt (float): The total sum of the specified amounts from the 'col_analisis' column.
            - ct (int): The count of unique clients, determined from the 'cliente_Skey' column in the DataFrame.
        """
        # Monto total y clientes totales
        mt, ct = self.estats_base(dataframe, col_analisis,col_id_cliente)
        return mt, ct

    def second_step(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_date : str = 'TRANSACTION DATE', col_id_cliente : str = 'cliente_Skey') -> tuple[matplotlib.figure.Figure, matplotlib.figure.Figure]: # Primeras gráficas: clientes vs montos y fechas vs montos
        """
        Generates two graphs: one showing the total amounts by customer, and another showing the total amounts by transaction date.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and one with transaction dates (e.g., 'TRANSACTION DATE').
        col_analisis (str, optional): The name of the column containing the amounts to be analyzed. Defaults to 'AMOUNT' if not provided.
        col_date (str, optional): The name of the column containing the transaction dates to be analyzed. Defaults to 'TRANSACTION DATE' if not provided.

        Returns:
        list: A list containing two plotly.graph_objects.Figure objects:
            - graph_am_cust (Figure): A graph showing the total amounts by customer.
            - graph_am_tr_date (Figure): A graph showing the total amounts by transaction date.
        """
        # Graficar montos contra fechas y montos contra código de cliente
        graph_am_cust = self.plot_total_amount_by_customer(dataframe, col_analisis,col_id_cliente)
        graph_am_tr_date = self.plot_total_amount_by_transaction_date(dataframe,col_analisis, col_date)

        return [graph_am_cust,graph_am_tr_date]


    def third_step(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT') -> pd.DataFrame: # Tabla de quantiles
        """
        Generates an HTML table displaying the quantiles of data from the 75th percentile to the 100th percentile. (not HTML anymore, holy shit that is fucking ugly)

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least one column with numerical values (typically 'AMOUNT').
        col_analisis (str, optional): The name of the column containing the values to be analyzed. Defaults to 'AMOUNT' if not provided.

        Returns:
        str: An HTML table (as a string) displaying the quantiles of the specified column. The table includes quantiles from the 75th to the 100th percentile.
        """
        html_table = self.quantile_table(dataframe,col_analisis)#.to_html(index = False)

        return html_table
    

    def forth_step(self, dataframe : pd.DataFrame, S_N_quantile : str | None, col_analisis : str = 'AMOUNT', col_date : str = 'TRANSACTION DATE', col_id_cliente : str = 'cliente_Skey', quantile : int = 0.95) -> tuple[pd.DataFrame, matplotlib.figure.Figure]: # Selección del model
        """
        Generates three graphs:
        1. Total amount by customer, with a horizontal line representing the data cutoff for training.
        2. Total amount by transaction date, with a horizontal line representing the data cutoff.
        3. The elbow method graph to help select the optimal number of clusters for data analysis.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and another with date values (e.g., 'TRANSACTION DATE').
        S_N_quantile (str): A 'Si' or 'No' value to specify whether the quantile cutoff should be different from the default.
        col_analisis (str, optional): The name of the column containing the values to be analyzed (e.g., 'AMOUNT'). Defaults to 'AMOUNT' if not provided.
        col_date (str, optional): The name of the column containing the transaction dates to be analyzed. Defaults to 'TRANSACTION DATE' if not provided.

        Returns:
        list: A list containing:
            - dataframe (DataFrame): A DataFrame with the filtered values based on the quantile or cutoff.
            - graph1 (Fig): A figure showing total amount by customer with a percentile line indicating the cutoff.
            - graph2 (Fig): A figure showing total amount by transaction date with a percentile line indicating the cutoff.
            - elbow_graph (Fig): A figure representing the elbow rule to select the optimal number of clusters.
        """
        if S_N_quantile == "Si":
            # Seleccionar el quantile adecuado
            try:
                #quantile = float(input("Seleccione un quantile (entre 75% y 99% inclusive)"))
                if (75 <= quantile < 100):
                    quantile = quantile/100
                elif (0.75 <= quantile < 1):
                    pass
                else:
                    raise ValueError(f"El valor {quantile} no se encuentra entre 0.75 y 1 o entre 75 y 100")
            except ValueError as e:
                print(e)

        # Eliminamos a partir del 95%
        percentile_95 = dataframe[col_analisis].quantile(quantile)

        # Graficamos a partir del corte
        #graph1 = self.plot_total_amount_by_customer(dataframe,col_analisis,col_id_cliente, percentile_95)
        #graph1.show()

        # Graficamos a partir del corte
        #graph2 = self.plot_total_amount_by_transaction_date(dataframe, col_analisis,col_date, percentile_95)
        #graph2.show()

        # Filtramos los datos
        dataframe = dataframe[dataframe[col_analisis] <= percentile_95]

        # Extraer la variable 'AMOUNT' para el entrenamiento
        x = dataframe[[col_analisis]].values

        # Lista para almacenar las inercias
        inertia = []

        # Probar con k desde 1 hasta 10
        k_range = range(1, min(11, len(dataframe)))
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=0)
            kmeans.fit(x)
            inertia.append(kmeans.inertia_)
        

        # Graficar la regla del codo
        fig = plt.figure(figsize=(8, 5))
        plt.plot(k_range, inertia, marker='o',color='#00008B')
        plt.xlabel('Número de clusters (k)')
        plt.title('Regla del codo para determinar k óptimo', loc='left')
        plt.grid(False)

        return [dataframe, fig] #[dataframe,graph1,graph2,fig] 



    def fifth_step(self, dataframe : pd.DataFrame, S_N_cluster : str | None, col_analisis : str = 'AMOUNT', col_date : str = 'TRANSACTION DATE', col_id_cliente = 'cliente_Skey', num_clusters : int = 3) -> pd.DataFrame: # Definición de modelo, predicción de cluster
        """
        Generates two graphs and a DataFrame:
        1. Amounts by customer, with clusters assigned.
        2. Amounts by transaction date, with clusters assigned.
        3. A DataFrame with a new 'Cluster' column indicating the assigned cluster for each data point.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and another with date values (e.g., 'TRANSACTION DATE').
        S_N_cluster (str): A 'Yes' or 'No' value indicating whether the number of clusters should differ from the default. If 'Yes', a custom number of clusters can be specified.
        col_analisis (str, optional): The name of the column containing the values to be analyzed (e.g., 'AMOUNT'). Defaults to 'AMOUNT' if not provided.
        col_date (str, optional): The name of the column containing the transaction dates to be analyzed. Defaults to 'TRANSACTION DATE' if not provided.

        Returns:
        list: A list containing:
            - cluster_df (DataFrame): A DataFrame with the 'Cluster' column indicating the predicted cluster for each row based on the analysis.
            - graph_am_ct_cluster (Figure): A figure showing the amounts by customer, with clusters visually assigned.
            - graph_tr_dt_cluster (Figure): A figure showing the amounts by transaction date, with clusters visually assigned.
        """
        if S_N_cluster == "Si":
            # Seleccionar la cantidad de clusters adecuados
            try:
                if not (0 < num_clusters < 11):
                    raise ValueError(f"El valor {num_clusters} no se encuentra entre 1 y 10.")
            except ValueError as e:
                print(e)

        # Extraer la variable 'AMOUNT' para el entrenamiento
        x = dataframe[[col_analisis]].values
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=0)

        dataframe['Cluster'] = kmeans.fit_predict(x)

        # Call plotting functions to generate the graphs
        #graph_am_ct_cluster = self.plot_total_amount_by_customer_cluster(dataframe, col_analisis, col_id_cliente)
        #graph_tr_dt_cluster = self.plot_total_amount_by_transaction_date_cluster(dataframe, col_analisis,col_date)

        return dataframe #[dataframe, graph_am_ct_cluster,graph_tr_dt_cluster]

    def sixth_step(self, dataframe : pd.DataFrame, col_analisis : str = 'AMOUNT', col_id_cliente : str = 'cliente_Skey') -> pd.DataFrame:
        """
        Generates a DataFrame containing statistical summaries for each cluster based on the specified amount column.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and another with date values (e.g., 'TRANSACTION DATE').
        col_analisis (str, optional): The name of the column containing the values to be analyzed (e.g., 'AMOUNT'). Defaults to 'AMOUNT' if not provided.

        Returns:
        cluster_stats (DataFrame): A DataFrame containing statistical summaries (e.g., mean, median, standard deviation) for each cluster, based on the specified amount column.
        """
        # Creamos una nueva tabla con las estadísticas
        cluster_stats = dataframe.groupby('Cluster').agg({
            col_id_cliente: 'nunique',  # Número de clientes únicos
            col_analisis: ['count','min', 'max', 'mean', 'std', 'sum']  # Estadísticas para el monto
        }).reset_index()

        # Renombrar las columnas para claridad
        cluster_stats.columns = [
            'Cluster',
            'Número de Clientes',
            'Número de Transacciones',
            'Monto Mínimo',
            'Monto Máximo',
            'Monto promedio',
            'Desviación estándar',
            'Monto total'
        ]

        return cluster_stats



    # Aplicación de lof
    def seventh_step(self, dataframe : pd.DataFrame, num_cluster : int, col_analisis : str = 'AMOUNT', neighbors : int = 20) -> pd.DataFrame:
        """
        Generates a DataFrame containing Local Outlier Factor (LOF) scores for each data point based on the specified amount column.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and another with date values (e.g., 'TRANSACTION DATE').
        col_analisis (str, optional): The name of the column containing the values to be analyzed (e.g., 'AMOUNT'). Defaults to 'AMOUNT' if not provided.
        neighbors (int): The number of neighbors to use for LOF calculation. This parameter controls the sensitivity of the anomaly detection.

        Returns:
        lof_data (DataFrame): A DataFrame containing the values from the specified amount column along with their respective LOF scores, indicating how much of an outlier each value is.
        """
        # Seleccionar el cluster para aplicar LOF
        try:
            if not (0 <=  num_cluster <= dataframe['Cluster'].max()):
                raise ValueError(f"El valor {0} no se encuentra entre 1 y {1}.".format(num_cluster, dataframe['Cluster'].max()))
        except ValueError as e:
            print(e)
            return
        # Filtramos para tener la información solo del último cluster
        last_cluster_data = dataframe[dataframe['Cluster'] == num_cluster][[col_analisis, 'Cluster']]

        # Aplicar LOF al Cluster seleccionado
        lof = LocalOutlierFactor(n_neighbors=neighbors)
        lof.fit(last_cluster_data)

        # Convertir los punteos LOF negativos a positivos
        negative_lof_scores = lof.negative_outlier_factor_
        positive_lof_scores = -negative_lof_scores  # Convert to positive

        # Crear un DataFrame para los punteos LOF y la data
        lof_data = pd.DataFrame(last_cluster_data, columns=[col_analisis])
        lof_data['LOF_Score'] = positive_lof_scores

        # Ordenamos los datos
        lof_data = lof_data.sort_values(by=['LOF_Score', col_analisis])
        # Filtrar los datos para cuando LOF es mayor que 1 y ordenamos por el punteo 
        lof_data = lof_data[lof_data['LOF_Score'] > 1.10]

        lof_data = lof_data.rename(columns = {col_analisis:'Monto','LOF_Score':'Valor atípico local'})

        lof_data =  lof_data.T.reset_index()
        #lof_data.columns =  [None] *  len(lof_data.columns)

    
        return  lof_data

    # Método de redondeo
    def eight_step(self, umb : int | float) -> int:
        """
        Generates a threshold factor to apply a floor adjustment to the given amount based on the specified value.

        Parameters:
        umb (int | float): The threshold value to which the floor adjustment will be applied. This value will determine the minimum possible value after applying the floor operation.

        Returns:
        adjusted_value (int): The value after applying the floor adjustment, ensuring it does not fall below the specified threshold.
        """
        try:
            umb = float(umb)
        except ValueError as e:
            print(e)
            return
        match umb:
            case umb if 0 <= umb < 10:
                factor = 10**0
            case umb if 10 <= umb < 100:
                factor = 10**1
            case umb if 100 <= umb < 1_000:
                factor = 10**1
            case umb if 1_000 <= umb < 10_000:
                factor = 10**2
            case umb if 10_000 <= umb < 100_000:
                factor = 10**2
            case umb if 100_000 <= umb < 1_000_000:
                factor = 10**2
            case umb if 1_000_000 <= umb < 10_000_000:
                factor = 10**3
            case umb if 10_000_000 <= umb < 100_000_000:
                factor = 10**3
            case umb if umb >= 100_000_000:
                factor = 10**4
            case _:
                return "Value out of range"
        # Return the adjusted value using floor
        return math.floor(umb / factor) * factor



    # Caracterización del parámetro
    def ninth_step(self, dataframe: pd.DataFrame, umb,col_analisis : str = 'AMOUNT', col_date : str = 'TRANSACTION DATE', col_id_cliente : str = 'cliente_Skey', t : int = 12) -> int:
        """
        Generates a DataFrame containing the results of the methodology, including detected transactions, clients, and related parameters.

        Parameters:
        dataframe (DataFrame): A pandas DataFrame containing at least two columns: one with numerical values (typically 'AMOUNT') and another with date values (e.g., 'TRANSACTION DATE').
        col_analisis (str, optional): The name of the column containing the values to be analyzed (e.g., 'AMOUNT'). Defaults to 'AMOUNT' if not provided.
        col_date (str, optional): The name of the column containing the transaction dates to be analyzed. Defaults to 'TRANSACTION DATE' if not provided.
        t (int, optional): The period of the data in months.

        Returns:
        tuple: A tuple containing:
            - new_row (DataFrame): A DataFrame containing the results of the methodology, such as detected transactions, clients, and associated parameters.
            - df_excel (DataFrame): A DataFrame with the amounts categorized as alerts for further analysis or reporting.
        """
        dataframe_alertado = dataframe[dataframe[col_analisis] >= umb]
        clientes_alertados = dataframe_alertado[col_id_cliente].nunique()
        monto_total_transado = dataframe[col_analisis].sum()
        porcentaje_total_monitoreado = dataframe_alertado[col_analisis].sum()/monto_total_transado
        alertas_generadas = len(dataframe_alertado)
        df_excel = dataframe_alertado[[col_id_cliente,col_analisis,col_date]]
        porcentaje_clientes_monitoreados = clientes_alertados / dataframe[col_id_cliente].nunique()
        estimado_mes = alertas_generadas / t
        data = [umb, dataframe[col_id_cliente].nunique(), monto_total_transado, porcentaje_total_monitoreado * 100, alertas_generadas,
                porcentaje_clientes_monitoreados * 100, (alertas_generadas / len(dataframe)) * 100, estimado_mes]


        # Creamos un DataFrame con la información que queremos agregar
        new_row = pd.DataFrame([data], columns=self.resultados.columns)
        return [new_row,df_excel]
    

    ################################################
    ####################### POST ###################
    #def analizar_alertas_por_umbral(self, df: pd.DataFrame, umbrales: list, t : int = 12, col_analisis : str = 'monto', col_date : str = 'fecha', col_id_cliente : str = 'cliente', title : str = 'Alertas generadas vs Umbral') -> pd.DataFrame:
    #    """
    #    Analyzes the number of alerts generated for different threshold values and visualizes the results.
#
    #    This method iterates over a list of threshold values, applies the alert detection methodology (via `ninth_step`), 
    #    collects the number of alerts generated for each threshold, and produces a line plot showing how alerts vary with the threshold.
#
    #    Parameters:
    #    df (DataFrame): A pandas DataFrame containing transactional data. Must include at least:
    #        - A numerical column for analysis (e.g., 'monto').
    #        - A date column indicating transaction dates.
    #        - A client identifier column.
    #    umbrales (list): A list of threshold values to evaluate.
    #    t (int, optional): The time period in months used to normalize alerts (defaults to 12 months).
    #    col_analisis (str, optional): Name of the column with values to analyze. Defaults to 'monto'.
    #    col_date (str, optional): Name of the column with transaction dates. Defaults to 'fecha'.
    #    col_id_cliente (str, optional): Name of the column identifying clients. Defaults to 'cliente'.
    #    title (str, optional): Title for the generated plot. Defaults to 'Alertas generadas vs Umbral'.
#
    #    Returns:
    #    DataFrame: A DataFrame summarizing the number of alerts generated for each threshold and the corresponding normalized (monthly) count.
    #    """
    #    # donde se almacenaran los parametros con sus alertas generadas
    #    resultados = []
#
    #    # loop para valuar varios umbrales
    #    for umb in umbrales:
    #        df_resultado, _ = self.ninth_step(df, umb=umb, col_analisis=col_analisis, col_date=col_date, col_id_cliente=col_id_cliente)
    #        # Asegúrate de que no esté vacío
    #        if not df_resultado.empty:
    #            parametro = df_resultado.loc[0, 'Parámetro']
    #            alertas = df_resultado.loc[0, 'Alertas generadas']
    #            resultados.append({'Umbral': parametro, 'Alertas generadas': alertas})
#
    #    # Crear DataFrame de resultados
    #    df_alertas = pd.DataFrame(resultados)
#
    #    # calculamos las alertas mensuales
    #    if isinstance(t, int):
    #        df_alertas['mensuales'] = df_alertas['Alertas generadas'] / t
    #    else: 
    #        df_alertas['mensuales'] = df_alertas['Alertas generadas'] / 12
#
    #    # Graficar
    #    plt.figure(figsize=(10, 6))
    #    plt.plot(df_alertas['Umbral'], df_alertas['mensuales'], marker='o')
    #    plt.title(title)
    #    plt.xlabel('Umbral')
    #    plt.ylabel('Alertas Generadas x Mes')
    #    plt.grid(True)
    #    plt.tight_layout()
    #    plt.show()
#
    #    return df_alertas


    def analizar_alertas_por_umbral(self, df: pd.DataFrame, umbrales: list, t: int = 12,
                                    col_analisis: str = 'monto', col_date: str = 'fecha',
                                    col_id_cliente: str = 'cliente', title: str = 'Alertas generadas vs Umbral',
                                    umbral_destacado: float = None) -> pd.DataFrame:
        """
        Analiza el número de alertas generadas para distintos valores de umbral y visualiza los resultados,
        con opción de destacar un umbral específico en rojo.

        Parámetros adicionales:
        umbral_destacado (float, opcional): Si se pasa un número, se mostrará en rojo en la gráfica.
        """
        resultados = []

        # Loop para evaluar distintos umbrales
        for umb in umbrales:
            df_resultado, _ = self.ninth_step(df, umb=umb, col_analisis=col_analisis, col_date=col_date, col_id_cliente=col_id_cliente)
            if not df_resultado.empty:
                parametro = df_resultado.loc[0, 'Parámetro']
                alertas = df_resultado.loc[0, 'Alertas generadas']
                resultados.append({'Umbral': parametro, 'Alertas generadas': alertas})

        df_alertas = pd.DataFrame(resultados)

        # Calculamos alertas mensuales
        df_alertas['mensuales'] = df_alertas['Alertas generadas'] / t

        # Si hay un umbral destacado, ajustamos la lista
        if umbral_destacado is not None:
            if umbral_destacado not in df_alertas['Umbral'].values:
                # Agregamos el umbral destacado con alertas = NaN temporalmente
                df_alertas = pd.concat([df_alertas, pd.DataFrame([{'Umbral': umbral_destacado, 'Alertas generadas': 0, 'mensuales': 0}])])
                df_alertas = df_alertas.sort_values('Umbral').reset_index(drop=True)
            # Creamos una columna de colores
            df_alertas['color'] = ['red' if x == umbral_destacado else 'blue' for x in df_alertas['Umbral']]
        else:
            df_alertas['color'] = 'blue'

        # Graficar
        plt.figure(figsize=(10, 6))
        plt.scatter(df_alertas['Umbral'], df_alertas['mensuales'], c=df_alertas['color'], s=100, zorder=2)
        plt.plot(df_alertas['Umbral'], df_alertas['mensuales'], color='blue', zorder=1)
        plt.title(title)
        plt.xlabel('Umbral')
        plt.ylabel('Alertas Generadas x Mes')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        return df_alertas
     


