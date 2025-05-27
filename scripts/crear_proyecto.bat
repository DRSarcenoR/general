@echo off

REM Script para crear la información del proyecto

set "PROJECT_NAME=%1"
if "%PROJECT_NAME%"=="" (
    echo Debes proporcionar un nombre para el proyecto
    echo Uso: crear_proyecto NombreDelProyecto
    exit /b 1
)

mkdir "%PROJECT_NAME%"
cd "%PROJECT_NAME%"

mkdir src notebooks sql misc data docs tex

type nul > main.py
type nul > Dockerfile
type nul > .env

echo Proyecto '%PROJECT_NAME%' creado con estructura básica.
