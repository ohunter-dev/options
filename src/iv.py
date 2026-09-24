import numpy as np
from scipy.optimize import brentq
from src.bs import bs_price

def implied_vol(market_price, S, K, T, r, option='call'):
    # want the sigma where BS price - market price = 0
    def objective(sigma):
        return bs_price(S, K, T, r, sigma, option) - market_price

    # brentq looks for the root between 0.001 and 5.0 (0.1% to 500% vol), so the answer has to be inside that bracket
    # not using newton, it steps using vega and vega goes to ~0 for deep ITM/OTM so it blows up right where I need a solid number. bracketing is safer
    return brentq(objective, 0.001, 5.0)