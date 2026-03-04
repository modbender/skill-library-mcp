"""
Apiosk Python Client
Easy API calls with automatic x402 payment
"""

import os
import json
import requests
from pathlib import Path

WALLET_FILE = Path.home() / '.apiosk' / 'wallet.json'
CONFIG_FILE = Path.home() / '.apiosk' / 'config.json'


def load_wallet():
    """Load wallet configuration"""
    if not WALLET_FILE.exists():
        raise FileNotFoundError('Wallet not found. Run ./setup-wallet.sh first')
    
    with open(WALLET_FILE) as f:
        wallet = json.load(f)
    
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    
    return wallet, config


def call_apiosk(api_id: str, params: dict = None) -> dict:
    """
    Call an Apiosk API
    
    Args:
        api_id: API identifier (e.g., 'weather', 'prices')
        params: API parameters
    
    Returns:
        API response as dictionary
    
    Raises:
        requests.HTTPError: If API call fails
        ValueError: If payment fails
    """
    wallet, config = load_wallet()
    params = params or {}
    
    url = f"{config['gateway_url']}/{api_id}"
    headers = {
        'Content-Type': 'application/json',
        'X-Wallet-Address': wallet['address'],
    }
    
    response = requests.post(url, json=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 402:
        error = response.json().get('error', 'Insufficient balance')
        raise ValueError(f'Payment required: {error}')
    else:
        response.raise_for_status()


def list_apis() -> list:
    """
    List available APIs
    
    Returns:
        List of API dictionaries
    """
    _, config = load_wallet()
    
    url = f"{config['gateway_url']}/v1/apis"
    response = requests.get(url)
    response.raise_for_status()
    
    return response.json()['apis']


def check_balance() -> dict:
    """
    Check wallet balance
    
    Returns:
        Balance information dictionary
    """
    wallet, config = load_wallet()
    
    url = f"{config['gateway_url']}/v1/balance"
    params = {'address': wallet['address']}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()


def usage_stats(period: str = 'all') -> dict:
    """
    Get usage statistics
    
    Args:
        period: 'all', 'today', 'week', or 'month'
    
    Returns:
        Usage statistics dictionary
    """
    wallet, config = load_wallet()
    
    url = f"{config['gateway_url']}/v1/usage"
    params = {
        'address': wallet['address'],
        'period': period,
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()


# Example usage
if __name__ == '__main__':
    print('🦞 Apiosk Client Example\n')
    
    try:
        # List APIs
        print('Available APIs:')
        apis = list_apis()
        for api in apis:
            print(f"- {api['id']}: ${api['price_usd']}/req - {api['description']}")
        
        print('\n')
        
        # Call weather API
        print('Calling weather API for Amsterdam...')
        weather = call_apiosk('weather', {'city': 'Amsterdam'})
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Condition: {weather['condition']}")
        print('✅ Paid: $0.001 USDC\n')
        
        # Check balance
        balance = check_balance()
        print(f"Remaining balance: ${balance['balance_usdc']} USDC")
        
    except Exception as e:
        print(f'❌ Error: {e}')
        exit(1)
