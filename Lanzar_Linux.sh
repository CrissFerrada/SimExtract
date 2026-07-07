#!/bin/bash
# ══════════════════════════════════════════════════════
#  Simulador de NADES para extraer polifenoles
#  © Cristofher Ferrada 2026 · Beta 0.6 · Linux
#
#  PRIMERA VEZ: abre una terminal y ejecuta:
#    chmod +x Lanzar_Linux.sh
#    ./Lanzar_Linux.sh
#
#  SIGUIENTES VECES: doble clic en el archivo
#  (selecciona "Ejecutar" o "Run in Terminal" en
#   Nautilus / Dolphin / Thunar / Nemo)
# ══════════════════════════════════════════════════════

# Ir al directorio donde está este script
cd "$(dirname "$0")"

# ── Si ya está instalado, arrancar directo ──
if [ -f ".venv/bin/streamlit" ]; then
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
    echo "  Para cerrar: Ctrl+C en esta terminal."
    echo "  =========================================="
    echo ""
    .venv/bin/streamlit run app.py --server.headless false
    exit 0
fi

# ── Primera vez: instalación automática ──
echo ""
echo "  =========================================="
echo "   Simulador de NADES — Primera instalación"
echo "   (solo ocurre una vez en este equipo)"
echo "  =========================================="
echo ""

# Detectar Python 3.10+
PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        maj=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        ver=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$maj" = "3" ] && [ "$ver" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "  [ERROR] Python 3.10+ no encontrado."
    echo ""
    echo "  Instala con el gestor de paquetes de tu distro:"
    echo "    Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "    Fedora:        sudo dnf install python3"
    echo "    Arch:          sudo pacman -S python"
    echo "    openSUSE:      sudo zypper install python3"
    echo ""
    read -p "  Presiona Enter para cerrar..."
    exit 1
fi

echo "  [OK] Python encontrado: $($PYTHON --version)"

# Verificar python3-venv (Ubuntu/Debian lo separan como paquete aparte)
"$PYTHON" -m venv --help &>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "  [ERROR] Módulo venv no disponible."
    echo "  En Ubuntu/Debian ejecuta:"
    echo "    sudo apt install python3-venv"
    echo ""
    read -p "  Presiona Enter para cerrar..."
    exit 1
fi

# Crear entorno virtual
echo "  [1/3] Creando entorno virtual local..."
"$PYTHON" -m venv .venv
if [ $? -ne 0 ]; then
    echo "  [ERROR] No se pudo crear el entorno virtual."
    read -p "  Presiona Enter para cerrar..."
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
    echo ""
    echo "  [ERROR] Falló la instalación de dependencias."
    echo "  Revisa tu conexión a internet e intenta de nuevo."
    read -p "  Presiona Enter para cerrar..."
    exit 1
fi

echo ""
echo "  [OK] Instalación completada."
echo ""
echo "  =========================================="
echo "   Iniciando el simulador..."
echo "   El navegador se abre automáticamente."
echo "   Para cerrar: Ctrl+C"
echo "  =========================================="
echo ""

.venv/bin/streamlit run app.py --server.headless false
