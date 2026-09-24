import numpy as np
from src.bs import bs_price, delta
from src.mc import gbm_paths

def simulate_hedge_on_path(path, S0, K, T, r, iv_sold, hedge_interval_days, fine_steps, cost_bps=0):
    fine_dt = T / fine_steps
    steps_per_hedge = max(1, round(hedge_interval_days / (T*365/fine_steps)))

    cash = bs_price(S0, K, T, r, iv_sold, option='call')
    position = 0.0
    total_cost = 0.0   # keep a running total of costs so I can see them on their own

    for i in range(0, fine_steps, steps_per_hedge):
        S = path[i]
        tau = max(T - i*fine_dt, 1e-9)
        current_delta = delta(S, K, tau, r, iv_sold, option='call')
        target_position = current_delta
        trade_size = target_position - position

        notional_traded = abs(trade_size) * S
        cost = notional_traded * (cost_bps / 10000)   # bps -> decimal

        cash -= trade_size * S    # the actual hedge trade
        cash -= cost              # the friction on top of it
        total_cost += cost
        position = target_position

    S_final = path[-1]
    payoff = max(S_final - K, 0)
    final_pnl = cash + position * S_final - payoff
    return final_pnl, total_cost


if __name__ == "__main__":
    S0, K, T, r = 78000, 78000, 27/365, 0.0
    iv_sold = 0.38
    sigma_realized = 0.55
    n_runs = 50
    fine_steps = 648
    cost_bps = 5   # 5bps per trade, roughly what crypto spot spread + fees look like

    daily_pnls, daily_costs = [], []
    hourly_pnls, hourly_costs = [], []

    for run in range(n_runs):
        np.random.seed(run)
        path = gbm_paths(S0, r, sigma_realized, T, fine_steps, n_paths=1)[0]

        d_pnl, d_cost = simulate_hedge_on_path(path, S0, K, T, r, iv_sold,
                                                hedge_interval_days=1, fine_steps=fine_steps, cost_bps=cost_bps)
        h_pnl, h_cost = simulate_hedge_on_path(path, S0, K, T, r, iv_sold,
                                                hedge_interval_days=1/24, fine_steps=fine_steps, cost_bps=cost_bps)

        daily_pnls.append(d_pnl); daily_costs.append(d_cost)
        hourly_pnls.append(h_pnl); hourly_costs.append(h_cost)

    print(f"Daily  | avg pnl: {np.mean(daily_pnls):>10.2f}  std: {np.std(daily_pnls):>10.2f}"
          f"  avg cost paid: {np.mean(daily_costs):>8.2f}")
    print(f"Hourly | avg pnl: {np.mean(hourly_pnls):>10.2f}  std: {np.std(hourly_pnls):>10.2f}"
          f"  avg cost paid: {np.mean(hourly_costs):>8.2f}")