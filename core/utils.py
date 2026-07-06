import requests
from django.core.cache import cache

def get_exchange_rate(base_currency='USD', target_currency='EUR'):
    """
    Fetch exchange rate from a public API, with caching to avoid rate limits.
    """
    if base_currency == target_currency:
        return 1.0

    cache_key = f'exchange_rate_{base_currency}_{target_currency}'
    rate = cache.get(cache_key)
    
    if rate is not None:
        return rate
        
    try:
        # Using exchangerate-api which has a free tier that requires no API key
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        rate = data['rates'].get(target_currency)
        if rate:
            # Cache for 12 hours
            cache.set(cache_key, rate, 60 * 60 * 12)
            return rate
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        
    return 1.0

def convert_currency(amount, base_currency, target_currency):
    """
    Convert an amount from one currency to another.
    """
    rate = get_exchange_rate(base_currency, target_currency)
    return float(amount) * float(rate)
