---
# Feast Weekly Plan
# Self-contained weekly meal plan with all recipes, themes, and music embedded
# This is the single source of truth for a week's meals

version: 1
weekOf: "YYYY-MM-DD"              # Date of week start
status: draft                     # draft, confirmed, active, complete
createdAt: null
confirmedAt: null

profile:
  portions: 1
  portionMultiplier: 1.0
  calorieTarget: null

weekTheme:
  name: null                      # Optional week theme (e.g., "Mediterranean Summer")
  event: null                     # Cultural event if relevant
  description: null               # Week theme description

days:
  - date: "YYYY-MM-DD"
    dayName: sunday
    type: cooking                 # cooking, cheat, skip
    revealed: false
    
    # ═══════════════════════════════════════════════════════════════
    # THE PLACE — Regional context (embedded, not linked)
    # ═══════════════════════════════════════════════════════════════
    place:
      country: null               # e.g., "Thailand"
      region: null                # e.g., "Northern Thailand"
      city: null                  # e.g., "Chiang Mai"
      
      # Evocative description of the region
      description: null           # 2-3 paragraphs about the region's character
      
      # What's happening there now (researched at planning time)
      currentContext: null        # News, events, seasonal notes
      
      # What the region is famous for
      famousFor: null
    
    # ═══════════════════════════════════════════════════════════════
    # THE DISH — Full recipe (embedded, not linked)
    # ═══════════════════════════════════════════════════════════════
    dish:
      name: null                  # Recipe name
      cuisine: null               # e.g., "Thai"
      
      # Origin story
      story: null                 # Where it came from, how it evolved
      culturalSignificance: null  # When eaten, by whom, what it means
      modernContext: null         # Street food? Home? Celebration?
      
      # Timing
      prepTime: null              # Minutes
      cookTime: null              # Minutes
      difficulty: null            # easy, medium, hard
      equipment: []               # Required equipment
      
      # Nutrition (optional)
      nutrition:
        caloriesPerServing: null
        protein: null
        carbs: null
        fat: null
        fibre: null
      
      # Full ingredient list
      ingredients:
        - name: null
          amount: null
          unit: null
          category: null          # protein, vegetable, spice, etc.
          notes: null
      
      # Full method
      method:
        - step: 1
          instruction: null
          tips: null
      
      # Tips and notes
      tips: []
      
      # Source
      source:
        url: null
        adapted: false
        notes: null
    
    # ═══════════════════════════════════════════════════════════════
    # THE SOUNDTRACK — Curated music (embedded, not linked)
    # ═══════════════════════════════════════════════════════════════
    music:
      philosophy: null            # Why these tracks? What vibe?
      duration: null              # e.g., "1h 45m"
      
      # Contemporary hits from the region
      contemporary:
        - artist: null
          track: null
          year: null
          notes: null
      
      # Classic/traditional from the region
      classic:
        - artist: null
          track: null
          era: null               # e.g., "1970s", "Traditional"
          notes: null
      
      # Full curated playlist (ordered)
      playlist:
        - artist: null
          track: null
      
      # Links
      spotifyLink: null
      youtubeLink: null
      fallbackSearch: null        # Backup search term
    
    # ═══════════════════════════════════════════════════════════════
    # SETTING THE SCENE — Atmosphere (embedded)
    # ═══════════════════════════════════════════════════════════════
    atmosphere:
      serving: null               # How to serve (shared plates? eaten how?)
      drinks: []                  # What to drink with it
      ambience: null              # Any atmosphere tips
    
    # ═══════════════════════════════════════════════════════════════
    # RESEARCH METADATA
    # ═══════════════════════════════════════════════════════════════
    research:
      confidenceLevel: null       # high, medium, low
      sources: []                 # URLs consulted
      compiled: null              # When researched
    
    # ═══════════════════════════════════════════════════════════════
    # TRACKING
    # ═══════════════════════════════════════════════════════════════
    cooked: false
    rating: null                  # 1-5 after cooking
    notes: null                   # Post-cooking notes

  # Repeat for each day...

# ═══════════════════════════════════════════════════════════════════
# SHOPPING — Consolidated list with price guidance
# ═══════════════════════════════════════════════════════════════════
shopping:
  status: pending                 # pending, approved, purchased
  generatedAt: null
  
  # Price checking
  priceCheck:
    performed: false
    checkedOn: null
    strategy: null                # single-store, split, deal-driven
    primaryStore: null
    secondaryStore: null
    potentialSavings: null
    disclaimer: "Prices checked on [date]. Verify in-store."
  
  # Key deals worth highlighting
  keyDeals:
    - item: null
      store: null
      deal: null
      savings: null
  
  # Full shopping list by category
  items:
    proteins:
      - name: null
        amount: null
        usedIn: []                # Which day(s) use this
        priceNote: null
        checked: false
    
    vegetables: []
    fruit: []
    dairy: []
    carbs: []
    tins: []
    herbs: []
    spices: []
    oils: []
    frozen: []
    bakery: []
    other: []
  
  # Storecupboard check
  storecupboard: []               # Items to verify you have
  
  # Totals
  estimatedCost: null
  actualCost: null

# ═══════════════════════════════════════════════════════════════════
# REVIEW — End of week reflection
# ═══════════════════════════════════════════════════════════════════
review:
  completed: false
  overallRating: null
  highlights: []
  improvements: []
  addToFavourites: []             # Dish names to add
  neverAgain: []                  # Dish names to avoid
  musicDiscoveries: []            # Artists/tracks worth remembering
---

# Meal Plan: Week of [DATE]

*[Theme/tagline for the week]*

---

## 🛒 Shopping List

### 💰 Price Guidance

**Strategy:** [Single store at X / Split: proteins at X, rest at Y]  
**Prices checked:** [Date]  
**Estimated total:** £XX

**Key deals:**
- [Deal 1]
- [Deal 2]

---

### Proteins
- [ ] Item — quantity — **~£X.XX** *(used in: Day 1, Day 3)*  
  💰 *[Price note]*

### Vegetables
- [ ] Item — quantity

### Dairy
- [ ] Item — quantity

### Carbs & Grains
- [ ] Item — quantity

### Tins & Jars
- [ ] Item — quantity

### Fresh Herbs
- [ ] Item — quantity

### Storecupboard Check
- [ ] Item (check you have)

---

## Day 1: [Day Name] — 🇹🇭 [Cuisine]

### 🌍 The Place: [Region], [Country]

[2-3 paragraphs about the region — its character, history, what makes it distinctive. Paint a picture of what it feels like to be there.]

**What's happening there now:** [Current context — news, events, seasonal notes from the region]

---

### 🍜 The Dish: [Meal Name]

[Story of this dish — where it originated, how it evolved, when it's eaten, what it means to people there.]

**Prep:** X mins | **Cook:** X mins | **Serves:** X

#### Ingredients

**Main:**
- Ingredient — amount
- Ingredient — amount

**Sauce/Seasoning:**
- Ingredient — amount

**To Serve:**
- Ingredient — amount

#### Method

1. **[Action verb]** — Description of step.

2. **[Action verb]** — Description of step.

3. **[Action verb]** — Description of step.

#### Tips
- Helpful tip or variation

---

### 🎵 The Soundtrack

**The Vibe:** [What mood and journey this playlist creates]

**Contemporary** (what [Region] listens to now):
- **[Artist]** — "[Track]" ([Year]) — *[brief note]*
- **[Artist]** — "[Track]"

**Classic/Traditional:**
- **[Artist]** — "[Track]" ([Era]) — *[brief note]*
- **[Artist]** — "[Track]"

**Full Playlist** (~X hours):
1. [Artist] — "[Track]"
2. [Artist] — "[Track]"
3. [Artist] — "[Track]"
4. ...

▶️ [Spotify Link] | [YouTube Link]

---

### ✨ Setting the Scene

**Serving:** [How to serve — shared plates? Individual? Eaten how?]

**Drinks:** [What to drink with it]

**Atmosphere:** [Any tips for enhancing the experience]

---

## Day 2: [Day Name] — 🇮🇹 [Cuisine]

*[Repeat full structure for each cooking day...]*

---

## End of Week Review

**Overall:** ⭐⭐⭐⭐☆

**Highlights:**
- 

**What to improve:**
- 

**Add to favourites:**
- 

**Never again:**
- 

**Music discoveries:**
- 
