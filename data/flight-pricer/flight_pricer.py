import os
import click
import yaml
import requests
import json
from datetime import datetime
from tabulate import tabulate

CONFIG_DIR = os.path.expanduser("~/.config/flight-pricer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
API_BASE_URL = "https://api.duffel.com/air/offer_requests"

def get_api_key():
    """Loads the API key from the config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('api_key')
    except (FileNotFoundError, yaml.YAMLError):
        return None

def format_datetime(dt_string):
    """Formats ISO datetime string to a readable format."""
    if not dt_string:
        return "N/A"
    dt_obj = datetime.fromisoformat(dt_string)
    return dt_obj.strftime('%Y-%m-%d %I:%M %p')

def format_duration(duration_string):
    """Formats ISO 8601 duration string like 'PT2H38M' to '2h 38m'."""
    if not duration_string or not duration_string.startswith('PT'):
        return "N/A"
    duration_string = duration_string[2:]
    h_part = "0h"
    m_part = "0m"
    if 'H' in duration_string:
        parts = duration_string.split('H')
        h_part = f"{parts[0]}h"
        duration_string = parts[1]
    if 'M' in duration_string:
        m_part = f"{duration_string.replace('M', '')}m"
    return f"{h_part} {m_part}"


def display_offers(offers):
    """Parses and displays flight offers in a table."""
    headers = ["Airline", "Flight No.", "Depart", "Arrive", "Duration", "Price"]
    table_data = []

    for offer in offers:
        airline = offer['owner']['name']
        price = f"{offer['total_amount']} {offer['total_currency']}"
        
        # Assuming one slice for now for simplicity
        if offer['slices']:
            slice_info = offer['slices'][0]
            duration = format_duration(slice_info.get('duration'))
            if slice_info['segments']:
                segment = slice_info['segments'][0]
                flight_no = f"{segment['marketing_carrier']['iata_code']}{segment['marketing_carrier_flight_number']}"
                depart = format_datetime(segment.get('departing_at'))
                arrive = format_datetime(segment.get('arriving_at'))
            else:
                flight_no, depart, arrive = "N/A", "N/A", "N/A"
        else:
            duration, flight_no, depart, arrive = "N/A", "N/A", "N/A", "N/A"
            
        table_data.append([airline, flight_no, depart, arrive, duration, price])

    if not table_data:
        click.echo("No flight offers found.")
        return

    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@click.group()
def cli():
    """A CLI tool to price flights."""
    pass

@cli.group()
def config():
    """Manage the flight-pricer configuration."""
    pass

@config.command()
@click.option('--api-key', 'api_key', required=True, help='Your flight search API key.')
def set(api_key):
    """Sets and saves the API key."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_data = {'api_key': api_key}
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config_data, f)
    click.echo(f"Configuration saved to {CONFIG_FILE}")

@cli.command()
@click.option('--from', 'from_iata', required=True, help='Departure airport IATA code.')
@click.option('--to', 'to_iata', required=True, help='Arrival airport IATA code.')
@click.option('--depart', 'depart_date', required=True, help='Departure date (YYYY-MM-DD).')
@click.option('--return', 'return_date', help='Return date for round-trip (YYYY-MM-DD).')
@click.option('--passengers', default=1, type=int, help='Number of passengers.')
@click.option('--max-stops', 'max_connections', default=None, type=int, help='Maximum number of stops (0 for non-stop).')
@click.option('--non-stop', 'non_stop_flag', is_flag=True, help='Alias for --max-stops 0.')
@click.option('--cabin', 'cabin_class', type=click.Choice(['economy', 'business', 'first', 'premium_economy']), help='Cabin class.')
def search(from_iata, to_iata, depart_date, return_date, passengers, max_connections, non_stop_flag, cabin_class):
    """Searches for flight prices with the specified criteria."""
    api_key = get_api_key()
    if not api_key:
        click.echo("API key not found. Please configure it using 'flight-pricer config set --api-key YOUR_KEY'")
        return

    final_max_connections = max_connections
    if non_stop_flag:
        final_max_connections = 0

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Duffel-Version": "v2",
        "Authorization": f"Bearer {api_key}"
    }

    slices = [
        {"origin": from_iata, "destination": to_iata, "departure_date": depart_date}
    ]
    if return_date:
        slices.append({"origin": to_iata, "destination": from_iata, "departure_date": return_date})

    passenger_list = [{"type": "adult"}] * passengers

    payload = {
        "data": {
            "slices": slices,
            "passengers": passenger_list
        }
    }
    
    if cabin_class:
        payload['data']['cabin_class'] = cabin_class
    if final_max_connections is not None:
        payload['data']['max_connections'] = final_max_connections
    
    click.echo("Searching for flights...")
    
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        offers = response_data.get('data', {}).get('offers', [])
        display_offers(offers)

    except requests.exceptions.HTTPError as err:
        click.echo(f"HTTP Error: {err}")
        click.echo("--- Error Response Body ---")
        try:
            click.echo(json.dumps(err.response.json(), indent=2))
        except json.JSONDecodeError:
            click.echo(err.response.text)
    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")

if __name__ == '__main__':
    cli()
