# Decision Framework — Food Delivery

## The Core Question

"What should I order?" is actually several questions:
1. What type of food? (cuisine)
2. From where? (restaurant)
3. What specifically? (dishes)
4. On which platform? (price optimization)

## Decision Flow

### Phase 1: Context Gathering

**Time-based defaults:**
| Time | Default mood |
|------|-------------|
| 6am-10am | Breakfast, light, quick |
| 11am-2pm | Lunch, functional, not heavy |
| 5pm-9pm | Dinner, main meal, flexible |
| 9pm-12am | Late night, comfort, indulgent |

**Day-based adjustments:**
| Day | Typical pattern |
|-----|-----------------|
| Mon-Thu | Functional, efficient, budget-conscious |
| Friday | Celebratory, can splurge, social |
| Saturday | Exploratory, trying new things |
| Sunday | Recovery, comfort, family-style |

**Ask if unclear:**
- "Quick meal or taking your time?"
- "Just you or others joining?"
- "Any occasion I should know about?"

### Phase 2: Filtering

**Hard filters (never skip):**
1. CRITICAL restrictions (allergies)
2. Restaurant currently open
3. Delivers to user's area
4. Within budget if stated

**Soft filters (apply when relevant):**
1. FIRM restrictions (dietary)
2. Variety protection triggers
3. Recent bad experiences
4. Slow delivery warnings

### Phase 3: Narrowing

**Too many options?**
Use binary narrowing:
- "Asian or Western?"
- "Something familiar or new?"
- "Quick or worth the wait?"
- "Light or filling?"

**User says "I don't know":**
1. First: "What do you NOT want?"
2. Then: "What about [past success]?"
3. Finally: Make a recommendation with confidence

### Phase 4: Presenting Options

**Always present 2-3 options, never more.**

Format each option:
```
[Restaurant Name] - [Cuisine]
Why: [reason based on their preferences]
Price: ~$X on [Platform]
Time: ~X min delivery
```

**Include a recommendation:**
"I'd go with [X] because [reason]"

### Phase 5: Refinement

If user rejects all options:
- Ask what's wrong with each
- Update mental model
- Try adjacent categories

If user picks one:
- Move to ordering phase
- Suggest specific dishes if you know favorites

## Price Comparison Strategy

Before finalizing restaurant:
1. Search same restaurant on all user's platforms
2. Check for platform-specific promos
3. Look for applicable coupons
4. Calculate true total (food + delivery + fees + tip)
5. Report savings opportunity

**When to mention:**
- Always if difference > $3
- Only if asked for smaller differences

## Special Situations

### "Surprise me"
1. Check variety - what haven't they had recently?
2. Pick from their favorites list
3. Weight toward highly-rated past orders
4. Make confident choice, don't ask questions

### "Same as last time"
1. Check orders.md for most recent
2. Verify restaurant still open
3. Confirm: "Ordering [X] from [Y] again?"
4. Execute directly

### "Something new"
1. Filter TO cuisines they like but haven't ordered recently
2. Check for new restaurants matching preferences
3. Look for high ratings + good delivery time
4. Present as discovery: "New spot that matches your taste..."

### "Healthy today"
1. Filter for health-conscious options
2. But don't assume salads only
3. Consider: poke, grain bowls, grilled options
4. Still apply taste preferences

### "Comfort food"
1. Lean into indulgent favorites
2. Suspend "healthy" suggestions
3. Pizza, burgers, fried foods, pasta
4. Familiar restaurants

## Group Order Strategy

### Step 1: Collect Restrictions
- Check people.md for known members
- Ask about anyone new
- Prioritize CRITICAL restrictions

### Step 2: Find Intersection
- What cuisines work for everyone?
- What restaurants have enough variety?
- Are there vegetarian AND meat options?

### Step 3: Coordinate
- Use restaurants with broad menus
- Suggest items for each person
- Handle "I'll have what they're having"

### Step 4: Logistics
- Calculate group total
- Split if needed
- One order or multiple?

## Confidence Calibration

**Be confident when:**
- User has clear history
- Request matches past patterns
- You've succeeded before

**Be tentative when:**
- New user / limited history
- Unusual request
- Past similar suggestions rejected
