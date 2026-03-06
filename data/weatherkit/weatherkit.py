import os
import jwt
import datetime
import requests
import json
import argparse
from urllib.parse import urlencode
import sys

# WeatherKit API endpoint
WEATHERKIT_BASE_URL = "https://weatherkit.apple.com/api/v1"

def generate_jwt(team_id, key_id, private_key_path, service_id):
    """
    Generates a JWT for WeatherKit API authentication.
    """
    try:
        with open(private_key_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"Error: Private key file not found at {private_key_path}", file=sys.stderr)
        return None

    headers = {
        "alg": "ES256",
        "kid": key_id
    }

    # Token expiration: 1 hour from now
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
    # Issued at time: now
    issued_at = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        "iss": team_id,
        "iat": int(issued_at.timestamp()),
        "exp": int(expiration.timestamp()),
        "sub": service_id # Using the new env var
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return encoded_jwt

def get_forecast(latitude, longitude, start_date=None, end_date=None, timezone="auto", data_sets=None, country_code="US"):
    """
    Fetches weather forecast from WeatherKit API.
    """
    team_id = os.getenv("APPLE_TEAM_ID")
    key_id = os.getenv("APPLE_KEY_ID")
    private_key_path = os.getenv("APPLE_WEATHERKIT_KEY_PATH")
    service_id = os.getenv("APPLE_SERVICE_ID")

    if not all([team_id, key_id, private_key_path, service_id]):
        print("Error: Missing one or more WeatherKit environment variables (APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_WEATHERKIT_KEY_PATH, APPLE_SERVICE_ID).", file=sys.stderr)
        sys.exit(1)

    # Generate JWT
    token = generate_jwt(team_id, key_id, private_key_path, service_id)
    if not token:
        sys.exit(1)

    # Prepare request headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Construct the URL for the API request
    # Example: /api/v1/weather/{latitude}/{longitude}?dataSets=currentWeather,forecastDaily&countryCode=US&timezone=America/Los_Angeles
    
    # Use comma-separated data_sets
    data_sets_param = ",".join(data_sets) if data_sets else "currentWeather,forecastDaily"
    
    # Construct the query parameters
    params = {
        "dataSets": data_sets_param,
        "countryCode": country_code,
        "timezone": timezone
    }

    # Add date range if provided for historical or specific forecasts
    # WeatherKit API handles this via dailyForecast.forecastStart/End for specific dates within the response
    # The main endpoint doesn't change for date ranges, the response structure does.
    # For a *range* of daily forecasts, we just ask for forecastDaily and parse the array.

    url_path = f"/weather/en-US/{latitude}/{longitude}"
    full_url = f"{WEATHERKIT_BASE_URL}{url_path}?{urlencode(params)}"

    print(f"DEBUG: Request URL: {full_url}", file=sys.stderr) # Debugging line

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        print(f"DEBUG: Raw response text: {response.text}", file=sys.stderr)
        weather_data = response.json()
        return weather_data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}", file=sys.stderr)
        print(f"Response body: {response.text}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as json_err: # Catch specific JSON decoding error
        print(f"JSON decoding error: {json_err}", file=sys.stderr)
        print(f"Response body that failed to decode: {response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Other error occurred: {err}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Apple WeatherKit skill for OpenClaw.")
    parser.add_argument("action", choices=["get_forecast"], help="Action to perform.")
    parser.add_argument("--latitude", type=float, required=True, help="Latitude of the location.")
    parser.add_argument("--longitude", type=float, required=True, help="Longitude of the location.")
    parser.add_argument("--start-date", type=str, help="Start date for the forecast (YYYY-MM-DD).")
    parser.add_argument("--end-date", type=str, help="End date for the forecast (YYYY-MM-DD).")
    parser.add_argument("--timezone", type=str, default="auto", help="IANA timezone name (e.g., 'America/Los_Angeles').")
    parser.add_argument("--data-sets", type=str, nargs='*', help="Which data sets to return (e.g., forecastDaily, currentWeather).")
    parser.add_argument("--country-code", type=str, default="US", help="ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB').")

    args = parser.parse_args()

    if args.action == "get_forecast":
        # WeatherKit API doesn't take start/end dates as direct URL params for forecastDaily
        # It returns an array of daily forecasts which we filter or interpret.
        # We will retrieve forecastDaily and then filter based on start/end dates in Python.
        
        # Ensure data_sets includes forecastDaily if date range is specified
        if (args.start_date or args.end_date) and (not args.data_sets or "forecastDaily" not in args.data_sets):
            if args.data_sets:
                args.data_sets.append("forecastDaily")
            else:
                args.data_sets = ["forecastDaily"]

        forecast_data = get_forecast(
            args.latitude,
            args.longitude,
            timezone=args.timezone,
            data_sets=args.data_sets,
            country_code=args.country_code
        )
        
        # Filter daily forecast data by date range if provided
        if "forecastDaily" in forecast_data and forecast_data["forecastDaily"]:
            filtered_days = []
            for day in forecast_data["forecastDaily"]["days"]:
                day_date = datetime.datetime.fromisoformat(day["forecastStart"]).date()
                
                # Check start date
                if args.start_date:
                    start_filter_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
                    if day_date < start_filter_date:
                        continue
                
                # Check end date
                if args.end_date:
                    end_filter_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d").date()
                    if day_date > end_filter_date:
                        continue
                
                filtered_days.append(day)
            
            # Replace the original days with filtered ones
            forecast_data["forecastDaily"]["days"] = filtered_days

        print(json.dumps(forecast_data, indent=2))

if __name__ == "__main__":
    import sys
    main()
