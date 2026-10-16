import requests
import numpy as np

def get_binance():
    r = requests.get("https://api.binance.com/api/v3/ticker/24hr", params={"symbol": "BTCUSDT"})
    data = r.json()
    return {'venue': 'binance', 'price': float(data['lastPrice']), 'volume': float(data['quoteVolume'])}

def get_coinbase():
    r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker")
    data = r.json()
    return {'venue': 'coinbase', 'price': float(data['price']), 'volume': float(data['volume']) * float(data['price'])}

def get_okx():
    r = requests.get("https://www.okx.com/api/v5/market/ticker", params={"instId": "BTC-USDT"})
    data = r.json()['data'][0]
    return {'venue': 'okx', 'price': float(data['last']), 'volume': float(data['volCcy24h'])}


def composite_mid(venue_data):
    prices = np.array([v['price'] for v in venue_data])
    volumes = np.array([v['volume'] for v in venue_data])
    weights = volumes / volumes.sum()
    return np.sum(weights * prices), weights

if __name__ == "__main__":
    venue_data = [get_binance(), get_coinbase(), get_okx()]

    for v in venue_data:
        print(f"{v['venue']:>10}:  price = {v['price']:>10,.2f}   volume = ${v['volume']:>18,.2f}")

    mid, weights = composite_mid(venue_data)
    print(f"\nComposite mid: {mid:,.2f}")
    for v, w in zip(venue_data, weights):
        print(f"  {v['venue']:>10} weight: {w*100:.1f}%")