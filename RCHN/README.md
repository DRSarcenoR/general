# Instalación y Actualización del Paquete

El paquete se instaló utilizando los siguientes pasos y comandos en la consola de R.

1. Luego de realizar todos los cambios a los scripts, actualizar y agregar los comentarios para generar la documentación de Roxygen2, se deben correr los siguientes comandos en la consola de R/RStudio:

```R
> library(roxygen2)
> roxygen2::roxygenise()
```

2. Ya con la documentación generada se puede crear el instalador del paquete: `> devtools::build()`. Esto debe de generar un archivo _.tar.gz_.
3. Con este archivo se puede instalar usando la siguiente línea de comandos en la consola de R:

```R
> install.packages("ruta/al/instalador/miPaquete.tar.gz", repos=NULL, type="source")
```

Puede ocurrir que no deje instalarlo por que ya se encuentre activo en el entorno, cosa que se puede resolver haciendo lo siguiente:

```R
> detach("package:miPaquete", unload=TRUE)
```

Para luego realizar la instalación correspondiente. 4. Probar que la instalación se realizó correctamente, revisando la versión del paquete en el entorno de R: `packageVersion(miPaquete)`.

## Actualización del Paquete.

1. Primero realiza los cambios pertinentes al paquete, revisa que las funciones nuevas o sus modificaciones funcionen correctamente y actualiza el archivo DESCRIPTION con las nuevas dependencias, librerías, archivos extra, datos externos y su nueva versión.
2. Ya con lo anterior revisado, procedemos a construir nuevamente el archivo de instalación: `devtools::build()`.
3. Desmontamos el paquete actual:

```R
> detach("package:miPaquete", unload = TRUE)
```

4. Instalamos la nueva versión del paquete.

```R
> install.packages("ruta/al/instalador/miPaquete.tar.gz", repos=NULL, type="source")
```

5. Verificamos la instalación: `packageVersion("miPaquete")`
