---
name: email-capture-generator
description: Build high-converting lead magnets, squeeze pages, and email capture funnels using proven 5-section conversion frameworks. Includes opt-in forms, thank you pages, and delivery automation hooks.
metadata:
  openclaw:
    requires:
      bins: []
      env: []
  tags:
    - email
    - lead-magnet
    - squeeze-page
    - opt-in
    - capture
    - funnel
    - marketing
  keywords:
    - "email capture"
    - "lead magnet"
    - "squeeze page"
    - "opt-in form"
    - "email list"
    - "conversion funnel"
    - "landing page"
  examples:
    - "Create a lead magnet landing page for a free ebook"
    - "Build an email capture funnel for a webinar"
    - "Design a newsletter signup squeeze page"
    - "Generate a free tool opt-in page"
---

# Email Capture Generator Skill

Build high-converting lead magnets, squeeze pages, and email capture funnels using proven conversion frameworks.

## The Email Capture Framework

### 5-Section Flow

Build email capture pages EXCLUSIVELY using this 5-section flow from top to bottom:

```
┌─────────────────────────────────────────────────────────┐
│ 1. HOOK (Hero Section)                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [Headline - Benefit-driven, specific]          │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [Subheadline - Expand on the promise]         │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │     [OPT-IN FORM]                               │   │
│  │     Email: [____________]                       │   │
│  │     [GET IT FREE]                              │   │
│  └─────────────────────────────────────────────────┘   │
│              [Lead magnet image]                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. VALUE (What's Inside)                               │
│    "Here's what you'll get:"                          │
│    ✓ [Benefit 1]                                      │
│    ✓ [Benefit 2]                                      │
│    ✓ [Benefit 3]                                      │
│         [Image showing the lead magnet]                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. PROOF (Social Validation)                          │
│    Headline: "Join X+ subscribers"                    │
│    [Testimonial 1]                                    │
│    [Testimonial 2]                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. URGENCY (Why Now)                                  │
│    "This offer expires..."                            │
│    [Scarcity element]                                 │
│    [Countdown timer if applicable]                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. REASSURANCE (Trust Builders)                       │
│    ✓ No spam, ever                                    │
│    ✓ Unsubscribe anytime                              │
│    ✓ [Privacy link] [Terms link]                     │
└─────────────────────────────────────────────────────────┘
```

### Section Breakdown

**1. HOOK (Hero Section)**
- Benefit-driven headline (specific, result-oriented)
- Subheadline expanding on the promise
- Email input field + CTA button
- Lead magnet visual (ebook, checklist, template preview)

**2. VALUE (What's Inside)**
- "Here's what you'll get" headline
- 3-5 bullet points with checkmarks
- Visual of the lead magnet (cover, preview, sample)

**3. PROOF (Social Validation)**
- Subscriber count
- 2-3 short testimonials
- Trust indicators (logos if applicable)

**4. URGENCY (Why Now)**
- Scarcity message (limited time, limited quantity)
- Countdown timer (optional)
- Reason to act now

**5. REASSURANCE (Trust Builders)**
- "No spam, ever" promise
- Unsubscribe guarantee
- Privacy/Terms links

## Template Variables

Replace these placeholders in your generated pages:

| Variable | Description |
|----------|-------------|
| `{{HEADLINE}}` | Main benefit-driven headline |
| `{{SUBHEADLINE}}` | Supporting description |
| `{{LEAD_MAGNET_NAME}}` | Name of the free offer |
| `{{BENEFIT_1}}` | First benefit bullet |
| `{{BENEFIT_2}}` | Second benefit bullet |
| `{{BENEFIT_3}}` | Third benefit bullet |
| `{{CTA_TEXT}}` | Button text (e.g., "Get It Free") |
| `{{EMAIL_PLACEHOLDER}}` | Input placeholder text |
| `{{SUBSCRIBER_COUNT}}` | Number of subscribers |
| `{{TESTIMONIAL_1}}` | First testimonial quote |
| `{{TESTIMONIAL_1_AUTHOR}}` | First testimonial author |
| `{{TESTIMONIAL_2}}` | Second testimonial quote |
| `{{TESTIMONIAL_2_AUTHOR}}` | Second testimonial author |
| `{{URGENCY_MESSAGE}}` | Scarcity/urgency text |
| `{{COUNTDOWN_DATE}}` | Expiration date (if applicable) |
| `{{LEAD_MAGNET_IMAGE}}` | Image of the free offer |
| `{{COMPANY_NAME}}` | Brand/company name |
| `{{PRIVACY_URL}}` | Privacy policy link |
| `{{TERMS_URL}}` | Terms of service link |

## Lead Magnet Types

This skill supports various lead magnet formats:

1. **Ebook** - Digital guide or report
2. **Checklist** - Printable or digital checklist
3. **Template** - Spreadsheet, Notion, or design template
4. **Quiz** - Interactive assessment with results delivered via email
5. **Free Tool** - Mini app or calculator
6. **Video Series** - Video course delivered via email
7. **Cheat Sheet** - Quick reference guide
8. **Swipe File** - Collection of examples

## Conversion Principles

### Headline Formulas
- "[Emotion] + [Specific Result] + [Timeframe]"
- Example: "Wake Up to 10x More Leads in 30 Days"
- "[Number] + [Specific Thing] + [in [Timeframe]]"
- Example: "7 Days to Your First 1,000 Email Subscribers"

### Form Best Practices
- Single field (email only) = highest conversion
- Place form above the fold
- Contrast button color from background
- Clear CTA: "Get My [Lead Magnet]" not "Submit"

### Above the Fold Must-Haves
1. Headline
2. Subheadline
3. Visual
4. Form

### Trust Elements Placement
- Before form (proof)
- After form (reassurance)

## File Structure

```
email-capture-generator/
├── SKILL.md                 # This file
├── templates/
│   ├── squeeze-page.html    # Basic squeeze page
│   ├── lead-magnet.html     # Detailed lead magnet page
│   └── thank-you.html       # Confirmation/thank you page
└── examples/
    ├── ebook-capture.md     # Example: ebook lead magnet
    ├── checklist-capture.md # Example: checklist lead magnet
```

## Example: Ebook Lead Magnet

**Lead Magnet:** "The Tiny Home Financing Guide"
**Target Audience:** Prospective tiny home buyers
**Primary Benefit:** Understanding financing options

```
HOOK:
- Headline: "Get Your Tiny Home Faster with the Financing Guide 90% of Buyers Miss"
- Subhead: "Discover the 7 financing strategies that helped 1,000+ families afford their dream tiny home"
- CTA: "Send Me The Guide"

VALUE:
- ✓ 7 proven financing strategies
- ✓ Comparison charts
- ✓ Lender contact list
- ✓ Mistakes to avoid

PROOF:
- "Join 5,000+ tiny home enthusiasts"
- Testimonial from satisfied reader

URGENCY:
- "This free guide is available for a limited time"

REASSURANCE:
- "We respect your privacy. No spam, ever."
```
