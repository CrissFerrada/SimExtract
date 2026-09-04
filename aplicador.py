"""What the sample applicator actually sees.

The properties panel reports viscosity at the extraction temperature, which is not
the temperature the syringe works at. For a NADES the difference is not cosmetic:
the Arrhenius term the model already uses gives roughly a factor of two between
40 °C and a climatised room.

Composition also drifts, but the direction is set by humidity, not by volatility.
A NADES is hygroscopic and its water activity sits well below unity — betaine-based
systems measure about 0.4 at 14-22 wt% water — so the deposit exchanges water with
the room until the two match. Above that relative humidity the NADES *takes up*
water and thins; below it, it dries and thickens toward the anhydrous eutectic,
whose melting point is far higher (choline chloride alone melts at 302 °C).

Both directions are reported because both occur, and which one applies is a
property of the room, not of the solvent. A sample prepared in humid air and
applied in dry air crosses from one branch to the other on the way, so the branch
that matters is the one at the applicator — which has to be measured there, with a
hygrometer, not assumed from where the extraction was done.

Nothing here predicts whether a given applicator will clog: that has no published
answer for NADES and is settled with a bench test, not a model.

Imports no Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass

from model import calculate_nades_properties

TEMP_APLICACION_C = 22.0
"""Default room temperature at the applicator. Overridable: it matters a lot."""

AGUA_RESIDUAL = (30.0, 20.0, 10.0, 0.0)
"""Water contents explored on the drying branch."""

AGUA_GANADA = (10.0, 20.0)
"""Extra water explored on the humid branch, in points above the current content."""

ACTIVIDAD_AGUA_TIPICA = 0.4
"""Water activity measured for betaine-based NADES at 14-22 wt% water.

The deposit exchanges water with the room until its activity matches the relative
humidity. Above this figure the NADES gains water; below it, it loses water. A
NADES at 30 % water sits higher than this, so treat it as a lower bound.
"""


@dataclass(frozen=True)
class LecturaAplicador:
    """Viscosity as the applicator sees it, and how it drifts as water leaves."""

    visc_extraccion: float
    temp_extraccion: float
    visc_aplicacion: float
    temp_aplicacion: float
    deriva: tuple[tuple[float, float], ...]
    hidratacion: tuple[tuple[float, float], ...]

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

    @property
    def factor_humedo(self) -> float:
        """How much thinner it becomes if it takes up water from the room."""
        if not self.hidratacion:
            return 1.0
        return self.hidratacion[-1][1] / max(self.visc_aplicacion, 1e-9)

    def rama_probable(self, humedad_relativa: float) -> str:
        """Return which branch a given room humidity puts the deposit on.

        Args:
            humedad_relativa: Room relative humidity, as a percentage.

        Returns:
            "hidratacion", "secado", or "equilibrio" when the two are close.
        """
        cruce = ACTIVIDAD_AGUA_TIPICA * 100
        if humedad_relativa > cruce + 5:
            return "hidratacion"
        if humedad_relativa < cruce - 5:
            return "secado"
        return "equilibrio"


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
    ganadas = tuple(min(water_pct + d, 90.0) for d in AGUA_GANADA)
    return LecturaAplicador(
        visc_extraccion=_visc(water_pct, temp_extraccion),
        temp_extraccion=temp_extraccion,
        visc_aplicacion=_visc(water_pct, temp_aplicacion),
        temp_aplicacion=temp_aplicacion,
        deriva=tuple((a, _visc(a, temp_aplicacion)) for a in aguas),
        hidratacion=tuple((a, _visc(a, temp_aplicacion)) for a in ganadas),
    )
