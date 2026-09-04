import numpy as np
from src.bs import bs_price, delta
from src.mc import gbm_paths

def simulate_hedge(S0, K, T, r, iv_sold, sigma_realized, steps):
    dt = T / steps

    path = gbm_paths(S0, r, sigma_realized, T, steps, n_paths=1)[0]
    cash = bs_price(S0, K, T, r, iv_sold, option='call')

    position = 0.0   # BTC currently held as hedge - this section is for hedging us selling a call (long delta)
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

import numpy as np #this section below runs 50 simulations at different realized vol levels, giving pnls is we sold at 38% IV. 

if __name__ == "__main__":
    iv_sold = 0.38
    n_runs = 50   # independent paths per vol level, to average out single-path noise

    print(f"Selling at iv_sold = {iv_sold*100:.0f}%\n")
    print(f"{'realized_vol':>14} {'avg_pnl':>12}")

    for sigma_realized in [0.20, 0.30, 0.38, 0.45, 0.60, 0.80]:
        pnls = []   # will collect one pnl per run at this vol level

        for run in range(n_runs):
            pnl, log = simulate_hedge(S0=78000, K=78000, T=27/365, r=0.0,
                                        iv_sold=iv_sold, sigma_realized=sigma_realized, steps=27)
            pnls.append(pnl)

        avg_pnl = np.mean(pnls)
        print(f"{sigma_realized*100:>13.0f}% {avg_pnl:>12.2f}")

