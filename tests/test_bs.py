"""Black-Scholes-Merton pricer and greeks.

Three kinds of check:
  1. Known values: textbook prices with no dividend, and an independent recomputation with one.
  2. No-arbitrage: put-call parity must hold for any inputs.
  3. Every analytical greek must match a finite-difference bump of the price.
"""

import numpy as np
import pytest

from optlib.bs import bs_price, delta, gamma, theta, vanna, vega, volga

# T != 1 on purpose: a stray *T or /T is invisible at T = 1.
CASES = [
    (100.0, 100.0, 0.5, 0.05, 0.20, 0.02),  # ATM
    (100.0, 120.0, 0.25, 0.03, 0.35, 0.00),  # OTM call, no dividend
    (771.79, 772.0, 28 / 365, 0.045, 0.129, 0.012),  # SPY-like, 2026-10-16
    (50.0, 40.0, 2.0, 0.01, 0.15, 0.04),  # deep ITM call, long-dated, high yield
]
RIGHTS = ["call", "put"]


def test_textbook_value_no_dividend() -> None:
    # Hull, Options, Futures and Other Derivatives: S=K=100, T=1, r=5%, vol=20%
    assert bs_price(100, 100, 1, 0.05, 0.2) == pytest.approx(10.450583572185565, abs=1e-12)
    assert bs_price(100, 100, 1, 0.05, 0.2, "put") == pytest.approx(5.573526022256971, abs=1e-12)


def test_dividend_values() -> None:
    assert bs_price(100, 100, 0.5, 0.05, 0.2, "call", q=0.02) == pytest.approx(
        6.307635154954198, abs=1e-12
    )


def test_q_zero_is_plain_black_scholes() -> None:
    for S, K, T, r, s, _ in CASES:
        for right in RIGHTS:
            assert bs_price(S, K, T, r, s, right) == bs_price(S, K, T, r, s, right, q=0.0)


def test_dividend_cheapens_calls_and_richens_puts() -> None:
    assert bs_price(100, 100, 1, 0.05, 0.2, "call", q=0.03) < bs_price(100, 100, 1, 0.05, 0.2)
    assert bs_price(100, 100, 1, 0.05, 0.2, "put", q=0.03) > bs_price(100, 100, 1, 0.05, 0.2, "put")


@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_put_call_parity(S: float, K: float, T: float, r: float, sigma: float, q: float) -> None:
    lhs = bs_price(S, K, T, r, sigma, "call", q=q) - bs_price(S, K, T, r, sigma, "put", q=q)
    assert lhs == pytest.approx(S * np.exp(-q * T) - K * np.exp(-r * T), abs=1e-10)


@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_delta_parity(S: float, K: float, T: float, r: float, sigma: float, q: float) -> None:
    diff = delta(S, K, T, r, sigma, "call", q=q) - delta(S, K, T, r, sigma, "put", q=q)
    assert diff == pytest.approx(np.exp(-q * T), abs=1e-12)


# ---- finite differences: analytical greek == numerical bump ----------------


def _bump(f, x: float, h: float) -> float:
    return (f(x + h) - f(x - h)) / (2 * h)


@pytest.mark.parametrize("right", RIGHTS)
@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_delta_matches_bump(S, K, T, r, sigma, q, right) -> None:
    num = _bump(lambda s: bs_price(s, K, T, r, sigma, right, q=q), S, S * 1e-4)
    assert delta(S, K, T, r, sigma, right, q=q) == pytest.approx(num, rel=1e-6, abs=1e-8)


@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_gamma_matches_bump(S, K, T, r, sigma, q) -> None:
    num = _bump(lambda s: delta(s, K, T, r, sigma, "call", q=q), S, S * 1e-4)
    assert gamma(S, K, T, r, sigma, q=q) == pytest.approx(num, rel=1e-5, abs=1e-10)


@pytest.mark.parametrize("right", RIGHTS)
@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_vega_matches_bump(S, K, T, r, sigma, q, right) -> None:
    num = _bump(lambda v: bs_price(S, K, T, r, v, right, q=q), sigma, 1e-5) / 100  # per vol point
    assert vega(S, K, T, r, sigma, q=q) == pytest.approx(num, rel=1e-6, abs=1e-10)


@pytest.mark.parametrize("right", RIGHTS)
@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_theta_matches_bump(S, K, T, r, sigma, q, right) -> None:
    # theta is value lost per calendar day as expiry approaches, i.e. -dV/dT / 365
    num = -_bump(lambda t: bs_price(S, K, t, r, sigma, right, q=q), T, 1e-6) / 365
    assert theta(S, K, T, r, sigma, right, q=q) == pytest.approx(num, rel=1e-5, abs=1e-9)


@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_vanna_matches_bump(S, K, T, r, sigma, q) -> None:
    num = _bump(lambda v: delta(S, K, T, r, v, "call", q=q), sigma, 1e-5)
    assert vanna(S, K, T, r, sigma, q=q) == pytest.approx(num, rel=1e-5, abs=1e-8)


@pytest.mark.parametrize(("S", "K", "T", "r", "sigma", "q"), CASES)
def test_volga_matches_bump(S, K, T, r, sigma, q) -> None:
    num = _bump(lambda v: vega(S, K, T, r, v, q=q), sigma, 1e-5)
    assert volga(S, K, T, r, sigma, q=q) == pytest.approx(num, rel=1e-5, abs=1e-10)
