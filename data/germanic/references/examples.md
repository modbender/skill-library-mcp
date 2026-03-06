# GERMANIC Workflow Examples

## Healthcare Practice (Built-in Schema)

```bash
# Input: dr-sonnenschein.json
{
  "name": "Dr. Sonnenschein",
  "bezeichnung": "Zahnarzt",
  "adresse": {
    "strasse": "Blumenweg",
    "hausnummer": "12",
    "plz": "80331",
    "ort": "Munchen",
    "land": "DE"
  },
  "telefon": "+49 89 12345678",
  "email": "praxis@sonnenschein.example",
  "website": "https://sonnenschein.example"
}

# Compile
germanic compile --schema practice --input dr-sonnenschein.json

# Output: dr-sonnenschein.grm (binary, ~200 bytes)
```

## Custom Restaurant Schema (Dynamic Mode)

```bash
# Step 1: Start with example data
cat > restaurant.json << 'EOF'
{
  "name": "Zur Goldenen Gans",
  "cuisine": "Bavarian",
  "rating": 4.7,
  "address": { "street": "Marienplatz 1", "city": "Munchen" },
  "tags": ["traditional", "beer garden", "family-friendly"]
}
EOF

# Step 2: Infer schema
germanic init --from restaurant.json --schema-id de.dining.restaurant.v1

# Step 3: Edit de_dining_restaurant_v1.schema.json
# -> Set "name" and "address.street" to required: true

# Step 4: Compile
germanic compile --schema de_dining_restaurant_v1.schema.json --input restaurant.json
```

## JSON Schema Draft 7 Input

GERMANIC auto-detects JSON Schema Draft 7 files:

```bash
# Works with standard JSON Schema files (e.g. from OpenAI, OpenClaw)
germanic compile --schema openai-output.schema.json --input response.json
```

## Inspect & Validate

```bash
$ germanic inspect dr-sonnenschein.grm
+---------------------------------------------
| GERMANIC Inspector
+---------------------------------------------
| File: dr-sonnenschein.grm
| Size: 247 bytes
|
| Header:
|   Schema-ID: de.gesundheit.praxis.v1
|   Signed:    No
|   Header length:  93 bytes
|   Payload length: 154 bytes
+---------------------------------------------
```

## Available Domains (42 German + 47 English)

Healthcare, Dining, Education, Legal, Real Estate, Mobility,
Services, Agriculture, Culture, Public Services, Business.

Run `germanic schemas` to list available built-in schemas.
