import requests
import json
import os
import time
import argparse
import sys

BASE_URL = 'https://api.kroger.com'

class KrogerClient:
    def __init__(self, state_file='state.json'):
        self.state_file = state_file
        self.state = self._load_state()
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/vnd.api+json'})

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_token(self):
        now = time.time()
        if self.state.get('access_token') and self.state.get('expires_at', 0) > now + 60:
            return self.state['access_token']
        if not self.state.get('refresh_token') and not self.state.get('access_token'):
            raise ValueError('No token available. Set up OAuth first.')
        if self.state.get('refresh_token'):
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.state['refresh_token'],
                'client_id': self.state['client_id'],
                'client_secret': self.state['client_secret']
            }
        else:
            # Use access_token if no refresh, but won't refresh
            return self.state['access_token']
        r = self.session.post(f'{BASE_URL}/v1/connect/oauth2/token', data=data)
        r.raise_for_status()
        tok = r.json()
        now = time.time()
        self.state['access_token'] = tok['access_token']
        if 'refresh_token' in tok:
            self.state['refresh_token'] = tok['refresh_token']
        self.state['expires_at'] = now + tok['expires_in']
        self._save_state()
        return self.state['access_token']

    def _update_auth(self):
        token = self.get_token()
        self.session.headers['Authorization'] = f'Bearer {token}'

    def search_products(self, term, location_id=None, chain_id=None, limit=10):
        self._update_auth()
        params = {'filter.term': term, 'pageSize': limit}
        if location_id:
            params['filter.locationId'] = location_id
        if chain_id:
            params['filter.chain'] = chain_id
        r = self.session.get(f'{BASE_URL}/v1/products', params=params)
        r.raise_for_status()
        return r.json()['data']

    def get_locations(self, zipcode, chain_id=None, radius=25):
        self._update_auth()
        params = {
            'filter.zipCode.near': zipcode,
            'filter.radiusInMiles': radius,
            'filter.limit': 10
        }
        if chain_id:
            params['filter.chain'] = chain_id
        r = self.session.get(f'{BASE_URL}/v1/locations', params=params)
        r.raise_for_status()
        return r.json()['data']

    def check_pickup_availability(self, location_id, items):
        self._update_auth()
        payload = {
            'pickup': {
                'locationId': location_id,
                'items': items
            }
        }
        r = self.session.post(f'{BASE_URL}/v1/fulfillment/messages/pickup-availability', json=payload)
        r.raise_for_status()
        return r.json()

    def create_pickup_order(self, location_id, pickup_datetime, items):
        self._update_auth()
        payload = {
            'fulfillment': {
                'pickup': {
                    'locationId': location_id,
                    'desiredPickupDateTime': pickup_datetime,
                    'items': items
                }
            }
        }
        r = self.session.post(f'{BASE_URL}/orders/pickup', json=payload)
        r.raise_for_status()
        return r.json()

    def get_cart(self):
        return self.state.get('cart', [])

    def add_to_cart(self, upc, quantity):
        cart = self.get_cart()
        for item in cart:
            if item['upc'] == upc:
                item['quantity'] += quantity
                self._save_state()
                return
        cart.append({'upc': upc, 'quantity': quantity})
        self.state['cart'] = cart
        self._save_state()

    def clear_cart(self):
        self.state['cart'] = []
        self._save_state()

    def set_location(self, location_id):
        self.state['location_id'] = location_id
        self._save_state()

    def exchange_code(self, code, redirect_uri):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.state['client_id'],
            'client_secret': self.state['client_secret']
        }
        r = self.session.post(f'{BASE_URL}/v1/connect/oauth2/token', data=data)
        r.raise_for_status()
        tok = r.json()
        now = time.time()
        self.state['access_token'] = tok['access_token']
        self.state['refresh_token'] = tok['refresh_token']
        self.state['expires_at'] = now + tok['expires_in']
        self._save_state()
        print('Tokens saved!')

    def get_auth_url(self, redirect_uri='http://localhost:8080'):
        scopes = 'product.compact locations.read fulfillment.readwrite orders.pickup.create'
        return f"{BASE_URL}/v1/connect/oauth2/authorize?response_type=code&client_id={self.state['client_id']}&redirect_uri={redirect_uri}&scope={scopes}"

def main():
    parser = argparse.ArgumentParser(description='Kroger API Client')
    parser.add_argument('--state', default='state.json', help='State file')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # search
    p = subparsers.add_parser('search', help='Search products')
    p.add_argument('term')
    p.add_argument('--location-id', help='Location ID')
    p.add_argument('--chain-id', default='213', help='Chain ID (213=QFC)')
    p.add_argument('--limit', type=int, default=10)

    # locations
    p = subparsers.add_parser('locations', help='Get locations near zip')
    p.add_argument('zipcode')
    p.add_argument('--chain-id', default='213')
    p.add_argument('--radius', type=int, default=25)

    # cart
    p = subparsers.add_parser('cart-add', help='Add to cart')
    p.add_argument('upc')
    p.add_argument('quantity', type=int)
    p = subparsers.add_parser('cart-get', help='Get cart')
    p = subparsers.add_parser('cart-clear', help='Clear cart')

    # availability
    p = subparsers.add_parser('availability', help='Check pickup availability')
    p.add_argument('location_id')
    p.add_argument('--items', required=True, help='JSON items list e.g. "[{\\"upc\\":\\"123\\",\\"quantity\\":1}]"')

    # order
    p = subparsers.add_parser('order-create', help='Create pickup order')
    p.add_argument('location_id')
    p.add_argument('pickup_datetime', help='ISO datetime')
    p.add_argument('--items', required=True, help='JSON items')

    # oauth
    p = subparsers.add_parser('oauth-url', help='Get auth URL')
    p.add_argument('--redirect-uri', default='http://localhost')
    p = subparsers.add_parser('oauth-exchange', help='Exchange code')
    p.add_argument('code')
    p.add_argument('--redirect-uri', default='http://localhost')

    # location set
    p = subparsers.add_parser('location-set', help='Set default location')
    p.add_argument('location_id')

    # grocery
    p = subparsers.add_parser('grocery', help='Process grocery-list.txt')
    p.add_argument('--zip', required=True)
    p.add_argument('--chain-id', default='213')

    args = parser.parse_args()

    client = KrogerClient(args.state)

    if args.command == 'search':
        results = client.search_products(args.term, args.location_id, args.chain_id, args.limit)
        print(json.dumps(results, indent=2))
    elif args.command == 'locations':
        results = client.get_locations(args.zipcode, args.chain_id, args.radius)
        print(json.dumps(results, indent=2))
    elif args.command == 'cart-add':
        client.add_to_cart(args.upc, args.quantity)
        print(json.dumps(client.get_cart(), indent=2))
    elif args.command == 'cart-get':
        print(json.dumps(client.get_cart(), indent=2))
    elif args.command == 'cart-clear':
        client.clear_cart()
        print('Cart cleared')
    elif args.command == 'availability':
        items = json.loads(args.items)
        results = client.check_pickup_availability(args.location_id, items)
        print(json.dumps(results, indent=2))
    elif args.command == 'order-create':
        items = json.loads(args.items)
        results = client.create_pickup_order(args.location_id, args.pickup_datetime, items)
        print(json.dumps(results, indent=2))
    elif args.command == 'oauth-url':
        url = client.get_auth_url(args.redirect_uri)
        print(url)
    elif args.command == 'oauth-exchange':
        client.exchange_code(args.code, args.redirect_uri)
    elif args.command == 'location-set':
        client.set_location(args.location_id)
        print(f'Location set to {args.location_id}')
    elif args.command == 'grocery':
        # Integrate grocery-list: simple demo
        try:
            with open('grocery-list.txt', 'r') as f:
                items_text = f.read().strip().split('\n')
        except FileNotFoundError:
            print('No grocery-list.txt found')
            sys.exit(1)
        print('Found grocery items:')
        for item in items_text:
            print(f'- {item}')
        # Agent would search each, add to cart, etc. This is placeholder.
        locs = client.get_locations(args.zip, args.chain_id)
        print('Nearby locations:')
        print(json.dumps(locs, indent=2))
        # Full integration: agent parses, searches, prompts
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
