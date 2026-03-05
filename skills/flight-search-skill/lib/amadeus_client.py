#!/usr/bin/python3
"""
Amadeus Flight Search API Client
Supports flight search, price comparison, and monitoring
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class AmadeusClient:
    """Client for Amadeus Flight Search API"""
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = True, 
                 base_url_test: str = None, base_url_production: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # Use URLs from config or defaults
        test_url = base_url_test or "https://test.api.amadeus.com"
        prod_url = base_url_production or "https://api.amadeus.com"
        
        self.auth_url = f"{test_url if sandbox else prod_url}/v1/security/oauth2/token"
        self.api_url = test_url if sandbox else prod_url
        self.token = None
        self.token_expires_at = None
    
    def authenticate(self) -> bool:
        """Get OAuth2 token from Amadeus API"""
        url = self.auth_url
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                # Token expires in ~30 minutes, set expiry 5 min early for safety
                self.token_expires_at = datetime.now() + timedelta(seconds=token_data.get("expires_in", 1800) - 300)
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Authentication error: {e}", file=sys.stderr)
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid token"""
        if self.token is None or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return self.authenticate()
        return self.token is not None
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        currency: str = "BRL",
        max_results: int = 20,
        max_stops: Optional[int] = None,
        travel_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for flights using Amadeus Flight Low-Fare Search API
        
        Args:
            origin: IATA code of origin airport (e.g., "CNF")
            destination: IATA code of destination airport (e.g., "BKK")
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Optional return date in YYYY-MM-DD format
            adults: Number of adult passengers
            currency: Currency code (default: BRL)
            max_results: Maximum number of results to return
            max_stops: Maximum number of stops (None = any)
            travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        
        Returns:
            List of flight offers with pricing and itinerary details
            None on error (network, API failure)
            Empty list [] on valid search with no results
        """
        if not self._ensure_authenticated():
            return None  # P1 fix: Return None on auth failure
        
        url = f"{self.api_url}/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": currency,
            "max": max_results
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        if max_stops is not None:
            params["maxStops"] = max_stops
        
        if travel_class:
            params["travelClass"] = travel_class
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_flight_results(response.json())
            elif response.status_code == 400:
                # P2 fix: HTTP 400 = bad request (invalid dates, airport codes, etc.)
                # This is NOT a valid empty result - it's a user input error!
                error_data = response.json()
                error_detail = error_data.get('errors', [{}])[0].get('detail', 'Unknown error')
                print(f"Search error: {error_detail}", file=sys.stderr)
                print("  • Check date format (YYYY-MM-DD)", file=sys.stderr)
                print("  • Verify airport codes are valid IATA (e.g., CNF, GRU, JFK)", file=sys.stderr)
                return None  # P2 fix: Return None to indicate error
            else:
                print(f"Search failed: {response.status_code} - {response.text}", file=sys.stderr)
                return None  # P1 fix: Return None on API error
        except requests.exceptions.Timeout:
            print("Search error: Request timeout", file=sys.stderr)
            return None  # P1 fix: Return None on timeout
        except requests.exceptions.ConnectionError:
            print("Search error: Connection failed", file=sys.stderr)
            return None  # P1 fix: Return None on connection error
        except Exception as e:
            print(f"Search error: {e}", file=sys.stderr)
            return None  # P1 fix: Return None on other errors
    
    def _parse_flight_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Amadeus flight search results into standardized format"""
        flights = []
        
        for offer in data.get("data", []):
            try:
                # Extract price
                price_info = offer.get("price", {})
                price = float(price_info.get("total", 0))
                currency = price_info.get("currency", "BRL")
                
                # Extract airline (first validating airline)
                airlines = offer.get("validatingAirlineCodes", [])
                airline = airlines[0] if airlines else "Unknown"
                
                # Parse itineraries (outbound and return)
                itineraries = []
                for itinerary in offer.get("itineraries", []):
                    segments = []
                    for segment in itinerary.get("segments", []):
                        segments.append({
                            "departure": segment["departure"]["at"],
                            "arrival": segment["arrival"]["at"],
                            "carrier": segment["carrierCode"],
                            "flight_number": segment["number"],
                            "duration": segment.get("duration", ""),
                            "from": segment["departure"]["iataCode"],
                            "to": segment["arrival"]["iataCode"],
                            "aircraft": segment.get("aircraft", {}).get("code", "Unknown")
                        })
                    
                    itineraries.append({
                        "duration": itinerary.get("duration", ""),
                        "segments": segments
                    })
                
                flight = {
                    "api": "amadeus",
                    "id": offer.get("id", ""),
                    "price": price,
                    "currency": currency,
                    "airline": airline,
                    "itineraries": itineraries,
                    "source": "amadeus_sandbox" if self.sandbox else "amadeus_production"
                }
                
                flights.append(flight)
            except Exception as e:
                print(f"Parse error for offer: {e}", file=sys.stderr)
                continue
        
        return flights
    
    def search_flexible_dates(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        trip_duration_days: Optional[int] = None,
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search flights across a date range for best prices
        
        Args:
            origin: IATA code of origin
            destination: IATA code of destination
            start_date: Start of date range (YYYY-MM-DD)
            end_date: End of date range (YYYY-MM-DD)
            trip_duration_days: Desired trip duration (optional)
            **kwargs: Additional search parameters
        
        Returns:
            Dictionary with dates as keys and flight lists as values
        """
        results = {}
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Search each date in range (limited to prevent API abuse)
        current = start
        max_days = 30  # Limit to 30 days to avoid rate limiting
        days_searched = 0
        
        while current <= end and days_searched < max_days:
            date_str = current.strftime("%Y-%m-%d")
            
            # Calculate return date if trip duration specified
            return_date = None
            if trip_duration_days:
                return_date = (current + timedelta(days=trip_duration_days)).strftime("%Y-%m-%d")
            
            flights = self.search_flights(
                origin=origin,
                destination=destination,
                departure_date=date_str,
                return_date=return_date,
                **kwargs
            )
            
            if flights:
                results[date_str] = sorted(flights, key=lambda x: x["price"])
            
            current += timedelta(days=1)
            days_searched += 1
        
        return results


def main():
    """CLI interface for Amadeus client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Search flights with Amadeus API")
    parser.add_argument("--origin", required=True, help="Origin IATA code (e.g., CNF)")
    parser.add_argument("--destination", required=True, help="Destination IATA code (e.g., BKK)")
    parser.add_argument("--departure", required=True, help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--return", dest="return_date", help="Return date (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=1, help="Number of adults")
    parser.add_argument("--currency", default="BRL", help="Currency code")
    parser.add_argument("--max", type=int, default=20, help="Maximum results")
    parser.add_argument("--max-stops", type=int, help="Maximum stops")
    parser.add_argument("--class", dest="travel_class", help="Travel class (ECONOMY, BUSINESS)")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    
    args = parser.parse_args()
    
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
    
    # P2 fix: Validate Amadeus config structure
    if "apis" not in config:
        print("Error: Invalid config.json - missing 'apis' section", file=sys.stderr)
        print("  See config.example.json for required format", file=sys.stderr)
        sys.exit(1)
    
    if "amadeus" not in config["apis"]:
        print("Error: Invalid config.json - missing 'apis.amadeus' section", file=sys.stderr)
        print("  See config.example.json for required format", file=sys.stderr)
        sys.exit(1)
    
    amadeus_config = config["apis"]["amadeus"]
    
    # P2 fix: Validate required Amadeus keys
    required_keys = ["api_key", "api_secret"]
    missing_keys = [key for key in required_keys if key not in amadeus_config]
    
    if missing_keys:
        print(f"Error: Invalid config.json - missing Amadeus keys: {', '.join(missing_keys)}", file=sys.stderr)
        print("  See config.example.json for required format", file=sys.stderr)
        sys.exit(1)
    
    # Validate non-empty values
    if not amadeus_config.get("api_key") or not amadeus_config.get("api_secret"):
        print("Error: Invalid config.json - api_key and api_secret cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    # Create client
    client = AmadeusClient(
        api_key=amadeus_config["api_key"],
        api_secret=amadeus_config["api_secret"],
        sandbox=amadeus_config.get("sandbox_mode", True),
        base_url_test=amadeus_config.get("base_url_test"),
        base_url_production=amadeus_config.get("base_url_production")
    )
    
    # Check authentication
    if not client.authenticate():
        print("Error: Failed to authenticate with Amadeus API", file=sys.stderr)
        print("Check your API key and secret in config.json", file=sys.stderr)
        sys.exit(1)
    
    # Search flights
    results = client.search_flights(
        origin=args.origin,
        destination=args.destination,
        departure_date=args.departure,
        return_date=args.return_date,
        adults=args.adults,
        currency=args.currency,
        max_results=args.max,
        max_stops=getattr(args, "max_stops", None),
        travel_class=args.travel_class
    )
    
    # P1 fix: Check if search actually succeeded
    # None indicates error (network, API failure), [] indicates valid no results
    if results is None:
        print("Error: Failed to search flights (network/API error)", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
