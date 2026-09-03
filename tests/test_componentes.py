from evidencia import Nivel
from explicacion import Lectura
from hptlc import Estado


def _lectura() -> Lectura:
    return Lectura(
        clave="polaridad",
        titulo="Polaridad (ETN)",
        valor=0.815,
        unidad="",
        calificativo="alta",
        por_que="Las antocianinas glicosiladas son muy polares.",
        fuente_id="espino2016",
        nivel=Nivel.MEDIDO,
    )


def test_el_texto_muestra_valor_y_calificativo_juntos() -> None:
    from tabs.componentes import texto_ficha

    texto = texto_ficha(_lectura())

    assert "0.815" in texto
    assert "alta" in texto
    assert "Polaridad" in texto


def test_la_franja_nombra_el_nades_activo_con_sus_condiciones() -> None:
    from tabs.componentes import nades_activo

    texto = nades_activo(
        {"water_pct": 30, "temp_C": 40},
        hba="Cloruro de Colina (ChCl)",
        hbd="Ácido Ascórbico (Vit. C)",
        ratio="1:1",
    )

    assert "Cloruro de Colina" in texto
    assert "Ácido Ascórbico" in texto
    assert "1:1" in texto
    assert "30" in texto
    assert "40" in texto


def test_insignia_por_nivel() -> None:
    from tabs.hptlc_tab import insignia

    assert insignia(Nivel.MEDIDO).startswith("🟩")
    assert insignia(Nivel.INFERIDO).startswith("🟨")
    assert insignia(Nivel.SIN_FUENTE).startswith("⬜")


def test_sin_evidencia_no_comparte_color_con_viable() -> None:
    from tabs.hptlc_tab import color_estado

    assert color_estado(Estado.SIN_EVIDENCIA) != color_estado(Estado.VIABLE)
    assert color_estado(Estado.SIN_EVIDENCIA) == "gray"
