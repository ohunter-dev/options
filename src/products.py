from src.bs import bs_price, delta, gamma, vega, theta
from src.surface import get_smile, interpolate_iv

def dual_currency_note(notional, S, K, T, r, sigma): #dual currency note
    call_price = bs_price(S, K, T, r, sigma, option='call')
    yield_pickup = call_price / S
    annualised_yield = yield_pickup / T

    btc_equiv = notional / S   # how many BTC this cash notional represents

    client_delta = -delta(S, K, T, r, sigma, option='call') * btc_equiv
    client_gamma = -gamma(S, K, T, r, sigma) * btc_equiv
    client_vega  = -vega(S, K, T, r, sigma) * btc_equiv
    client_theta = -theta(S, K, T, r, sigma, option='call') * btc_equiv

    return {
        'call_price': call_price,
        'yield_pickup_pct': yield_pickup * 100,
        'annualised_yield_pct': annualised_yield * 100,
        'client_delta': client_delta, 'client_gamma': client_gamma,
        'client_vega': client_vega, 'client_theta': client_theta,
        'desk_delta': -client_delta, 'desk_gamma': -client_gamma,
        'desk_vega': -client_vega, 'desk_theta': -client_theta,
    }

#risk reversal: client buys put, sells call so they're short delta. desk is the other side (short put, long call) so long delta
def risk_reversal(notional, S, K_put, K_call, T, r, sigma_put, sigma_call): 
    btc_equiv = notional / S

    # client: long put at K_put, short call at K_call
    put_price  = bs_price(S, K_put, T, r, sigma_put, option='put')
    call_price = bs_price(S, K_call, T, r, sigma_call, option='call')
    net_cost   = put_price - call_price   # +ve = client pays a debit, -ve = they collect a credit

    client_delta = (delta(S, K_put, T, r, sigma_put, option='put')
                   - delta(S, K_call, T, r, sigma_call, option='call')) * btc_equiv

    client_gamma = (gamma(S, K_put, T, r, sigma_put)
                   - gamma(S, K_call, T, r, sigma_call)) * btc_equiv

    client_vega = (vega(S, K_put, T, r, sigma_put)
                  - vega(S, K_call, T, r, sigma_call)) * btc_equiv

    client_theta = (theta(S, K_put, T, r, sigma_put, option='put')
                   - theta(S, K_call, T, r, sigma_call, option='call')) * btc_equiv

    skew = sigma_put - sigma_call   # skew is the actual thing I'm exposed to here

    return {
        'put_price': put_price, 'call_price': call_price, 'net_cost': net_cost,
        'client_delta': client_delta, 'client_gamma': client_gamma,
        'client_vega': client_vega, 'client_theta': client_theta,
        'desk_delta': -client_delta, 'desk_gamma': -client_gamma,
        'desk_vega': -client_vega, 'desk_theta': -client_theta,
        'skew_pct': skew * 100,
    }

def risk_reversal_live(notional, K_put, K_call, target_days=30):
    spot, days, smile = get_smile(target_days=target_days)
    T = days / 365

    sigma_put  = interpolate_iv(smile, K_put)
    sigma_call = interpolate_iv(smile, K_call)

    result = risk_reversal(notional, spot, K_put, K_call, T, r=0.0,
                            sigma_put=sigma_put, sigma_call=sigma_call)
    result['spot'] = spot
    result['days'] = days
    result['sigma_put'] = sigma_put
    result['sigma_call'] = sigma_call
    return result

if __name__ == "__main__":
    print("=== Risk reversal, live market ===")
    live = risk_reversal_live(notional=100000, K_put=70000, K_call=88000, target_days=30)
    for key, val in live.items():
        if isinstance(val, float):
            print(f"{key:>22}: {val:.6f}")
        else:
            print(f"{key:>22}: {val}")

        