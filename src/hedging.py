import numpy as np
from src.bs import bs_price, delta
from src.mc import gbm_paths

def simulate_hedge(S0, K, T, r, iv_sold, sigma_realized, steps):
    dt = T / steps

    path = gbm_paths(S0, r, sigma_realized, T, steps, n_paths=1)[0]
    cash = bs_price(S0, K, T, r, iv_sold, option='call')

    position = 0.0   # BTC currently held as hedge
    log = []

    for i in range(steps):
        S = path[i]
        tau = max(T - i*dt, 1e-9)   # time remaining, floored to avoid T=0

        # delta of the call we SOLD, priced at iv_sold — that's our own model
        current_delta = delta(S, K, tau, r, iv_sold, option='call')
        target_position = +current_delta   # short the call -> hedge by buying delta

        trade_size = target_position - position
        cash -= trade_size * S    # buying spends cash, selling raises it
        position = target_position

        log.append({'day': i, 'S': S, 'delta': current_delta,
                    'position': position, 'trade_size': trade_size, 'cash': cash})

    S_final = path[-1]
    payoff = max(S_final - K, 0)
    final_pnl = cash + position * S_final - payoff

    return final_pnl, log

if __name__ == "__main__":
    pnl, log = simulate_hedge(S0=78000, K=78000, T=27/365, r=0.0,
                                iv_sold=0.38, sigma_realized=0.38, steps=27)
    print(f"Final P&L: {pnl:.2f}")
    print("\nFirst 5 days:")
    for row in log[:5]:
        print(f"day={row['day']:>2}  S={row['S']:>8.0f}  delta={row['delta']:.4f}  "
              f"position={row['position']:>7.4f}  trade={row['trade_size']:>8.4f}  cash={row['cash']:>10.2f}")