# جاك العلم — Brand Guideline

## Brand Voice
- صديقك اللي يفهم
- مباشر وواضح بدون تكلف
- ممنوع: "نوصي بشدة" أو "ننصح بشراء" أو أي لغة AI واضحة
- الأسلوب: نجدي طبيعي للتوصيات وفصحى خفيفة للتحليل

## Typography
- **Primary Font:** Rubik (Google Fonts)
- **Preconnect:**
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet">
  ```
- **Fallback:** -apple-system, 'Segoe UI', Tahoma, sans-serif

## Color System (CSS Variables)

```css
:root {
  /* Backgrounds */
  --bg: #F8F7F4;              /* Canvas — main page background */
  --card: #1d1d1f;            /* Dark cards */
  --card-alt: #2d2d2f;        /* Card inner sections */

  /* Tier Accents */
  --best-value: #34c759;      /* Green — Best Value */
  --near-pro: #007aff;        /* Blue — Near-Pro */
  --budget-killer: #ff9500;   /* Orange — Budget Killer */

  /* Functional */
  --accent-green: #34c759;
  --accent-blue: #007aff;
  --accent-orange: #ff9500;
  --accent-red: #ff3b30;
  --accent-purple: #af52de;

  /* Text */
  --text-primary: #ffffff;    /* On dark cards */
  --text-secondary: #a1a1a6;  /* Muted text on dark */
  --text-dark: #1d1d1f;       /* On light background */
}
```

## Card Design

### Structure
```
┌─────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓ 4px accent stripe  │
│                                 │
│  [Badge: tier label]            │
│                                 │
│  [Product Image] (optional)     │
│                                 │
│  Product Name (h3)              │
│  Price (large, bold)            │
│                                 │
│  ┌─ Kill Doubt Box ──────────┐  │
│  │ ليش هذا الأفضل لك؟        │  │
│  │ [reasoning text]           │  │
│  └────────────────────────────┘  │
│                                 │
│  ⚖️ التنازل: [tradeoff]        │
│                                 │
│  [delivery badge] [trust badge] │
│  [deal tags: coupon, tamara]    │
│                                 │
│  ┌─────────────────────────────┐│
│  │      اشتري الآن ←          ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

### Corner Radius
- Cards: `16px`
- Inner elements (kill-doubt box): `12px`
- Badges: `8px`
- Tier badges: `20px` (pill shape)
- Buy button: `12px`

### Accent Stripe
- 4px top border on each card
- Color matches tier: green / blue / orange

### Kill Doubt Box
- Background: `var(--card-alt)` (#2d2d2f)
- Padding: `12px`
- Border-radius: `12px`
- "ليش هذا الأفضل لك؟" in `var(--accent-green)` bold

## Layout
- Max-width: `600px` (Telegram mobile-friendly)
- Direction: RTL (`dir="rtl"`)
- Padding: `16px` body
- No external JS dependencies
- No CDN links except Google Fonts

## Badge System

### Delivery
| Speed | Badge | Color Class |
|-------|-------|-------------|
| 1-2 days | 🟢 1-2 أيام | `delivery-fast` (green) |
| 3-7 days | 🟡 3-7 أيام | `delivery-medium` (orange) |
| 2-4 weeks | 🔴 2-4 أسابيع | `delivery-slow` (red) |

### Trust
| Level | Badge | Color Class |
|-------|-------|-------------|
| Known retailer | ✅ بائع موثوق | `trust-verified` (green) |
| Unknown seller | ⚠️ تحقق من البائع | `trust-unverified` (red) |

### Deal Tags
- Purple background (`var(--accent-purple)`)
- White text, `6px` radius
- Examples: `كوبون: CODE` / `تمارا 3×` / `كاشباك 5%`
