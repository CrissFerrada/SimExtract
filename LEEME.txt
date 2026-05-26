══════════════════════════════════════════════════════════════════
  Simulador de NADES para extraer polifenoles — Beta 0.6
  © Cristofher Ferrada, 2026. Todos los derechos reservados.
  Berberis microphylla G. Forst — Tesis Doctoral
══════════════════════════════════════════════════════════════════

DESCRIPCION
-----------
Software de simulación interactiva para el diseño y evaluación de
Solventes Eutécticos Profundos Naturales (NADES) aplicados a la
extracción de polifenoles extraíbles (EP) y no extraíbles (NEP)
de Berberis microphylla G. Forst (calafate).

Funcionalidades principales:
  - Diseño de NADES con 11 HBA × 23 HBD disponibles
  - Simulación de extracción EP (28 compuestos, Ruiz et al. 2024)
  - Modelo teórico novel de extracción NEP (Ferrada 2026)
  - Extracción asistida por ultrasonido (UAE, 0-100 kHz)
  - Cinética de extracción + optimización razón S:L
  - Análisis de incertidumbre Monte Carlo (modelo NEP)
  - Análisis económico + reutilización del NADES
  - Generador de diseño experimental (Box-Behnken / CCD / Factorial)
  - Importar y comparar datos experimentales propios (CSV)
  - Exportar resultados a Excel (5 hojas)
  - Perfiles para Fruto, Hojas y Tallo/Corteza
  - Recomendador automático (759 combinaciones)

══════════════════════════════════════════════════════════════════
  MODOS DE USO SEGÚN PLATAFORMA
══════════════════════════════════════════════════════════════════

  Hay dos modalidades de uso dependiendo del sistema operativo:

  ┌─────────────────────┬───────────────────────┬────────────────┐
  │ Sistema             │ Python requerido       │ Cómo abrir     │
  ├─────────────────────┼───────────────────────┼────────────────┤
  │ Windows (MODO A)    │ NO — incluido en       │ Doble clic en  │
  │ Bundle completo     │ python-embed\          │ el .bat        │
  ├─────────────────────┼───────────────────────┼────────────────┤
  │ Windows (MODO B)    │ SÍ — Python 3.10+      │ Doble clic en  │
  │ Instalación normal  │ instalado en el PC     │ el .bat        │
  ├─────────────────────┼───────────────────────┼────────────────┤
  │ macOS               │ SÍ — Python 3.10+      │ Doble clic en  │
  │                     │ (Homebrew o python.org)│ .command       │
  ├─────────────────────┼───────────────────────┼────────────────┤
  │ Linux               │ SÍ — Python 3.10+      │ ./Lanzar_      │
  │                     │ (gestor de paquetes)   │ Linux.sh       │
  └─────────────────────┴───────────────────────┴────────────────┘

══════════════════════════════════════════════════════════════════
  WINDOWS — MODO A: BUNDLE COMPLETO (SIN INSTALAR NADA)
══════════════════════════════════════════════════════════════════

  Este modo incluye Python dentro de la carpeta del programa.
  No requiere instalar Python en el PC destino.
  Tamaño total de la carpeta: ~450 MB.

  PASO 1 — En un PC con internet (SOLO UNA VEZ):
  -----------------------------------------------
  Haz doble clic en:
  >> PREPARAR_BUNDLE_COMPLETO_WINDOWS.bat

  Este script descarga automáticamente:
    - Python 3.11 embebido (~25 MB, sin instalador)
    - Todos los paquetes necesarios (~400 MB)
    - Los instala en la carpeta python-embed\

  Tiempo estimado: 10-20 minutos según tu conexión.

  PASO 2 — Copiar al PC destino (sin internet):
  -----------------------------------------------
  Copia TODA la carpeta al pendrive o PC destino.
  Asegúrate de incluir la subcarpeta python-embed\.

  PASO 3 — Ejecutar en el PC destino:
  -----------------------------------------------
  Doble clic en:
  >> Simulador de NADES para extraer polifenoles CFERRADA 2026.bat

  El lanzador detecta automáticamente el Python embebido.
  No necesita internet, no necesita instalación.
  Funciona en cualquier Windows 10/11 de 64 bits.

══════════════════════════════════════════════════════════════════
  WINDOWS — MODO B: INSTALACIÓN NORMAL (CON PYTHON DEL SISTEMA)
══════════════════════════════════════════════════════════════════

  PASO 1 — Instalar Python (si no lo tienes):
  --------------------------------------------
  a) Ve a: https://www.python.org/downloads/
  b) Descarga Python 3.11 o superior
  c) Durante la instalación, MARCA la casilla:
       [x] Add Python to PATH
  d) Completa la instalación

  PASO 2 — Ejecutar el simulador:
  --------------------------------
  Doble clic en:
  >> Simulador de NADES para extraer polifenoles CFERRADA 2026.bat

  La primera vez instala los paquetes automáticamente (2-5 min).
  Las siguientes veces abre directamente sin espera.

══════════════════════════════════════════════════════════════════
  macOS — EJECUCIÓN CON UN CLIC
══════════════════════════════════════════════════════════════════

  NOTA SOBRE macOS Y PYTHON EMBEBIDO:
  Apple restringe la ejecución de binarios externos no firmados
  (Gatekeeper + SIP), por lo que NO es posible bundlear Python
  dentro de la carpeta como en Windows. Necesitas Python instalado.

  PASO 1 — Instalar Python (si no lo tienes):
  --------------------------------------------
  Opción A (recomendada) — Homebrew:
    1. Abre Terminal
    2. Ejecuta: /bin/bash -c "$(curl -fsSL https://brew.sh/install.sh)"
    3. Luego:   brew install python@3.11

  Opción B — Instalador oficial:
    Ve a https://www.python.org/downloads/macos/
    Descarga y ejecuta el .pkg

  PASO 2 — Dar permiso al lanzador (SOLO UNA VEZ):
  --------------------------------------------------
  a) Abre Terminal
  b) Arrastra el archivo Lanzar_macOS.command a la Terminal
     (aparece la ruta completa)
  c) Escribe antes del path: chmod +x  (con espacio)
     Ejemplo: chmod +x /Users/tu/carpeta/Lanzar_macOS.command
  d) Presiona Enter

  PASO 3 — Ejecutar todas las veces:
  ------------------------------------
  Doble clic en:
  >> Lanzar_macOS.command

  La primera vez instala los paquetes (2-5 min).
  Las siguientes veces abre el navegador directamente.

  ATAJO — Si prefieres Terminal siempre:
    cd /ruta/al/simulador
    bash Lanzar_macOS.command

  Si macOS dice "desarrollador no identificado":
    Clic derecho en el archivo → Abrir → Abrir de todos modos

══════════════════════════════════════════════════════════════════
  LINUX — EJECUCIÓN
══════════════════════════════════════════════════════════════════

  NOTA SOBRE LINUX Y PYTHON EMBEBIDO:
  Cada distribución Linux usa versiones diferentes de libc y
  compiladores, lo que hace imposible incluir un Python portable
  que funcione en todas. En Linux, Python casi siempre está
  preinstalado o se instala con un comando.

  PASO 1 — Verificar/instalar Python:
  ------------------------------------
  Ubuntu/Debian:  sudo apt install python3 python3-venv python3-pip
  Fedora:         sudo dnf install python3 python3-pip
  Arch Linux:     sudo pacman -S python
  openSUSE:       sudo zypper install python3 python3-pip

  PASO 2 — Dar permiso al lanzador (SOLO UNA VEZ):
  --------------------------------------------------
  Abre una terminal en la carpeta del simulador y ejecuta:
    chmod +x Lanzar_Linux.sh

  PASO 3 — Ejecutar:
  -------------------
  Doble clic en Lanzar_Linux.sh en tu gestor de archivos
  (selecciona "Ejecutar como programa" o "Ejecutar en terminal")

  O desde terminal:
    ./Lanzar_Linux.sh

══════════════════════════════════════════════════════════════════
  ARCHIVOS DEL PAQUETE
══════════════════════════════════════════════════════════════════

  LANZADORES:
  Simulador de NADES para extraer
  polifenoles CFERRADA 2026.bat    → Lanzador Windows (doble clic)
  Lanzar_macOS.command             → Lanzador macOS   (doble clic)
  Lanzar_Linux.sh                  → Lanzador Linux   (doble clic*)

  SETUP Y OFFLINE:
  PREPARAR_BUNDLE_COMPLETO_WINDOWS.bat  → Crea bundle sin dependencias
  SETUP.bat                             → Instalador manual Windows
  SETUP_OFFLINE_descargar.bat           → Descarga paquetes para offline

  CÓDIGO FUENTE:
  app.py                           → Aplicación principal
  data.py                          → Base de datos de compuestos
  model.py                         → Modelos de simulación
  requirements.txt                 → Lista de dependencias Python
  LEEME.txt                        → Este archivo

  GENERADO AUTOMÁTICAMENTE (no incluir en ZIP mínimo):
  python-embed\   → Python embebido para Windows (solo Modo A)
  wheels\         → Paquetes offline descargados
  .venv\          → Entorno virtual (Modo B Windows / Mac / Linux)

  (*) chmod +x Lanzar_Linux.sh  en terminal, solo la primera vez

══════════════════════════════════════════════════════════════════
  USO DEL PROGRAMA
══════════════════════════════════════════════════════════════════

  1. Abre con el lanzador de tu sistema → se abre el navegador
  2. En el sidebar izquierdo:
     - Selecciona la parte de la planta (Fruto / Hojas / Tallo)
     - Elige HBA + HBD + Razón + % Agua + Temperatura
     - Ajusta la frecuencia de ultrasonido (0 = sin UAE)
  3. Explora las pestañas:
     - Resultados     : índices EP, NEP, Estabilidad + Exportar Excel
     - Ultrasonido    : efecto UAE por frecuencia
     - Interacción    : diagrama NADES-polifenol + heatmap
     - Extracción EP  : detalle de los compuestos EP
     - Extracción NEP : modelo novel + Monte Carlo
     - Estabilidad    : protección oxidativa
     - Economía       : costo + reutilización del NADES
     - Cinética       : curva C(t) + optimización razón S:L
     - Diseño Exp.    : generador Box-Behnken / CCD / Factorial
     - Mis Datos      : importar CSV experimental + Parity Plot
     - Cribado Tesis  : los 6 NADES del experimento
     - Recomendador   : búsqueda automática del mejor NADES
     - Metodología    : fundamento científico y referencias
  4. Para cerrar: cierra la consola (Windows) o Ctrl+C (Mac/Linux)

══════════════════════════════════════════════════════════════════
  SOLUCION DE PROBLEMAS
══════════════════════════════════════════════════════════════════

  Windows: "Python no encontrado"
    → Opción A: Ejecuta PREPARAR_BUNDLE_COMPLETO_WINDOWS.bat
    → Opción B: Instala Python 3.11+ con "Add Python to PATH"

  Windows: El programa se cierra antes de abrir
    → Clic derecho en el .bat → "Ejecutar como administrador"

  macOS: "No se puede abrir porque es de un desarrollador..."
    → Clic derecho → Abrir → Abrir de todos modos
    → O desde Terminal: bash Lanzar_macOS.command

  macOS: "Permission denied"
    → En Terminal: chmod +x Lanzar_macOS.command

  Linux: "Permission denied"
    → En terminal: chmod +x Lanzar_Linux.sh

  Linux Ubuntu: "No module named venv"
    → sudo apt install python3-venv && ./Lanzar_Linux.sh

  Todos: El navegador no se abre solo
    → Abre tu navegador y ve a: http://localhost:8501

  Todos: Pantalla en blanco en el navegador
    → Espera 10-15 segundos y recarga (F5)

  Todos: Para reinstalar desde cero
    → Elimina la carpeta .venv\ (o python-embed\ si usas Modo A)
    → Ejecuta el lanzador de nuevo

══════════════════════════════════════════════════════════════════
  INFORMACION LEGAL Y ACADEMICA
══════════════════════════════════════════════════════════════════

  Autor     : Cristofher Ferrada
  Año       : 2026
  Versión   : Beta 0.6
  Contexto  : Tesis Doctoral — Extracción de polifenoles de
              Berberis microphylla G. Forst con NADES

  Copyright (c) 2026 Cristofher Ferrada.
  Todos los derechos reservados.

  Este software es parte de un trabajo de tesis doctoral en
  desarrollo. Queda prohibida su reproducción, distribución
  o modificación total o parcial sin la autorización expresa
  y por escrito del autor.

  Los modelos de simulación están basados en literatura
  científica indexada (ver pestaña Metodología en el programa).
  El modelo de extracción NEP es una contribución teórica
  original del autor.

══════════════════════════════════════════════════════════════════
  REFERENCIAS PRINCIPALES
══════════════════════════════════════════════════════════════════

  Ruiz, A. et al. (2024) Horticulturae 10, 458
  Espino, M. et al. (2016) Talanta 162, 412-419
  Benvenutti, L. et al. (2019) Food Res. Int. 119, 710-718
  Dai, Y. et al. (2013) Anal. Chim. Acta 766, 61-68
  Mocan, A. et al. (2017) Front. Pharmacol. 8, 234
  Muñoz, O. et al. (2011) J. Ethnopharmacol. 136, 57
  Saura-Calixto, F. et al. (2010) J. Agric. Food Chem. 58, 11932
  Tiwari, B.K. et al. (2010) Food Res. Int. 43, 1956
  Cacace, J.E. & Mazza, G. (2003) J. Food Eng. 59, 379
  Florindo, C. et al. (2019) ACS Sustain. Chem. Eng. 7, 3
  Box, G.E.P. & Behnken, D.W. (1960) Technometrics 2, 455
  Montgomery, D.C. (2017) Design and Analysis of Experiments, 9th ed.

══════════════════════════════════════════════════════════════════
