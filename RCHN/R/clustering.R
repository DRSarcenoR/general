# -------------------------------------------------------------------------
# Archivo: clustering.R
# Descripción: Contiene funciones de clusterización y graficación
# Autor: Diego Sarceño
# -------------------------------------------------------------------------

#' @title Prueba del Codo
#' 
#' @description Hacer la gráfica para la prueba del codo para un dataset
#'
#' @param data Dataframe para el clustering
#' @param cluster_range n vector numérico con los valores de `k` a evaluar (por defecto 1:10)
#' @param output_name Nombre del archivo PDF donde guardar el gráfico (opcional)
#' @return Un gráfico mostrando la inercia vs número de clusters
#' @examples
#' \dontrun{
#' elbow_test(data, cluster_range = 1:10)
#' }
#' @export
elbow_test <- function(data, cluster_range = 1:10, output_name = NULL) {
  data <- scale(data)

  inertia_values <- sapply(cluster_range, function(k) {
    kmeans(data, centers = k, nstart = 10)$tot.withinss
  })
  
  plot(cluster_range, inertia_values, type = "o", col = "blue", xlab = "Número de Clústeres (k)", ylab = "Inercia", main = "Método del Codo")
  if (!is.null(output_name)) {
    ggsave(paste0(output_name, ".pdf"))
  }
}


#' @title Scatterplot de Clusters
#' 
#' @description Funcion que grafica en 2D los clusteres generados con kmeans
#' 
#' @param df Dataframe segmentado en clusters
#' @param x_col nombre de la columna a colocar en el eje x
#' @param y_col nombre de la columna a colocar en el eje y
#' @param cluster_col Nombre de la columna en la que se encuentra la segmentacion por cluster (por defecto 'Cluster')
#' @param output_name Nombre del archivo PDF donde guardar el gráfico (opcional)
#' @return Un gráfico mostrando las columnas ingresadas.
#' @examples
#' \dontrun{
#' scatter_cluster(df, "eje x", "eje y", "Cluster")
#' }
#' @export
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