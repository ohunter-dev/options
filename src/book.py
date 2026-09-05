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

def scenario_grid(book, spot_range, vol_shift_range, r):
    # spot_range: array of spot levels to test
    # vol_shift_range: array of vol shifts (added to each position's own sigma)
    results = np.zeros((len(vol_shift_range), len(spot_range)))

    for i, vol_shift in enumerate(vol_shift_range):
        for j, S in enumerate(spot_range):
            # build a shifted copy of the book — same strikes/qty, vol bumped
            shifted_book = []
            for pos in book:
                shifted_pos = pos.copy()
                shifted_pos['sigma'] = pos['sigma'] + vol_shift
                shifted_book.append(shifted_pos)

            total = price_book(shifted_book, S, r)
            results[i, j] = total['price']

    return results

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

    print("\n--- Scenario grid (book P&L) ---")
    spot_range = np.array([70000, 74000, 78000, 82000, 86000, 90000])
    vol_shift_range = np.array([-0.10, -0.05, 0.0, 0.05, 0.10])

    grid = scenario_grid(book, spot_range, vol_shift_range, r)

    header = "vol_shift\\spot  " + "  ".join(f"{s:>8}" for s in spot_range)
    print(header)
    for i, vol_shift in enumerate(vol_shift_range):
            row = "  ".join(f"{grid[i,j]:>8.0f}" for j in range(len(spot_range)))
            print(f"{vol_shift:>+13.2f}  {row}")