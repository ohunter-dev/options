import time
from src.data import get_instruments, get_ticker
from src.iv import implied_vol

instruments = get_instruments()
now_ms = time.time() * 1000

# Reuse the same ATM-ish instrument selection
sample = get_ticker(instruments[0]['instrument_name'])
spot = sample['underlying_price']

for inst in instruments:
    inst['days_to_expiry'] = (inst['expiration_timestamp'] - now_ms) / (1000*60*60*24)

target_days = 30
chosen = min(set(round(i['days_to_expiry']) for i in instruments),
             key=lambda d: abs(d - target_days))
bucket = [i for i in instruments
          if round(i['days_to_expiry']) == chosen and i['option_type'] == 'call']
inst = min(bucket, key=lambda i: abs(i['strike'] - spot))

ticker = get_ticker(inst['instrument_name'])

# deribit prices options in BTC so convert mark_price to USD and treat it as non inverse. approximation
mark_price_btc = ticker['mark_price']
spot_now = ticker['underlying_price']
market_price_usd = mark_price_btc * spot_now

K = inst['strike']
T = chosen / 365           # days to years
r = 0.0                    # matches Deribit's interest_rate set to zero

my_iv = implied_vol(market_price_usd, S=spot_now, K=K, T=T, r=r, option='call')

print("instrument:      ", inst['instrument_name'])
print("my implied vol:  ", round(my_iv * 100, 2), "%")
print("Deribit mark_iv: ", ticker['mark_iv'], "%")