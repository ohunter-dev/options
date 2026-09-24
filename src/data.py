import requests
import time

#obtaining deribit's live data of options

def get_instruments(currency='BTC'):
    url = "https://www.deribit.com/api/v2/public/get_instruments"
    params = {"currency": currency, "kind": "option", "expired": "false"}
    response = requests.get(url, params=params)
    data = response.json()
    return data['result']


#obtaining a ticker now on deribit directly to see mark_iv field: 
def get_ticker(instrument_name):
    url = "https://www.deribit.com/api/v2/public/ticker"
    params = {"instrument_name": instrument_name}
    response = requests.get(url, params=params)
    data = response.json()
    return data['result']

def get_last_trades(instrument_name, count=200):
    url = "https://www.deribit.com/api/v2/public/get_last_trades_by_instrument"
    params = {"instrument_name": instrument_name, "count": count}
    response = requests.get(url, params=params)
    data = response.json()
    return data['result']['trades']

#pull btc options nearest the money with some time left, first step for building the vol surface
if __name__ == "__main__":
    instruments = get_instruments()
    print("Number of live BTC options:", len(instruments))

    sample_ticker = get_ticker(instruments[0]['instrument_name'])
    spot = sample_ticker['underlying_price']
    print("Current BTC spot:", spot)

    now_ms = time.time() * 1000   # current time in milliseconds, to match Deribit

    # Compute days-to-expiry for each instrument and attach it
    for inst in instruments:
        inst['days_to_expiry'] = (inst['expiration_timestamp'] - now_ms) / (1000 * 60 * 60 * 24)

    # List the distinct expiries available, sorted
    expiries = sorted(set(round(inst['days_to_expiry']) for inst in instruments))
    print("Available expiries (days out):", expiries)

    # Pick the expiry closest to 30 days
    target_days = 30
    chosen_expiry = min(expiries, key=lambda d: abs(d - target_days))
    print("Chosen expiry (days out):", chosen_expiry)

    # Keep only calls in that expiry bucket
    bucket = [inst for inst in instruments
              if round(inst['days_to_expiry']) == chosen_expiry
              and inst['option_type'] == 'call']

    # Within that expiry, find the strike closest to spot
    closest = min(bucket, key=lambda inst: abs(inst['strike'] - spot))
    print("Closest-to-ATM in that expiry:", closest['instrument_name'], "strike:", closest['strike'])

    ticker = get_ticker(closest['instrument_name'])
    print("delta:", ticker['greeks']['delta'], "| mark_iv:", ticker['mark_iv'],
          "| volume:", ticker['stats']['volume'])