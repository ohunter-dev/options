# Options / Vol Desk - self-study project

A from-scratch build of the pricing, hedging, and risk-management toolkit used on
a crypto options desk: Black-Scholes engine, live implied-vol surface construction,
product decomposition (dual-currency notes, risk reversals, sharkfins), a Monte
Carlo barrier pricer, a delta-hedging simulator, and book-level risk aggregation.
Built to understand market microstructure and options mechanics from first
principles, using live BTC/ETH data from Deribit's public API.

## Structure

- `src/bs.py` - Black-Scholes pricer and all six greeks (delta, gamma, vega,
  theta, vanna, volga), each validated against numerical finite-difference bumps.
- `src/data.py` - Deribit public API client (instruments, tickers, trade tape).
- `src/iv.py` - implied vol solver (Brent's method root-finding).
- `src/surface.py` - live vol smile construction from OTM options, with
  strike-interpolation for pricing at non-listed strikes.
- `src/term_structure.py` - ATM implied vol across all listed expiries.
- `src/products.py` - decomposition and live pricing of dual-currency notes
  and risk reversals (reads real market skew via the surface module).
- `src/mc.py` - GBM path simulation and Monte Carlo pricing of the sharkfin
  (up-and-out barrier option) - no closed form under discrete monitoring, so MC.
- `src/hedging.py` - delta-hedging P&L simulator: sells an option, dynamically
  hedges it along a simulated price path, and decomposes the result into the
  sold-vs-realized-vol identity, hedge-frequency effects, and transaction costs.
- `src/book.py` - multi-position book aggregation, scenario grids (spot × vol),
  and full greek stack including vanna/volga.
- `src/tca.py` / `src/tca_live.py` - mark-out analysis (impact vs information)
  on synthetic and real Deribit trade-tape data.
- `src/composite_mid.py` - volume-weighted composite mid price across Binance,
  Coinbase, and OKX.

## Running

Each module can be run directly to see its own worked example, e.g.:

```
python -m src.bs
python -m src.surface
python -m src.hedging
python -m src.book
python -m src.tca_live
```

Set up the environment first:
```
uv venv
uv pip install -r requirements.txt
```

## Known simplifications

Stuff I've simplified on purpose, written down so it doesn't look like a bug:

- **r = 0 throughout.** Matches Deribit's own convention (`interest_rate: 0.0`
  in every ticker response) - not an approximation for this venue, but worth
  flagging since it wouldn't hold on a rates-bearing instrument.
- **Options are priced off the forward, not spot**, using each instrument's
  own `underlying_price` from its ticker. Pricing off spot directly produces a
  visible kink at the ATM put/call boundary (documented via the debugging
  process in commit history) - using the correct per-expiry forward removes it.
- **No inverse/BTC-settlement adjustment.** Deribit's BTC options settle and
  are margined in BTC, not USD. This project treats them as standard USD-
  denominated vanillas after converting the BTC-denominated mark price to USD
  at the prevailing forward. Doing it properly means changing the numeraire
  itself, so I know this is an approximation.
- **Barrier monitoring in the Monte Carlo sharkfin pricer is discrete**
  (checked once per simulated time step), not continuous. This understates
  the true knock-out probability relative to continuous monitoring. The
  standard correction (Broadie-Glasserman-Kou barrier shift) is not applied.
- **The composite mid has no staleness filtering or outlier rejection** - it
  is a single live pull, volume-weighted across three venues, intended as a
  proof of the weighting mechanism rather than a production-grade index.
- **Vol surface interpolation is linear** (`np.interp`) between listed
  strikes, and flat-extrapolates outside the observed strike range. A
  production surface would use an arbitrage-free parametric fit (e.g. SVI).

## What this demonstrates

The main thing this project is about: vanilla risk (delta, gamma,
vega, theta, and their second-order extensions vanna/volga) is hedgeable with
the underlying and other vanillas. Path-dependent risk (a barrier) is much
harder to hedge with vanillas, and with the barrier checked at discrete points
there's no closed form, so the sharkfin gets priced with Monte Carlo instead, rather than a straight extension of Black-Scholes
I went with MC mainly to learn path simulation. The faster production route
would be the continuous-monitoring closed form (Reiner-Rubinstein) with the
Broadie-Glasserman-Kou barrier shift to adjust for discrete monitoring.