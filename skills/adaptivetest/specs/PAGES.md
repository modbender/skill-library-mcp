# AdaptiveTest Skill -- Pages Spec

> **Page structure for the `/developers` landing page on adaptivetest-marketing. Content is in CONTENT.md. Visuals are in DESIGN-SYSTEM.md.**
> **Target repo:** `adaptivetest-marketing`

---

## Developers Page (`/developers`)

Convince EdTech developers and OpenClaw users to try the AdaptiveTest API. The visitor should understand what the API does, see how simple integration is, and start a free trial.

### Sections (in order):

---

**1. Hero**

- Layout: full-width gradient background (see DESIGN-SYSTEM.md > Hero Section)
- Content: see CONTENT.md > Landing Page Copy > Hero Section
- Label: small caps `text-indigo-200 text-sm font-semibold tracking-wider uppercase mb-4`
- Headline: `text-5xl md:text-6xl font-bold text-white mb-6`
- Subtitle: `text-xl md:text-2xl text-indigo-100 max-w-3xl mx-auto mb-10`
- CTAs: Two buttons side by side, centered
  - Primary: "Start Free Trial" -> Stripe Checkout redirect (see SITE-ARCHITECTURE.md)
  - Secondary (ghost): "View Documentation" -> `#capabilities` anchor scroll
- Responsive: Stack buttons vertically on mobile (`flex-col sm:flex-row`)

---

**2. Capabilities Grid**

- Background: `white`
- Layout: section container, centered heading, 3-column grid
- Content: see CONTENT.md > Capabilities Section
- Section heading pattern:
  - Label: `text-indigo-600 text-sm font-semibold tracking-wider uppercase mb-2`
  - Headline: `text-4xl md:text-5xl font-bold text-gray-900 mb-4`
  - Subtitle: `text-xl text-gray-600 max-w-2xl mx-auto mb-16`
- Grid: `grid md:grid-cols-2 lg:grid-cols-3 gap-8`
- Cards: Feature Card pattern (DESIGN-SYSTEM.md) with icon colors from CONTENT.md capability table
- Anchor: `id="capabilities"`
- Responsive: 1 column on mobile, 2 on tablet, 3 on desktop

---

**3. Code Example**

- Background: `gray-50`
- Layout: two-column split (`grid lg:grid-cols-2 gap-12 items-center`)
- Left column: Text content
  - Headline: see CONTENT.md > Code Example Section > Headline
  - Subtitle: see CONTENT.md > Code Example Section > Subtitle
  - Bullet list of key points (3-4 items):
    - "Three API calls to start an adaptive session"
    - "JSON responses with real-time ability estimates"
    - "AI question generation in a single POST"
    - "Works with any HTTP client or language"
  - Each bullet: `flex items-start gap-3` with `Check` icon `text-indigo-600`
- Right column: Code block component (DESIGN-SYSTEM.md > Code Block)
  - Language: Python
  - Content: see CONTENT.md > Code Example Section > code block
- Responsive: Stack vertically on mobile (text first, then code)

---

**4. How It Works**

- Background: `white`
- Layout: section container, centered heading, then 2x2 grid or vertical stack
- Content: see CONTENT.md > How It Works Section
- Section heading: same pattern as Capabilities
- Steps: 4 Step Cards (DESIGN-SYSTEM.md > Step Card)
  - Numbered circles: 1, 2, 3, 4
  - Grid: `grid md:grid-cols-2 gap-8` or `space-y-8` for vertical
- Responsive: Stack to single column on mobile

---

**5. Pricing**

- Background: `gray-50`
- Layout: section container, centered heading, 3-column pricing grid
- Content: see CONTENT.md > Pricing Section
- Section heading: same pattern
- Grid: `grid md:grid-cols-3 gap-8 items-start`
- Cards: Pricing Card pattern (DESIGN-SYSTEM.md)
  - Free Trial: standard border, "Start Free Trial" CTA -> Stripe Checkout
  - Pro: `ring-2 ring-indigo-600 md:scale-105`, "Popular" badge, "Subscribe" CTA -> Stripe Checkout
  - Enterprise: standard border, "Contact Us" CTA -> `mailto:jim@woodstocksoftware.com`
- Feature lists: check marks for included features, dash or absent for excluded
- Responsive: Stack vertically on mobile, Pro card loses `scale-105`

---

**6. FAQ**

- Background: `white`
- Layout: section container, centered heading, accordion list
- Content: see CONTENT.md > FAQ Section
- Section heading: same pattern
- Accordion: FAQ Accordion pattern (DESIGN-SYSTEM.md)
- Max width: `max-w-3xl mx-auto`
- Behavior: Click to expand/collapse. One open at a time (accordion mode).
- Default: First FAQ item open on page load
- Responsive: Full width, no layout changes

---

**7. Bottom CTA**

- Background: full-width gradient (same as hero)
- Layout: centered text on gradient
- Content: see CONTENT.md > Bottom CTA Section
- Headline: `text-4xl md:text-5xl font-bold text-white mb-4`
- Subtitle: `text-xl text-indigo-100 mb-10`
- CTAs: Same button pair as hero
  - "Start Free Trial" -> Stripe Checkout
  - "Read the Docs" -> `#capabilities` or future docs URL
- Responsive: Stack buttons vertically on mobile

---

## Component Dependencies

New components needed for this page (not on existing marketing site):

| Component | Used In | Notes |
|-----------|---------|-------|
| `CodeBlock` | Code Example section | Terminal-style code display with syntax highlighting |
| `StepCard` | How It Works section | Numbered step with title and description |
| `FAQAccordion` | FAQ section | Expandable Q&A list |
| `PricingCard` | Pricing section | May already exist on marketing site -- check and reuse |

Existing components to reuse:
- Navbar (add "Developers" link)
- Footer (add "Developers" link)
- Section heading pattern (label + h2 + subtitle)
- Button components (primary, ghost, outline variants)
