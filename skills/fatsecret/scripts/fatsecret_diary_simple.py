#!/usr/bin/env python3
"""
Simplified script to add foods to the FatSecret diary.
"""

import json
import os
import sys
import time
import hashlib
import hmac
import base64
import urllib.parse
import requests
from datetime import datetime

# Configuration - use FATSECRET_CONFIG_DIR env var for persistent storage in containers
CONFIG_DIR = os.environ.get("FATSECRET_CONFIG_DIR", os.path.expanduser("~/.config/fatsecret"))
TOKENS_FILE = os.path.join(CONFIG_DIR, "oauth1_access_tokens.json")
API_URL = "https://platform.fatsecret.com/rest/server.api"

# Proxy configuration (optional)
def get_proxies():
    """Get proxy configuration from environment or config file."""
    proxy_url = os.environ.get("FATSECRET_PROXY")
    if not proxy_url and os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE) as f:
                tokens = json.load(f)
                proxy_url = tokens.get("proxy")
        except:
            pass
    if not proxy_url:
        config_file = os.path.join(CONFIG_DIR, "config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    proxy_url = config.get("proxy")
            except:
                pass
    if proxy_url:
        return {"http": proxy_url, "https": proxy_url}
    return None  # No proxy by default

PROXIES = get_proxies()

def load_tokens():
    """Load access tokens."""
    if not os.path.exists(TOKENS_FILE):
        print("❌ Tokens not found!")
        print(f"Run first: python3 fatsecret_auth.py")
        return None
    
    with open(TOKENS_FILE) as f:
        tokens = json.load(f)
    
    required = ["access_token", "access_token_secret", "consumer_key", "consumer_secret"]
    for key in required:
        if key not in tokens:
            print(f"❌ Missing token: {key}")
            return None
    
    return tokens

def make_oauth_request(method, params, tokens):
    """Make an OAuth1 signed request."""
    consumer_key = tokens["consumer_key"]
    consumer_secret = tokens["consumer_secret"]
    access_token = tokens["access_token"]
    access_token_secret = tokens["access_token_secret"]
    
    # Add OAuth parameters
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_token": access_token,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": hashlib.md5(str(time.time()).encode()).hexdigest(),
        "oauth_version": "1.0"
    }
    
    # Combine all parameters
    all_params = {**params, **oauth_params}
    
    # Sort parameters
    sorted_params = sorted(all_params.items())
    
    # Create signature string
    parameter_string = "&".join([f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
    base_string = f"{method}&{urllib.parse.quote(API_URL, safe='')}&{urllib.parse.quote(parameter_string, safe='')}"
    
    # Calculate signature
    signing_key = f"{consumer_secret}&{access_token_secret}"
    signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
    
    # Add signature
    oauth_params["oauth_signature"] = signature
    
    # Create Authorization header
    auth_header = "OAuth " + ", ".join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in oauth_params.items()])
    
    headers = {
        "Authorization": auth_header
    }
    
    # Make request
    if method == "GET":
        response = requests.get(API_URL, params=params, headers=headers, proxies=PROXIES)
    else:  # POST
        response = requests.post(API_URL, data=params, headers=headers, proxies=PROXIES)
    
    return response

def search_food(query, tokens, max_results=5):
    """Search for a food."""
    print(f"🔍 Searching: {query}")
    
    params = {
        "format": "json",
        "method": "foods.search",
        "search_expression": query,
        "max_results": str(max_results)
    }
    
    response = make_oauth_request("GET", params, tokens)
    
    if response.status_code != 200:
        print(f"❌ Search error: {response.status_code}")
        return []
    
    data = response.json()
    if "foods" not in data or "food" not in data["foods"]:
        return []
    
    foods = data["foods"]["food"]
    if not isinstance(foods, list):
        foods = [foods]
    
    return foods

def get_food_details(food_id, tokens):
    """Get food details."""
    params = {
        "format": "json",
        "method": "food.get.v4",
        "food_id": food_id
    }
    
    response = make_oauth_request("GET", params, tokens)
    
    if response.status_code != 200:
        print(f"❌ Details error: {response.status_code}")
        return None
    
    data = response.json()
    return data.get("food")

def log_food(food_id, serving_id, grams_or_ml, meal="Breakfast", food_entry_name=None, tokens=None):
    """
    Add a food to the diary.
    
    IMPORTANT: grams_or_ml is the ACTUAL amount in grams or ml, NOT a multiplier!
    
    Example:
        - To log 156g of cookies with a "100g" serving: grams_or_ml = 156
        - To log 200ml of milk with a "100ml" serving: grams_or_ml = 200
        - To log 2 eggs with a "1 large egg" serving: grams_or_ml = 2
    
    Args:
        food_id: FatSecret food ID
        serving_id: FatSecret serving ID (defines the unit: g, ml, piece, etc.)
        grams_or_ml: Actual amount in the serving's unit (grams, ml, or count)
        meal: "Breakfast", "Lunch", "Dinner", or "Snack"
        food_entry_name: Display name for the entry
        tokens: OAuth tokens (loaded automatically if None)
    """
    if tokens is None:
        tokens = load_tokens()
        if not tokens:
            return False
    
    if food_entry_name is None:
        food_entry_name = f"Food {food_id}"
    
    # Warning if value seems suspiciously low (likely a multiplier mistake)
    if grams_or_ml < 10 and grams_or_ml != int(grams_or_ml):
        print(f"⚠️  WARNING: grams_or_ml={grams_or_ml} seems low!")
        print(f"   Remember: this is the ACTUAL amount (g/ml), not a multiplier.")
        print(f"   For 156g, use grams_or_ml=156, NOT 1.56")
    
    params = {
        "format": "json",
        "method": "food_entry.create",
        "food_id": food_id,
        "serving_id": serving_id,
        "number_of_units": str(grams_or_ml),
        "meal": meal,
        "food_entry_name": food_entry_name
    }
    
    print(f"📝 Logging: {food_entry_name} ({grams_or_ml}g/ml)")
    response = make_oauth_request("POST", params, tokens)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"   Message: {response.text}")
        return False
    
    data = response.json()
    if "food_entry_id" in data:
        entry_id = data["food_entry_id"].get("value")
        print(f"✅ Logged! Entry ID: {entry_id}")
        return True
    else:
        print(f"❌ Unexpected response: {data}")
    
    return False

def interactive_log():
    """Interactive mode to log foods."""
    print("="*60)
    print("FATSECRET DIARY - LOG FOODS")
    print("="*60)
    
    # Load tokens
    tokens = load_tokens()
    if not tokens:
        return
    
    print(f"✅ Tokens loaded from: {TOKENS_FILE}")
    
    # Search food
    query = input("\n🔍 Search food: ").strip()
    if not query:
        print("❌ No search query specified")
        return
    
    foods = search_food(query, tokens)
    
    if not foods:
        print("❌ No results found")
        return
    
    # Show results
    print(f"\n📋 Results found ({len(foods)}):")
    for i, food in enumerate(foods[:10], 1):
        food_id = food.get("food_id")
        food_name = food.get("food_name", "Unknown")
        food_type = food.get("food_type", "")
        brand = food.get("brand_name", "")
        
        brand_str = f" ({brand})" if brand else ""
        type_str = f" [{food_type}]" if food_type else ""
        
        print(f"{i}. {food_name}{brand_str}{type_str} (ID: {food_id})")
    
    # Select food
    try:
        choice = int(input(f"\nSelect food (1-{len(foods)}): ")) - 1
        if choice < 0 or choice >= len(foods):
            print("❌ Invalid choice")
            return
    except ValueError:
        print("❌ Enter a valid number")
        return
    
    selected_food = foods[choice]
    food_id = selected_food.get("food_id")
    food_name = selected_food.get("food_name", "Food")
    
    # Get details (for servings)
    print(f"\n📊 Getting details for: {food_name}")
    food_details = get_food_details(food_id, tokens)
    
    if not food_details or "servings" not in food_details or "serving" not in food_details["servings"]:
        print("❌ Cannot get servings")
        return
    
    servings = food_details["servings"]["serving"]
    if not isinstance(servings, list):
        servings = [servings]
    
    # Show servings
    print(f"\n🍽️  Available servings:")
    for i, serving in enumerate(servings[:10], 1):
        serving_id = serving.get("serving_id")
        description = serving.get("serving_description", "Unknown")
        calories = serving.get("calories", "?")
        
        print(f"{i}. {description} ({calories} kcal)")
    
    # Select serving
    try:
        serving_choice = int(input(f"\nSelect serving (1-{len(servings)}): ")) - 1
        if serving_choice < 0 or serving_choice >= len(servings):
            print("❌ Invalid choice")
            return
    except ValueError:
        print("❌ Enter a valid number")
        return
    
    selected_serving = servings[serving_choice]
    serving_id = selected_serving.get("serving_id")
    serving_desc = selected_serving.get("serving_description", "Serving")
    
    # Quantity
    try:
        quantity = float(input(f"\nQuantity (how many '{serving_desc}'): "))
        if quantity <= 0:
            print("❌ Quantity must be > 0")
            return
    except ValueError:
        print("❌ Enter a valid number")
        return
    
    # Meal
    print("\n🍽️  Available meals:")
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    for i, meal in enumerate(meals, 1):
        print(f"{i}. {meal}")
    
    try:
        meal_choice = int(input(f"\nSelect meal (1-{len(meals)}): ")) - 1
        if meal_choice < 0 or meal_choice >= len(meals):
            meal_choice = 0  # Default to Breakfast
    except ValueError:
        meal_choice = 0
    
    meal = meals[meal_choice]
    
    # Entry name
    food_entry_name = input(f"\nEntry name (default: '{food_name}'): ").strip()
    if not food_entry_name:
        food_entry_name = food_name
    
    # Confirm
    print(f"\n📋 Summary:")
    print(f"   Food: {food_name}")
    print(f"   Serving: {serving_desc}")
    print(f"   Quantity: {quantity}")
    print(f"   Meal: {meal}")
    print(f"   Entry name: {food_entry_name}")
    
    confirm = input("\nConfirm entry? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled")
        return
    
    # Log
    success = log_food(food_id, serving_id, quantity, meal, food_entry_name, tokens)
    
    if success:
        print(f"\n✅ {food_entry_name} added to diary ({meal})")
    else:
        print(f"\n❌ Error adding to diary")

def quick_log(food_name, quantity=1, meal="Breakfast"):
    """
    Quick log for common foods.
    
    NOTE: 'quantity' here is passed directly to FatSecret as number_of_units.
    - For countable items (eggs, apples): quantity = count (e.g., 3 eggs)
    - For weighted items with "100g" serving: quantity = grams (e.g., 150 for 150g)
    
    For precise logging with grams, use log_food() directly.
    """
    tokens = load_tokens()
    if not tokens:
        return False
    
    # Search food
    foods = search_food(food_name, tokens, max_results=3)
    if not foods:
        print(f"❌ '{food_name}' not found")
        return False
    
    # Take first result
    food = foods[0]
    food_id = food.get("food_id")
    food_name_display = food.get("food_name", food_name)
    
    # Get details
    food_details = get_food_details(food_id, tokens)
    if not food_details or "servings" not in food_details or "serving" not in food_details["servings"]:
        print(f"❌ Cannot get servings for '{food_name}'")
        return False
    
    servings = food_details["servings"]["serving"]
    if not isinstance(servings, list):
        servings = [servings]
    
    # Prefer countable servings (1 egg, 1 piece) over weight-based (100g)
    serving = servings[0]
    for s in servings:
        desc = s.get("serving_description", "").lower()
        if any(word in desc for word in ["1 ", "piece", "egg", "slice", "cup"]):
            serving = s
            break
    
    serving_id = serving.get("serving_id")
    serving_desc = serving.get("serving_description", "")
    
    print(f"ℹ️  Using serving: {serving_desc}")
    
    # Log
    return log_food(food_id, serving_id, quantity, meal, food_name_display, tokens)

def main():
    """Main menu."""
    print("="*60)
    print("FATSECRET DIARY TOOL")
    print("="*60)
    print("\n1. Interactive mode")
    print("2. Quick log (e.g.: 'python3 fatsecret_diary_simple.py egg 3')")
    print("3. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        interactive_log()
    elif choice == "2" and len(sys.argv) > 1:
        # Command line usage: python3 script.py "egg" 3 "Breakfast"
        food_name = sys.argv[1]
        quantity = float(sys.argv[2]) if len(sys.argv) > 2 else 1
        meal = sys.argv[3] if len(sys.argv) > 3 else "Breakfast"
        
        print(f"\nQuick log: {quantity}x {food_name} ({meal})")
        success = quick_log(food_name, quantity, meal)
        
        if success:
            print(f"✅ {food_name} added to diary!")
        else:
            print(f"❌ Error adding {food_name}")
    else:
        print("Goodbye!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Non-interactive mode
        food_name = sys.argv[1]
        quantity = float(sys.argv[2]) if len(sys.argv) > 2 else 1
        meal = sys.argv[3] if len(sys.argv) > 3 else "Breakfast"
        
        print(f"Quick log: {quantity}x {food_name} ({meal})")
        success = quick_log(food_name, quantity, meal)
        
        if success:
            print(f"✅ {food_name} added to diary!")
        else:
            print(f"❌ Error adding {food_name}")
    else:
        # Interactive mode
        main()