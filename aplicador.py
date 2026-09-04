"""What the sample applicator actually sees.

The properties panel reports viscosity at the extraction temperature, which is not
the temperature the syringe works at. For a NADES the difference is not cosmetic:
the Arrhenius term the model already uses gives roughly a factor of two between
40 °C and a climatised room.

Worse for the capillary is composition drift. Water is the only volatile component
of a hydrated NADES, so in a fine bore with a large surface-to-volume ratio the
mixture moves toward the anhydrous eutectic as water leaves — and viscosity climbs
steeply while the melting point rises (choline chloride itself melts at 302 °C).

Nothing here is a prediction of whether a given applicator will clog: that has no
published answer for NADES and is settled with a bench test, not a model. The
module reports the numbers the operator should have in front of them before
putting a NADES through an expensive instrument.

Imports no Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass

from model import calculate_nades_properties

TEMP_APLICACION_C = 22.0
"""Default room temperature at the applicator. Overridable: it matters a lot."""

AGUA_RESIDUAL = (30.0, 20.0, 10.0, 0.0)
"""Water contents explored as the capillary loses the volatile fraction."""


@dataclass(frozen=True)
class LecturaAplicador:
    """Viscosity as the applicator sees it, and how it drifts as water leaves."""

    visc_extraccion: float
    temp_extraccion: float
    visc_aplicacion: float
    temp_aplicacion: float
    deriva: tuple[tuple[float, float], ...]

    @property
    def factor_temperatura(self) -> float:
        """How much thicker it is at the applicator than at extraction."""
        return self.visc_aplicacion / max(self.visc_extraccion, 1e-9)

    @property
    def factor_secado(self) -> float:
        """How much thicker it becomes if the added water is lost entirely."""
        if not self.deriva:
            return 1.0
        return self.deriva[-1][1] / max(self.visc_aplicacion, 1e-9)


def lectura_aplicador(
    hba: str,
    hbd: str,
    ratio_hba: float,
    ratio_hbd: float,
    water_pct: float,
    temp_extraccion: float,
    hba_db: dict,
    hbd_db: dict,
    temp_aplicacion: float = TEMP_APLICACION_C,
) -> LecturaAplicador:
    """Report viscosity at the applicator and its drift as water evaporates.

    Args:
        hba: Hydrogen-bond acceptor name.
        hbd: Hydrogen-bond donor name.
        ratio_hba: Molar parts of the acceptor.
        ratio_hbd: Molar parts of the donor.
        water_pct: Added water, as set for the extraction.
        temp_extraccion: Extraction temperature, in °C.
        hba_db: Acceptor database.
        hbd_db: Donor database.
        temp_aplicacion: Temperature at the syringe, in °C.

    Returns:
        The reading, with the drift series ordered from the current water content
        down to none.
    """

    def _visc(agua: float, temp: float) -> float:
        return calculate_nades_properties(
            hba, hbd, ratio_hba, ratio_hbd, agua, temp, hba_db, hbd_db
        )["viscosidad"]

    aguas = tuple(a for a in AGUA_RESIDUAL if a <= water_pct) or (water_pct,)
    return LecturaAplicador(
        visc_extraccion=_visc(water_pct, temp_extraccion),
        temp_extraccion=temp_extraccion,
        visc_aplicacion=_visc(water_pct, temp_aplicacion),
        temp_aplicacion=temp_aplicacion,
        deriva=tuple((a, _visc(a, temp_aplicacion)) for a in aguas),
    )
