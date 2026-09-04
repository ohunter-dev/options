import matplotlib.pyplot as plt
from src.mc import price_sharkfin

S0, K, B, T, r, sigma, rebate = 78000, 78000, 95000, 27/365, 0.0, 0.38, 200

result = price_sharkfin(S0, K, B, T, r, sigma, rebate, steps=27, n_paths=100000)

print(f"Price: {result['price']:.2f}")
print(f"Std error: {result['std_error']:.2f}")
print(f"Knockout rate: {result['knockout_rate']:.4f}")

paths = result['sample_paths']
knocked = result['sample_knocked']

fig, ax = plt.subplots(figsize=(10, 6))

for i in range(len(paths)):
    color = 'red' if knocked[i] else 'steelblue'
    alpha = 0.7 if knocked[i] else 0.4
    ax.plot(paths[i], color=color, alpha=alpha, linewidth=1)

ax.axhline(B, color='black', linestyle='--', linewidth=1.5, label=f'Barrier ({B:,.0f})')
ax.axhline(S0, color='gray', linestyle=':', linewidth=1, label=f'Spot ({S0:,.0f})')
ax.set_title(f"Sample of {len(paths)} simulated paths — red = knocked out")
ax.set_xlabel("Day")
ax.set_ylabel("BTC price")
ax.legend()
plt.tight_layout()
plt.show()