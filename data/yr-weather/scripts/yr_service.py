#!/usr/bin/env python3
"""
Yr.no Weather Service Module
Handles API calls to MET Norway's Locationforecast API.
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

def get_location_forecast(lat: float, lon: float, altitude: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch weather forecast data for the given coordinates.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        altitude: Altitude in meters (optional)
    
    Returns:
        Raw JSON response from API.
    
    Raises:
        urllib.error.URLError: On network or HTTP errors.
    """
    params = {"lat": str(lat), "lon": str(lon)}
    if altitude is not None:
        params["altitude"] = str(altitude)
    
    query_string = urllib.parse.urlencode(params)
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?{query_string}"
    
    headers = {
        "User-Agent": "OpenClawYrWeather/1.0 (https://github.com/openclaw/openclaw)"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except urllib.error.URLError as e:
        raise urllib.error.URLError(f"Error fetching weather from MET API: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error: {e}") from e
