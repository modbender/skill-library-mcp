---
name: landing-page-builder
description: |
  Build a single-page landing page from a text prompt or design brief.

  USE WHEN:
  - User asks for a landing page, marketing page, product page, sales page, or startup website
  - User provides a business name/idea and wants a deployable web page
  - User sends an HTML template and wants it adapted with new content/branding
  - User asks for a "one-pager" or "single-page site"

  DON'T USE WHEN:
  - User wants a multi-page website (use a web framework instead)
  - User wants an email template or newsletter (different format/constraints)
  - User wants a blog, documentation site, or wiki
  - User wants to edit an existing live site (this builds new pages, not patches)
  - User wants a web app with backend logic, auth, or databases

  OUTPUTS: Single self-contained .html file (no external dependencies except Google Fonts). Ready to open in browser, deploy to any static host, or deliver to a client.

  INPUTS: Business name, what it does, target audience, desired tone. Optionally: a reference HTML template to adapt.
---

# Landing Page Builder

Generate polished, conversion-optimized landing pages from natural language descriptions.

## Workflow

### If user provides a reference HTML template:
1. Read the provided template
2. Identify all text content, branding, and copy
3. **Modify the existing template — do NOT rewrite from scratch**
4. Replace copy, brand name, colors, and content to match the user's brief
5. Preserve ALL CSS, animations, layout structure, SVG filters, and JavaScript exactly
6. Output the adapted `.html` file

### If no template provided:
1. Ask the user (if not provided): product/service name, what it does, target audience, desired tone
2. Read the base template at `assets/template.html`
3. Replace all `{{PLACEHOLDER}}` tokens with content tailored to the user's request
4. Customize colors, copy, sections — add or remove sections as needed
5. Output a single self-contained `.html` file

## Template Placeholders (base template only)

| Placeholder | Description |
|---|---|
| `{{TITLE}}` | Page `<title>` |
| `{{BRAND}}` | Brand/company name |
| `{{PRIMARY_COLOR}}` | Hex color (e.g., `#6366f1`) |
| `{{BG_COLOR}}` | Background color |
| `{{TEXT_COLOR}}` | Body text color |
| `{{ACCENT_COLOR}}` | Accent color |
| `{{HEADLINE}}` | Hero headline — punchy, benefit-driven |
| `{{SUBHEADLINE}}` | 1-2 sentence supporting text |
| `{{CTA_TEXT}}` | Button text (e.g., "Start Free Trial") |
| `{{CTA_URL}}` | Button link |
| `{{FEATURES_HEADING}}` | Section heading |
| `{{FEATURES}}` | HTML feature cards (use `.feature-card` divs) |
| `{{PRICING_HEADING}}` | Section heading |
| `{{PRICING_CARDS}}` | HTML pricing cards (use `.price-card` divs) |
| `{{TESTIMONIALS_HEADING}}` | Section heading |
| `{{TESTIMONIALS}}` | HTML testimonial cards (use `.testimonial` divs) |
| `{{FINAL_CTA_HEADING}}` | Bottom CTA heading |
| `{{FINAL_CTA_TEXT}}` | Bottom CTA description |
| `{{YEAR}}` | Current year |

## Design Principles

- Mobile-first responsive design
- Clean typography with Inter font
- Subtle shadows, rounded corners, generous whitespace
- Conversion-focused: clear hierarchy, single primary CTA repeated
- Fast: no JS frameworks, no external dependencies beyond Google Fonts
- Accessible: semantic HTML, good contrast ratios

## Common Mistakes to Avoid

- **Don't rewrite templates from scratch** — when adapting a reference, modify in place. Rewriting loses the design quality.
- **Don't use generic stock copy** — every line should feel specific to the business, not "lorem ipsum with nouns swapped in"
- **Don't add sections the user didn't ask for** — less is more. A tight 3-section page beats a bloated 8-section page.
- **Don't break responsive behavior** — test mentally that your changes work at mobile widths

## Customization

Feel free to:
- Add/remove entire sections (not all pages need pricing or testimonials)
- Change the grid layouts, add animations with CSS
- Swap the font via the Google Fonts link
- Add custom CSS variables for additional theming
- Embed forms, videos, or other interactive elements as needed

## Output

Save the final HTML file to the user's workspace or specified path. Suggest deployment options:
- **Quick:** Open locally or share the file
- **Free hosting:** GitHub Pages, Netlify, Vercel, Cloudflare Pages
- **Custom domain:** Pair with any of the above
