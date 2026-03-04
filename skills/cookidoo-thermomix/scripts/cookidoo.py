#!/usr/bin/env python3
"""Cookidoo CLI — standalone wrapper for the Cookidoo (Thermomix) REST API.

No external dependencies — uses only Python stdlib (urllib, json).
Requires COOKIDOO_EMAIL and COOKIDOO_PASSWORD environment variables.

Usage:
  cookidoo.py login
  cookidoo.py user-info
  cookidoo.py subscription
  cookidoo.py recipe <recipe_id>
  cookidoo.py calendar [<date>]
  cookidoo.py calendar-add <date> <recipe_id> [<recipe_id> ...]
  cookidoo.py calendar-remove <date> <recipe_id>
  cookidoo.py shopping-list
  cookidoo.py shopping-add <recipe_id> [<recipe_id> ...]
  cookidoo.py shopping-remove <recipe_id> [<recipe_id> ...]
  cookidoo.py shopping-clear
  cookidoo.py additional-items
  cookidoo.py additional-add <item> [<item> ...]
  cookidoo.py additional-remove <item_id> [<item_id> ...]
  cookidoo.py collections
  cookidoo.py collection-add <name>
  cookidoo.py collection-remove <collection_id>
  cookidoo.py collection-add-recipe <collection_id> <recipe_id> [<recipe_id> ...]
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

# --- Constants (from reverse-engineered Android app API) ---
CLIENT_ID = "kupferwerk-client-nwot"
CLIENT_SECRET = "Ls50ON1woySqs1dCdJge"
AUTH_HEADER = "Basic a3VwZmVyd2Vyay1jbGllbnQtbndvdDpMczUwT04xd295U3FzMWRDZEpnZQ=="

# Country code mapping for API endpoint
COUNTRY_CODES = {
    "ch": "ch", "de": "de", "at": "at", "fr": "fr", "it": "it",
    "es": "es", "pt": "pt", "pl": "pl", "gb": "gb", "us": "xp",
    "au": "xp", "international": "xp",
}

# Language mapping (country -> default language)
DEFAULT_LANGUAGES = {
    "ch": "de-CH", "de": "de-DE", "at": "de-AT", "fr": "fr-FR",
    "it": "it-IT", "es": "es-ES", "pt": "pt-PT", "pl": "pl-PL",
    "gb": "en-GB", "us": "en-US", "au": "en-AU",
}


def get_config():
    email = os.environ.get("COOKIDOO_EMAIL")
    password = os.environ.get("COOKIDOO_PASSWORD")
    if not email or not password:
        print("Error: COOKIDOO_EMAIL and COOKIDOO_PASSWORD must be set.", file=sys.stderr)
        sys.exit(1)
    country = os.environ.get("COOKIDOO_COUNTRY", "ch").lower()
    language = os.environ.get("COOKIDOO_LANGUAGE", DEFAULT_LANGUAGES.get(country, "de-CH"))
    cc = COUNTRY_CODES.get(country, country)
    base_url = f"https://{cc}.tmmobile.vorwerk-digital.com"
    return email, password, base_url, language


def api_request(url, method="GET", data=None, headers=None, json_data=None):
    """Make an HTTP request and return parsed JSON."""
    if json_data is not None:
        data = json.dumps(json_data).encode("utf-8")
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
    elif data is not None and isinstance(data, str):
        data = data.encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            if body:
                return json.loads(body)
            return None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def login(base_url, email, password):
    """Authenticate and return access token."""
    token_url = f"{base_url}/ciam/auth/token"
    form_data = urllib.parse.urlencode({
        "grant_type": "password",
        "username": email,
        "password": password,
    })
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": AUTH_HEADER,
    }
    result = api_request(token_url, method="POST", data=form_data, headers=headers)
    return result["access_token"], result["token_type"]


def api_headers(token, token_type="Bearer", accept="application/json"):
    return {
        "Accept": accept,
        "Authorization": f"{token_type} {token}",
    }


def pp(obj):
    """Pretty-print JSON."""
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def parse_date(s):
    if not s:
        return datetime.now().strftime("%Y-%m-%d")
    return s


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    email, password, base_url, lang = get_config()
    token, token_type = login(base_url, email, password)
    hdrs = api_headers(token, token_type)

    if cmd == "login":
        print("✅ Login successful.")
        result = api_request(f"{base_url}/community/profile", headers=hdrs)
        pp(result)

    elif cmd == "user-info":
        result = api_request(f"{base_url}/community/profile", headers=hdrs)
        pp(result)

    elif cmd == "subscription":
        result = api_request(f"{base_url}/ownership/subscriptions", headers=hdrs)
        active = [s for s in (result or []) if s.get("active")]
        if active:
            pp(active[0])
        else:
            print("No active subscription.")

    elif cmd == "recipe":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py recipe <recipe_id>", file=sys.stderr)
            sys.exit(1)
        rid = sys.argv[2]
        result = api_request(f"{base_url}/recipes/recipe/{lang}/{rid}", headers=hdrs)
        pp(result)

    elif cmd == "calendar":
        day = parse_date(sys.argv[2] if len(sys.argv) > 2 else None)
        result = api_request(f"{base_url}/planning/{lang}/api/my-week/{day}", headers=hdrs)
        pp(result)

    elif cmd == "calendar-add":
        if len(sys.argv) < 4:
            print("Usage: cookidoo.py calendar-add <date> <recipe_id> [...]", file=sys.stderr)
            sys.exit(1)
        day = sys.argv[2]
        recipe_ids = sys.argv[3:]
        payload = {"date": day, "recipeIds": recipe_ids}
        result = api_request(f"{base_url}/planning/{lang}/api/my-day", method="POST",
                             json_data=payload, headers=hdrs)
        pp(result)
        print(f"✅ Added {len(recipe_ids)} recipe(s) to {day}.")

    elif cmd == "calendar-remove":
        if len(sys.argv) < 4:
            print("Usage: cookidoo.py calendar-remove <date> <recipe_id>", file=sys.stderr)
            sys.exit(1)
        day, rid = sys.argv[2], sys.argv[3]
        api_request(f"{base_url}/planning/{lang}/api/my-day/{day}/recipes/{rid}",
                    method="DELETE", headers=hdrs)
        print(f"✅ Removed {rid} from {day}.")

    elif cmd == "shopping-list":
        result = api_request(f"{base_url}/shopping/{lang}", headers=hdrs)
        pp(result)

    elif cmd == "shopping-add":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py shopping-add <recipe_id> [...]", file=sys.stderr)
            sys.exit(1)
        recipe_ids = sys.argv[2:]
        payload = {"recipeIds": recipe_ids}
        result = api_request(f"{base_url}/shopping/{lang}/recipes/add", method="POST",
                             json_data=payload, headers=hdrs)
        pp(result)
        print(f"✅ Added ingredients for {len(recipe_ids)} recipe(s).")

    elif cmd == "shopping-remove":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py shopping-remove <recipe_id> [...]", file=sys.stderr)
            sys.exit(1)
        recipe_ids = sys.argv[2:]
        payload = {"recipeIds": recipe_ids}
        result = api_request(f"{base_url}/shopping/{lang}/recipes/remove", method="POST",
                             json_data=payload, headers=hdrs)
        pp(result)
        print(f"✅ Removed ingredients for {len(recipe_ids)} recipe(s).")

    elif cmd == "shopping-clear":
        # Clear = remove all recipes + additional items
        data = api_request(f"{base_url}/shopping/{lang}", headers=hdrs)
        if data:
            # Try to extract recipe IDs and remove them
            recipes = data.get("recipes", [])
            if recipes:
                rids = [r.get("id") or r.get("recipeId") for r in recipes if r.get("id") or r.get("recipeId")]
                if rids:
                    api_request(f"{base_url}/shopping/{lang}/recipes/remove", method="POST",
                                json_data={"recipeIds": rids}, headers=hdrs)
            additional = data.get("additionalItems", [])
            if additional:
                aids = [a["id"] for a in additional if "id" in a]
                if aids:
                    api_request(f"{base_url}/shopping/{lang}/additional-items/remove", method="POST",
                                json_data={"additionalItemIds": aids}, headers=hdrs)
        print("✅ Shopping list cleared.")

    elif cmd == "additional-items":
        result = api_request(f"{base_url}/shopping/{lang}", headers=hdrs)
        items = result.get("additionalItems", []) if result else []
        pp(items)

    elif cmd == "additional-add":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py additional-add <item> [...]", file=sys.stderr)
            sys.exit(1)
        items = sys.argv[2:]
        payload = {"items": items}
        result = api_request(f"{base_url}/shopping/{lang}/additional-items/add", method="POST",
                             json_data=payload, headers=hdrs)
        pp(result)
        print(f"✅ Added {len(items)} item(s).")

    elif cmd == "additional-remove":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py additional-remove <item_id> [...]", file=sys.stderr)
            sys.exit(1)
        item_ids = sys.argv[2:]
        payload = {"additionalItemIds": item_ids}
        api_request(f"{base_url}/shopping/{lang}/additional-items/remove", method="POST",
                    json_data=payload, headers=hdrs)
        print(f"✅ Removed {len(item_ids)} item(s).")

    elif cmd == "collections":
        custom_hdrs = {**hdrs, "Accept": "application/vnd.vorwerk.organize.custom-list.mobile+json"}
        custom = api_request(f"{base_url}/organize/{lang}/api/custom-list", headers=custom_hdrs)
        managed_hdrs = {**hdrs, "Accept": "application/vnd.vorwerk.organize.managed-list.mobile+json"}
        managed = api_request(f"{base_url}/organize/{lang}/api/managed-list", headers=managed_hdrs)
        print("=== Custom Collections ===")
        pp(custom)
        print("\n=== Managed Collections ===")
        pp(managed)

    elif cmd == "collection-add":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py collection-add <name>", file=sys.stderr)
            sys.exit(1)
        name = sys.argv[2]
        custom_hdrs = {**hdrs, "Accept": "application/vnd.vorwerk.organize.custom-list.mobile+json"}
        result = api_request(f"{base_url}/organize/{lang}/api/custom-list", method="POST",
                             json_data={"name": name}, headers=custom_hdrs)
        pp(result)
        print(f"✅ Collection '{name}' created.")

    elif cmd == "collection-remove":
        if len(sys.argv) < 3:
            print("Usage: cookidoo.py collection-remove <collection_id>", file=sys.stderr)
            sys.exit(1)
        cid = sys.argv[2]
        api_request(f"{base_url}/organize/{lang}/api/custom-list/{cid}", method="DELETE", headers=hdrs)
        print(f"✅ Collection {cid} removed.")

    elif cmd == "collection-add-recipe":
        if len(sys.argv) < 4:
            print("Usage: cookidoo.py collection-add-recipe <collection_id> <recipe_id> [...]", file=sys.stderr)
            sys.exit(1)
        cid = sys.argv[2]
        recipe_ids = sys.argv[3:]
        custom_hdrs = {**hdrs, "Accept": "application/vnd.vorwerk.organize.custom-list.mobile+json"}
        result = api_request(f"{base_url}/organize/{lang}/api/custom-list/{cid}", method="PUT",
                             json_data={"recipeIds": recipe_ids}, headers=custom_hdrs)
        pp(result)
        print(f"✅ Added {len(recipe_ids)} recipe(s) to collection.")

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
