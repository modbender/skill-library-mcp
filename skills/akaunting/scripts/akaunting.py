#!/usr/bin/env python3
"""
Akaunting CLI - Interact with Akaunting accounting software via REST API.
"""

import argparse
import json
import os
import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# Config file location
CONFIG_PATH = Path.home() / ".config" / "akaunting" / "config.json"


def load_config():
    """Load configuration from file or environment."""
    config = {
        "url": os.environ.get("AKAUNTING_URL"),
        "email": os.environ.get("AKAUNTING_EMAIL"),
        "password": os.environ.get("AKAUNTING_PASSWORD"),
    }
    
    # Try loading from config file if env vars not set
    if not all(config.values()) and CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            file_config = json.load(f)
            config.update({k: v for k, v in file_config.items() if v})
    
    return config


def api_request(method, endpoint, config, data=None, params=None):
    """Make an API request to Akaunting."""
    url = f"{config['url'].rstrip('/')}/api/{endpoint.lstrip('/')}"
    auth = HTTPBasicAuth(config["email"], config["password"])
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    try:
        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            json=data,
            params=params,
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def cmd_ping(args, config):
    """Test API connection."""
    result = api_request("GET", "ping", config)
    if result.get("status") == "ok":
        print("✓ Connected to Akaunting")
        print(f"  Timestamp: {result.get('timestamp')}")
    else:
        print("✗ Connection failed")
        print(f"  Error: {result}")
    return result


def cmd_accounts(args, config):
    """List bank accounts."""
    result = api_request("GET", "accounts", config)
    
    if "data" in result:
        accounts = result["data"]
        if not accounts:
            print("No accounts found.")
            return result
            
        print(f"{'ID':<5} {'Name':<20} {'Type':<10} {'Balance':<15}")
        print("-" * 50)
        for acc in accounts:
            print(f"{acc['id']:<5} {acc['name']:<20} {acc['type']:<10} {acc['current_balance_formatted']:<15}")
    else:
        print(f"Error: {result}")
    
    return result


def cmd_categories(args, config):
    """List categories."""
    params = {}
    if args.type:
        params["search"] = f"type:{args.type}"
    
    result = api_request("GET", "categories", config, params=params)
    
    if "data" in result:
        categories = result["data"]
        if not categories:
            print("No categories found.")
            return result
            
        print(f"{'ID':<5} {'Name':<20} {'Type':<10}")
        print("-" * 35)
        for cat in categories:
            print(f"{cat['id']:<5} {cat['name']:<20} {cat['type']:<10}")
    else:
        print(f"Error: {result}")
    
    return result


def cmd_transactions(args, config):
    """List transactions."""
    params = {}
    if args.type:
        params["search"] = f"type:{args.type}"
    
    result = api_request("GET", "transactions", config, params=params)
    
    if "data" in result:
        txns = result["data"]
        if not txns:
            print("No transactions found.")
            return result
            
        print(f"{'ID':<5} {'Date':<12} {'Type':<8} {'Amount':<12} {'Description':<30}")
        print("-" * 70)
        for txn in txns:
            desc = (txn.get('description') or '')[:30]
            print(f"{txn['id']:<5} {txn['paid_at'][:10]:<12} {txn['type']:<8} {txn.get('amount_formatted', txn['amount']):<12} {desc:<30}")
    else:
        print(f"Error: {result}")
    
    return result


def cmd_items(args, config):
    """List items (products/services)."""
    result = api_request("GET", "items", config)
    
    if "data" in result:
        items = result["data"]
        if not items:
            print("No items found.")
            return result
            
        print(f"{'ID':<5} {'Name':<30} {'Price':<12}")
        print("-" * 50)
        for item in items:
            print(f"{item['id']:<5} {item['name']:<30} {item.get('sale_price_formatted', item.get('sale_price', 'N/A')):<12}")
    else:
        print(f"Error: {result}")
    
    return result


def cmd_income(args, config):
    """Create income transaction."""
    # Get category ID
    categories = api_request("GET", "categories", config, params={"search": f"name:{args.category}"})
    cat_id = None
    if "data" in categories and categories["data"]:
        cat_id = categories["data"][0]["id"]
    else:
        # Try getting all and finding by name
        categories = api_request("GET", "categories", config)
        if "data" in categories:
            for cat in categories["data"]:
                if cat["name"].lower() == args.category.lower() and cat["type"] in ["income", "other"]:
                    cat_id = cat["id"]
                    break
    
    if not cat_id:
        print(f"Error: Category '{args.category}' not found")
        return {"error": "Category not found"}
    
    # Get first account
    accounts = api_request("GET", "accounts", config)
    if "data" not in accounts or not accounts["data"]:
        print("Error: No accounts found")
        return {"error": "No accounts"}
    
    account_id = args.account or accounts["data"][0]["id"]
    
    # Count existing transactions for number
    txns = api_request("GET", "transactions", config)
    next_num = len(txns.get("data", [])) + 1
    
    data = {
        "type": "income",
        "number": f"INC-{next_num:04d}",
        "account_id": account_id,
        "category_id": cat_id,
        "amount": args.amount,
        "currency_code": "USD",
        "currency_rate": 1.0,
        "paid_at": args.date or "2026-02-07",
        "payment_method": "offline-payments.cash.1",
        "description": args.description or ""
    }
    
    result = api_request("POST", "transactions", config, data=data)
    
    if "data" in result:
        print(f"✓ Created income transaction #{result['data']['id']}")
        print(f"  Amount: ${args.amount}")
        print(f"  Category: {args.category}")
    else:
        print(f"Error creating transaction: {result}")
    
    return result


def cmd_expense(args, config):
    """Create expense transaction."""
    # Similar to income but type=expense
    categories = api_request("GET", "categories", config)
    cat_id = None
    if "data" in categories:
        for cat in categories["data"]:
            if cat["name"].lower() == args.category.lower() and cat["type"] in ["expense", "other"]:
                cat_id = cat["id"]
                break
    
    if not cat_id:
        print(f"Error: Category '{args.category}' not found")
        return {"error": "Category not found"}
    
    accounts = api_request("GET", "accounts", config)
    if "data" not in accounts or not accounts["data"]:
        print("Error: No accounts found")
        return {"error": "No accounts"}
    
    account_id = args.account or accounts["data"][0]["id"]
    
    txns = api_request("GET", "transactions", config)
    next_num = len(txns.get("data", [])) + 1
    
    data = {
        "type": "expense",
        "number": f"EXP-{next_num:04d}",
        "account_id": account_id,
        "category_id": cat_id,
        "amount": args.amount,
        "currency_code": "USD",
        "currency_rate": 1.0,
        "paid_at": args.date or "2026-02-07",
        "payment_method": "offline-payments.cash.1",
        "description": args.description or ""
    }
    
    result = api_request("POST", "transactions", config, data=data)
    
    if "data" in result:
        print(f"✓ Created expense transaction #{result['data']['id']}")
        print(f"  Amount: ${args.amount}")
        print(f"  Category: {args.category}")
    else:
        print(f"Error creating transaction: {result}")
    
    return result


def cmd_item(args, config):
    """Create an item (product/service)."""
    data = {
        "name": args.name,
        "sale_price": args.price,
        "purchase_price": args.cost or 0,
        "category_id": 5,  # General category
        "enabled": True
    }
    
    result = api_request("POST", "items", config, data=data)
    
    if "data" in result:
        print(f"✓ Created item #{result['data']['id']}: {args.name}")
        print(f"  Sale price: ${args.price}")
    else:
        print(f"Error creating item: {result}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Akaunting CLI")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ping
    subparsers.add_parser("ping", help="Test API connection")
    
    # accounts
    subparsers.add_parser("accounts", help="List accounts")
    
    # categories
    cat_parser = subparsers.add_parser("categories", help="List categories")
    cat_parser.add_argument("--type", choices=["income", "expense", "item", "other"])
    
    # transactions
    txn_parser = subparsers.add_parser("transactions", help="List transactions")
    txn_parser.add_argument("--type", choices=["income", "expense"])
    
    # items
    subparsers.add_parser("items", help="List items")
    
    # income
    inc_parser = subparsers.add_parser("income", help="Create income transaction")
    inc_parser.add_argument("--amount", type=float, required=True)
    inc_parser.add_argument("--category", default="Sales")
    inc_parser.add_argument("--description", default="")
    inc_parser.add_argument("--date", help="YYYY-MM-DD format")
    inc_parser.add_argument("--account", type=int, help="Account ID")
    
    # expense
    exp_parser = subparsers.add_parser("expense", help="Create expense transaction")
    exp_parser.add_argument("--amount", type=float, required=True)
    exp_parser.add_argument("--category", default="Other")
    exp_parser.add_argument("--description", default="")
    exp_parser.add_argument("--date", help="YYYY-MM-DD format")
    exp_parser.add_argument("--account", type=int, help="Account ID")
    
    # item
    item_parser = subparsers.add_parser("item", help="Create item")
    item_parser.add_argument("--name", required=True)
    item_parser.add_argument("--price", type=float, required=True)
    item_parser.add_argument("--cost", type=float, help="Purchase cost")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    config = load_config()
    
    if not all([config.get("url"), config.get("email"), config.get("password")]):
        print("Error: Missing configuration. Set AKAUNTING_URL, AKAUNTING_EMAIL, AKAUNTING_PASSWORD")
        print("       Or create ~/.config/akaunting/config.json")
        sys.exit(1)
    
    commands = {
        "ping": cmd_ping,
        "accounts": cmd_accounts,
        "categories": cmd_categories,
        "transactions": cmd_transactions,
        "items": cmd_items,
        "income": cmd_income,
        "expense": cmd_expense,
        "item": cmd_item,
    }
    
    result = commands[args.command](args, config)
    
    if args.json:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
