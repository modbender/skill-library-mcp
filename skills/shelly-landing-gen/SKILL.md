---
name: Landing Page Generator
version: 1.0.0
description: Generate complete, responsive HTML landing pages from a product name, tagline, and description. Clean CSS, mobile-ready, with hero, features, CTA, and footer sections.
---

# Landing Page Generator 🦞

Generate beautiful, responsive HTML landing pages instantly.

## Usage

```bash
bash generate.sh "Product Name" "Your Tagline" "A longer description of your product."
```

### Arguments

| # | Arg | Description |
|---|-----|-------------|
| 1 | Product Name | The name shown in the hero and title |
| 2 | Tagline | Short catchy phrase for the hero |
| 3 | Description | Longer text used in the features/about section |

### Output

Prints a complete, self-contained HTML file to stdout. Redirect to save:

```bash
bash generate.sh "Acme" "Build faster" "Acme helps you ship." > page.html
```

### Features of Generated Pages

- Responsive design (mobile-first)
- Hero section with CTA button
- Features grid (3 columns)
- Call-to-action banner
- Footer with copyright
- Modern gradient styling, no external dependencies
