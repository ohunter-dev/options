import numpy as np

def compute_markouts(trade_price, side, mid_series, horizons):
    # trade_price: the price you actually traded at
    # side: 'buy' or 'sell' — direction matters for how we score the outcome
    # mid_series: array of market mid-prices, indexed by time AFTER the trade
    #             mid_series[0] should be the mid right at/near trade time
    # horizons: list of indices into mid_series to check (e.g. [0, 1, 10, 60])

    markouts = {}
    for h in horizons:
        mid_at_h = mid_series[h]
        if side == 'buy':
            # if you bought, you WANT the price to rise afterward — that's a good mark-out
            markout = mid_at_h - trade_price
        else:
            # if you sold, you WANT the price to fall afterward
            markout = trade_price - mid_at_h
        markouts[h] = markout

    return markouts

if __name__ == "__main__":
    # SCENARIO 1: pure temporary impact — you buy, push the price up briefly,
    # then it reverts back down as your pressure disappears
    mid_series_impact = np.array([78010, 78008, 78003, 77998, 77996, 77995])
    trade_price = 78010   # you bought right as your own order pushed the mid up

    print("=== Scenario 1: temporary impact (should revert) ===")
    result = compute_markouts(trade_price, side='buy',
                                mid_series=mid_series_impact,
                                horizons=[0, 1, 2, 3, 4, 5])
    for h, m in result.items():
        print(f"  +{h} steps: markout = {m:>8.2f}")


        # SCENARIO 2: information — you bought right before the market kept moving
    # against you, with no reversion. Someone/something knew more than you did.
    mid_series_info = np.array([78010, 78015, 78022, 78028, 78035, 78040])
    trade_price = 78010

    print("\n=== Scenario 2: information (should NOT revert) ===")
    result2 = compute_markouts(trade_price, side='buy',
                                 mid_series=mid_series_info,
                                 horizons=[0, 1, 2, 3, 4, 5])
    for h, m in result2.items():
        print(f"  +{h} steps: markout = {m:>8.2f}")