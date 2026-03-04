#!/usr/bin/env python3
"""
Open Food Facts API Client
Free, no authentication required, European/Italian products included.
"""

import json
import sys
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library required")
    sys.exit(1)


class OpenFoodFactsClient:
    """Open Food Facts API client - completely free, no auth needed."""
    
    # Use Italian instance for better local product coverage
    BASE_URL = "https://world.openfoodfacts.org"
    IT_URL = "https://it.openfoodfacts.org"
    
    def __init__(self, country: str = "world"):
        """Initialize client.
        
        Args:
            country: Country code (it, world, us, fr, etc.)
        """
        if country == "it":
            self.base_url = self.IT_URL
        else:
            self.base_url = f"https://{country}.openfoodfacts.org" if country != "world" else self.BASE_URL
    
    def search(self, query: str, page: int = 1, page_size: int = 20) -> dict:
        """Search products by name.
        
        Args:
            query: Search term
            page: Page number (1-indexed)
            page_size: Results per page
        
        Returns:
            Dict with products
        """
        response = requests.get(
            f"{self.base_url}/cgi/search.pl",
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page": page,
                "page_size": page_size
            },
            headers={"User-Agent": "OpenClaw/1.0"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_product(self, barcode: str) -> dict:
        """Get product by barcode.
        
        Args:
            barcode: Product barcode (EAN/UPC)
        
        Returns:
            Dict with product data
        """
        response = requests.get(
            f"{self.base_url}/api/v2/product/{barcode}.json",
            headers={"User-Agent": "OpenClaw/1.0"}
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == 0:
            raise Exception(f"Product not found: {barcode}")
        return data


def extract_nutrition(product: dict) -> dict:
    """Extract nutrition info from OFF product."""
    nutriments = product.get("nutriments", {})
    return {
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "quantity": product.get("quantity", ""),
        "serving_size": product.get("serving_size", ""),
        "per_100g": {
            "calories": nutriments.get("energy-kcal_100g", nutriments.get("energy_100g", "?")),
            "protein": nutriments.get("proteins_100g", "?"),
            "carbs": nutriments.get("carbohydrates_100g", "?"),
            "fat": nutriments.get("fat_100g", "?"),
            "fiber": nutriments.get("fiber_100g", "?"),
            "sugar": nutriments.get("sugars_100g", "?"),
            "salt": nutriments.get("salt_100g", "?"),
        },
        "per_serving": {
            "calories": nutriments.get("energy-kcal_serving", "?"),
            "protein": nutriments.get("proteins_serving", "?"),
            "carbs": nutriments.get("carbohydrates_serving", "?"),
            "fat": nutriments.get("fat_serving", "?"),
        } if nutriments.get("energy-kcal_serving") else None
    }


def format_product(product: dict) -> str:
    """Format product for display."""
    nutr = extract_nutrition(product)
    lines = [
        f"**{nutr['name']}**",
        f"Brand: {nutr['brand'] or 'N/A'}",
        f"Quantity: {nutr['quantity'] or 'N/A'}",
    ]
    
    p = nutr["per_100g"]
    lines.append(f"\nPer 100g:")
    lines.append(f"  {p['calories']} kcal | P {p['protein']}g | C {p['carbs']}g | F {p['fat']}g")
    if p.get('fiber') and p['fiber'] != '?':
        lines.append(f"  Fiber: {p['fiber']}g | Sugar: {p['sugar']}g")
    
    if nutr["per_serving"]:
        s = nutr["per_serving"]
        lines.append(f"\nPer serving ({nutr['serving_size']}):")
        lines.append(f"  {s['calories']} kcal | P {s['protein']}g | C {s['carbs']}g | F {s['fat']}g")
    
    return "\n".join(lines)


def format_search_results(data: dict) -> str:
    """Format search results for display."""
    products = data.get("products", [])
    count = data.get("count", len(products))
    lines = [f"Found {count} results:\n"]
    
    for p in products[:10]:
        name = p.get("product_name", "Unknown")
        brand = p.get("brands", "")
        barcode = p.get("code", "")
        nutr = p.get("nutriments", {})
        kcal = nutr.get("energy-kcal_100g", "?")
        
        brand_str = f" ({brand})" if brand else ""
        lines.append(f"• [{barcode}] {name}{brand_str}")
        lines.append(f"  Per 100g: {kcal} kcal")
    
    return "\n".join(lines)


# ==================== CLI ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Open Food Facts CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Search command
    search_p = subparsers.add_parser("search", help="Search products")
    search_p.add_argument("query", help="Search term")
    search_p.add_argument("--country", default="it", help="Country (it, world, us, etc.)")
    search_p.add_argument("--max", type=int, default=10)
    search_p.add_argument("--json", action="store_true")
    
    # Barcode command
    barcode_p = subparsers.add_parser("barcode", help="Lookup by barcode")
    barcode_p.add_argument("barcode", help="Product barcode")
    barcode_p.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "search":
            client = OpenFoodFactsClient(country=args.country)
            result = client.search(args.query, page_size=args.max)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_search_results(result))
        
        elif args.command == "barcode":
            client = OpenFoodFactsClient()
            result = client.get_product(args.barcode)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_product(result.get("product", {})))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
