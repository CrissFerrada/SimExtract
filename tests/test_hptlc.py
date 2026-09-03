import pytest

from evidencia import EVIDENCIA, Nivel
from hptlc import PLACAS, Estado, evaluar_placa, protocolo_candidato

PROPS_ACIDO = {"viscosidad": 120.0, "water_pct": 30.0, "pH": 3.1}


# ── Task 1: registro de evidencia y catálogo ──────────────────────


def test_toda_fuente_tiene_doi_y_afirmacion() -> None:
    assert EVIDENCIA, "el registro de evidencia no puede estar vacio"
    for fuente_id, fuente in EVIDENCIA.items():
        assert fuente.id == fuente_id
        assert fuente.doi, f"{fuente_id} sin DOI"
        assert fuente.afirma, f"{fuente_id} sin afirmacion"


def test_catalogo_incluye_la_placa_del_laboratorio_y_las_rp() -> None:
    assert "silice-60G-F254" in PLACAS
    assert "rp18-w-f254s" in PLACAS
    assert "rp18-zona-concentracion" in PLACAS


def test_placa_del_laboratorio_es_grado_tlc_fase_normal() -> None:
    placa = PLACAS["silice-60G-F254"]
    assert placa.modo == "NP"
    assert placa.grado == "TLC"
    assert placa.indicador == "F254"
    assert placa.catalogo == "1.00390"
    assert placa.espesor_um == 250.0


def test_la_w_implica_humectable_con_agua() -> None:
    assert PLACAS["rp18-w-f254s"].humectable_agua is True
    assert PLACAS["rp18-f254s"].humectable_agua is False


# ── Task 2: veredicto y niveles de evidencia ──────────────────────


def test_fase_normal_reproduce_el_fracaso_publicado() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    assert v.estado is Estado.REQUIERE_LIMPIEZA
    assert any(f.fuente_id == "quinoa2025" for f in v.factores)


def test_fase_reversa_nunca_sale_viable() -> None:
    for placa_id in ("rp18-f254s", "rp18-w-f254s", "rp18-zona-concentracion"):
        v = evaluar_placa(PROPS_ACIDO, PLACAS[placa_id], volumen_uL=2.0, dilucion=10.0)
        assert v.estado is not Estado.VIABLE, placa_id
        assert v.estado is Estado.SIN_EVIDENCIA, placa_id


def test_ningun_factor_emite_valor_sin_fuente_resoluble() -> None:
    for placa in PLACAS.values():
        v = evaluar_placa(PROPS_ACIDO, placa, volumen_uL=4.0, dilucion=10.0)
        for f in v.factores:
            if f.valor is not None:
                assert f.fuente_id in EVIDENCIA, f"{f.id} emite valor sin fuente"
            if f.nivel is Nivel.SIN_FUENTE:
                assert f.valor is None, f"{f.id} es SIN_FUENTE pero trae valor"


def test_los_vacios_se_declaran_y_no_se_rellenan() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], volumen_uL=2.0, dilucion=10.0)
    ids = {f.id for f in v.vacios}
    assert ids == {
        "cruce-nades-rp18",
        "umbral-viscosidad",
        "carga-tolerable",
        "revelado-sin-limpieza",
        "componentes-hptlc",
        "raspado-hplc",
        "obstruccion-aplicador",
    }
    assert all(f.valor is None for f in v.vacios)


def test_indicador_no_acido_con_nades_acido_produce_aviso() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    aviso = next(f for f in v.factores if f.id == "indicador")
    assert "F254s" in aviso.texto
    assert aviso.fuente_id == "merck-placas"


def test_zona_de_concentracion_repone_el_enfoque_de_banda() -> None:
    sin_zona = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], 2.0, 10.0)
    con_zona = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-zona-concentracion"], 2.0, 10.0)
    f_sin = next(f for f in sin_zona.factores if f.id == "enfoque-banda")
    f_con = next(f for f in con_zona.factores if f.id == "enfoque-banda")
    assert f_sin.fuente_id == "camag-linomat"
    assert f_con.fuente_id == "merck-zona"


def test_carga_no_volatil_se_compara_contra_el_punto_de_fracaso() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    carga = next(f for f in v.factores if f.id == "carga-no-volatil")
    assert carga.valor == pytest.approx(0.4)
    assert carga.fuente_id == "quinoa2025"


def test_dilucion_invalida_es_error() -> None:
    with pytest.raises(ValueError):
        evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], volumen_uL=2.0, dilucion=0.0)


# ── Task 3: protocolo candidato ───────────────────────────────────


def test_protocolo_usa_el_volumen_de_farmacopea_segun_grado() -> None:
    v_tlc = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], 4.0, 10.0)
    v_hptlc = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], 2.0, 10.0)
    assert protocolo_candidato(v_tlc).volumen_max_uL == 10.0
    assert protocolo_candidato(v_hptlc).volumen_max_uL == 2.0
    assert protocolo_candidato(v_tlc).fuente_volumen == "merck-placas"


def test_protocolo_en_fase_normal_exige_limpieza_previa() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], 4.0, 10.0)
    p = protocolo_candidato(v)
    assert p.limpieza_previa is True
    assert "SPE" in p.notas


def test_protocolo_con_zona_de_concentracion_no_exige_spe() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-zona-concentracion"], 2.0, 10.0)
    assert protocolo_candidato(v).limpieza_previa is False
