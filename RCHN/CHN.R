# Librería de Utilidades en R
#
# Funciones de conexión a bases de datos
#
# Autor: Diego Sarceño
# Contacto: dsarceno68@gmail.com | diego.sarceno@chn.com.gt
# Tel: (+502) 4204 4629
#
# ------------------------------>
# <---- paquetes necesarios ---->
library(DBI)
library(odbc)
library(readxl)
library(ggplot2)
library(dplyr)
library(cluster)
# ------------------------------>

# ------------------------------------------------------------------------->
# funcion que carga los paquetes que mas utilizo
carga_paquetes <- function() {
  # manipulacion y analisis de datos
  library(dplyr) #tidyverse, manipulacion de datos
  library(tidyr) #tidyverse,limpieza y reestructuracion de datos
  library(data.table) # manipulacion de datos rapidos y eficientes
  library(readr) # tidyverse, importacion de datos
  # visualizacion de datos
  library(ggplot2) # tidyverse, visualizacion de datos
  library(plotly) # graficos interactivos
  library(ggmap) # mapas
  library(leaflet) # mapas
  # modelado y analisis estadistico
  library(caret) # creacion de modelos predictivos
  library(randomForest) # algoritmos de random forest
  library(e1071) # funciones para modelos de regresion y clasificacion
  # dataframes para practicar
  #library(iris) # diversos datasets clasicos
  library(tidyverse) # herramientas de manipulacion y visualizacion de datos, incluye datasets
  library(gapminder) # datos de desarrollo mundial
  library(palmerpenguins) # datasets sobre especies de pinguinos, muy utilizado para demostraciones
  library(nycflights13) # informacion sobre vuelos en Nueva York
  # bases de datos
  library(readxl)
  library(writexl)
  library(openxlsx)
  library(RSQLite)
  library(RMySQL)
  library(RPostgreSQL)
  library(haven) # bases de datos SPSS, SAS, STATA
  library(DBI)
  library(odbc)
  library(jsonlite)
  # documentacion de funciones
  library(roxygen2)
  library(usethis) # crea la estructura basica del paquete
  library(devtools) # generar la documentacion
  # da estadísticas detalaldas sobre la ejecución del código
  library(microbenchmark)
}
# ------------------------------------------------------------------------->


# ------------------------------------------------------------------------->
# CONNECTIONS
credentials <- list(
  DW = list(
    Banco = list(
      driver = "ODBC Driver 17 for SQL Server",
      server = "172.31.100.37",
      port = "1433",
      database = "kpi_dataw"
    ),
    Seguros = list(
      driver = "ODBC Driver 17 for SQL Server",
      server = "172.31.100.67",
      port = "1433",
      database = "DW"
    )
  )
)
# ------------------------------------------------------------------------->



# ------------------------------------------------------------------------->
# conneccion a la base
# Función para conexión a bases de datos
connection <- function(query, db) {
  # Seleccionar la base de datos
  select_db <- c("Banco", "Seguros")
  selected_db <- select_db[db]
  
  # Intentar la conexión
  tryCatch({
    con <- dbConnect(
      odbc::odbc(),
      Driver = credentials$DW[[selected_db]]$driver,
      Server = credentials$DW[[selected_db]]$server,
      Database = credentials$DW[[selected_db]]$database,
      Port = credentials$DW[[selected_db]]$port,
      Trusted_Connection = "Yes"
    )
    
    # Ejecutar la consulta
    df <- dbGetQuery(con, query)
    
    # Cerrar conexión
    dbDisconnect(con)
    
    return(df)
  }, error = function(e) {
    message("Error: ", e$message)
    return(NULL)
  })
}
# ------------------------------------------------------------------------->





# ------------------------------------------------------------------------->
# Función para leer múltiples archivos Excel
read_lots_excels <- function(path) {
  if (!dir.exists(path)) {
    message("La carpeta no existe.")
    return(list())
  }
  
  archivos <- list.files(path, pattern = "\\.xls[x]?$", full.names = TRUE)
  if (length(archivos) == 0) {
    message("No se encontraron archivos de Excel en la carpeta.")
    return(list())
  }
  
  dfs <- lapply(archivos, function(archivo) {
    tryCatch(
      read_excel(archivo),
      error = function(e) {
        message("Error al leer el archivo: ", archivo, " - ", e$message)
        return(NULL)
      }
    )
  })
  
  return(dfs)
}
# ------------------------------------------------------------------------->



# ------------------------------------------------------------------------->
# Función para el método del codo en clustering
elbow_test <- function(X_scaled, cluster_range = 1:10, output_name = NULL) {
  inertia_values <- sapply(cluster_range, function(k) {
    kmeans(X_scaled, centers = k, nstart = 10)$tot.withinss
  })
  
  plot(cluster_range, inertia_values, type = "o", col = "blue", xlab = "Número de Clústeres (k)", ylab = "Inercia", main = "Método del Codo")
  if (!is.null(output_name)) {
    ggsave(paste0(output_name, ".pdf"))
  }
}
# ------------------------------------------------------------------------->




# ------------------------------------------------------------------------->
# Función para scatter plot de clustering
scatter_cluster <- function(df, x_col, y_col, cluster_col = "Cluster", output_name = NULL) {
  p <- ggplot(df, aes_string(x = x_col, y = y_col, color = cluster_col)) +
    geom_point() +
    theme_minimal() +
    labs(title = "Clustering de empleados basado en diferencias", x = x_col, y = y_col)
  print(p)
  if (!is.null(output_name)) {
    ggsave(paste0(output_name, ".pdf"))
  }
}
# ------------------------------------------------------------------------->





# ------------------------------------------------------------------------->
# Función para calcular percentiles
table_percentiles <- function(df, columna, pasos = 1) {
  percentiles <- seq(0, 1, by = pasos / 100)
  values <- quantile(df[[columna]], percentiles, na.rm = TRUE)
  data.frame(Percentil = percentiles * 100, Valor = values)
}
# ------------------------------------------------------------------------->





# ------------------------------------------------------------------------->
# Función para detección de outliers basada en Tukey
tukey <- function(df, varColumn, outputColumn, c = 2.5) {
  q1 <- quantile(df[[varColumn]], 0.25, na.rm = TRUE)
  q3 <- quantile(df[[varColumn]], 0.75, na.rm = TRUE)
  IQR_value <- q3 - q1
  
  x_inf <- q1 - c * IQR_value
  x_sup <- q3 + c * IQR_value
  
  df[[outputColumn]] <- ifelse(df[[varColumn]] < x_inf | df[[varColumn]] > x_sup, 1, 0)
  return(df)
}
# ------------------------------------------------------------------------->





# ------------------------------------------------------------------------->
# Función para redondear valores
redondear <- function(monto) {
  intervalos <- data.frame(
    linf = c(0, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000),
    lsup = c(10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, Inf),
    f = c(1, 10, 10, 100, 100, 100, 1000, 1000, 10000)
  )
  
  row <- intervalos[monto >= intervalos$linf & monto < intervalos$lsup, ]
  return(floor(monto / row$f) * row$f)
}
# ------------------------------------------------------------------------->












