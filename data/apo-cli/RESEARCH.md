# apohealth.de - API Research Report

**Erstellt:** 2026-02-05  
**Scout Agent:** Analyse für apo-cli Projekt

---

## 1. Technologie-Stack

### Plattform
- **E-Commerce System:** Shopify
- **Shop ID:** 9522380863
- **Myshopify Domain:** `apohealth.myshopify.com`
- **Theme:** Empire 9.0.1 (angepasst: "Empire 16.07.2024 (Geolizr cleanup)")
- **CDN:** Cloudflare + Shopify CDN

### Authentifizierung
- **Storefront API Token:** `965d12c54028db404dcedb3f9e9c4b03` (öffentlich im HTML)
- **Customer Accounts:** Shopify New Customer Accounts (`account.apohealth.de`)
- **Sessions:** Cookie-basiert (`_shopify_essential`, `secure_customer_sig`)

### Zusätzliche Dienste
- Google Tag Manager (GTM-K97KS2G)
- Microsoft Clarity (Analytics)
- Trustpilot Reviews
- Pandectes GDPR Compliance
- hCaptcha für Formulare

---

## 2. Verfügbare API-Endpoints

### 2.1 Products API (öffentlich, keine Auth nötig)

#### Alle Produkte auflisten
```
GET https://www.apohealth.de/products.json
GET https://www.apohealth.de/products.json?limit=50&page=2
```
**Response-Felder:**
```json
{
  "products": [{
    "id": 4748985237567,
    "title": "ASPIRIN Complex Granulat, 20 St. Beutel",
    "handle": "aspirin-complex-granulat-20-st-beutel-4114918",
    "body_html": "...",
    "vendor": "ASPIRIN",
    "product_type": "apothekenpflichtiges Arzneimittel",
    "tags": ["OTC", "PZN: 04114918", ...],
    "variants": [{
      "id": 32907653677119,
      "price": "16.70",
      "sku": "J-04114918",
      "compare_at_price": "19.49",
      "available": true
    }],
    "images": [...]
  }]
}
```

#### Einzelnes Produkt
```
GET https://www.apohealth.de/products/{handle}.json

# Beispiel:
GET https://www.apohealth.de/products/aspirin-complex-granulat-20-st-beutel-4114918.json
```

### 2.2 Search API (Predictive Search)

#### Produktsuche
```
GET https://www.apohealth.de/search/suggest.json?q={query}&resources[type]=product&resources[limit]=10
```
**Response:**
```json
{
  "resources": {
    "results": {
      "products": [{
        "id": 4748985237567,
        "title": "ASPIRIN Complex Granulat, 20 St. Beutel",
        "handle": "...",
        "price": "16.70",
        "compare_at_price_max": "19.49",
        "image": "https://cdn.shopify.com/...",
        "url": "/products/...",
        "available": true,
        "vendor": "ASPIRIN",
        "type": "apothekenpflichtiges Arzneimittel"
      }]
    }
  }
}
```

### 2.3 Collections API (Kategorien)

#### Collection-Produkte
```
GET https://www.apohealth.de/collections/{handle}/products.json?limit=50

# Beispiele:
GET https://www.apohealth.de/collections/schmerzen-1/products.json
GET https://www.apohealth.de/collections/erkaltung-1/products.json
GET https://www.apohealth.de/collections/bestseller-1/products.json
```

#### Bekannte Collection-Handles
- `schmerzen-1` - Schmerzmittel
- `erkaltung-1` - Erkältungsprodukte
- `verdauung-2` - Verdauung
- `kosmetik-korperpflege` - Kosmetik
- `covid-19` - Desinfektion & Schutz
- `naturmedizin-homoopathie` - Naturheilkunde
- `nutrition-1` - Nahrungsergänzung
- `bestseller-1` - Bestseller

### 2.4 Cart API (Session-basiert)

#### Warenkorb anzeigen
```
GET https://www.apohealth.de/cart.json
```
**Response:**
```json
{
  "token": "27b938ef0a8211f55e000fcff62bb6c9",
  "note": null,
  "item_count": 0,
  "items": [],
  "total_price": 0,
  "currency": "EUR",
  "requires_shipping": false
}
```

#### Produkt hinzufügen
```
POST https://www.apohealth.de/cart/add.js
Content-Type: application/x-www-form-urlencoded

id={variant_id}&quantity=1
```

Alternative (JSON):
```
POST https://www.apohealth.de/cart/add.json
Content-Type: application/json

{"items": [{"id": 32907653677119, "quantity": 1}]}
```

#### Warenkorb aktualisieren
```
POST https://www.apohealth.de/cart/update.js
Content-Type: application/json

{"updates": {"32907653677119": 2}}
```

#### Warenkorb leeren
```
POST https://www.apohealth.de/cart/clear.js
```

### 2.5 Storefront GraphQL API

```
POST https://www.apohealth.de/api/2024-01/graphql.json
Headers:
  Content-Type: application/json
  X-Shopify-Storefront-Access-Token: 965d12c54028db404dcedb3f9e9c4b03
```

**Beispiel-Query:**
```graphql
{
  shop {
    name
    description
  }
  products(first: 10) {
    edges {
      node {
        id
        title
        handle
        priceRange {
          minVariantPrice {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
```

### 2.6 Customer Account API

**Login-Redirect:**
```
GET https://www.apohealth.de/account/login
→ Redirect zu https://account.apohealth.de
```

**Hinweis:** Customer Authentication nutzt Shopify's New Customer Accounts mit OAuth-ähnlichem Flow. Für CLI-Login wäre eine headless Browser-Automation nötig.

---

## 3. Datenstrukturen

### Produkt-Identifikatoren
- **Product ID:** Shopify-interne numerische ID (z.B. `4748985237567`)
- **Variant ID:** Für Cart-Operationen (z.B. `32907653677119`)
- **Handle:** URL-freundlicher Slug (z.B. `aspirin-complex-granulat-20-st-beutel-4114918`)
- **SKU:** Shop-interne Artikelnummer (z.B. `J-04114918`)
- **PZN:** Pharmazentralnummer in Tags (z.B. `PZN: 04114918`)

### Preise
- Alle Preise in **EUR** als String mit Punkt-Dezimaltrenner
- `price`: Aktueller Verkaufspreis
- `compare_at_price`: UVP/Streichpreis

### Tags (für Filterung relevant)
- `Artikelart_*` - Produktkategorie
- `Darreichungsform_*` - Tabletten, Lösung, etc.
- `Hersteller_*` - Herstellername
- `Marke_*` - Marke
- `Packungsgröße_*` - Packungsgröße
- `OTC` - Ohne Rezept erhältlich
- `Gefahrstoff_False/True` - Gefahrstoff-Kennzeichnung

---

## 4. Empfohlene CLI-Features

### Phase 1: Read-Only (ohne Auth)
1. **`apo search <query>`** - Produktsuche via Predictive Search API
2. **`apo product <handle|pzn>`** - Produktdetails anzeigen
3. **`apo list [--category <name>] [--limit <n>]`** - Produkte auflisten
4. **`apo categories`** - Collections anzeigen

### Phase 2: Cart Management (Session-basiert)
5. **`apo cart`** - Warenkorb anzeigen
6. **`apo cart add <product> [--qty <n>]`** - Produkt hinzufügen
7. **`apo cart remove <product>`** - Produkt entfernen
8. **`apo cart clear`** - Warenkorb leeren

### Phase 3: Advanced (optional)
9. **`apo price-watch <product>`** - Preisüberwachung
10. **`apo export [--format json|csv]`** - Produktdaten exportieren

### Nicht empfohlen für CLI
- **Checkout/Kauf:** Erfordert komplexe Session-Handling, Captcha, Zahlungsintegration
- **Customer Login:** OAuth-Flow zu komplex für CLI, besser Browser nutzen
- **Rezepteinlösung:** Erfordert authentifizierten Upload, nicht für CLI geeignet

---

## 5. Implementierungsnotizen

### HTTP Headers (empfohlen)
```
User-Agent: apo-cli/1.0
Accept: application/json
Accept-Language: de-DE
```

### Rate Limiting
Shopify-Standard: ~2 Requests/Sekunde bei öffentlichen APIs. Bei höherem Volumen GraphQL bevorzugen.

### Session-Handling für Cart
```javascript
// Cart-Token aus Cookie speichern
const cookies = response.headers['set-cookie'];
// cart Token ist in cart.json Response enthalten
const { token } = await fetch('/cart.json').then(r => r.json());
```

### PZN-Suche
PZN ist in Tags enthalten. Für direkte PZN-Suche:
```
GET /search/suggest.json?q=04114918&resources[type]=product
```

---

## 6. Beispiel-Implementierung (Node.js)

```javascript
const BASE_URL = 'https://www.apohealth.de';

// Produktsuche
async function searchProducts(query, limit = 5) {
  const url = `${BASE_URL}/search/suggest.json?q=${encodeURIComponent(query)}&resources[type]=product&resources[limit]=${limit}`;
  const res = await fetch(url);
  const data = await res.json();
  return data.resources.results.products;
}

// Produkt abrufen
async function getProduct(handle) {
  const res = await fetch(`${BASE_URL}/products/${handle}.json`);
  const data = await res.json();
  return data.product;
}

// Warenkorb abrufen
async function getCart() {
  const res = await fetch(`${BASE_URL}/cart.json`);
  return res.json();
}

// Zum Warenkorb hinzufügen
async function addToCart(variantId, quantity = 1) {
  const res = await fetch(`${BASE_URL}/cart/add.json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: [{ id: variantId, quantity }] })
  });
  return res.json();
}
```

---

## 7. Einschränkungen & Risiken

1. **Keine offizielle API:** Alle Endpoints sind undokumentiert und können sich ändern
2. **Rate Limiting:** Bei zu vielen Requests können IP-Sperren erfolgen
3. **Captcha:** Formulare (Login, Kontakt) sind durch hCaptcha geschützt
4. **Geo-Restrictions:** Shop nutzt Geolizr für Währungs-/Länderanpassung
5. **Rechtliches:** Scraping kann gegen ToS verstoßen - nur für persönlichen Gebrauch

---

## 8. Nächste Schritte

1. [ ] CLI-Grundstruktur mit Commander.js oder yargs erstellen
2. [ ] API-Client-Modul implementieren
3. [ ] Produktsuche implementieren
4. [ ] Cart-Management implementieren
5. [ ] Konfigurationsdatei für Einstellungen
6. [ ] Tests schreiben

---

*Report erstellt durch automatisierte API-Analyse. Alle Endpoints wurden am 2026-02-05 getestet.*
