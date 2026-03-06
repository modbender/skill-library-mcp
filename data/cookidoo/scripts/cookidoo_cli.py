#!/usr/bin/env python3
"""Cookidoo CLI - Access Thermomix recipes and shopping lists."""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path

try:
    from cookidoo_api import Cookidoo
except ImportError:
    print("Error: cookidoo-api not installed. Run: pip install cookidoo-api")
    sys.exit(1)


def get_credentials():
    """Get credentials from environment or config file."""
    email = os.environ.get("COOKIDOO_EMAIL")
    password = os.environ.get("COOKIDOO_PASSWORD")
    
    if not email or not password:
        env_file = Path.home() / ".config/atlas/cookidoo.env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("COOKIDOO_EMAIL="):
                    email = line.split("=", 1)[1].strip()
                elif line.startswith("COOKIDOO_PASSWORD="):
                    password = line.split("=", 1)[1].strip()
    
    if not email or not password:
        print("Error: COOKIDOO_EMAIL and COOKIDOO_PASSWORD required")
        print("Set in environment or ~/.config/atlas/cookidoo.env")
        sys.exit(1)
    
    return email, password


async def main():
    parser = argparse.ArgumentParser(description="Cookidoo CLI")
    parser.add_argument("command", choices=["recipes", "plan", "shopping", "search", "recipe", "info"])
    parser.add_argument("query", nargs="?", help="Search query or recipe ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")
    args = parser.parse_args()
    
    email, password = get_credentials()
    
    async with Cookidoo(email, password) as cookidoo:
        await cookidoo.login()
        
        if args.command == "info":
            info = await cookidoo.get_user_info()
            if args.json:
                print(json.dumps(info, indent=2, default=str))
            else:
                print(f"User: {info.get('email', 'N/A')}")
                print(f"Country: {info.get('country', 'N/A')}")
        
        elif args.command == "recipes":
            recipes = await cookidoo.get_owned_recipes()
            if args.json:
                print(json.dumps(recipes[:args.limit], indent=2, default=str))
            else:
                print(f"📖 Saved Recipes ({len(recipes)} total):\n")
                for r in recipes[:args.limit]:
                    name = r.get("name", r.get("title", "Unknown"))
                    rid = r.get("id", "?")
                    print(f"  • {name} (ID: {rid})")
        
        elif args.command == "plan":
            plan = await cookidoo.get_active_subscription()
            # Note: actual weekly plan endpoint may differ
            if args.json:
                print(json.dumps(plan, indent=2, default=str))
            else:
                print("📅 Weekly Plan:")
                print(json.dumps(plan, indent=2, default=str))
        
        elif args.command == "shopping":
            shopping = await cookidoo.get_shopping_list()
            if args.json:
                print(json.dumps(shopping, indent=2, default=str))
            else:
                print("🛒 Cookidoo Shopping List:\n")
                for item in shopping:
                    name = item.get("name", item.get("ingredient", "?"))
                    amount = item.get("amount", "")
                    print(f"  • {name} {amount}".strip())
        
        elif args.command == "search":
            if not args.query:
                print("Error: search requires a query")
                sys.exit(1)
            results = await cookidoo.search_recipes(args.query)
            if args.json:
                print(json.dumps(results[:args.limit], indent=2, default=str))
            else:
                print(f"🔍 Search results for '{args.query}':\n")
                for r in results[:args.limit]:
                    name = r.get("name", r.get("title", "Unknown"))
                    rid = r.get("id", "?")
                    print(f"  • {name} (ID: {rid})")
        
        elif args.command == "recipe":
            if not args.query:
                print("Error: recipe command requires a recipe ID")
                sys.exit(1)
            recipe = await cookidoo.get_recipe(args.query)
            if args.json:
                print(json.dumps(recipe, indent=2, default=str))
            else:
                print(f"📖 {recipe.get('name', recipe.get('title', 'Recipe'))}\n")
                print("Ingredients:")
                for ing in recipe.get("ingredients", []):
                    print(f"  • {ing}")
                print("\nSteps:")
                for i, step in enumerate(recipe.get("steps", []), 1):
                    print(f"  {i}. {step}")


if __name__ == "__main__":
    asyncio.run(main())
