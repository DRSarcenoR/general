# -------------------------------------------------------------------------
# Archivo: general.R
# Descripción: Funciones de uso general.
# Autor: Diego Sarceño
# -------------------------------------------------------------------------


#' @title carga_paquetes
#' 
#' @description Esta función carga los paquetes comúnmente utilizados para análisis de datos, visualización y modelado estadístico.
#'
#' @import dplyr
#' @import tidyr
#' @import data.table
#' @import readr
#' @import cluster
#' @import ggplot2
#' @import plotly
#' @import ggmap
#' @import leaflet
#' @import caret
#' @import randomForest
#' @import e1071
#' @import tidyverse
#' @import gapminder
#' @import palmerpenguins
#' @import nycflights13
#' @import readxl
#' @import writexl
#' @import openxlsx
#' @import RSQLite
#' @import RMySQL
#' @import RPostgreSQL
#' @import haven
#' @import DBI
#' @import odbc
#' @import jsonlite
#' @import roxygen2
#' @import usethis
#' @import devtools
#' @import microbenchmark
#'
#' @examples
#' carga_paquetes()
#' 
#' @export
carga_paquetes <- function() {
  library(dplyr)
  library(tidyr)
  library(data.table)
  library(readr)
  library(cluster)
  library(ggplot2)
  library(plotly)
  library(ggmap)
  library(leaflet)
  library(caret)
  library(randomForest)
  library(e1071)
  library(tidyverse)
  library(gapminder)
  library(palmerpenguins)
  library(nycflights13)
  library(readxl)
  library(writexl)
  library(openxlsx)
  library(RSQLite)
  library(RMySQL)
  library(RPostgreSQL)
  library(haven)
  library(DBI)
  library(odbc)
  library(jsonlite)
  library(roxygen2)
  library(usethis)
  library(devtools)
  library(microbenchmark)
}
