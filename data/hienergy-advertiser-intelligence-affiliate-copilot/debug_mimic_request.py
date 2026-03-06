import os
import requests
import sys

api_key = os.environ.get('HIENERGY_API_KEY')
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json',
    'User-Agent': 'openclaw-hi-energy-affiliate-copilot/1.0'
}
url = "https://app.hienergy.ai/api/v1/advertisers"
params = {'limit': 1, 'name': 'weightloss'}

print(f"Requesting {url} with params {params}...")
try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Data length: {len(response.text)}")
except Exception as e:
    print(f"Error: {e}")
