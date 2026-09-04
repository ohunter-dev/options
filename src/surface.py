import time
import numpy as np
from src.data import get_instruments, get_ticker
from src.iv import implied_vol

def get_smile(target_days=30, currency='BTC'):
    instruments = get_instruments(currency)
    now_ms = time.time() * 1000


    # any ticker gives us current spot
    sample = get_ticker(instruments[0]['instrument_name'])
    spot = sample['underlying_price']

    for inst in instruments:
        inst['days_to_expiry'] = (inst['expiration_timestamp'] - now_ms) / (1000*60*60*24)

    # snap to whichever listed expiry is nearest our target
    chosen = min(set(round(i['days_to_expiry']) for i in instruments),
                 key=lambda d: abs(d - target_days))
    T = chosen / 365

        # everything in this expiry, calls and puts both
    bucket = [i for i in instruments if round(i['days_to_expiry']) == chosen]

    # keep only the out-of-the-money side at each strike:
    # puts below spot, calls above. these are the liquid, vega-rich ones.
    otm = []
    for i in bucket:
        K = i['strike']
        if K < spot and i['option_type'] == 'put':
            otm.append(i)
        elif K >= spot and i['option_type'] == 'call':
            otm.append(i)
    otm.sort(key=lambda i: i['strike'])

    results = []
    for inst in otm:
        ticker = get_ticker(inst['instrument_name'])
        mark_btc = ticker['mark_price']
        if mark_btc is None or mark_btc <= 0:      # no usable price
            continue
        F = ticker['underlying_price']             # forward for THIS expiry, not spot
        price_usd = mark_btc * F
        K = inst['strike']
        opt = inst['option_type']                  # put below spot, call above
        try:
            iv = implied_vol(price_usd, S=F, K=K, T=T, r=0.0, option=opt)
        except ValueError:                         # solver couldn't bracket a root
            continue
        results.append({
            'strike': K,
            'iv': iv,
            'type': opt,
            'volume': ticker['stats']['volume'],
            'mark_iv': ticker['mark_iv'],
        })

    return spot, chosen, results

def interpolate_iv(smile_results, strike): #to interpolate, as clients was 25 delta calls rather than asking for quotes at strike at 77k.
    # smile_results is the list of dicts from get_smile()
    strikes = np.array([row['strike'] for row in smile_results])
    ivs     = np.array([row['iv'] for row in smile_results])
    # linear interpolation between the two nearest listed strikes;
    # np.interp clamps to the edge value if strike is outside the range
    return float(np.interp(strike, strikes, ivs))


if __name__ == "__main__":
    spot, days, smile = get_smile(target_days=30)
    print(f"Spot: {spot}, Expiry: {days} days, {len(smile)} strikes")
    for row in smile:
        print(f"K={row['strike']:>8.0f}  {row['type']:>4}  my_iv={row['iv']*100:>6.2f}%  "
              f"deribit={row['mark_iv']:>6.2f}%  vol={row['volume']:>7.1f}")