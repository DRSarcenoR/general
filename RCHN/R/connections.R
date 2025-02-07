# -------------------------------------------------------------------------
# Archivo: connections.R
# Descripción: Contiene funciones para conectar a bases de datos SQL Server.
# Autor: Diego Sarceño
# -------------------------------------------------------------------------


#' Lista de credenciales para bases de datos
#'
#' Contiene la información de conexión a las bases de datos "Banco" y "Seguros".
#' Se usa internamente en la función `connection()`.
#'
#' @keywords internal
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

#' @title Ejecutar una consulta SQL en una base de datos
#'
#' @description Se conecta a una base de datos SQL Server mediante ODBC y ejecuta una consulta SQL.
#'
#' @param query Cadena de texto con la consulta SQL que se desea ejecutar.
#' @param db Número entero: `1` para la base de datos "Banco", `2` para "Seguros".
#' @return Un dataframe con los resultados de la consulta o `NULL` si ocurre un error.
#' @examples
#' \dontrun{
#' result <- connection("SELECT * FROM tabla", db = 1)
#' }
#' @export
connection <- function(query, db) {
  select_db <- c("Banco", "Seguros")
  selected_db <- select_db[db]
  
  tryCatch({
    con <- dbConnect(
      odbc::odbc(),
      Driver = credentials$DW[[selected_db]]$driver,
      Server = credentials$DW[[selected_db]]$server,
      Database = credentials$DW[[selected_db]]$database,
      Port = credentials$DW[[selected_db]]$port,
      Trusted_Connection = "Yes"
    )
    
    df <- dbGetQuery(con, query)
    dbDisconnect(con)
    
    return(df)
  }, error = function(e) {
    message("Error: ", e$message)
    return(NULL)
  })
}
