import numpy as np
import matplotlib.pyplot as plt

from src.bs import bs_price, delta, gamma, vega, theta


print(bs_price(S=100, K=100, T=1, r=0.05, sigma=0.2, option='call'))

#put call parity sanity checker
call = bs_price(S=100, K=100, T=1, r=0.05, sigma=0.2, option='call')
put  = bs_price(S=100, K=100, T=1, r=0.05, sigma=0.2, option='put')
lhs = call - put
rhs = 100 - 100*np.exp(-0.05*1)
print("C - P:", lhs)
print("S - K*e^-rT:", rhs)

#calculating delta in 2 ways - numerical and analytical:
h = 0.01
price_up   = bs_price(S=100+h, K=100, T=1, r=0.05, sigma=0.2, option='call')
price_down = bs_price(S=100-h, K=100, T=1, r=0.05, sigma=0.2, option='call')
numerical_delta = (price_up - price_down) / (2*h)

analytical_delta = delta(S=100, K=100, T=1, r=0.05, sigma=0.2, option='call')

print("numerical: ", numerical_delta)
print("analytical:", analytical_delta)

#testing bumping the price (by h) and therefore calculating gamma: 
delta_up   = delta(S=100+h, K=100, T=1, r=0.05, sigma=0.2, option='call')
delta_down = delta(S=100-h, K=100, T=1, r=0.05, sigma=0.2, option='call')
numerical_gamma = (delta_up - delta_down) / (2*h)

analytical_gamma = gamma(S=100, K=100, T=1, r=0.05, sigma=0.2)

print("numerical gamma: ", numerical_gamma)
print("analytical gamma:", analytical_gamma)

#vega calcs - bumping volatility this time
h_sigma = 0.0001
price_vol_up   = bs_price(S=100, K=100, T=1, r=0.05, sigma=0.2+h_sigma, option='call')
price_vol_down = bs_price(S=100, K=100, T=1, r=0.05, sigma=0.2-h_sigma, option='call')
numerical_vega = (price_vol_up - price_vol_down) / (2*h_sigma) / 100

analytical_vega = vega(S=100, K=100, T=1, r=0.05, sigma=0.2)

print("numerical vega: ", numerical_vega)
print("analytical vega:", analytical_vega)

#theta calcs now - note h_T done in calendar days 365. bumping by a day.
h_T = 1/365
price_T_up   = bs_price(S=100, K=100, T=1+h_T, r=0.05, sigma=0.2, option='call')
price_T_down = bs_price(S=100, K=100, T=1-h_T, r=0.05, sigma=0.2, option='call')
numerical_theta = (price_T_down - price_T_up) / (2*h_T) / 365 #note this is price down - price up, comes out -ve as theta should. Sign matches.

analytical_theta = theta(S=100, K=100, T=1, r=0.05, sigma=0.2, option='call')

print("numerical theta: ", numerical_theta)
print("analytical theta:", analytical_theta)    

#plots below

# Plot each greek's shape as spot varies, holding K, T, r, sigma fixed
spots = np.linspace(50, 150, 200)   # 200 spot points from 50 to 150

deltas = [delta(S, K=100, T=1, r=0.05, sigma=0.2, option='call') for S in spots]
gammas = [gamma(S, K=100, T=1, r=0.05, sigma=0.2) for S in spots]
vegas  = [vega(S, K=100, T=1, r=0.05, sigma=0.2) for S in spots]
thetas = [theta(S, K=100, T=1, r=0.05, sigma=0.2, option='call') for S in spots]

fig, axs = plt.subplots(2, 2, figsize=(10, 8))
axs[0,0].plot(spots, deltas); axs[0,0].set_title("Delta vs Spot"); axs[0,0].axvline(100, color='gray', linestyle='--')
axs[0,1].plot(spots, gammas); axs[0,1].set_title("Gamma vs Spot"); axs[0,1].axvline(100, color='gray', linestyle='--')
axs[1,0].plot(spots, vegas);  axs[1,0].set_title("Vega vs Spot");  axs[1,0].axvline(100, color='gray', linestyle='--')
axs[1,1].plot(spots, thetas); axs[1,1].set_title("Theta vs Spot"); axs[1,1].axvline(100, color='gray', linestyle='--')
plt.tight_layout()
plt.show()