"""Checks that the circuit elements degenerate to the textbook cases."""

import numpy as np

from impedance import components, cpe, impedance, log_frequency, rc, zarc

W = log_frequency(-4, 4, 200)
PARAMS = dict(R0=0.01, R1=0.02, C1=100, R2=0.025, A2=1000, phi2=0.8, A3=20000, phi3=0.5)


def test_cpe_with_phi_one_is_a_capacitor():
    np.testing.assert_allclose(cpe(W, 1e-3, 1.0), 1 / (1j * W * 1e-3))


def test_cpe_with_phi_zero_is_a_resistor():
    np.testing.assert_allclose(cpe(W, 50.0, 0.0), np.full_like(W, 1 / 50.0, dtype=complex))


def test_cpe_phase_is_constant():
    phi = 0.6
    phase = np.angle(cpe(W, 500, phi))
    np.testing.assert_allclose(phase, -phi * np.pi / 2, atol=1e-12)


def test_rc_spans_from_r_to_short_circuit():
    z = rc(W, R=0.02, C=100)
    assert np.isclose(z[0].real, 0.02, rtol=1e-3)  # DC end: the resistor
    assert abs(z[-1]) < 1e-6  # HF end: the capacitor shorts it out


def test_zarc_with_phi_one_is_an_rc():
    np.testing.assert_allclose(zarc(W, R=0.02, A=100, phi=1.0), rc(W, R=0.02, C=100))


def test_model_converges_to_r0_at_high_frequency():
    z = impedance(log_frequency(8, 9, 10), **PARAMS)
    np.testing.assert_allclose(z.real, PARAMS["R0"], rtol=1e-3)


def test_model_is_passive():
    z = impedance(W, **PARAMS)
    assert np.all(z.real > 0)  # dissipates energy, never supplies it
    assert np.all(-z.imag >= 0)  # capacitive: the Nyquist curve stays above the axis


def test_components_sum_to_the_full_model():
    c = components(W, **PARAMS)
    # Each part carries the resistances plotted ahead of it, so summing the
    # three parts counts R0 three times and R1 twice where the model has R0 once.
    duplicated = 2 * PARAMS["R0"] + 2 * PARAMS["R1"] + PARAMS["R2"]
    np.testing.assert_allclose(c["RC"] + c["ZARC"] + c["CPE"] - duplicated, c["Z"])
