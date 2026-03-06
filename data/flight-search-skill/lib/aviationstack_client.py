#!/usr/bin/python3
"""
AviationStack Flight Status API Client
Supports real-time flight status, tracking, and historical data
"""

import requests
import json
import sys
import os
from typing import Dict, Optional, Any
from datetime import datetime

class AviationStackClient:
    """Client for AviationStack Flight Status API"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        # Default to HTTPS for security (API key sent in query params)
        self.base_url = base_url or "https://api.aviationstack.com/v1"
        self.request_count = 0
        self.monthly_limit = 100  # Free tier limit
    
    def get_flight_status(
        self,
        flight_iata: Optional[str] = None,
        flight_icao: Optional[str] = None,
        flight_number: Optional[str] = None,
        date: Optional[str] = None,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get flight status information
        
        Args:
            flight_iata: Flight IATA code (e.g., "AA123")
            flight_icao: Flight ICAO code (e.g., "AAL123")
            flight_number: Flight number only (e.g., "123")
            date: Flight date in YYYY-MM-DD format
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
        
        Returns:
            Flight status information or None if not found
            None on error (network, API failure)
        """
        # Check rate limit
        if self.request_count >= self.monthly_limit:
            print("Warning: Approaching monthly rate limit", file=sys.stderr)
        
        url = f"{self.base_url}/flights"
        params = {"access_key": self.api_key}
        
        # Add optional parameters
        if flight_iata:
            params["flight_iata"] = flight_iata.upper()
        elif flight_icao:
            params["flight_icao"] = flight_icao.upper()
        
        if flight_number:
            params["flight_number"] = flight_number
        
        if date:
            params["flight_date"] = date
        
        if dep_iata:
            params["dep_iata"] = dep_iata.upper()
        
        if arr_iata:
            params["arr_iata"] = arr_iata.upper()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_data(data)
            else:
                print(f"Status check failed: {response.status_code}", file=sys.stderr)
                return None  # P2 fix: Return None on HTTP error
        
        except requests.exceptions.Timeout:
            print("Status check error: Request timeout", file=sys.stderr)
            return None  # P2 fix: Return None on timeout
        except requests.exceptions.ConnectionError:
            print("Status check error: Connection failed", file=sys.stderr)
            return None  # P2 fix: Return None on connection error
        except Exception as e:
            print(f"Status check error: {e}", file=sys.stderr)
            return None  # P2 fix: Return None on other errors
    
    def _parse_flight_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse AviationStack response into standardized format
        
        Returns:
            Dict with flight data if found
            {} (empty dict) if valid response but no flights found
            None if data is invalid/malformed
        """
        if not data.get("data"):
            # Check if this is a valid response with no data vs invalid response
            # HTTP 200 with empty "data" array = valid "not found"
            if "data" in data and data["data"] == []:
                return {}  # P2 fix: Empty dict = valid "not found"
            return None  # Invalid/malformed response
        
        # Get first result
        flight = data["data"][0]
        
        # ... rest of parsing ...
        
        # Determine status emoji and text
        status = flight.get("flight_status", "unknown")
        status_map = {
            "scheduled": {"emoji": "⏰", "text": "Scheduled"},
            "active": {"emoji": "✈️", "text": "In Flight"},
            "landed": {"emoji": "✅", "text": "Landed"},
            "cancelled": {"emoji": "❌", "text": "Cancelled"},
            "incident": {"emoji": "⚠️", "text": "Incident"},
            "diverted": {"emoji": "🔀", "text": "Diverted"}
        }
        status_info = status_map.get(status, {"emoji": "❓", "text": "Unknown"})
        
        # Parse departure info
        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})
        airline = flight.get("airline", {})
        flight_info = flight.get("flight", {})
        aircraft = flight.get("aircraft", {})
        
        result = {
            "api": "aviationstack",
            "flight_number": flight_info.get("iata") or flight_info.get("icao"),
            "airline": {
                "name": airline.get("name"),
                "iata": airline.get("iata"),
                "icao": airline.get("icao")
            },
            "status": {
                "code": status,
                "emoji": status_info["emoji"],
                "text": status_info["text"]
            },
            "departure": {
                "airport": departure.get("airport"),
                "iata": departure.get("iata"),
                "icao": departure.get("icao"),
                "terminal": departure.get("terminal"),
                "gate": departure.get("gate"),
                "scheduled": departure.get("scheduled"),
                "estimated": departure.get("estimated"),
                "actual": departure.get("actual"),
                "delay": departure.get("delay", 0)
            },
            "arrival": {
                "airport": arrival.get("airport"),
                "iata": arrival.get("iata"),
                "icao": arrival.get("icao"),
                "terminal": arrival.get("terminal"),
                "gate": arrival.get("gate"),
                "baggage": arrival.get("baggage"),
                "scheduled": arrival.get("scheduled"),
                "estimated": arrival.get("estimated"),
                "actual": arrival.get("actual"),
                "delay": arrival.get("delay", 0)
            },
            "aircraft": {
                "registration": aircraft.get("registration"),
                "iata": aircraft.get("iata"),
                "icao": aircraft.get("icao")
            },
            "live": flight.get("live")
        }
        
        return result
    
    def search_flights_by_route(
        self,
        dep_iata: str,
        arr_iata: str,
        date: Optional[str] = None
    ) -> Optional[list]:
        """
        Search flights by route (departure and arrival airports)
        
        Args:
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            date: Optional date in YYYY-MM-DD format
        
        Returns:
            List of flights on this route
            None on error (network, API failure)
            Empty list [] on valid search with no results
        """
        url = f"{self.base_url}/flights"
        params = {
            "access_key": self.api_key,
            "dep_iata": dep_iata.upper(),
            "arr_iata": arr_iata.upper()
        }
        
        if date:
            params["flight_date"] = date
        
        try:
            response = requests.get(url, params=params, timeout=30)
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                flights = []
                
                for flight in data.get("data", []):
                    parsed = self._parse_flight_data({"data": [flight]})
                    if parsed:
                        flights.append(parsed)
                
                return flights
            else:
                print(f"Route search failed: {response.status_code}", file=sys.stderr)
                return None  # P2 fix: Return None on HTTP error
        
        except requests.exceptions.Timeout:
            print("Route search error: Request timeout", file=sys.stderr)
            return None  # P2 fix: Return None on timeout
        except requests.exceptions.ConnectionError:
            print("Route search error: Connection failed", file=sys.stderr)
            return None  # P2 fix: Return None on connection error
        except Exception as e:
            print(f"Route search error: {e}", file=sys.stderr)
            return None  # P2 fix: Return None on other errors


def main():
    """CLI interface for AviationStack client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check flight status with AviationStack API")
    parser.add_argument("--flight", help="Flight number (IATA: AA123 or number: 123)")
    parser.add_argument("--date", help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--dep", help="Departure airport IATA code")
    parser.add_argument("--arr", help="Arrival airport IATA code")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    
    args = parser.parse_args()
    
    if not args.flight and not (args.dep and args.arr):
        parser.error("Either --flight or both --dep and --arr must be specified")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "..", args.config)
    if not os.path.exists(config_path):
        config_path = args.config
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if AviationStack is configured
    apis_config = config.get("apis", {})
    avs_config = apis_config.get("aviationstack", {})
    
    if not avs_config:
        print("AviationStack is not configured in config.json", file=sys.stderr)
        print("Add 'aviationstack' section to config.json to enable flight status", file=sys.stderr)
        sys.exit(1)
    
    if not avs_config.get("enabled", False):
        print("AviationStack is disabled in config", file=sys.stderr)
        sys.exit(1)
    
    # P2 fix: Validate AviationStack config keys
    if "api_key" not in avs_config:
        print("Error: Invalid config.json - missing 'apis.aviationstack.api_key'", file=sys.stderr)
        print("  See config.example.json for required format", file=sys.stderr)
        sys.exit(1)
    
    # Validate non-empty value
    if not avs_config.get("api_key"):
        print("Error: Invalid config.json - api_key cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    # Create client
    client = AviationStackClient(
        api_key=avs_config["api_key"],
        base_url=avs_config.get("base_url")
    )
    
    # Get flight status
    if args.flight:
        # Auto-detect if input is IATA code (AA123) or flight number (123)
        flight_input = args.flight.strip()
        
        # Check if it's numeric only (flight number)
        if flight_input.isdigit():
            # Pure numeric - use flight_number parameter
            result = client.get_flight_status(
                flight_number=flight_input,
                date=args.date
            )
        elif len(flight_input) >= 2 and flight_input[:2].isalpha():
            # Starts with letters - IATA code (e.g., AA123, LA1234)
            result = client.get_flight_status(
                flight_iata=flight_input.upper(),
                date=args.date
            )
        else:
            # Default to IATA for backwards compatibility
            result = client.get_flight_status(
                flight_iata=flight_input.upper(),
                date=args.date
            )
    else:
        results = client.search_flights_by_route(
            dep_iata=args.dep,
            arr_iata=args.arr,
            date=args.date
        )
        
        # P2 fix: Check for error vs empty results
        if results is None:
            print("Error: Failed to search flights by route (network/API error)", file=sys.stderr)
            sys.exit(1)
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    
    # Single flight status check
    if result:
        # Success - found flight
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif result is None:
        # P2 fix: Network/API error
        print("Error: Failed to check flight status (network/API error)", file=sys.stderr)
        sys.exit(1)
    elif result == {}:
        # P2 fix: Valid response but flight not found
        print("Flight not found", file=sys.stderr)
        print("  • Check flight number (IATA code: AA123 or number: 123)", file=sys.stderr)
        print("  • Verify flight exists for this date", file=sys.stderr)
        sys.exit(1)
    else:
        # Unexpected result type
        print("Error: Unexpected response format", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
