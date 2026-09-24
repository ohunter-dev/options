import numpy as np
#monte carlo, simulating price paths. sharkfin needs the whole path not just the end price because of the barrier
def gbm_paths(S0, r, sigma, T, steps, n_paths):
    dt = T / steps
    # one random shock per step per path, drawn from a standard normal
    Z = np.random.standard_normal((n_paths, steps))
    # GBM step, same drift/vol setup as BS but done step by step instead of all in one go
    increments = (r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z #lognormal drift adjustment
    log_paths = np.log(S0) + np.cumsum(increments, axis=1)
    return np.exp(log_paths)   # shape: (n_paths, steps)

def price_sharkfin(S0, K, B, T, r, sigma, rebate, steps, n_paths):
    paths = gbm_paths(S0, r, sigma, T, steps, n_paths)

    knocked_out = paths.max(axis=1) >= B

    S_T = paths[:, -1]
    payoff_alive  = np.clip(S_T - K, 0, B - K)
    payoffs = np.where(knocked_out, rebate, payoff_alive)

    discounted = payoffs * np.exp(-r*T)
    price = discounted.mean()
    std_error = discounted.std() / np.sqrt(n_paths)
    knockout_rate = knocked_out.mean()

    # only keep ~40 paths for plotting, no point sending back all 100k
    sample_size = min(40, n_paths)
    sample_paths = paths[:sample_size]
    sample_knocked = knocked_out[:sample_size]

    return {
        'price': price, 'std_error': std_error, 'knockout_rate': knockout_rate,
        'sample_paths': sample_paths, 'sample_knocked': sample_knocked
    }

#sanity check: mean of log(S_T/S0) should come out at (r - 0.5sigma^2)T and the std at sigma*sqrt(T)
if __name__ == "__main__":
    # --- validate the path simulator itself ---
    S0, r, sigma, T = 78000, 0.0, 0.38, 27/365
    n_paths = 50000

    paths = gbm_paths(S0, r, sigma, T, steps=27, n_paths=n_paths)
    log_returns = np.log(paths[:, -1] / S0)

    theoretical_mean = (r - 0.5*sigma**2) * T
    theoretical_std  = sigma * np.sqrt(T)

    print("=== GBM validation ===")
    print(f"Simulated mean log return:  {log_returns.mean():.6f}")
    print(f"Theoretical mean:           {theoretical_mean:.6f}")
    print(f"Simulated std of log return:{log_returns.std():.6f}")
    print(f"Theoretical std:            {theoretical_std:.6f}")

    # --- price the sharkfin ---
    print("\n=== Sharkfin price ===")
    result = price_sharkfin(S0=78000, K=78000, B=95000, T=27/365, r=0.0,
                             sigma=0.38, rebate=200, steps=27, n_paths=100000)
    for key, val in result.items():
        print(f"{key:>15}: {val:.4f}")