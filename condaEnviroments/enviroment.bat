@echo off
setlocal enabledelayedexpansion

:: Solicitar el nombre del entorno
echo Introduce el nombre para el nuevo entorno:
set /p env_name=

:: Verificar si el nombre es válido
if "%env_name%"=="" (
    echo No se ingreso un nombre de entorno valido. Saliendo...
    pause
    exit /b
)

:: Mostrar confirmación del nombre ingresado
echo Creando entorno con el nombre: %env_name%
echo.

:: Verificar si conda está configurado en PATH
where conda >nul 2>&1
if errorlevel 1 (
    echo Conda no se encuentra en el PATH. Verifica que Anaconda o Miniconda este instalado.
    pause
    exit /b
)


::::::
:: Modificar el archivo .yaml para actualizar el nombre del entorno
set "yaml_file=default.yaml"
for /f "delims=" %%i in (%yaml_file%) do (
    set "line=%%i"
    if "!line!"=="name: default" (
        echo name: %env_name% >> temp.yaml
    ) else (
        echo !line! >> temp.yaml
    )
)

:: Reemplazar el archivo .yaml original con el modificado
move /y temp.yaml %yaml_file%
:::::::


:: Crear el entorno desde el archivo YAML
conda env create -n %env_name% -f nombre_del_archivo.yaml

:: Comprobar si el entorno se creo correctamente
if errorlevel 1 (
    echo Ocurrio un error al crear el entorno. Revisa el archivo YAML.
    pause
    exit /b
)

:: Activar el entorno
echo Activando el entorno %env_name%...
call conda activate %env_name%

:: Mostrar mensaje para instalar paquetes adicionales
echo El entorno %env_name% esta listo. Ahora puedes instalar paquetes adicionales con:
echo conda install [nombre_del_paquete]
pause
exit /b
