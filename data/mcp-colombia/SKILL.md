---
name: mcp-colombia
description: "MCP Colombia Hub — aggregates Colombian services via MCP protocol. Soulprint identity verification integrated — verify Colombian users before sensitive operations. Use when: searching MercadoLibre products, finding hotels via Booking.com (real-time prices), searching flights (Avianca/LATAM/Skyscanner), applying to jobs with real listings from El Empleo/Computrabajo/LinkedIn, comparing CDTs, simulating credits/loans, or comparing bank accounts in Colombia. Requires an MCP-compatible client (Claude Desktop, OpenClaw, etc.)."
homepage: https://www.npmjs.com/package/mcp-colombia-hub
metadata:
  {
    "openclaw":
      {
        "emoji": "🇨🇴",
        "requires": { "bins": ["node", "npx"] },
      },
  }
---

# MCP Colombia Hub

Aggregates Colombian services into a single MCP server — search products, find hotels and flights, compare financial products.

**npm:** https://www.npmjs.com/package/mcp-colombia-hub  
**GitHub:** https://github.com/manuelariasfz/mcp-colombia  
**Version:** 1.3.0

---

## When to Use

✅ **USE this skill when:**

- "Search for [product] on MercadoLibre Colombia"
- "Find hotels in [city] Colombia from [date] to [date]"
- "Search flights from [origin] to [destination]"
- "Compare CDT rates in Colombia"
- "Simulate a credit/loan of $X at Y months"
- "Compare bank accounts / cuentas de ahorros"

❌ **DON'T use this skill when:**

- Querying MercadoLibre from other countries (use their native ML API)
- Real-time stock prices or forex (use dedicated finance APIs)

---

## Installation

### Claude Desktop / OpenClaw (`claude_desktop_config.json` or `mcp.json`)

```json
{
  "mcpServers": {
    "colombia": {
      "command": "npx",
      "args": ["-y", "mcp-colombia-hub"]
    }
  }
}
```

### Direct run

```bash
npx -y mcp-colombia-hub
```

---

## Available Tools (10)

### 🛒 MercadoLibre

#### `ml_buscar_productos`
Search products on MercadoLibre Colombia.

```
Parameters:
  query        (string, required)  — search term
  limit        (number, optional)  — results per page (default: 10, max: 50)
  offset       (number, optional)  — pagination offset

Returns: title, price (COP), condition, seller, URL, thumbnail
```

#### `ml_detalle_producto`
Get full details of a MercadoLibre listing.

```
Parameters:
  item_id      (string, required)  — e.g. "MCO123456789"

Returns: full description, attributes, available quantity, shipping info
```

### ✈️ Travel (Awin / Booking.com)

#### `viajes_buscar_hotel`
Search hotels via Booking.com — **real-time data** (v1.2.2).

```
Parameters:
  destino      (string, required)  — city or region (e.g. "Medellín")
  checkin      (string, required)  — YYYY-MM-DD
  checkout     (string, required)  — YYYY-MM-DD
  adultos      (number, optional)  — guests (default: 2)
  habitaciones (number, optional)  — rooms (default: 1)
  precio_max   (number, optional)  — max price per night (COP)

Returns: hotels with real prices (COP/night), stars, zone, direct Booking.com link (Awin affiliate).
Data source priority:
  1. Booking.com live page (JSON-LD extraction)
  2. Brave Search results from booking.com
  3. Curated fallback data
Field `fuente`: "tiempo_real" | "curados"
```

#### `viajes_buscar_vuelos`
Search flights with real price references (v1.2.2).

```
Parameters:
  origen       (string, required)  — IATA code (e.g. "BOG")
  destino      (string, required)  — IATA code (e.g. "MDE")
  fecha        (string, required)  — YYYY-MM-DD
  ida_vuelta   (bool, optional)    — round trip (default: false)
  fecha_regreso (string, optional) — YYYY-MM-DD
  pasajeros    (number, optional)  — passengers (default: 1)

Returns: direct links to Avianca, LATAM, Skyscanner + precios_encontrados
  from real Brave Search results when BRAVE_API_KEY is set.
```

### 💰 Finanzas

#### `finanzas_comparar_cdt`
Compare CDT (Certificado de Depósito a Término) rates from Colombian banks.

```
Parameters:
  monto        (number, required)  — amount in COP
  plazo_dias   (number, optional)  — term in days (default: 90)

Returns: bank name, annual rate (%), effective return, minimum amount
Sorted by: best rate first
```

#### `finanzas_simular_credito`
Simulate a credit/loan with Colombian banks.

```
Parameters:
  monto        (number, required)  — loan amount in COP
  plazo_meses  (number, required)  — term in months
  tasa_mensual (number, optional)  — monthly rate % (uses market average if omitted)

Returns: monthly payment, total interest, total to pay, amortization table
```

#### `finanzas_comparar_cuentas`
Compare savings/checking accounts from Colombian banks.

```
Parameters:
  tipo         (string, optional)  — "ahorros" | "corriente" (default: "ahorros")

Returns: bank, account type, 4×4 maintenance fee, GMF exemption, digital/physical
```

---

## Soulprint Integration (v1.3.0)

The server accepts optional Soulprint identity tokens for verified access:

```typescript
// In MCP capabilities (Claude Desktop)
{
  "x-soulprint-token": "<your SPT token>"
}
```

### `soulprint_status` — Check identity & on-chain reputation
Check if a user has a valid Soulprint identity. Queries the live validator node for on-chain data.

```
Parameters: none (reads from x-soulprint-token capability)
Returns:
  status          — "active" | "no_token" | "invalid"
  did             — decentralized identity
  score           — trust score (0–100)
  node_info       — live data from validator node
  node_reputation — on-chain reputation
  premium_access  — which tools are unlocked
Validator node: https://soulprint-node-production.up.railway.app
```

Tools with score requirements:
- Standard tools: score ≥ 0 (open access)
- `trabajo_aplicar` (job applications): score ≥ **40** — requires basic identity verification

### `trabajo_aplicar` — Real job listings (v1.2.2)
```
Parameters:
  cargo        (string, required)   — job title (e.g. "Desarrollador Backend Senior")
  ciudad       (string, required)   — city
  cv_url       (string, optional)   — CV or LinkedIn URL
  salario_esp  (number, optional)   — expected salary (COP/month)
  modalidad    (enum, optional)     — "presencial" | "remoto" | "híbrido" (default: "remoto")
  mensaje      (string, optional)   — cover message (max 500 chars)

Returns:
  vacante.link_aplicar  — direct application link (elempleo.com, computrabajo, linkedin, indeed)
  vacante.empresa       — company name (extracted from listing)
  vacante.salario       — salary range found in listing
  donde_aplicar         — search links for all 4 portals
  otras_vacantes        — up to 4 additional relevant listings
  candidato             — verified Soulprint identity (DID, score, trust level)
```
Requires `BRAVE_API_KEY` env var for real-time job search.

Bot reputation is tracked automatically — good tool usage earns +1 attestations.

---

## Usage Examples

### Search products

```
User: "Busca auriculares inalámbricos en MercadoLibre Colombia"
Tool: ml_buscar_productos({ query: "auriculares inalámbricos", limit: 5 })
```

### Compare CDTs

```
User: "¿Qué CDT me da mejor rendimiento para $5,000,000 COP a 90 días?"
Tool: finanzas_comparar_cdt({ monto: 5000000, plazo_dias: 90 })
```

### Find hotels

```
User: "Hoteles en Cartagena del 15 al 20 de marzo para 2 personas"
Tool: viajes_buscar_hotel({ destino: "Cartagena", checkin: "2026-03-15", checkout: "2026-03-20", adultos: 2 })
```

### Simulate credit

```
User: "¿Cuánto pagaría por un crédito de $10,000,000 a 24 meses?"
Tool: finanzas_simular_credito({ monto: 10000000, plazo_meses: 24 })
```

---

## Notes

- MercadoLibre: direct API (no key needed for search)
- Hotels/flights: real-time data from Booking.com + Brave Search; Awin affiliate links (publisher `2784246`)
- Job applications (`trabajo_aplicar`): real listings from El Empleo, Computrabajo, LinkedIn, Indeed via Brave Search
- Financial data: scraped from public bank rate pages
- All prices in COP (Colombian Pesos)
