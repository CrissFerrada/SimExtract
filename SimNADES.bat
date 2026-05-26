@echo off
title SimNADES — Simulador NADES para Polifenoles — CFERRADA 2026 — Beta 0.6
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
echo   SimNADES — Simulador NADES
echo   para extraccion de polifenoles
echo   Beta 0.6 — (c) Cristofher Ferrada 2026
echo.
echo   Primera instalacion
echo   (solo ocurre una vez en este PC)
echo  ==========================================
echo.

:: Buscar Python: primero el Launcher (py), luego python3, luego python
set PYTHON_CMD=
where py      >nul 2>&1 && set PYTHON_CMD=py      && goto :CHECK_PY_OK
where python3 >nul 2>&1 && set PYTHON_CMD=python3 && goto :CHECK_PY_OK
where python  >nul 2>&1 && (
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 set PYTHON_CMD=python && goto :CHECK_PY_OK
)

color 0C
echo.
echo  [ERROR] Python no encontrado.
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

:CHECK_PY_OK
echo  Python encontrado: %PYTHON_CMD%
%PYTHON_CMD% --version

echo.
echo  [1/3] Creando entorno virtual local...
%PYTHON_CMD% -m venv .venv
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
    echo  [ERROR] Fallo la instalacion de dependencias.
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
echo   SimNADES — Simulador NADES
echo   para extraccion de polifenoles
echo   Beta 0.6 — (c) Cristofher Ferrada 2026
echo.
echo   Berberis microphylla G. Forst
echo   Fruto / Hojas / Tallo
echo   Python embebido (sin instalacion)
echo  ==========================================
echo.
echo  Iniciando servidor... espera unos segundos.
echo  El navegador se abrira solo cuando este listo.
echo.
echo  Si no se abre, ve manualmente a:
echo      http://localhost:8501
echo.
echo  Para cerrar el simulador: cierra esta ventana.
echo  ==========================================
echo.
"python-embed\Scripts\streamlit.exe" run app.py
pause
exit /b 0

:: ══════════════════════════════════════════════
:LAUNCH_VENV
:: ══════════════════════════════════════════════
echo.
echo  ==========================================
echo   SimNADES — Simulador NADES
echo   para extraccion de polifenoles
echo   Beta 0.6 — (c) Cristofher Ferrada 2026
echo.
echo   Berberis microphylla G. Forst
echo   Fruto / Hojas / Tallo
echo  ==========================================
echo.
echo  Iniciando servidor... espera unos segundos.
echo  El navegador se abrira solo cuando este listo.
echo.
echo  Si no se abre, ve manualmente a:
echo      http://localhost:8501
echo.
echo  Para cerrar el simulador: cierra esta ventana.
echo  ==========================================
echo.
.venv\Scripts\streamlit.exe run app.py
pause
