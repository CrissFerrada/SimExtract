@echo off
title Simulador NADES — Preparar bundle completo sin dependencias (Windows)
color 0B
cd /d "%~dp0"

echo.
echo  ================================================================
echo   Simulador de NADES para extraer polifenoles — Beta 0.6
echo   (c) Cristofher Ferrada 2026 - Licenciado bajo Apache License 2.0
echo.
echo   PREPARADOR DE BUNDLE COMPLETO (SIN INTERNET EN DESTINO)
echo   -------------------------------------------------------
echo   Este script descarga Python 3.11 embebido + todos los
echo   paquetes necesarios. El resultado es una carpeta que
echo   funciona en CUALQUIER PC con Windows sin instalar nada.
echo.
echo   Tamaño final: ~400-500 MB
echo   Tiempo estimado: 10-20 minutos (según conexión)
echo  ================================================================
echo.
echo  Verificando herramientas necesarias...

:: Verificar curl
curl --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo  [ERROR] curl no encontrado. Requiere Windows 10 v1803 o superior.
    pause & exit /b 1
)

:: Verificar PowerShell
powershell -command "exit 0" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo  [ERROR] PowerShell no disponible.
    pause & exit /b 1
)

echo  [OK] curl y PowerShell disponibles.
echo.

:: ══════════════════════════════════════════════════════════
:: PASO 1 — Descargar Python embebido
:: ══════════════════════════════════════════════════════════
if exist "python-embed\python.exe" (
    echo  [OK] Python embebido ya existe, saltando descarga.
    goto :PASO2
)

echo  [1/4] Descargando Python 3.11 embebido (64-bit)...
echo        (~25 MB — puede tardar 1-2 minutos)
echo.

set PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
set PY_ZIP=%TEMP%\python-embed-temp.zip

curl -L --progress-bar -o "%PY_ZIP%" "%PY_URL%"
if %ERRORLEVEL% neq 0 (
    color 0C
    echo.
    echo  [ERROR] No se pudo descargar Python.
    echo  Verifica tu conexion a internet.
    pause & exit /b 1
)

echo.
echo  Extrayendo Python embebido...
if exist "python-embed" rmdir /s /q "python-embed"
powershell -command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath 'python-embed' -Force"
del "%PY_ZIP%"

if not exist "python-embed\python.exe" (
    color 0C
    echo  [ERROR] La extraccion fallo.
    pause & exit /b 1
)
echo  [OK] Python 3.11 embebido extraido.

:: ══════════════════════════════════════════════════════════
:: PASO 2 — Activar pip en el Python embebido
:: ══════════════════════════════════════════════════════════
:PASO2
echo.
echo  [2/4] Activando pip en Python embebido...

:: Descomentar "import site" en el archivo .pth (necesario para que pip funcione)
powershell -command ^
    "(Get-Content 'python-embed\python311._pth') -replace '#import site', 'import site' | Set-Content 'python-embed\python311._pth'"

:: Descargar get-pip.py si no existe pip
if exist "python-embed\Scripts\pip.exe" (
    echo  [OK] pip ya instalado, saltando.
    goto :PASO3
)

echo  Descargando pip installer...
curl -L --progress-bar -o "python-embed\get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
if %ERRORLEVEL% neq 0 (
    color 0C
    echo  [ERROR] No se pudo descargar get-pip.py
    pause & exit /b 1
)

"python-embed\python.exe" "python-embed\get-pip.py" --no-warn-script-location --quiet
del "python-embed\get-pip.py"

if not exist "python-embed\Scripts\pip.exe" (
    color 0C
    echo  [ERROR] pip no se instalo correctamente.
    pause & exit /b 1
)
echo  [OK] pip instalado en Python embebido.

:: ══════════════════════════════════════════════════════════
:: PASO 3 — Descargar wheels (paquetes offline)
:: ══════════════════════════════════════════════════════════
:PASO3
echo.
echo  [3/4] Descargando paquetes Python a carpeta wheels\...
echo        streamlit, plotly, pandas, numpy, matplotlib, openpyxl
echo        (~350-400 MB — puede tardar 10-15 minutos)
echo.

if not exist "wheels" mkdir "wheels"

"python-embed\Scripts\pip.exe" download ^
    -r requirements.txt ^
    -d wheels ^
    --platform win_amd64 ^
    --python-version 3.11 ^
    --only-binary=:all: ^
    --quiet

if %ERRORLEVEL% neq 0 (
    echo.
    echo  Reintentando sin restriccion de plataforma...
    "python-embed\Scripts\pip.exe" download -r requirements.txt -d wheels --quiet
)

echo  [OK] Paquetes descargados en wheels\

:: ══════════════════════════════════════════════════════════
:: PASO 4 — Instalar paquetes en el Python embebido
:: ══════════════════════════════════════════════════════════
echo.
echo  [4/4] Instalando paquetes en Python embebido...

"python-embed\Scripts\pip.exe" install ^
    --no-index ^
    --find-links wheels ^
    -r requirements.txt ^
    --no-warn-script-location ^
    --quiet

if %ERRORLEVEL% neq 0 (
    echo  Reintentando con descarga online...
    "python-embed\Scripts\pip.exe" install -r requirements.txt --no-warn-script-location --quiet
)

if not exist "python-embed\Scripts\streamlit.exe" (
    color 0C
    echo.
    echo  [ERROR] streamlit no se instalo correctamente.
    pause & exit /b 1
)

echo  [OK] Todos los paquetes instalados.

:: ══════════════════════════════════════════════════════════
:: RESUMEN FINAL
:: ══════════════════════════════════════════════════════════
color 0A
echo.
echo  ================================================================
echo   [LISTO] Bundle completo preparado exitosamente.
echo.
echo   Esta carpeta ya NO necesita Python instalado en el PC destino.
echo   Solo copia la carpeta completa (incluyendo python-embed\)
echo   a cualquier PC con Windows 10/11 (64-bit) y haz doble clic en:
echo.
echo   >> Simulador de NADES para extraer polifenoles CFERRADA 2026.bat
echo.
echo   Tamaño aproximado de la carpeta completa:
for /f "tokens=3" %%a in ('dir /s /-c /a-d "python-embed" 2^>nul ^| find "bytes"') do set SIZE=%%a
echo   python-embed\  : %SIZE% bytes aprox.
echo  ================================================================
echo.
pause
