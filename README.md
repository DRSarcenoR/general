# General

Paquetes, desarrollos, modelos, etcs. sin categorización definida.

## En este repositorio

```
general/
├── .gitignore
├── CHN/
    ├── CHN/
        ├── __init__.py
        ├── credenciales.json
        ├── general.py
        └── text.py
    ├── MANIFEST.in
    ├── README.md
    ├── build/
        ├── bdist.win-amd64/
        └── lib/
            └── CHN/
                ├── __init__.py
                ├── general.py
                └── text.py
    ├── dist/
    └── setup.py
├── Conexiones/
    ├── connections.ipynb
    └── credenciales.json
├── LICENSE
├── RCHN/
    ├── .Rbuildignore
    ├── .gitignore
    ├── DESCRIPTION
    ├── NAMESPACE
    ├── R/
        ├── analysis.R
        ├── clustering.R
        ├── connections.R
        ├── general.R
        └── utils.R
    ├── RCHN.Rproj
    ├── README.md
    └── man/
        ├── connection.Rd
        ├── credentials.Rd
        ├── elbow_test.Rd
        ├── read_lots_excels.Rd
        ├── redondear.Rd
        ├── scatter_cluster.Rd
        ├── table_percentiles.Rd
        ├── tukey.Rd
        └── tukey_alternative.Rd
├── README.md
└── condaEnviroments/
    ├── enviroment.bat
    ├── shinyscrap.yaml
    └── shinyscrap_v1.yaml
```

## Entornos Virtuales en R

#### Crear y Configurar

1. Instalar los paquetes para poder crear entornos virtuales:

```R
> install.packages("renv")
```

2. Creas un proyecto y dentro de su carpeta ejecutas lo siguiente:

```R
> library(renv)
> renv::init()
```

3. Para la configuración del entorno e instalar paquetes, se puede hacer con el siguiente comando:

```R
> renv::install("paquete")
```

4. Para ver el estado del entorno virtual, los paquetes instalados, etc.

```R
> renv::status()
```

5. El equivalente del _requirements.txt_ de python se puede generar con el siguiente comando:

```R
> renv::snapshot()
```

6. Activar y desactivar el entorno. Esto debe ejecutarse dentro del proyecto (independientemente si es en RStudio o la consola de R, además RStudio lo activa por defecto al abrir el proyecto):

```R
> renv::activate()
> renv::deactivate()
```

7. En caso de querer crear el entorno virtual a partir del archivo generado por el _snapshot_, se puede hacer teniendo el archivo `renv.lock` en la carpeta del proyecto y ejecutando lo siguiente:

```R
> renv.restore()
```

esto instalará todas las librerías y dependencias del archivo `renv.lock`. Además, si se desea actualizar el entorno virtual con las dependencias más recientes de las registrada en el `renv.lock`, se puede utilizar `renv::update()`.
