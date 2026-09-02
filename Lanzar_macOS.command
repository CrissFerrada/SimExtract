#!/bin/bash
# ══════════════════════════════════════════════════════
#  Simulador de NADES para extraer polifenoles
#  © Cristofher Ferrada 2026 · Beta 0.6 · macOS
#  Doble clic en Finder para ejecutar
# ══════════════════════════════════════════════════════

# Ir al directorio donde está este script
cd "$(dirname "$0")"

# ── Función de alerta visual en macOS ──
alert() {
    osascript -e "display alert \"Simulador NADES\" message \"$1\"" 2>/dev/null \
        || echo "[AVISO] $1"
}

# ── Si ya está instalado, arrancar directo ──
if [ -x ".venv/bin/python" ]; then
    echo ""
    echo "  =========================================="
    echo "   Simulador de NADES para extraer"
    echo "   polifenoles — Beta 0.6"
    echo "   © Cristofher Ferrada 2026"
    echo "   Licenciado bajo Apache License 2.0"
    echo ""
    echo "   Berberis microphylla G. Forst"
    echo "   Fruto / Hojas / Tallo"
    echo "  =========================================="
    echo ""
    echo "  Iniciando... El navegador se abre solo."
    echo "  Para cerrar: cierra esta ventana."
    echo "  =========================================="
    echo ""
    .venv/bin/python -m streamlit run app.py --server.headless false
    exit 0
fi

# ── Primera vez: instalación automática ──
echo ""
echo "  =========================================="
echo "   Simulador de NADES — Primera instalación"
echo "   (solo ocurre una vez en este Mac)"
echo "  =========================================="
echo ""

# Detectar Python 3
PYTHON=""
for cmd in python3 python3.12 python3.11 python3.10 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        maj=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$maj" = "3" ] && [ "$ver" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    alert "Python 3.10+ no encontrado.\n\nDescarga desde:\nhttps://www.python.org/downloads/\n\nY marca 'Add Python to PATH'."
    echo ""
    echo "  [ERROR] Python 3.10+ no encontrado."
    echo "  Descarga desde: https://www.python.org/downloads/"
    echo ""
    read -p "  Presiona Enter para cerrar..."
    exit 1
fi

echo "  [OK] Python encontrado: $($PYTHON --version)"

# Crear entorno virtual
echo "  [1/3] Creando entorno virtual local..."
"$PYTHON" -m venv .venv
if [ $? -ne 0 ]; then
    alert "No se pudo crear el entorno virtual.\nRevisa los permisos de la carpeta."
    exit 1
fi
echo "  [OK] Entorno virtual creado."

# Actualizar pip
echo "  [2/3] Actualizando pip..."
.venv/bin/python -m pip install --upgrade pip --quiet

# Instalar dependencias
echo "  [3/3] Instalando dependencias (2-5 minutos)..."
echo "        streamlit, plotly, pandas, numpy, matplotlib, openpyxl"
echo ""

if [ -d "wheels" ]; then
    echo "  Modo offline detectado (carpeta wheels/)..."
    .venv/bin/python -m pip install --no-index --find-links wheels -r requirements.txt --quiet
else
    .venv/bin/python -m pip install -r requirements.txt --quiet
fi

if [ $? -ne 0 ]; then
    alert "Falló la instalación de dependencias.\nRevisa tu conexión a internet e intenta de nuevo."
    echo "  [ERROR] Falló la instalación."
    read -p "  Presiona Enter para cerrar..."
    exit 1
fi

echo ""
echo "  [OK] Instalación completada."
echo ""
echo "  =========================================="
echo "   Iniciando el simulador..."
echo "   El navegador se abre automáticamente."
echo "   Para cerrar: cierra esta ventana."
echo "  =========================================="
echo ""

.venv/bin/python -m streamlit run app.py --server.headless false
