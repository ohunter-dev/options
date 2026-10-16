import numpy as np
from scipy.stats import norm


def _d1(S, K, T, r, sigma, q=0.0):
    """Standardised distance to strike under the risk-neutral drift r - q."""
    return (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def bs_price(S, K, T, r, sigma, option="call", q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    d2 = d1 - sigma * np.sqrt(T)
    if option == "call":
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


# sigma*np.sqrt(T) in the denominator - vol scales with the square root of time, not linearly.
## This is why a 1-year option isn't 12x as vol-exposed as a 1-month one, only sqrt(12) ~ 3.46x.
## Same reason hedge frequency matters in hedging.py


# defining delta: differentiate C − P = S·e^(−qT) − K·e^(−rT) with respect to S: Δ_call − Δ_put
# =e^(−qT). With q = 0 this is the familiar 1.
def delta(S, K, T, r, sigma, option="call", q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    if option == "call":
        return np.exp(-q * T) * norm.cdf(d1)
    else:
        return np.exp(-q * T) * (norm.cdf(d1) - 1)  # cumulative dist function


# gamma = how fast delta changes when spot moves. same for a call and a put at the same strike
# biggest when spot is near the strike and expiry is close, so short dated ATM options are the ones
# that move delta around the most
# if I'm short an option I'm short gamma, so delta moves the wrong way and I end up buying high and
# selling low to stay hedged. that's why short gamma bleeds money
def gamma(S, K, T, r, sigma, q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    return np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))


# note the /100 at the end is due to it being in % terms. The / 100 at the end is the "quote per 1
# vol point" convention.
def vega(S, K, T, r, sigma, q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100


def theta(S, K, T, r, sigma, option="call", q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    d2 = d1 - sigma * np.sqrt(T)
    term1 = -(S * np.exp(-q * T) * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option == "call":
        term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
        term3 = q * S * np.exp(-q * T) * norm.cdf(d1)
    else:
        term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
        term3 = -q * S * np.exp(-q * T) * norm.cdf(-d1)
    return (term1 + term2 + term3) / 365


def vanna(S, K, T, r, sigma, q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    d2 = d1 - sigma * np.sqrt(T)
    return -np.exp(-q * T) * norm.pdf(d1) * d2 / sigma


def volga(S, K, T, r, sigma, q=0.0):
    d1 = _d1(S, K, T, r, sigma, q)
    d2 = d1 - sigma * np.sqrt(T)
    v = vega(S, K, T, r, sigma, q=q) * 100  # undo the /100 convention so the identity is clean
    return v * d1 * d2 / sigma / 100  # reapply the per-vol-point convention


if __name__ == "__main__":
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    h = 0.0001

    # vanna = d(delta)/d(sigma) - bump sigma, watch delta move
    delta_up = delta(S, K, T, r, sigma + h)
    delta_down = delta(S, K, T, r, sigma - h)
    numerical_vanna = (delta_up - delta_down) / (2 * h)
    print("numerical vanna: ", numerical_vanna)
    print("analytical vanna:", vanna(S, K, T, r, sigma))

    # volga = d(vega)/d(sigma) - bump sigma, watch vega move
    vega_up = vega(S, K, T, r, sigma + h)
    vega_down = vega(S, K, T, r, sigma - h)
    numerical_volga = (vega_up - vega_down) / (2 * h)
    print("numerical volga: ", numerical_volga)
    print("analytical volga:", volga(S, K, T, r, sigma))
