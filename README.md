# Options Pricing & Risk Library
[![CI](https://github.com/ohunter-dev/options/actions/workflows/ci.yml/badge.svg)](https://github.com/ohunter-dev/options/actions/workflows/ci.yml)

A from-scratch build of the pricing, hedging and risk tools an options desk uses: a Black-Scholes engine with the full Greek stack, implied vol smiles and term structure from live Deribit BTC/ETH data, pricing of the structured products clients actually buy (dual-currency notes, risk reversals, sharkfins), a delta-hedging simulator, and book-level risk with scenario grids. Every analytical Greek is tested against a finite-difference bump.

## Example: what delta hedging actually earns

`python -m optlib.hedging` sells a 27-day at-the-money BTC call at 38% vol, then hedges it along 500 simulated paths where the market actually realises 55%, paying 5bp per hedge trade:

```
sold at 38% vol, realised 55%: theory C(38%) - C(55%) = -1435.86

Daily  | avg pnl:   -1545.51  std:    1074.35  avg cost paid:    95.68
Hourly | avg pnl:   -1853.62  std:     888.59  avg cost paid:   399.52
Daily  | pnl before costs vs theory:   -13.97  (std error 48.05)
Hourly | pnl before costs vs theory:   -18.24  (std error 39.74)
```

**Reading it.** An option seller who delta hedges is short realised vol. Selling at 38% when the market moves at 55% should lose the difference between the option priced at the two vols, about 1,436 per contract. Before costs, the simulation lands within one standard error of that number at both hedge frequencies, which checks the pricer, the Greeks and the hedging loop against each other. Hedging hourly instead of daily cuts the spread of outcomes (std 889 vs 1,074) but costs four times as much in fees. That trade-off is the real decision a desk makes.

## Setup

```
uv sync --group dev
uv run pytest -q
```

Without uv: `pip install -e .` then `pip install pytest`. Each module runs its own worked example:

```
uv run python -m optlib.bs        # Greeks vs finite-difference bumps
uv run python -m optlib.mc        # GBM check, then the sharkfin price
uv run python -m optlib.hedging   # the example above
uv run python -m optlib.book      # book Greeks and a spot x vol scenario grid
uv run python -m optlib.surface   # live: needs internet access to Deribit
uv run python -m optlib.products  # live: dual-currency note and risk reversal
```

## Modules

| File | What it does |
| --- | --- |
| `bs.py` | Black-Scholes price and six Greeks (delta, gamma, vega, theta, vanna, volga) |
| `iv.py` | Implied vol solver (Brent's method) |
| `data.py` | Deribit public API client: instruments, tickers, trade tape |
| `surface.py` | Live vol smile from out-of-the-money options, interpolated to any strike |
| `term_structure.py` | At-the-money implied vol across all listed expiries |
| `products.py` | Dual-currency notes and risk reversals, broken into vanillas and priced off the live smile |
| `mc.py` | GBM path simulation and Monte Carlo pricing of the sharkfin (up-and-out call with rebate) |
| `hedging.py` | Delta-hedging simulator: realised vs sold vol, hedge frequency and transaction costs |
| `book.py` | Multi-position book: aggregate Greeks and spot x vol scenario grids |
| `tca.py` / `tca_live.py` | Mark-outs on synthetic and real Deribit trades: does the price revert (impact) or keep going (information)? |
| `composite_mid.py` | Volume-weighted mid across Binance, Coinbase and OKX |

## Testing

48 parametrised test cases in `tests/test_bs.py` check every analytical Greek against a numerical bump, plus put-call parity, delta parity and dividend cases. CI runs `ruff` and `pytest` on Python 3.11 and 3.12 on every push.

## Known simplifications

Things simplified on purpose, written down so they don't look like bugs:

- **r = 0 throughout.** This matches Deribit's own convention (`interest_rate: 0.0` in every ticker), but wouldn't hold for a rates-bearing underlying.
- **Options are priced off each expiry's forward, not spot**, using the instrument's own `underlying_price`. Pricing off spot produced a visible kink at the at-the-money put/call boundary; using the forward removes it.
- **No inverse settlement adjustment.** Deribit BTC options settle in BTC. They're treated here as USD vanillas after converting the mark price at the forward. Doing it properly means changing the numeraire.
- **The sharkfin barrier is checked once per time step**, not continuously, which understates the knock-out probability. The standard fix (the Broadie-Glasserman-Kou barrier shift) isn't applied, and the faster production route would be the closed form (Reiner-Rubinstein) with that shift. Monte Carlo was chosen here to learn path simulation.
- **The hedging simulator uses GBM paths at a constant realised vol**, so it shows the vol identity cleanly but not jumps or vol-of-vol, which is where real hedging losses come from.
- **Vol smile interpolation is linear** between listed strikes and flat outside them. A production surface would use an arbitrage-free fit such as SVI.
- **The composite mid has no staleness or outlier filtering.** It's a single live pull showing the weighting, not a production index.
