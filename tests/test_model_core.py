import pandas as pd

from data import HBA_COMPONENTS, HBD_COMPONENTS, THESIS_NADES, get_polyphenol_database
from model import (
    calculate_nades_properties,
    combined_score,
    ep_extraction_score,
    nep_extraction_score,
    par_inmiscible,
    run_full_simulation,
    simulate_3step_process,
    stability_score,
)


def _thesis_props() -> dict:
    candidate = THESIS_NADES[0]
    return calculate_nades_properties(
        hba_name=candidate["hba"],
        hbd_name=candidate["hbd"],
        ratio_hba=candidate["ratio_hba"],
        ratio_hbd=candidate["ratio_hbd"],
        water_pct=candidate["water_pct"],
        temp_C=40,
        hba_db=HBA_COMPONENTS,
        hbd_db=HBD_COMPONENTS,
    )


def test_calculate_nades_properties_returns_physical_ranges() -> None:
    props = _thesis_props()

    assert 0 <= props["polaridad"] <= 1
    assert props["viscosidad"] >= 1
    assert 1 <= props["pH"] <= 8.5
    assert props["cap_hbd"] > 0
    assert props["cap_hba"] > 0


def test_core_scores_are_bounded_for_representative_polyphenol() -> None:
    props = _thesis_props()
    poly = get_polyphenol_database().iloc[0]

    ep = ep_extraction_score(props, poly)
    nep = nep_extraction_score(props, poly)
    stability = stability_score(props, poly)

    assert 0 <= ep["total"] <= 1
    assert 0 <= nep["total"] <= 1
    assert 0 <= stability["total"] <= 1
    assert 0 <= combined_score(ep["total"], nep["total"]) <= 1


def test_run_full_simulation_returns_expected_columns() -> None:
    props = _thesis_props()
    poly_df = get_polyphenol_database().head(6)

    simulation = run_full_simulation(props, poly_df, freq_us=25)

    assert isinstance(simulation, pd.DataFrame)
    assert len(simulation) == len(poly_df)
    assert {"EP (%)", "NEP (%)", "Estab. (%)", "Combinado (%)"}.issubset(simulation.columns)
    assert simulation["Combinado (%)"].between(0, 100).all()


def _hdes_props(water_pct: float) -> dict:
    return calculate_nades_properties(
        hba_name="Mentol",
        hbd_name="Timol",
        ratio_hba=1,
        ratio_hbd=1,
        water_pct=water_pct,
        temp_C=40,
        hba_db=HBA_COMPONENTS,
        hbd_db=HBD_COMPONENTS,
    )


def test_hdes_terpenoide_satura_el_agua_y_marca_bifasico() -> None:
    seco = _hdes_props(0)
    inundado = _hdes_props(40)

    assert seco["hidrofobico"] is True
    assert seco["bifasico"] is False
    # El exceso sobre la saturación (~5 % m/m) no entra en la fase eutéctica.
    assert inundado["bifasico"] is True
    assert inundado["water_pct_efectivo"] <= 5.0
    assert inundado["water_pct"] == 40


def test_hdes_es_apolar_y_castiga_glucosidos_polares() -> None:
    hdes = _hdes_props(0)
    hidrofilo = _thesis_props()
    antocianina = get_polyphenol_database().iloc[0]  # Dp-3-glu, polaridad óptima 0.85

    assert hdes["polaridad"] < 0.40
    ep_hdes = ep_extraction_score(hdes, antocianina)["total"]
    ep_hidrofilo = ep_extraction_score(hidrofilo, antocianina)["total"]
    assert ep_hdes < ep_hidrofilo


def test_par_inmiscible_bloquea_terpenoide_con_azucar_y_permite_acido_corto() -> None:
    assert par_inmiscible("Timol (como HBA)", "Glucosa", HBA_COMPONENTS, HBD_COMPONENTS) is True
    assert par_inmiscible("Timol (como HBA)", "Sorbitol", HBA_COMPONENTS, HBD_COMPONENTS) is True
    assert (
        par_inmiscible("Timol (como HBA)", "Ácido Láctico", HBA_COMPONENTS, HBD_COMPONENTS) is False
    )
    assert par_inmiscible("Mentol", "Timol", HBA_COMPONENTS, HBD_COMPONENTS) is False
    assert (
        par_inmiscible("Cloruro de Colina (ChCl)", "Glicerol", HBA_COMPONENTS, HBD_COMPONENTS)
        is False
    )


def test_simulate_3step_process_keeps_final_scores_in_bounds() -> None:
    props = _thesis_props()
    poly_df = get_polyphenol_database().head(6)

    process = simulate_3step_process(props, poly_df, freq_us=25, temp_C=45, time_min=15)

    assert {"EP final (%)", "NEP final (%)", "Combinado final (%)"}.issubset(process.columns)
    assert process["EP final (%)"].between(0, 100).all()
    assert process["NEP final (%)"].between(0, 100).all()
