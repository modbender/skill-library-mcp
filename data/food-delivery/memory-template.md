# Memory Setup — Food Delivery

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/food-delivery
```

## memory.md Template

Copy to `~/food-delivery/memory.md`:

```markdown
# Food Delivery Preferences

## Critical Restrictions
<!-- Allergies and medical - ALWAYS filter, add note to orders -->
<!-- Format: - allergen (severity if known) -->

## Firm Restrictions
<!-- Religious, ethical, dietary - filter unless override -->
<!-- Format: - restriction (reason) -->
<!-- Examples: no pork, vegetarian, halal, kosher, vegan -->

## Avoid
<!-- Taste preferences - consider but flexible -->
<!-- Format: - item -->

## Preferences
<!-- Positive preferences -->
spice_level: medium
cuisine_favorites:
  - Thai
  - Mexican
  - Japanese

## Defaults
default_budget: $25
usual_order_time: dinner
preferred_platforms:
  - Uber Eats
  - DoorDash

## Notes
<!-- Any other relevant context -->
<!-- e.g., "prefers family restaurants", "likes trying new places" -->

---
*Last updated: YYYY-MM-DD*
```

## restaurants.md Template

Copy to `~/food-delivery/restaurants.md`:

```markdown
# Restaurant Notes

<!-- Add restaurants as you try them -->

## [Restaurant Name]
- Platform: Uber Eats / DoorDash / etc
- Rating: ⭐⭐⭐⭐⭐ (1-5)
- Cuisine: [type]
- Price: $ / $$ / $$$ / $$$$
- Delivery: fast / average / slow
- Favorites: [dishes that were good]
- Avoid: [dishes that disappointed]
- Notes: [any other observations]
- Last ordered: YYYY-MM-DD

---

## [Another Restaurant]
...
```

## orders.md Template

Copy to `~/food-delivery/orders.md`:

```markdown
# Recent Orders

<!-- Track for variety - keep last 14 days -->

| Date | Restaurant | Cuisine | Rating |
|------|------------|---------|--------|
| 2024-01-15 | Thai Palace | Thai | ⭐⭐⭐⭐ |
| 2024-01-14 | Pizza Place | Italian | ⭐⭐⭐ |
| ... | ... | ... | ... |

## Variety Notes
- Thai: 2x this week
- Pizza: 1x this week

---
*Prune entries older than 14 days*
```

## people.md Template

Copy to `~/food-delivery/people.md` (for households/groups):

```markdown
# Household & Regular Group Members

## [Name]
- Critical: [allergies]
- Restrictions: [dietary]
- Avoids: [dislikes]
- Loves: [favorites]
- Notes: [e.g., "kids menu age", "picky eater"]

## [Another Person]
...

---
*Update when you learn new preferences*
```

## Maintenance

### Weekly
- Prune orders.md to last 14 days
- Update restaurant ratings if opinions changed

### Monthly
- Review preferences for accuracy
- Archive inactive household members
- Check if defaults still apply

### After Bad Experience
- Update restaurant notes immediately
- Downgrade rating
- Note specific issues for future
