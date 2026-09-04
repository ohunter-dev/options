import numpy as np
from scipy.optimize import brentq
from src.bs import bs_price

def implied_vol(market_price, S, K, T, r, option='call'):
    # The function whose root we want: BS price minus market price = 0
    def objective(sigma):
        return bs_price(S, K, T, r, sigma, option) - market_price

    # brentq searches for the sigma that makes objective() zero,
    # within the bracket [0.001, 5.0] (0.1% to 500% vol) - bracketing here, we must be certain it is between our set criteria.
    #The alternative, Newton's method, uses vega as its step size and diverges when vega is near zero — 
    # which happens for deep ITM/OTM options, exactly where you most need a reliable number. Hence we pick bracketing.
    return brentq(objective, 0.001, 5.0)