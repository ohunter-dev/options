import numpy as np
from src.bs import bs_price, delta
from src.mc import gbm_paths

def simulate_hedge_on_path(path, S0, K, T, r, iv_sold, hedge_interval_days, fine_steps):
    # path is a single, already-generated fine-resolution price path.
    # hedge_interval_days controls how often we ACT on it — everything else fixed.
    fine_dt = T / fine_steps
    steps_per_hedge = max(1, round(hedge_interval_days / (T*365/fine_steps)))

    cash = bs_price(S0, K, T, r, iv_sold, option='call')
    position = 0.0

    for i in range(0, fine_steps, steps_per_hedge):
        S = path[i]
        tau = max(T - i*fine_dt, 1e-9)
        current_delta = delta(S, K, tau, r, iv_sold, option='call')
        target_position = current_delta
        trade_size = target_position - position
        cash -= trade_size * S
        position = target_position

    S_final = path[-1]
    payoff = max(S_final - K, 0)
    return cash + position * S_final - payoff


if __name__ == "__main__":
    S0, K, T, r = 78000, 78000, 27/365, 0.0
    iv_sold = 0.38
    sigma_realized = 0.55
    n_runs = 50
    fine_steps = 648   # hourly resolution — fine enough for both strategies to sample from

    daily_pnls = []
    hourly_pnls = []

    for run in range(n_runs):
        np.random.seed(run)   # SAME seed for both strategies this run —
                                # guarantees they see the identical path
        path = gbm_paths(S0, r, sigma_realized, T, fine_steps, n_paths=1)[0]

        daily_pnl  = simulate_hedge_on_path(path, S0, K, T, r, iv_sold,
                                             hedge_interval_days=1, fine_steps=fine_steps)
        hourly_pnl = simulate_hedge_on_path(path, S0, K, T, r, iv_sold,
                                             hedge_interval_days=1/24, fine_steps=fine_steps)

        daily_pnls.append(daily_pnl)
        hourly_pnls.append(hourly_pnl)

    print(f"Daily hedging  — avg: {np.mean(daily_pnls):>10.2f}   std: {np.std(daily_pnls):>10.2f}")
    print(f"Hourly hedging — avg: {np.mean(hourly_pnls):>10.2f}   std: {np.std(hourly_pnls):>10.2f}")