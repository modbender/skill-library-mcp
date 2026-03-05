# Paywall Layout Patterns

## Core Components

Every paywall needs these elements. Order matters.

### 1. Value Proposition (Top)
- Headline: What they get
- Subheadline or benefit list
- Visual: Product preview, illustration, or video

### 2. Plan Options (Middle)
- 2-3 plans displayed
- One highlighted as recommended
- Clear price and billing period

### 3. CTA (Prominent)
- Single action button
- Action-oriented text ("Start free trial")
- Visually distinct

### 4. Trust Signals (Near CTA)
- Trial terms visible
- "Cancel anytime"
- Social proof or reviews

### 5. Dismiss Option (Required)
- X button or "Not now" link
- Don't hide it (app store compliance)

---

## Mobile Layout Patterns

### Pattern 1: Feature Carousel + Plans

```
┌─────────────────────────┐
│   [Swipeable benefits]  │
│   ●  ○  ○  ○  ○        │
├─────────────────────────┤
│ [Weekly] [Yearly ✓]     │
│          BEST VALUE     │
├─────────────────────────┤
│  [ Continue - $X.XX ]   │
│  Cancel anytime · ⭐4.8 │
└─────────────────────────┘
                      [✕]
```

Best for: Apps with multiple features to showcase

### Pattern 2: Single Focus + Plans

```
┌─────────────────────────┐
│    🎨 Go Premium        │
│                         │
│  ✓ Unlimited exports    │
│  ✓ No watermarks        │
│  ✓ Priority support     │
├─────────────────────────┤
│ [Monthly $9] [Year $49] │
├─────────────────────────┤
│  [ Start 7-day trial ]  │
│  Then $49/year          │
└─────────────────────────┘
                      [✕]
```

Best for: Simple upgrade, clear value prop

### Pattern 3: Full-Screen Visual

```
┌─────────────────────────┐
│                         │
│    [Hero image/video]   │
│                         │
│    Unlock Everything    │
│    Join 2M+ creators    │
├─────────────────────────┤
│  [ Start free trial ]   │
│  7 days free, then $X   │
│       Skip for now      │
└─────────────────────────┘
```

Best for: Visual apps, content apps

### Pattern 4: Comparison View

```
┌─────────────────────────┐
│      Free vs Pro        │
├──────────┬──────────────┤
│ Free     │ Pro          │
├──────────┼──────────────┤
│ 5 proj   │ Unlimited ✓  │
│ Ads      │ No ads ✓     │
│ Basic    │ All tools ✓  │
├──────────┴──────────────┤
│  [ Upgrade to Pro ]     │
└─────────────────────────┘
```

Best for: Clear free/paid differentiation

---

## Web Layout Patterns

### Pattern 1: Three-Column Plans

```
┌─────────┬─────────┬─────────┐
│  FREE   │   PRO   │ BUSINESS│
│         │ Popular │         │
├─────────┼─────────┼─────────┤
│   $0    │  $29    │   $99   │
│         │  /mo    │   /mo   │
├─────────┼─────────┼─────────┤
│ ✓ A     │ ✓ A     │ ✓ A     │
│ ✓ B     │ ✓ B     │ ✓ B     │
│ ✗ C     │ ✓ C     │ ✓ C     │
│ ✗ D     │ ✗ D     │ ✓ D     │
├─────────┼─────────┼─────────┤
│[Get free]│[Start] │[Contact]│
└─────────┴─────────┴─────────┘
```

Standard SaaS pricing page layout.

### Pattern 2: Two Plans + Enterprise

```
┌───────────────┬───────────────┐
│     PRO       │   BUSINESS    │
│   For indie   │   For teams   │
├───────────────┼───────────────┤
│     $19       │      $49      │
├───────────────┼───────────────┤
│    [Start]    │    [Start]    │
└───────────────┴───────────────┘

Need more? Contact us for Enterprise
```

Simpler, works for focused products.

---

## Visual Hierarchy Rules

### Size
- Headline: Largest text
- Price: Second largest
- CTA button: Visually dominant
- Fine print: Smallest (but readable)

### Color
- Recommended plan: Accent color border/background
- CTA: Brand color, high contrast
- Secondary actions: Muted

### Spacing
- Group related elements
- White space around CTA
- Don't crowd the plan options

---

## Mobile-Specific Considerations

### Thumb Zone
- CTA in bottom 1/3 (easy reach)
- Dismiss button in corner (accessible but not prominent)

### Scroll Behavior
- Above-fold: Value prop + plans visible
- Below-fold: Feature details, reviews, FAQ

### Screen Sizes
- Test on smallest supported device
- Plan cards may need to stack vertically on small screens

---

## Dark vs Light Background

| Dark | Light |
|------|-------|
| Premium, sophisticated feel | Clean, approachable |
| Good for media/entertainment | Good for productivity/utility |
| Text needs high contrast | More forgiving on contrast |
| Photos/videos pop | Icons and illustrations work well |

**Test both.** Results vary by audience.

---

## Animation & Motion

### Effective Uses
- Carousel auto-advance (subtle)
- CTA button pulse (once, on load)
- Value prop fade-in
- Confetti on purchase (celebration)

### Avoid
- Distracting loops
- Slow animations that delay interaction
- Motion that obscures content

---

## Accessibility Checklist

- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Price readable without squinting
- [ ] CTA button large enough (44pt minimum tap target)
- [ ] Screen reader compatible
- [ ] Dismiss option keyboard accessible
