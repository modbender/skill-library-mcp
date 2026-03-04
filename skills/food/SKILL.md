---
name: "Food Tracker"
description: "Your intelligent food system. Absorbs, analyzes, and organizes everything you eat."
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
---

## Intelligent Food Absorption

This skill absorbs ANY food input, auto-classifies it, and organizes for insights.

**Rules:**
- Auto-detect input type: meal photo, nutrition label, recipe, menu, text
- Extract and structure: items, portions, context, nutrition when visible
- Tag everything: #meal, #recipe, #product, #restaurant, #inventory
- Offer analysis: "Want nutrition estimate?" — don't force it
- Build personal database: scanned labels, frequent meals, saved recipes
- Provide insights: patterns, variety, timing, correlations
- Remember restrictions permanently, flag conflicts proactively
- For detailed macro tracking → complement with `calories` skill
- Check `processing.md` for how each input type is handled

---

## Memory Storage

All user data persists in: `~/food/memory.md`

**Format:**
```markdown
### Preferences
<!-- Their food preferences and restrictions. Format: "item: type" -->
<!-- Examples: nuts: allergy, gluten: intolerance, vegetarian: choice -->

### Products
<!-- Scanned/saved products for quick-log. Format: "product: cal/serving" -->
<!-- Examples: Hacendado yogurt: 120/170g, Oatly oat milk: 45/100ml -->

### Patterns
<!-- Detected eating patterns. Format: "pattern" -->
<!-- Examples: breakfast ~8am, snacks after 10pm, eats out Fridays -->

### Places
<!-- Restaurants and spots. Format: "place: notes" -->
<!-- Examples: Noma: loved fermented plum, Local Thai: go-to takeout -->

### Recipes
<!-- Saved recipes. Format: "dish: key info" -->
<!-- Examples: quick hummus: chickpeas+tahini+lemon 5min, Sunday roast: 2h -->
```

---
*Empty sections = no data yet. Absorb, classify, organize.*

**Insights provided:** Weekly variety score, meal timing patterns, frequent foods, eating out ratio, nutrition estimates when asked. Not medical advice.
