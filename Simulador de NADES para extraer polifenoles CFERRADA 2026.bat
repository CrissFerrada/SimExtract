@echo off
title Simulador de NADES para extraer polifenoles — CFERRADA 2026 — Beta 0.6
color 0A
cd /d "%~dp0"

:: ══════════════════════════════════════════════
::   PRIORIDAD 1: Python embebido incluido
::   (bundle completo, sin instalacion requerida)
:: ══════════════════════════════════════════════
if exist "python-embed\Scripts\streamlit.exe" goto :LAUNCH_EMBED

:: ══════════════════════════════════════════════
::   PRIORIDAD 2: venv local ya instalado
:: ══════════════════════════════════════════════
if exist ".venv\Scripts\streamlit.exe" goto :LAUNCH_VENV

:: ══════════════════════════════════════════════
::   Primera vez: instalar en venv local
:: ══════════════════════════════════════════════
color 0E
echo.
echo  ==========================================
echo   Simulador de NADES para extraer
echo   polifenoles — Beta 0.6
echo   (c) Cristofher Ferrada 2026
echo   Todos los derechos reservados
echo.
echo   Primera instalacion
echo   (solo ocurre una vez en este PC)
echo  ==========================================
echo.

:: Verificar Python del sistema
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Python no esta instalado.
    echo.
    echo  Opciones:
    echo   A) Descarga Python 3.11+ desde:
    echo      https://www.python.org/downloads/
    echo      Marca "Add Python to PATH" al instalar.
    echo.
    echo   B) Ejecuta PREPARAR_BUNDLE_COMPLETO_WINDOWS.bat
    echo      para crear una version sin dependencias.
    echo.
    pause
    exit /b 1
)

echo  [1/3] Creando entorno virtual local...
python -m venv .venv
if %ERRORLEVEL% neq 0 (
    color 0C
    echo  [ERROR] No se pudo crear el entorno virtual.
    pause & exit /b 1
)

echo  [2/3] Actualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo  [3/3] Instalando dependencias...
echo        (puede tardar 2-5 minutos la primera vez)
echo.

if exist "wheels" (
    echo  Modo offline detectado ^(wheels/^)...
    .venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r requirements.txt --quiet
) else (
    .venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
)

if %ERRORLEVEL% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Fallo la instalacion.
    echo  Revisa tu conexion a internet y vuelve a intentar.
    pause & exit /b 1
)

color 0A
echo.
echo  [OK] Instalacion completada.
echo.
goto :LAUNCH_VENV

:: ══════════════════════════════════════════════
:LAUNCH_EMBED
:: ══════════════════════════════════════════════
echo.
echo  ==========================================
echo   Simulador de NADES para extraer
echo   polifenoles — Beta 0.6
echo   (c) Cristofher Ferrada 2026
echo   Todos los derechos reservados
echo.
echo   Berberis microphylla G. Forst
echo   Fruto / Hojas / Tallo
echo   Python embebido (sin instalacion)
echo  ==========================================
echo.
echo  Iniciando... El navegador se abre solo.
echo  Para cerrar: cierra esta ventana.
echo  ==========================================
echo.
"python-embed\Scripts\streamlit.exe" run app.py --server.headless false
pause
exit /b 0

:: ══════════════════════════════════════════════
:LAUNCH_VENV
:: ══════════════════════════════════════════════
echo.
echo  ==========================================
echo   Simulador de NADES para extraer
echo   polifenoles — Beta 0.6
echo   (c) Cristofher Ferrada 2026
echo   Todos los derechos reservados
echo.
echo   Berberis microphylla G. Forst
echo   Fruto / Hojas / Tallo
echo  ==========================================
echo.
echo  Iniciando... El navegador se abre solo.
echo  Para cerrar: cierra esta ventana.
echo  ==========================================
echo.
.venv\Scripts\streamlit.exe run app.py --server.headless false
pause
