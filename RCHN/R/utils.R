# -------------------------------------------------------------------------
# Archivo: utils.R
# Descripción: Funciones de utilidades varias.
# Autor: Diego Sarceño
# -------------------------------------------------------------------------

#' @title Lectura de Muchos Excels
#' 
#' @description Función que lee todos los archivos de excel en una ruta dada.
#' 
#' @param path Ruta a la carpeta que se desea utilizar.
#' @return lista de todos los dataframes leídos.
#' @examples
#' \dontrun{
#' dfs_list <- read_lots_excels('path/to/directory')
#' }
#' @export
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