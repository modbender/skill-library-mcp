# auth_setup.py
import os
from web3 import Web3
import requests

def authenticate_with_clob(private_key):
    # Set up Web3 provider for Polygon
    w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/polygon'))
    account = w3.eth.account.from_key(private_key)
    
    # EIP-712 signature setup (simplified; adapt from docs)
    message = {
        "domain": {},  # Define as per Polymarket docs
        "message": {},
        "primaryType": "SomeType"
    }
    signed_message = w3.eth.account.signTypedData(message, private_key=private_key)
    
    # Derive API key using CLOB endpoint
    url = "https://clob.polymarket.com/api-keys"
    response = requests.post(url, json={"signed_message": signed_message})
    if response.status_code == 200:
        api_data = response.json()
        return api_data  # Returns API key, secret, passphrase
    else:
        raise Exception("Authentication failed")

# Example usage
if __name__ == "__main__":
    private_key = os.getenv('POLY_PRIVATE_KEY')  # Load from env for security
    if private_key:
        try:
            creds = authenticate_with_clob(private_key)
            print("API creds derived:", creds)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Set POLY_PRIVATE_KEY environment variable.")
