# Shopping List — Command Reference

> This file is loaded on-demand when a shopping command is invoked.
> It is NOT loaded at session start. SKILL.md points here for details.

---

## 1. Commands

| Command | Description |
|---------|-------------|
| `shopping add <item>` | Add item(s) — "add 2 gallons milk" or "add eggs, bread, butter" |
| `shopping list` | Show active list grouped by category |
| `shopping check <item>` | Check off — "check milk" or "got the milk" |
| `shopping remove <item>` | Delete permanently, no archive |
| `shopping edit <item>` | Edit qty/unit/category/notes — "make milk 2 gallons" |
| `shopping categories` | Show categories with item counts |
| `shopping history` | Recent purchase history — "history" or "history february" |
| `shopping suggest` | Restock suggestions (Phase 2, not yet implemented) |
| `shopping clear` | Force-archive all checked items now |
| `shopping export` | Clean copy-paste list, no formatting |
| `shopping switch-user` | Change identity (AJ <-> Shal) |

---

## 2. Natural Language Mapping

Users will rarely type exact commands. Map these phrases to the right action.

| User says | Action |
|-----------|--------|
| "Add milk to the shopping list" | add milk |
| "We need eggs, bread, and butter" | add eggs, add bread, add butter |
| "Got the milk" / "Bought the milk" / "Cross off milk" | check milk |
| "What do we need from the store?" | list |
| "Never mind on the bananas" | remove bananas |
| "Make that 2 gallons instead of 1" | edit milk 2 gallons |
| "What have we been buying lately?" | history |
| "Anything we're running low on?" | suggest |
| "Move rice to Pantry" | edit rice (change category) |

---

## 3. Output Format Templates

### shopping list

```
Shopping List (8 items)

PRODUCE
  [ ] Avocados  3
  [ ] Bananas  1 bunch

DAIRY
  [ ] Whole Milk  2 gallons
  [x] Butter  1 lb                    <- archiving in 18h

MEAT
  [ ] Chicken Breast  2 lbs

PANTRY
  [ ] Black Beans  3 cans
  [ ] Rice  1 bag

HOUSEHOLD
  [ ] Paper Towels  1 pack
```

Formatting rules:
- Checked-off items show `[x]` with time until archive (24h countdown).
- Items without quantity/unit show just the name.
- Categories with zero unchecked and zero checked items are hidden entirely.
- Items are sorted alphabetically within each category.
- Category headers are UPPERCASE.

### shopping export

```
Shopping List
-------------
Produce: Avocados (3), Bananas (1 bunch)
Dairy: Whole Milk (2 gallons)
Meat: Chicken Breast (2 lbs)
Pantry: Black Beans (3 cans), Rice (1 bag)
Household: Paper Towels (1 pack)
```

Formatting rules:
- No emoji, no metadata, no checkboxes.
- Checked-off items are excluded.
- Output is plain text, copy-pasteable to Notes or Reminders.

### shopping categories

```
Categories (5 with items)
  Produce      2 items
  Dairy        2 items
  Meat         1 item
  Pantry       2 items
  Household    1 item
```

Formatting rules:
- Only categories that currently have items are shown.
- Singular "item" when count is 1, plural "items" otherwise.

### shopping history

```
Recent Purchases (last 30 days)

Feb 23: Whole Milk (2 gallons), Eggs (1 dozen), Bread (1 loaf)
Feb 19: Chicken Breast (2 lbs), Rice (1 bag)
Feb 15: Whole Milk (2 gallons), Bananas (1 bunch)
```

Formatting rules:
- Groups by date, most recent first.
- If user says "history february" then filter to February only.
- Reads from `data/history-YYYY-MM.json` files.

### Confirmation Messages (mutating commands)

**shopping add (single item):**
```
Added: Whole Milk (2 gallons) — Dairy
```

**shopping add (multi-item):**
```
Added 3 items:
  Eggs — Dairy
  Bread — Pantry
  Whole Milk (2 gallons) — Dairy
```

**shopping check:**
```
Checked off: Whole Milk — archiving in 24h
```

**shopping remove:**
```
Removed: Bananas
```

**shopping edit:**
```
Updated: Whole Milk — quantity: 1 → 2 gallons
```

**shopping clear:**
```
Archived 3 checked-off items.
```

**shopping switch-user:**
```
Switched to: shal
```

---

## 4. Edge Cases

### Fuzzy matching

- `"milk"` matches `"whole milk"` if it is the only milk on the list. Proceed without asking.
- `"milk"` matches both `"whole milk"` and `"oat milk"`. Ask: "Which one — whole milk or oat milk?"
- `"xyz"` matches nothing. Respond: "I don't see xyz on the list." Then show current items so the user can pick.

### Multi-item parsing

- `"add eggs, bread, and 2 gallons milk"` becomes 3 separate items: eggs, bread, 2 gallons milk.
- Ambiguous input like `"add 2 lbs chicken breast and thighs"` — unclear whether "2 lbs" applies to both or just chicken breast. Ask for clarification.
- Rule: when in doubt, ask. Never silently parse incorrectly.

### Quantity validation

- Quantity is optional. `"add milk"` creates an item with no quantity and no unit.
- `"add 2 milks"` sets quantity to 2 with no unit.
- If present, quantity must be > 0. Fractional values are allowed (e.g., 0.5 lbs).
- Zero or negative quantities are rejected: "Quantity must be greater than zero."

### Custom categories

- If the user specifies a category that does not exist in the preset list, create it automatically.
- Example: `"add vitamins to Supplements"` — if "Supplements" is not in the categories array, add it. Confirm: "Created new category: Supplements"
- Custom categories appear after the preset categories, sorted alphabetically among themselves.

### Force clear

- `shopping clear` archives ALL checked items immediately, regardless of the normal 24-hour auto-archive window. Use after a shopping trip to clean up the list.
- If there are no checked items: "Nothing to clear — no items are checked off."

### Empty list

- `shopping list` when the list has zero items: "Your shopping list is empty. Add something with 'shopping add <item>'."

### Phase 2 not ready

- `shopping suggest` before Phase 2 is implemented: "Restock suggestions aren't available yet. Keep using the list — I'll learn your patterns over time."
