import pandas as pd

from data import HBA_COMPONENTS, HBD_COMPONENTS, THESIS_NADES, get_polyphenol_database
from model import (
    calculate_nades_properties,
    combined_score,
    ep_extraction_score,
    nep_extraction_score,
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


def test_simulate_3step_process_keeps_final_scores_in_bounds() -> None:
    props = _thesis_props()
    poly_df = get_polyphenol_database().head(6)

    process = simulate_3step_process(props, poly_df, freq_us=25, temp_C=45, time_min=15)

    assert {"EP final (%)", "NEP final (%)", "Combinado final (%)"}.issubset(process.columns)
    assert process["EP final (%)"].between(0, 100).all()
    assert process["NEP final (%)"].between(0, 100).all()
