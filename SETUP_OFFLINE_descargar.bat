@echo off
title SimExtract — Descargar paquetes para uso offline
color 0E
cd /d "%~dp0"

echo.
echo  ==========================================
echo   SimExtract v3  ^|  Descarga offline
echo   Ejecutar en el PC con internet ANTES de
echo   copiar al pendrive/PC sin internet.
echo  ==========================================
echo.
echo  Se descargaran los paquetes a la carpeta
echo  "wheels\" para instalacion sin internet.
echo.
echo  Tamanio estimado: ~400 MB
echo  Tiempo estimado:  5-10 min
echo.
pause

python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Python no encontrado. Instala Python primero.
    pause
    exit /b 1
)

if not exist "wheels" mkdir wheels

echo  Descargando paquetes...
python -m pip download -r requirements.txt -d wheels --platform win_amd64 --python-version 311 --only-binary=:all:
if %ERRORLEVEL% neq 0 (
    echo.
    echo  Intentando descarga sin restriccion de plataforma...
    python -m pip download -r requirements.txt -d wheels
)

echo.
echo  ==========================================
echo   [LISTO] Paquetes guardados en wheels\
echo.
echo   Ahora copia TODA la carpeta del proyecto
echo   (incluyendo wheels\) al pendrive/PC destino.
echo.
echo   En el PC destino ejecuta SETUP.bat
echo  ==========================================
echo.
pause
