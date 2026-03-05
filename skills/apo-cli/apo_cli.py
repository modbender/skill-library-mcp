#!/usr/bin/env python3
"""apohealth.de CLI - Apotheken-Produktsuche und Warenkorb.

Rein Python, keine externen Dependencies (nur stdlib).

Nutzung:
    python3 apo_cli.py search "Aspirin"         # Produktsuche
    python3 apo_cli.py product <handle>         # Produktdetails
    python3 apo_cli.py categories               # Kategorien auflisten
    python3 apo_cli.py cart                     # Warenkorb anzeigen
    python3 apo_cli.py cart add <variant_id>    # Produkt hinzufügen
    python3 apo_cli.py cart checkout            # Browser öffnen
"""

import argparse
import json
import re
import ssl
import sys
import urllib.request
import urllib.error
import urllib.parse
import webbrowser
from http.cookiejar import CookieJar, Cookie
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Config & Paths
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
COOKIES_FILE = SCRIPT_DIR / "apo_cookies.json"
CART_FILE = SCRIPT_DIR / "apo_cart.json"

BASE_URL = "https://www.apohealth.de"
USER_AGENT = "apo-cli/1.0 (Python stdlib)"

# Bekannte Collections
COLLECTIONS = {
    "schmerzen": "schmerzen-1",
    "erkältung": "erkaltung-1",
    "verdauung": "verdauung-2",
    "kosmetik": "kosmetik-korperpflege",
    "corona": "covid-19",
    "naturmedizin": "naturmedizin-homoopathie",
    "nahrungsergänzung": "nutrition-1",
    "bestseller": "bestseller-1",
    "allergie": "allergie",
    "diabetes": "diabetes",
    "herz-kreislauf": "herz-kreislauf",
}


# ─────────────────────────────────────────────────────────────────────────────
# Cookie & Session Management
# ─────────────────────────────────────────────────────────────────────────────

def load_cookies() -> dict[str, str]:
    """Load cookies from JSON file."""
    if not COOKIES_FILE.exists():
        return {}
    
    try:
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies_raw = json.load(f)
        
        # Format: {name: value, ...}
        if isinstance(cookies_raw, dict):
            return cookies_raw
        
        # Puppeteer format: list of {name, value, ...}
        cookies = {}
        for c in cookies_raw:
            name = c.get("name")
            value = c.get("value")
            if name and value:
                cookies[name] = value
        return cookies
    except (json.JSONDecodeError, KeyError):
        return {}


def save_cookies(cookies: dict[str, str]):
    """Save cookies to JSON file."""
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


def format_cookie_header(cookies: dict[str, str]) -> str:
    """Format cookies as HTTP Cookie header."""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def load_cart_token() -> Optional[str]:
    """Load cart token from file."""
    if not CART_FILE.exists():
        return None
    try:
        with open(CART_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("token")
    except:
        return None


def save_cart_token(token: str):
    """Save cart token to file."""
    with open(CART_FILE, "w", encoding="utf-8") as f:
        json.dump({"token": token}, f)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP Client
# ─────────────────────────────────────────────────────────────────────────────

class ApoClient:
    """HTTP client for apohealth.de Shopify API."""
    
    def __init__(self):
        self.cookies = load_cookies()
        self.ctx = ssl.create_default_context()
        self.jar = CookieJar()
        
        # Load existing cookies into jar
        for name, value in self.cookies.items():
            cookie = Cookie(
                version=0, name=name, value=value,
                port=None, port_specified=False,
                domain="www.apohealth.de", domain_specified=True, domain_initial_dot=False,
                path="/", path_specified=True,
                secure=True, expires=None, discard=True,
                comment=None, comment_url=None, rest={}, rfc2109=False
            )
            self.jar.set_cookie(cookie)
        
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPSHandler(context=self.ctx),
        )
    
    def _headers(self, extra: Optional[dict] = None) -> dict:
        """Build request headers."""
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "de-DE,de;q=0.9",
        }
        if self.cookies:
            headers["Cookie"] = format_cookie_header(self.cookies)
        if extra:
            headers.update(extra)
        return headers
    
    def _save_response_cookies(self):
        """Save cookies from jar to file."""
        for cookie in self.jar:
            self.cookies[cookie.name] = cookie.value
        save_cookies(self.cookies)
    
    def get(self, path: str, params: Optional[dict] = None) -> tuple[int, dict | str]:
        """GET request, return (status, json_or_text)."""
        url = f"{BASE_URL}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        req = urllib.request.Request(url, headers=self._headers())
        
        try:
            with self.opener.open(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                self._save_response_cookies()
                
                try:
                    return resp.status, json.loads(body)
                except json.JSONDecodeError:
                    return resp.status, body
        except urllib.error.HTTPError as e:
            return e.code, {}
        except Exception as e:
            print(f"HTTP Error: {e}")
            return 0, {}
    
    def post(self, path: str, data: dict, content_type: str = "application/json") -> tuple[int, dict | str]:
        """POST request, return (status, json_or_text)."""
        url = f"{BASE_URL}{path}"
        
        if content_type == "application/json":
            body = json.dumps(data).encode("utf-8")
        else:
            body = urllib.parse.urlencode(data).encode("utf-8")
        
        headers = self._headers({
            "Content-Type": content_type,
            "Origin": BASE_URL,
        })
        
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        try:
            with self.opener.open(req, timeout=30) as resp:
                response_body = resp.read().decode("utf-8", errors="replace")
                self._save_response_cookies()
                
                try:
                    return resp.status, json.loads(response_body)
                except json.JSONDecodeError:
                    return resp.status, response_body
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8", errors="replace")
                return e.code, json.loads(error_body)
            except:
                return e.code, {}
        except Exception as e:
            print(f"HTTP Error: {e}")
            return 0, {}


# ─────────────────────────────────────────────────────────────────────────────
# API Functions
# ─────────────────────────────────────────────────────────────────────────────

def search_products(query: str, limit: int = 10) -> list[dict]:
    """Search products via Predictive Search API."""
    client = ApoClient()
    
    params = {
        "q": query,
        "resources[type]": "product",
        "resources[limit]": str(limit),
    }
    
    status, data = client.get("/search/suggest.json", params)
    
    if status != 200 or not isinstance(data, dict):
        return []
    
    products = data.get("resources", {}).get("results", {}).get("products", [])
    return products


def get_product(handle: str) -> Optional[dict]:
    """Get product details by handle."""
    client = ApoClient()
    
    status, data = client.get(f"/products/{handle}.json")
    
    if status != 200 or not isinstance(data, dict):
        return None
    
    return data.get("product")


def list_products(collection: Optional[str] = None, limit: int = 20, page: int = 1) -> list[dict]:
    """List products, optionally filtered by collection."""
    client = ApoClient()
    
    if collection:
        # Use collection handle
        collection_handle = COLLECTIONS.get(collection.lower(), collection)
        path = f"/collections/{collection_handle}/products.json"
    else:
        path = "/products.json"
    
    params = {"limit": str(limit), "page": str(page)}
    status, data = client.get(path, params)
    
    if status != 200 or not isinstance(data, dict):
        return []
    
    return data.get("products", [])


def get_cart() -> Optional[dict]:
    """Get current cart."""
    client = ApoClient()
    
    status, data = client.get("/cart.json")
    
    if status != 200 or not isinstance(data, dict):
        return None
    
    # Save cart token for later
    if "token" in data:
        save_cart_token(data["token"])
    
    return data


def add_to_cart(variant_id: str, quantity: int = 1) -> tuple[bool, str]:
    """Add item to cart."""
    client = ApoClient()
    
    data = {
        "items": [{"id": int(variant_id), "quantity": quantity}]
    }
    
    status, result = client.post("/cart/add.json", data)
    
    if status in (200, 201):
        # Get updated cart to save token
        get_cart()
        return True, f"Produkt hinzugefügt (Variante: {variant_id})"
    
    error = result.get("description", "Unbekannter Fehler") if isinstance(result, dict) else str(result)
    return False, error


def update_cart(updates: dict[str, int]) -> tuple[bool, str]:
    """Update cart quantities. Use quantity=0 to remove."""
    client = ApoClient()
    
    data = {"updates": updates}
    
    status, result = client.post("/cart/update.js", data)
    
    if status == 200:
        return True, "Warenkorb aktualisiert"
    
    return False, "Fehler beim Aktualisieren"


def clear_cart() -> tuple[bool, str]:
    """Clear the entire cart."""
    client = ApoClient()
    
    status, result = client.post("/cart/clear.js", {})
    
    if status == 200:
        return True, "Warenkorb geleert"
    
    return False, "Fehler beim Leeren"


def build_cart_permalink(items: list[dict]) -> str:
    """Build Shopify cart permalink URL.
    
    Format: /cart/{variant_id}:{quantity},{variant_id}:{quantity},...
    This creates a new cart in the browser with the specified items.
    """
    if not items:
        return f"{BASE_URL}/cart"
    
    parts = []
    for item in items:
        variant_id = item.get("variant_id") or item.get("id")
        quantity = item.get("quantity", 1)
        if variant_id:
            parts.append(f"{variant_id}:{quantity}")
    
    if not parts:
        return f"{BASE_URL}/cart"
    
    return f"{BASE_URL}/cart/{','.join(parts)}"


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def extract_pzn(product: dict) -> Optional[str]:
    """Extract PZN from product tags."""
    tags = product.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    
    for tag in tags:
        if tag.startswith("PZN:"):
            return tag.replace("PZN:", "").strip()
        # Also check SKU
    
    # Check variant SKU
    variants = product.get("variants", [])
    if variants:
        sku = variants[0].get("sku", "")
        # SKU format: J-04114918
        if sku.startswith("J-"):
            return sku[2:]
    
    return None


def format_price(price: str | float) -> str:
    """Format price for display."""
    if isinstance(price, str):
        try:
            price = float(price)
        except:
            return price
    return f"{price:.2f} €"


def get_availability(product: dict) -> str:
    """Get availability status."""
    variants = product.get("variants", [])
    if not variants:
        return "❓ Unbekannt"
    
    available = variants[0].get("available", False)
    return "✅ Verfügbar" if available else "❌ Nicht verfügbar"


def get_discount(product: dict) -> Optional[str]:
    """Calculate discount percentage if applicable."""
    variants = product.get("variants", [])
    if not variants:
        return None
    
    variant = variants[0]
    price = float(variant.get("price", 0))
    compare = variant.get("compare_at_price")
    
    if compare:
        compare = float(compare)
        if compare > price:
            discount = ((compare - price) / compare) * 100
            return f"-{discount:.0f}%"
    
    return None


# ─────────────────────────────────────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_search(args):
    """Search for products."""
    query = args.query
    limit = getattr(args, 'limit', 10)
    
    print()
    print(f"🔍 Suche: '{query}'")
    print("─" * 50)
    
    results = search_products(query, limit)
    
    if not results:
        print("Keine Produkte gefunden.")
        print()
        return
    
    print(f"Gefunden: {len(results)} Produkte")
    print()
    
    for i, p in enumerate(results, 1):
        title = p.get("title", "Unbekannt")
        price = p.get("price", "?")
        compare = p.get("compare_at_price_max")
        available = p.get("available", False)
        handle = p.get("handle", "")
        vendor = p.get("vendor", "")
        ptype = p.get("type", "")
        
        # Format price
        price_str = format_price(price)
        if compare and float(compare) > float(price):
            price_str += f" (statt {format_price(compare)})"
        
        # Status
        status = "✅" if available else "❌"
        
        print(f"  {i:2}. {status} {title}")
        if vendor:
            print(f"      Marke: {vendor}")
        print(f"      Preis: {price_str}")
        if ptype:
            print(f"      Typ: {ptype}")
        print(f"      → apo product {handle}")
        print()


def cmd_product(args):
    """Show product details."""
    handle = args.handle
    
    print()
    print(f"📦 Lade Produkt: {handle}")
    
    product = get_product(handle)
    
    if not product:
        print("❌ Produkt nicht gefunden.")
        print()
        return
    
    title = product.get("title", "Unbekannt")
    vendor = product.get("vendor", "")
    ptype = product.get("product_type", "")
    description = product.get("body_html", "")
    tags = product.get("tags", [])
    variants = product.get("variants", [])
    
    # Clean description
    description = re.sub(r'<[^>]+>', '', description)
    description = description.replace("&nbsp;", " ").strip()
    if len(description) > 300:
        description = description[:300] + "..."
    
    # Extract PZN
    pzn = extract_pzn(product)
    
    # Header
    print()
    print("╔" + "═" * 58 + "╗")
    print(f"║  {title[:54]:<54}  ║")
    print("╠" + "═" * 58 + "╣")
    
    info_parts = []
    if vendor:
        info_parts.append(f"🏭 {vendor}")
    if pzn:
        info_parts.append(f"📋 PZN: {pzn}")
    
    if info_parts:
        info_str = "  │  ".join(info_parts)
        print(f"║  {info_str:<54}  ║")
    
    if ptype:
        print(f"║  📁 {ptype:<52}  ║")
    
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Variants (Preise)
    print("💰 PREISE & VARIANTEN")
    print("─" * 40)
    
    for v in variants:
        v_title = v.get("title", "Standard")
        v_price = format_price(v.get("price", "0"))
        v_compare = v.get("compare_at_price")
        v_available = v.get("available", False)
        v_id = v.get("id", "")
        v_sku = v.get("sku", "")
        
        status = "✅" if v_available else "❌"
        
        # Price display
        if v_compare and float(v_compare) > float(v.get("price", 0)):
            discount = get_discount({"variants": [v]})
            price_display = f"{v_price} (statt {format_price(v_compare)}) {discount}"
        else:
            price_display = v_price
        
        if v_title != "Default Title":
            print(f"  {status} {v_title}: {price_display}")
        else:
            print(f"  {status} {price_display}")
        
        print(f"      Variante-ID: {v_id}")
        if v_sku:
            print(f"      SKU: {v_sku}")
        print()
    
    # Description
    if description:
        print("📝 BESCHREIBUNG")
        print("─" * 40)
        # Word wrap
        words = description.split()
        lines = []
        current = []
        for word in words:
            if len(' '.join(current + [word])) > 55:
                lines.append(' '.join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(' '.join(current))
        
        for line in lines:
            print(f"  {line}")
        print()
    
    # Tags
    relevant_tags = []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    for tag in tags:
        if any(x in tag for x in ["Darreichungsform", "Hersteller", "Marke", "Packungsgröße"]):
            relevant_tags.append(tag)
    
    if relevant_tags:
        print("🏷️  EIGENSCHAFTEN")
        print("─" * 40)
        for tag in relevant_tags[:5]:
            parts = tag.split("_", 1)
            if len(parts) == 2:
                print(f"  • {parts[0]}: {parts[1]}")
            else:
                print(f"  • {tag}")
        print()
    
    # Action hints
    print("🛒 ZUM WARENKORB HINZUFÜGEN:")
    if variants:
        v_id = variants[0].get("id", "")
        print(f"   apo cart add {v_id}")
    print()
    print(f"🔗 {BASE_URL}/products/{handle}")
    print()


def cmd_categories(args):
    """List available categories/collections."""
    print()
    print("📂 Verfügbare Kategorien")
    print("─" * 40)
    print()
    
    for name, handle in sorted(COLLECTIONS.items()):
        print(f"  • {name:<20} → {handle}")
    
    print()
    print("Verwendung:")
    print("  apo list --category schmerzen")
    print("  apo list --category bestseller --limit 10")
    print()


def cmd_list(args):
    """List products, optionally filtered by category."""
    category = getattr(args, 'category', None)
    limit = getattr(args, 'limit', 20)
    page = getattr(args, 'page', 1)
    
    print()
    if category:
        print(f"📦 Produkte in Kategorie: {category}")
    else:
        print("📦 Alle Produkte")
    print("─" * 50)
    
    products = list_products(category, limit, page)
    
    if not products:
        print("Keine Produkte gefunden.")
        print()
        return
    
    print(f"Zeige: {len(products)} Produkte (Seite {page})")
    print()
    
    for i, p in enumerate(products, 1):
        title = p.get("title", "Unbekannt")
        handle = p.get("handle", "")
        vendor = p.get("vendor", "")
        
        variants = p.get("variants", [])
        if variants:
            price = format_price(variants[0].get("price", "0"))
            available = variants[0].get("available", False)
        else:
            price = "?"
            available = False
        
        status = "✅" if available else "❌"
        pzn = extract_pzn(p)
        pzn_str = f" [PZN: {pzn}]" if pzn else ""
        
        print(f"  {i:2}. {status} {title}{pzn_str}")
        if vendor:
            print(f"      {vendor} • {price}")
        else:
            print(f"      {price}")
        print(f"      → apo product {handle}")
        print()
    
    if len(products) >= limit:
        print(f"Mehr laden: apo list --page {page + 1}")
        print()


def cmd_cart_show(args):
    """Show current cart."""
    print()
    print("🛒 WARENKORB")
    print("─" * 50)
    
    cart = get_cart()
    
    if not cart:
        print("❌ Konnte Warenkorb nicht laden.")
        print()
        return
    
    items = cart.get("items", [])
    total = cart.get("total_price", 0) / 100  # Shopify returns cents
    item_count = cart.get("item_count", 0)
    currency = cart.get("currency", "EUR")
    
    if not items:
        print("Der Warenkorb ist leer.")
        print()
        print("Produkt hinzufügen:")
        print("  apo search 'Aspirin'")
        print("  apo cart add <variant_id>")
        print()
        return
    
    print(f"Artikel: {item_count}")
    print()
    
    for item in items:
        title = item.get("title", "Unbekannt")
        variant_title = item.get("variant_title", "")
        quantity = item.get("quantity", 1)
        price = item.get("price", 0) / 100
        line_price = item.get("line_price", 0) / 100
        variant_id = item.get("variant_id", "")
        handle = item.get("handle", "")
        
        # Display variant info
        if variant_title and variant_title != "Default Title":
            title_display = f"{title} ({variant_title})"
        else:
            title_display = title
        
        print(f"  • {title_display}")
        print(f"    {quantity}x {price:.2f} € = {line_price:.2f} €")
        print(f"    Variante: {variant_id}")
        print()
    
    print("─" * 50)
    print(f"  GESAMT: {total:.2f} {currency}")
    print()
    print("Aktionen:")
    print("  apo cart checkout    → Zur Kasse (Browser)")
    print("  apo cart clear       → Warenkorb leeren")
    print("  apo cart remove <id> → Produkt entfernen")
    print()


def cmd_cart_add(args):
    """Add product to cart."""
    variant_id = args.variant_id
    quantity = getattr(args, 'qty', 1)
    
    print()
    print(f"🛒 Füge hinzu: Variante {variant_id} (Anzahl: {quantity})")
    
    success, message = add_to_cart(variant_id, quantity)
    
    if success:
        print(f"✅ {message}")
        print()
        # Show updated cart
        cmd_cart_show(args)
    else:
        print(f"❌ Fehler: {message}")
        print()


def cmd_cart_remove(args):
    """Remove product from cart."""
    variant_id = args.variant_id
    
    print()
    print(f"🗑️  Entferne: Variante {variant_id}")
    
    success, message = update_cart({variant_id: 0})
    
    if success:
        print(f"✅ Produkt entfernt")
        print()
        cmd_cart_show(args)
    else:
        print(f"❌ Fehler: {message}")
        print()


def cmd_cart_clear(args):
    """Clear the cart."""
    print()
    print("🗑️  Leere Warenkorb...")
    
    success, message = clear_cart()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    print()


def cmd_cart_checkout(args):
    """Open checkout in browser."""
    print()
    print("🛒 Öffne Checkout im Browser...")
    
    # First check if cart has items
    cart = get_cart()
    if not cart or not cart.get("items"):
        print("⚠️  Der Warenkorb ist leer!")
        print()
        return
    
    items = cart.get("items", [])
    
    # Build cart permalink - this creates a new cart in browser with our items
    checkout_url = build_cart_permalink(items)
    
    print(f"\n   Artikel: {len(items)}")
    print(f"   URL: {checkout_url}")
    print()
    
    try:
        webbrowser.open(checkout_url)
        print("✅ Browser geöffnet mit deinen Artikeln!")
        print("   Der Browser hat jetzt einen neuen Warenkorb mit deinen Produkten.")
    except Exception as e:
        print(f"❌ Konnte Browser nicht öffnen: {e}")
        print(f"   Bitte manuell öffnen: {checkout_url}")
    print()


def cmd_status(args):
    """Show CLI status."""
    print()
    print("📊 APO-CLI Status")
    print("─" * 40)
    
    # Cookies
    cookies = load_cookies()
    print(f"🍪 Cookies: {len(cookies)} gespeichert")
    
    # Cart token
    token = load_cart_token()
    if token:
        print(f"🛒 Cart-Token: {token[:20]}...")
    else:
        print("🛒 Cart-Token: (keiner)")
    
    # Try to get cart
    cart = get_cart()
    if cart:
        items = cart.get("item_count", 0)
        total = cart.get("total_price", 0) / 100
        print(f"📦 Warenkorb: {items} Artikel ({total:.2f} €)")
    
    print()
    print(f"📁 Cookies: {COOKIES_FILE}")
    print(f"📁 Cart:    {CART_FILE}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI Parser
# ─────────────────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        description="💊 apohealth.de CLI - Apotheken-Produkte suchen & bestellen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  apo search "Ibuprofen"                Produktsuche
  apo search "04114918"                 PZN-Suche
  apo product aspirin-complex-...       Produktdetails
  apo list --category schmerzen         Kategorie durchsuchen
  apo cart add 32907653677119           Zum Warenkorb hinzufügen
  apo cart                              Warenkorb anzeigen
  apo cart checkout                     Checkout im Browser öffnen
"""
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    # search command
    search_parser = sub.add_parser("search", help="Produkte suchen")
    search_parser.add_argument("query", help="Suchbegriff (Name, PZN, Marke)")
    search_parser.add_argument("-n", "--limit", type=int, default=10, help="Anzahl Ergebnisse (default: 10)")
    search_parser.set_defaults(func=cmd_search)
    
    # product command
    product_parser = sub.add_parser("product", help="Produktdetails anzeigen")
    product_parser.add_argument("handle", help="Produkt-Handle (aus URL oder Suche)")
    product_parser.set_defaults(func=cmd_product)
    
    # list command
    list_parser = sub.add_parser("list", help="Produkte auflisten")
    list_parser.add_argument("-c", "--category", help="Kategorie-Filter")
    list_parser.add_argument("-n", "--limit", type=int, default=20, help="Anzahl (default: 20)")
    list_parser.add_argument("-p", "--page", type=int, default=1, help="Seite (default: 1)")
    list_parser.set_defaults(func=cmd_list)
    
    # categories command
    categories_parser = sub.add_parser("categories", help="Kategorien anzeigen")
    categories_parser.set_defaults(func=cmd_categories)
    
    # cart command with subcommands
    cart_parser = sub.add_parser("cart", help="Warenkorb verwalten")
    cart_sub = cart_parser.add_subparsers(dest="cart_action")
    
    # cart (no subcommand) = show
    cart_parser.set_defaults(func=cmd_cart_show)
    
    # cart add
    cart_add = cart_sub.add_parser("add", help="Produkt hinzufügen")
    cart_add.add_argument("variant_id", help="Varianten-ID des Produkts")
    cart_add.add_argument("--qty", type=int, default=1, help="Anzahl (default: 1)")
    cart_add.set_defaults(func=cmd_cart_add)
    
    # cart remove
    cart_remove = cart_sub.add_parser("remove", help="Produkt entfernen")
    cart_remove.add_argument("variant_id", help="Varianten-ID des Produkts")
    cart_remove.set_defaults(func=cmd_cart_remove)
    
    # cart clear
    cart_clear = cart_sub.add_parser("clear", help="Warenkorb leeren")
    cart_clear.set_defaults(func=cmd_cart_clear)
    
    # cart checkout
    cart_checkout = cart_sub.add_parser("checkout", help="Checkout im Browser öffnen")
    cart_checkout.set_defaults(func=cmd_cart_checkout)
    
    # status command
    status_parser = sub.add_parser("status", help="CLI-Status anzeigen")
    status_parser.set_defaults(func=cmd_status)
    
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
