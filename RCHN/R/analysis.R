# -------------------------------------------------------------------------
# Archivo: analysis.R
# Descripción: Contiene funciones para analisis generales.
# Autor: Diego Sarceño
# -------------------------------------------------------------------------

#' @title Función de redondeo
#' 
#' @description Función que toma un número entero o decimal y lo redondea según ciertas reglas y según su orden de magnitud.
#' 
#' @param monto Número a redondear
#' @return Un entero redondeado
#' @examples
#' \dontrun{
#' redondeado <- redondear(monto)
#' }
#' @export
redondear <- function(monto) {
  intervalos <- data.frame(
    linf = c(0, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000),
    lsup = c(10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, Inf),
    f = c(1, 10, 10, 100, 100, 100, 1000, 1000, 10000)
  )
  
  row <- intervalos[monto >= intervalos$linf & monto < intervalos$lsup, ]
  return(floor(monto / row$f) * row$f)
}


#' @title Método de Tukey
#' 
#' @description Función que implementa el método de tukey por rango intercuartílico para la detección de outliers.
#'
#' @param df Dataframe
#' @param varColumn Nombre de la columna a analizar.
#' @param outputColumne Nombre de la columna en la que se categorizan como outliers o no (por defecto 'outlier').
#' @param c Factor de ajuste (por defecto 1.5).
#' @return Dataframe original con una nueva columna que indica si un valor es un outlier (1) o no (0).
#' @examples
#' \dontrun{
#' resultado <- tukey(df, "valor")
#' }
#' @export
tukey <- function(df, varColumn, outputColumn = 'outlier', c = 1.5) {
  q1 <- quantile(df[[varColumn]], 0.25, na.rm = TRUE)
  q3 <- quantile(df[[varColumn]], 0.75, na.rm = TRUE)
  IQR_value <- q3 - q1
  
  x_inf <- q1 - c * IQR_value
  x_sup <- q3 + c * IQR_value
  
  df[[outputColumn]] <- ifelse(df[[varColumn]] < x_inf | df[[varColumn]] > x_sup, 1, 0)
  return(df)
}


#' @title Método Alternativo de Tukey
#' 
#' @description Otra implementación del método de tukey, basada en la media superior e inferior.
#' 
#' @param df Dataframe
#' @param varColumn Nombre de la columna a analizar.
#' @param outputColumne Nombre de la columna en la que se categorizan como outliers o no (por defecto 'outlier').
#' @param c Factor de ajuste (por defecto 1.5).
#' @param low_percentile Percentil inferior para la filtración de datos antes del análisis (por defecto 0.05).
#' @param high_percentile Percentil superior para la filtración de datos antes del análisis (por defecto 0.95). 
#' @param filter Booleano. Si es TRUE, se filtran los datos dentro del rango de percentiles antes de calcular los límites (por defecto TRUE).
#' @return Dataframe original con una nueva columna que indica si un valor es un outlier (1) o no (0).
#' @examples
#' \dontrun{
#' resultado <- tukey_alternative(df, "valor")
#' }
#' @export
tukey_alternative <- function(df, varColumn, outputColumn = "outlier", c = 1.5, low_percentile = 0.05, high_percentile = 0.95, filter = TRUE) {
  # Filtrar valores no NA
  data <- df[!is.na(df[[varColumn]]), ]
  
  # Calcular percentiles
  low <- quantile(data[[varColumn]], low_percentile, na.rm = TRUE)
  high <- quantile(data[[varColumn]], high_percentile, na.rm = TRUE)
  
  # Filtrar datos según percentiles (si filter = TRUE)
  if (filter) {
    data <- subset(data, data[[varColumn]] >= low & data[[varColumn]] <= high)
  }
  
  # Medidas estadísticas
  media <- mean(data[[varColumn]], na.rm = TRUE)
  mediana <- median(data[[varColumn]], na.rm = TRUE)
  mediasup <- mean(data[data[[varColumn]] > mediana, varColumn], na.rm = TRUE)
  mediainf <- mean(data[data[[varColumn]] < mediana, varColumn], na.rm = TRUE)
  
  # Cálculo de límites ajustados por 'c'
  xinf <- media - mediainf
  xsup <- mediasup - media
  x_sup <- media + c * xsup
  x_inf <- media - c * xinf
  
  # Marcar outliers en la columna de salida
  df[[outputColumn]] <- 0
  df[[outputColumn]][df[[varColumn]] < x_inf | df[[varColumn]] > x_sup] <- 1
  
  return(df)
}


#' @title Tabla con los Percentiles de un Dataset
#' 
#' @description Genera una tabla con los percentiles de un dataframe proporcionado
#' 
#' @param df Dataframe donde se encuentra la columna a utilizar.
#' @param columna Nombre de la columna a analizar.
#' @param pasos Rango de la división de percentiles (por defecto 1).
#' @return Un dataframe con los percentiles de la columna proporcionada
#' @examples 
#' \dontrun{
#' result <- table_percentiles(df, "valor")
#' }
#' @export
table_percentiles <- function(df, columna, pasos = 1) {
  percentiles <- seq(0, 1, by = pasos / 100)
  values <- quantile(df[[columna]], percentiles, na.rm = TRUE)
  result <- data.frame(Percentil = percentiles * 100, Valor = values)

  return(result)
}
