import os
import json
import time
import requests
from datetime import datetime

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
EXAMPLE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.example.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        import shutil
        print(f"Config not found. Creating from example: {CONFIG_PATH}")
        shutil.copy(EXAMPLE_CONFIG_PATH, CONFIG_PATH)
        
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_cache_path(date_str):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{date_str}.json")

def fetch_data(endpoint, params):
    # Construct a cache key based on params to avoid collisions if params change
    today = datetime.now().strftime("%Y-%m-%d")
    cache_file = get_cache_path(f"{endpoint.replace('/', '_')}_{today}")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)

    # Use Aladhan API
    url = f"https://api.aladhan.com{endpoint}"
    
    # Handle Zakat specially via IslamicAPI.com
    if 'zakat' in endpoint:
        config = load_config()
        api_key = os.environ.get('ZAKAT_API_KEY') or config.get('zakat', {}).get('api_key')
        
        if not api_key:
            return {"error": "Missing API Key. Please get one from https://islamicapi.com/"}
            
        # IslamicAPI URL
        url = "https://islamicapi.com/api/v1/zakat-nisab/"
        # Merge params
        params['api_key'] = api_key
        
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_prayer_times():
    config = load_config()
    params = {
        'latitude': config['location']['latitude'],
        'longitude': config['location']['longitude'],
        'method': config['calculation']['method'],
        'school': config['calculation']['school']
    }
    # Aladhan API uses DD-MM-YYYY in path
    today = datetime.now().strftime("%d-%m-%Y")
    return fetch_data(f'/v1/timings/{today}', params)

def get_fasting_times():
    # Same as prayer times for Aladhan
    return get_prayer_times()

def get_calendar_by_city(city, country, month=None, year=None):
    config = load_config()
    
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
        
    params = {
        'city': city,
        'country': country,
        'method': config['calculation']['method'],
        'school': config['calculation']['school'],
        'month': month,
        'year': year
    }
    
    return fetch_data(f'/v1/calendarByCity', params)

def get_random_quote():
    # Based on the JS found on the site, there are at least 84 quotes
    import random
    quote_id = random.randint(1, 84)
    url = f"https://ilm.islamic.network/items/quotes/{quote_id}?fields=text,reference,translations.*,author.name"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None

def get_zakat_gold_silver(currency=None):
    config = load_config()
    curr = currency or config['zakat']['currency']
    
    # IslamicAPI specific params
    params = {
        'currency': curr,
        'standard': 'common', # hardcoded default for now
        'unit': 'g'
    }
    return fetch_data('zakat', params)
