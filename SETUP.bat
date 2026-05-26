@echo off
title Simulador de NADES — CFERRADA 2026 — Configuracion Inicial
color 0B
cd /d "%~dp0"

echo.
echo  ==========================================
echo   Simulador de NADES para extraer
echo   polifenoles — Beta 0.6
echo   (c) Cristofher Ferrada 2026
echo   Configuracion inicial
echo  ==========================================
echo.

:: ---- Verificar si ya existe el entorno virtual ----
if exist ".venv\Scripts\streamlit.exe" (
    echo  [OK] Simulador de NADES — CFERRADA 2026 ya esta instalado.
    echo       Para reinstalar, elimina la carpeta .venv y vuelve a ejecutar.
    echo.
    pause
    exit /b 0
)

:: ---- Verificar Python ----
echo  [1/4] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo  Descarga Python 3.11 o superior desde:
    echo  https://www.python.org/downloads/
    echo.
    echo  Durante la instalacion marca la opcion:
    echo  "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo  [OK] Python encontrado.
echo.

:: ---- Crear entorno virtual local ----
echo  [2/4] Creando entorno virtual local en .venv ...
python -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)
echo  [OK] Entorno virtual creado.
echo.

:: ---- Actualizar pip ----
echo  [3/4] Actualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo  [OK] pip actualizado.
echo.

:: ---- Instalar dependencias ----
echo  [4/4] Instalando dependencias (puede tardar 2-5 min)...
echo        streamlit, plotly, pandas, numpy, matplotlib
echo.

:: Primero intentar desde carpeta wheels/ (modo offline)
if exist "wheels" (
    echo  Modo offline detectado (carpeta wheels/)...
    .venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r requirements.txt
) else (
    echo  Descargando desde internet...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Fallo la instalacion de dependencias.
    echo  Revisa tu conexion a internet y vuelve a intentar.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   [LISTO] Instalacion completada.
echo.
echo   Ejecuta:
echo   "Simulador de NADES para extraer
echo    polifenoles CFERRADA 2026.bat"
echo  ==========================================
echo.
pause
