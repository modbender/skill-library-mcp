import os
import sys
import requests

# Set the API key
api_key = os.environ.get('HIENERGY_API_KEY')
if not api_key:
    print("Error: HIENERGY_API_KEY not found in environment")
    sys.exit(1)

print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")

try:
    url = "https://app.hienergy.ai/api/v1/advertisers"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    print(f"Requesting {url}...")
    response = requests.get(url, headers=headers, params={'limit': 1}, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("Success! API is accessible.")
    else:
        print("Failed to access API.")

except Exception as e:
    print(f"Error executing skill: {e}")
    import traceback
    traceback.print_exc()
