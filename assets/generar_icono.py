"""Genera el icono de SimExtract (calafate sobre gota de disolvente).

Se ejecuta una sola vez; el .ico resultante se versiona junto al código para que
los accesos directos no dependan de tener Pillow instalado.

    python assets/generar_icono.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

# Paleta: morado calafate sobre el azul del disolvente.
FONDO_EXT = (26, 22, 51)
FONDO_INT = (46, 38, 92)
BAYA = (74, 42, 122)
BAYA_LUZ = (138, 92, 186)
BRILLO = (226, 210, 245)
GOTA = (96, 205, 214)

LADO = 512
CENTRO = LADO / 2


def _circulo(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color) -> None:
    """Dibuja un círculo lleno a partir de centro y radio."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def construir() -> Image.Image:
    img = Image.new("RGBA", (LADO, LADO), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Disco de fondo con degradado radial barato (anillos concéntricos).
    pasos = 90
    for i in range(pasos, 0, -1):
        t = i / pasos
        color = tuple(
            int(FONDO_INT[c] + (FONDO_EXT[c] - FONDO_INT[c]) * t) for c in range(3)
        )
        _circulo(d, CENTRO, CENTRO, CENTRO * t, color + (255,))

    # Gota de disolvente: media luna clara en el borde inferior izquierdo.
    d.arc(
        [46, 46, LADO - 46, LADO - 46],
        start=115,
        end=245,
        fill=GOTA + (255,),
        width=16,
    )

    # Racimo de tres bayas de calafate.
    bayas = [(CENTRO - 78, CENTRO - 34, 92), (CENTRO + 74, CENTRO - 48, 78),
             (CENTRO + 8, CENTRO + 86, 104)]
    for cx, cy, r in bayas:
        _circulo(d, cx, cy, r, BAYA + (255,))
        # Realce superior izquierdo: da volumen sin usar sombreado real.
        _circulo(d, cx - r * 0.22, cy - r * 0.24, r * 0.62, BAYA_LUZ + (150,))
        _circulo(d, cx - r * 0.34, cy - r * 0.36, r * 0.22, BRILLO + (215,))

    return img


def main() -> None:
    destino = Path(__file__).resolve().parent / "simextract.ico"
    img = construir()
    # Windows escoge el tamaño según el contexto (barra de tareas, escritorio…).
    img.save(destino, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    img.resize((256, 256), Image.LANCZOS).save(destino.with_suffix(".png"))
    print(f"escrito: {destino}")


if __name__ == "__main__":
    main()
