#plotting the surface (get_smile() (IV vs strike) and get_term_structure() (ATM IV vs days))
import matplotlib.pyplot as plt
from src.surface import get_smile
from src.term_structure import get_term_structure

spot, days, smile = get_smile(target_days=30)
_, term = get_term_structure()

strikes  = [row['strike'] for row in smile]
smile_iv = [row['iv']*100 for row in smile]

term_days = [row['days'] for row in term]
term_iv   = [row['atm_iv']*100 for row in term]

fig, axs = plt.subplots(1, 2, figsize=(12, 5))

axs[0].plot(strikes, smile_iv, marker='o', markersize=3)
axs[0].axvline(spot, color='gray', linestyle='--', label='spot')
axs[0].set_title(f"Vol smile, {days} day expiry")
axs[0].set_xlabel("Strike")
axs[0].set_ylabel("Implied vol (%)")
axs[0].legend()

axs[1].plot(term_days, term_iv, marker='o', markersize=4)
axs[1].set_title("Term structure, ATM IV")
axs[1].set_xlabel("Days to expiry")
axs[1].set_ylabel("ATM implied vol (%)")

plt.tight_layout()
plt.show()