# AdaptiveTest Skill -- Design System Spec

> **Source of truth for visual decisions on the `/developers` landing page. Must match the existing adaptivetest-marketing site.**
> **Target repo:** `adaptivetest-marketing`

---

## Color Palette

Match the existing marketing site exactly. Do not introduce new colors.

### Primary
| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Indigo 600 | `#4F46E5` | `indigo-600` | Primary buttons, links, active states, focus rings |
| Purple 600 | `#9333EA` | `purple-600` | Gradient accent (hero backgrounds) |
| Indigo 800 | `#3730A3` | `indigo-800` | Gradient endpoint (hero backgrounds) |

### Backgrounds
| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| White | `#FFFFFF` | `white` | Primary background, cards |
| Gray 50 | `#F9FAFB` | `gray-50` | Alternating section backgrounds |
| Gray 900 | `#111827` | `gray-900` | Footer background |

### Text
| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Gray 900 | `#111827` | `gray-900` / `text-gray-900` | Headings, primary text |
| Gray 600 | `#4B5563` | `gray-600` / `text-gray-600` | Body text, descriptions |
| Gray 400 | `#9CA3AF` | `gray-400` / `text-gray-400` | Muted text, footer links default |
| White | `#FFFFFF` | `text-white` | Text on dark/gradient backgrounds |
| Indigo 100 | `#E0E7FF` | `text-indigo-100` | Subtitle text on indigo backgrounds |

### Accent (Feature Icons)
| Color | Background | Icon | Usage |
|-------|-----------|------|-------|
| Indigo | `bg-indigo-100` | `text-indigo-600` | Default capability icon |
| Purple | `bg-purple-100` | `text-purple-600` | AI-related capabilities |
| Green | `bg-green-100` | `text-green-600` | Analytics/results capabilities |
| Orange | `bg-orange-100` | `text-orange-600` | Management capabilities |

### Never Use
- Pure black `#000000` for text -- use `gray-900`
- Custom colors not in this palette
- Opacity-based text colors on white backgrounds

---

## Typography

### Font
**Inter** via `next/font/google` -- matches existing marketing site.

```tsx
import { Inter } from "next/font/google";
const inter = Inter({ subsets: ["latin"] });
```

Applied to `<body>` via `inter.className`. Do NOT use Geist -- the marketing site uses Inter.

### Type Scale

| Element | Tailwind Classes | Usage |
|---------|-----------------|-------|
| H1 (Hero) | `text-5xl md:text-6xl font-bold` | Page hero headline |
| H2 (Section) | `text-4xl md:text-5xl font-bold` | Section headings |
| H3 (Subsection) | `text-3xl font-bold` | Card group headings |
| H4 (Card title) | `text-xl font-semibold` | Feature card titles |
| Body large | `text-xl md:text-2xl` | Hero subtitle, section intros |
| Body | `text-base` | Default paragraph text |
| Body small | `text-sm` | Labels, captions, metadata |
| Code | `font-mono text-sm` | Inline code, code blocks |

---

## Component Patterns

### Hero Section (Gradient)
```
Container: bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 text-white
Padding: py-20 md:py-24
Inner: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center
```

### Section Container
```
Padding: py-20
Inner: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
Alternating: white bg, then gray-50, repeating
```

### Primary Button
```
bg-indigo-600 text-white px-8 py-4 rounded-lg font-semibold
hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2
active:bg-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed transition
```

### Secondary Button (on gradient background)
```
bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold
hover:bg-indigo-100 focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600
active:bg-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed transition
```

### Ghost Button (on gradient background)
```
border-2 border-white text-white px-8 py-4 rounded-xl font-semibold
hover:bg-white/10 focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600
active:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition
```

### Outline Button (on white background)
```
border-2 border-indigo-600 text-indigo-600 px-8 py-4 rounded-xl font-semibold
hover:bg-indigo-50 focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2
active:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed transition
```

### Feature Card (Capability Grid)
```
Container: text-center p-6
Icon wrapper: bg-{color}-100 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4
Icon: w-8 h-8 text-{color}-600
Title: text-xl font-semibold text-gray-900 mb-2
Description: text-gray-600
```

### Pricing Card
```
Container: bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-200
Popular variant: ring-2 ring-indigo-600 md:scale-105
Badge (popular): bg-indigo-600 text-white text-center py-2 text-sm font-semibold
Body: p-8
Price: text-5xl font-bold text-gray-900
Period: text-gray-600
Features: list with Check icon text-indigo-600
CTA: full-width primary button
```

### Code Block (NEW -- not on existing site)
```
Container: bg-gray-900 rounded-2xl overflow-hidden shadow-xl
Header: bg-gray-800 px-6 py-3 flex items-center gap-2
  Dots: flex gap-2 (three 3x3 rounded-full: bg-red-500, bg-yellow-500, bg-green-500)
  Language label: text-gray-400 text-sm ml-auto
Body: p-6 overflow-x-auto
  Code: font-mono text-sm text-gray-300 leading-relaxed
  Comments: text-gray-400
  Strings: text-green-400
  Keywords: text-purple-400
  Functions: text-blue-400
```

### Step Card (How It Works)
```
Container: flex items-start gap-6
Number: w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-lg flex-shrink-0
Content: flex-1
Title: text-xl font-semibold text-gray-900 mb-2
Description: text-gray-600
```

### FAQ Accordion
```
Container: max-w-3xl mx-auto divide-y divide-gray-200
Item: py-6
Question: text-lg font-semibold text-gray-900 cursor-pointer flex justify-between items-center
  Icon: ChevronDown w-5 h-5 text-gray-400, rotate on open
Answer: text-gray-600 mt-4 (hidden when collapsed)
```

---

## Layout Patterns

### Responsive Container
```
max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
```

### Grid Patterns
| Layout | Classes |
|--------|---------|
| Capabilities (6 items) | `grid md:grid-cols-2 lg:grid-cols-3 gap-8` |
| Pricing (3 tiers) | `grid md:grid-cols-3 gap-8 items-start` |
| How It Works (4 steps) | `grid md:grid-cols-2 gap-8` or vertical stack |
| Code + Description | `grid lg:grid-cols-2 gap-12 items-center` |

### Section Spacing
- Between sections: `py-20`
- Hero: `py-20 md:py-24`
- Within sections (heading to content): `mb-12` or `mb-16`

---

## Navbar Updates

Add "Developers" link to existing navbar. Position: between existing links, before CTA buttons.

```
Link text: "Developers"
Href: "/developers"
Style: text-gray-600 hover:text-indigo-600 transition (matches existing nav links)
Mobile: add to mobile menu in same position
```

---

## Footer Updates

Add "Developers" link to the appropriate footer column (likely "Product" or "Resources" column).

```
Link text: "Developers"
Href: "/developers"
Style: text-gray-400 hover:text-white transition (matches existing footer links)
```

---

## Animations

Follow existing marketing site patterns. No Framer Motion -- the current site uses CSS transitions only.

- **Hover transitions:** `transition` class on all interactive elements
- **Card hover:** `hover:shadow-xl transition` where appropriate
- **No scroll animations** unless existing site uses them
- **Reduced motion:** Respect `prefers-reduced-motion` -- transitions are enhancement only
