# Birdfolio — You.com Search Query Templates

These query patterns are proven to return useful results from You.com for bird data.
Replace `[REGION]`, `[SPECIES]`, and `[SEASON]` with actual values.

---

## Setup — Building the Regional Checklist

Use these queries when setting up Birdfolio to fetch 10 common + 5 rare + 1 super rare species.

```
[REGION] most common backyard birds eBird species list
[REGION] common birds year-round residents eBird checklist
[REGION] top 10 birds beginners eBird frequency
[REGION] uncommon seasonal birds eBird rare sightings
[REGION] rare vagrant endangered birds [REGION] eBird
```

**Parsing guidance:**
- Common: species listed as "abundant", "widespread", "year-round resident"
- Rare: species listed as "seasonal", "migratory", "uncommon"
- Super Rare: species listed as "endangered", "vagrant", "accidental", "rarely seen"

**Target counts:** 10 common, 5 rare, 1 super rare per region.

---

## Bird Identification — Rarity Lookup

After Vision identifies the species, use this to classify rarity:

```
[SPECIES] [REGION] eBird frequency how common rare
[SPECIES] bird [REGION] rarity sighting frequency
```

**Classification signals:**

| Signal words | Tier |
|---|---|
| "abundant", "widespread", "year-round", "common resident", >50% of checklists | Common 🟢 |
| "uncommon", "seasonal", "migratory", "occasional", 5–50% of checklists | Rare 🟡 |
| "rare", "vagrant", "accidental", "endangered", "rarely seen", <5% of checklists | Super Rare 🔴 |

When ambiguous → default to **Rare**.

---

## Species Facts

Fetch 1–2 interesting facts for the trading card fun fact field:

```
[SPECIES] bird interesting facts habitat behavior
[SPECIES] bird facts range diet lifespan
```

**Extract:** One punchy fact, 1–2 sentences max. Avoid generic facts like "it is a bird."

---

## Bird Image Search

Fetch a photo URL for the trading card:

```
[SPECIES] bird photo wildlife
[SPECIES] bird Audubon photo
```

**Use:** The first usable image URL. Prefer naturalistic photos over cartoons/illustrations.
The `generate_card.py` script will download and embed the image as base64.

---

## Species Lookup (no logging)

When user asks "Tell me about [species]" without sending a photo:

```
[SPECIES] bird facts habitat range behavior diet
[SPECIES] bird [REGION] eBird frequency resident or migratory
```

Return a conversational summary — do not log or generate a card.

---

## Rarest Bird Alert (optional)

```
rare bird sightings [REGION] this week eBird alerts
```

Use for proactive rare bird mentions if implementing v2 rarity alerts.
