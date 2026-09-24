import numpy as np
from src.data import get_last_trades
from src.tca import compute_markouts

# using the BTC perp, most liquid thing on deribit so best chance of clean frequent trades
trades = get_last_trades("BTC-PERPETUAL", count=200)

# deribit gives newest first, flip it so it's in time order
trades = list(reversed(trades))

print(f"Pulled {len(trades)} trades")
print("First trade:", trades[0])
print("Last trade:", trades[-1])

def markout_from_tape(trades, reference_idx, horizons_seconds):
    ref_trade = trades[reference_idx]
    ref_time = ref_trade['timestamp']
    ref_price = ref_trade['price']
    side = ref_trade['direction']

    results = {}
    for h in horizons_seconds:
        target_time = ref_time + h * 1000   # convert seconds to ms, Deribit's unit

        # first trade at or after target_time, best guess at where the market was then
        future_trades = [t for t in trades if t['timestamp'] >= target_time]
        if not future_trades:
            results[h] = None   # ran off the end of the data I pulled
            continue

        price_at_h = future_trades[0]['price']

        if side == 'buy':
            markout = price_at_h - ref_price
        else:
            markout = ref_price - price_at_h
        results[h] = markout

    return results

if __name__ == "__main__":
    horizons_seconds = [1, 5, 15, 30, 60]
    all_results = {h: [] for h in horizons_seconds}

    # only use trades 20 to len-20 so each one has enough tape after it for the +60s markout
    for i in range(20, len(trades) - 20):
        result = markout_from_tape(trades, i, horizons_seconds)
        for h in horizons_seconds:
            if result[h] is not None:
                all_results[h].append(result[h])

    print(f"Averaged over trades (sample sizes vary by horizon):\n")
    for h in horizons_seconds:
        values = all_results[h]
        print(f"  +{h:>3}s: avg markout = {np.mean(values):>7.2f}   "
              f"n = {len(values):>4}   std = {np.std(values):>7.2f}")