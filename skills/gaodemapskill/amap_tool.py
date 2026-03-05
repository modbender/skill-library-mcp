import os
import sys
import json
import requests
import argparse

class AMapClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v3"

    def place_search(self, keywords, city=None):
        """
        Search for places based on keywords.
        """
        url = f"{self.base_url}/place/text"
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "output": "json"
        }
        if city:
            params["city"] = city
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1":
                return data.get("pois", [])
            else:
                return {"error": data.get("info", "Unknown error")}
        except Exception as e:
            return {"error": str(e)}

    def geocode(self, address, city=None):
        """
        Convert address to coordinates.
        """
        url = f"{self.base_url}/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        if city:
            params["city"] = city
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1" and data.get("geocodes"):
                return data["geocodes"][0]["location"]
            else:
                return None
        except:
            return None

    def route_planning(self, origin, destination, mode="driving", city=None):
        """
        Plan a route between origin and destination.
        Origin and destination can be coordinates (lon,lat) or names.
        If names are provided, geocoding will be attempted.
        """
        # If origin/destination don't look like coordinates, try to geocode them
        if "," not in origin:
            loc = self.geocode(origin, city)
            if loc:
                origin = loc
            else:
                return {"error": f"Could not geocode origin: {origin}"}
        
        if "," not in destination:
            loc = self.geocode(destination, city)
            if loc:
                destination = loc
            else:
                return {"error": f"Could not geocode destination: {destination}"}

        if mode == "driving":
            url = f"{self.base_url}/direction/driving"
        elif mode == "walking":
            url = f"{self.base_url}/direction/walking"
        elif mode == "bicycling":
            url = f"{self.base_url}/direction/bicycling"
        elif mode == "transit":
            url = f"{self.base_url}/direction/transit/integrated"
            if not city:
                 return {"error": "City is required for transit route planning"}
        else:
            return {"error": f"Unsupported mode: {mode}"}

        params = {
            "key": self.api_key,
            "origin": origin,
            "destination": destination,
            "output": "json"
        }
        
        if mode == "transit" and city:
             params["city"] = city

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1":
                return data.get("route", {})
            else:
                return {"error": data.get("info", "Unknown error")}
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="AMap (Gaode Map) Skill Tool")
    parser.add_argument("action", choices=["search", "route"], help="Action to perform")
    parser.add_argument("--key", help="AMap API Key (can also be set via AMAP_API_KEY env var)")
    parser.add_argument("--keywords", help="Keywords for place search")
    parser.add_argument("--city", help="City for search or route planning")
    parser.add_argument("--origin", help="Origin for route planning")
    parser.add_argument("--destination", help="Destination for route planning")
    parser.add_argument("--mode", default="driving", choices=["driving", "walking", "bicycling", "transit"], help="Route planning mode")

    args = parser.parse_args()

    api_key = args.key or os.environ.get("AMAP_API_KEY")
    if not api_key:
        print(json.dumps({"error": "AMap API Key is required. Set AMAP_API_KEY env var or pass --key."}))
        sys.exit(1)

    client = AMapClient(api_key)
    result = {}

    if args.action == "search":
        if not args.keywords:
            result = {"error": "--keywords is required for search"}
        else:
            result = client.place_search(args.keywords, args.city)
    elif args.action == "route":
        if not args.origin or not args.destination:
            result = {"error": "--origin and --destination are required for route"}
        else:
            result = client.route_planning(args.origin, args.destination, args.mode, args.city)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
