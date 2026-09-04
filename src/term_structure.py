import time
from src.data import get_instruments, get_ticker
from src.iv import implied_vol

def get_term_structure(currency='BTC'):
    instruments = get_instruments(currency)
    now_ms = time.time() * 1000

    sample = get_ticker(instruments[0]['instrument_name'])
    spot = sample['underlying_price']

    for inst in instruments:
        inst['days_to_expiry'] = (inst['expiration_timestamp'] - now_ms) / (1000*60*60*24)

    # distinct expiries, skip anything under 2 days (0DTE greeks are junk)
    expiries = sorted(set(round(i['days_to_expiry']) for i in instruments))
    expiries = [d for d in expiries if d >= 2]

    results = []
    for days in expiries:
        # nearest-to-ATM instrument in this expiry
        bucket = [i for i in instruments if round(i['days_to_expiry']) == days]
        if not bucket:
            continue
        atm = min(bucket, key=lambda i: abs(i['strike'] - spot))

        ticker = get_ticker(atm['instrument_name'])
        mark_btc = ticker['mark_price']
        if mark_btc is None or mark_btc <= 0:
            continue

        F = ticker['underlying_price']          # forward for this expiry
        price_usd = mark_btc * F
        K = atm['strike']
        T = days / 365
        opt = atm['option_type']
        try:
            iv = implied_vol(price_usd, S=F, K=K, T=T, r=0.0, option=opt)
        except ValueError:
            continue

        results.append({'days': days, 'atm_iv': iv, 'mark_iv': ticker['mark_iv']})

    return spot, results

if __name__ == "__main__":
    spot, term = get_term_structure()
    print(f"Spot: {spot}")
    print(f"{'days':>6} {'my_atm_iv':>10} {'deribit':>9}")
    for row in term:
        print(f"{row['days']:>6} {row['atm_iv']*100:>9.2f}% {row['mark_iv']:>8.2f}%")