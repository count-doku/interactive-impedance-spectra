"""Equivalent-circuit impedance of a lithium-ion cell.

Sign convention follows electrochemical impedance spectroscopy (EIS): the
angular frequency ``w`` is in rad/s, impedances are complex and in Ohm, and a
Nyquist plot shows ``-Im(Z)`` over ``Re(Z)``.

The full model is

    Z(w) = R0 + Z_RC(w) + Z_ZARC(w) + Z_CPE(w)

where each term maps onto a physical effect of the cell:

    R0      ohmic resistance of current collectors, electrolyte and contacts
    RC      a charge-transfer process with ideal double-layer capacitance
    ZARC    the same, but with a distributed time constant (depressed arc)
    CPE     diffusion-like low-frequency tail
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

Complex = NDArray[np.complex128]


def cpe(w: ArrayLike, A: float, phi: float) -> Complex:
    """Constant phase element ``1 / (A (jw)**phi)``.

    ``phi = 1`` degenerates to a capacitor of capacitance ``A``, ``phi = 0`` to
    a resistor of ``1 / A``. Intermediate values give the constant phase angle
    of ``-phi * 90 deg`` that gives the element its name.
    """
    return 1 / (A * (1j * np.asarray(w, dtype=float)) ** phi)


def rc(w: ArrayLike, R: float, C: float) -> Complex:
    """Resistor parallel to a capacitor — a semicircle in the Nyquist plane."""
    return 1 / (1 / R + 1j * np.asarray(w, dtype=float) * C)


def zarc(w: ArrayLike, R: float, A: float, phi: float) -> Complex:
    """Resistor parallel to a CPE — a semicircle depressed by ``phi``."""
    return 1 / (1 / R + 1 / cpe(w, A, phi))


def impedance(
    w: ArrayLike,
    R0: float,
    R1: float,
    C1: float,
    R2: float,
    A2: float,
    phi2: float,
    A3: float,
    phi3: float,
) -> Complex:
    """Impedance of the full R0 + RC + ZARC + CPE model."""
    return R0 + rc(w, R1, C1) + zarc(w, R2, A2, phi2) + cpe(w, A3, phi3)


def components(
    w: ArrayLike,
    R0: float,
    R1: float,
    C1: float,
    R2: float,
    A2: float,
    phi2: float,
    A3: float,
    phi3: float,
) -> dict[str, Complex]:
    """The model and its parts, each shifted by the resistances ahead of it.

    Shifting is what makes the parts line up with the full spectrum in a
    Nyquist plot, so every arc sits where it actually shows up in a measurement
    instead of all of them starting at the origin.
    """
    return {
        "RC": R0 + rc(w, R1, C1),
        "ZARC": R0 + R1 + zarc(w, R2, A2, phi2),
        "CPE": R0 + R1 + R2 + cpe(w, A3, phi3),
        "Z": impedance(w, R0, R1, C1, R2, A2, phi2, A3, phi3),
    }


def log_frequency(f_low: float = -6, f_high: float = 3, n: int = 1000) -> NDArray[np.float64]:
    """Angular frequencies [rad/s] over ``10**f_low .. 10**f_high`` Hz."""
    return 2 * np.pi * np.logspace(f_low, f_high, n)
