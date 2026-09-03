import re

from tema import PALETA, css


def test_la_paleta_es_la_del_calafate_no_azul_generico() -> None:
    assert PALETA["primario"] == "#4A2A7A"
    assert PALETA["acento"] == "#60CDD6"


def test_toda_animacion_queda_bajo_prefers_reduced_motion() -> None:
    hoja = css()
    assert "prefers-reduced-motion: no-preference" in hoja
    # Ninguna transicion ni animacion puede vivir fuera de esa consulta.
    fuera = hoja.split("@media (prefers-reduced-motion: no-preference)")[0]
    assert "transition:" not in fuera
    assert "animation:" not in fuera


def test_las_transiciones_estan_en_la_ventana_recomendada() -> None:
    duraciones = [int(x) for x in re.findall(r"(\d+)ms", css())]
    assert duraciones, "no se declaro ninguna duracion"
    assert all(150 <= d <= 300 for d in duraciones), duraciones


def test_el_texto_principal_es_oscuro_para_contraste() -> None:
    assert PALETA["texto"] == "#1E1633"
