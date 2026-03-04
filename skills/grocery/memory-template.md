# Memory Setup — Grocery

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/grocery
touch ~/grocery/memory.md
touch ~/grocery/pantry.md
```

## memory.md Template

Copy to `~/grocery/memory.md`:

```markdown
# Grocery Memory

## Household
<!-- Size, members, special notes -->
- Size: 
- Members: 

## Restrictions
<!-- Allergies, diets, strong dislikes -->

## Preferences
<!-- Brands, stores, typical quantities -->
- Primary store: 
- Backup store: 
- Quantities: 

## Current List
<!-- Active shopping list -->

## Picky Eaters
<!-- Per-person restrictions within household -->

---
*Last: YYYY-MM-DD*
```

## pantry.md Template

Copy to `~/grocery/pantry.md`:

```markdown
# Pantry Inventory

## Fridge
| Item | Qty | Expires |
|------|-----|---------|

## Freezer
| Item | Qty | Expires |
|------|-----|---------|

## Pantry
| Item | Qty | Expires |
|------|-----|---------|

## Running Low
<!-- Items to restock soon -->

---
*Updated: YYYY-MM-DD*
```

## stores.md Template (optional)

```markdown
# Store Information

## Primary: [Store Name]
- Typical aisle order: produce → dairy → meat → frozen → pantry

## Backup: [Store Name]
- Notes: better prices on X, worse selection on Y
```

## history.md Template (optional)

```markdown
# Purchase History

## Recent Trips
| Date | Store | Items | Notes |
|------|-------|-------|-------|

## Patterns
<!-- Observed buying patterns for suggestions -->
```
