import numpy as np
from src.bs import bs_price, delta, gamma, vega, theta

def price_position(position, S, r):
    # position is a dict describing one holding: strike, expiry, type, quantity
    K = position['K']
    T = position['T']
    sigma = position['sigma']
    option = position['type']
    qty = position['qty']   # positive = long, negative = short

    price = bs_price(S, K, T, r, sigma, option) * qty
    pos_delta = delta(S, K, T, r, sigma, option) * qty
    pos_gamma = gamma(S, K, T, r, sigma) * qty
    pos_vega  = vega(S, K, T, r, sigma) * qty
    pos_theta = theta(S, K, T, r, sigma, option) * qty

    return {'price': price, 'delta': pos_delta, 'gamma': pos_gamma,
            'vega': pos_vega, 'theta': pos_theta}

# this def price_book function allows us to aggregate greeks
def price_book(book, S, r):
    totals = {'price': 0, 'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0}

    for pos in book:
        result = price_position(pos, S, r)
        for key in totals:
            totals[key] += result[key]

    return totals

if __name__ == "__main__":
    book = [
        {'K': 85000, 'T': 27/365, 'sigma': 0.36, 'type': 'call', 'qty': -10},
        {'K': 70000, 'T': 27/365, 'sigma': 0.40, 'type': 'put',  'qty': 5},
    ]

    S = 78000
    r = 0.0

    for pos in book:
        result = price_position(pos, S, r)
        print(f"K={pos['K']} {pos['type']:>4} qty={pos['qty']:>4}  "
              f"price={result['price']:>10.2f}  delta={result['delta']:>8.4f}  "
              f"gamma={result['gamma']:>10.6f}  vega={result['vega']:>8.4f}  theta={result['theta']:>8.4f}")

    print("\n--- Book totals ---")
    net = price_book(book, S, r)
    for key, val in net.items():
        print(f"{key:>8}: {val:.4f}")