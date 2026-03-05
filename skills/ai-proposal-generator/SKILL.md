---
name: ai-proposal-generator
description: Generate professional HTML proposals from meeting notes. Features 5 proposal styles (Corporate, Entrepreneur, Creative, Consultant, Minimal), 6+ color themes, and a Design Wizard for custom templates. Triggers on "create proposal", "proposal for [client]", "proposal wizard", "proposal from [notes]", "show proposal styles", "finalize proposal". Integrates with ai-meeting-notes for context. Outputs beautiful, responsive HTML ready to send or export as PDF.
---

# AI Proposal Generator

Generate professional, beautifully-designed HTML proposals from meeting notes in minutes.

## System Overview

```
Meeting Notes + Your Template + Color Theme = Professional HTML Proposal
```

## File Locations

```
proposals/
├── templates/           ← Style templates (markdown structure)
│   ├── corporate.md
│   ├── entrepreneur.md
│   ├── creative.md
│   ├── consultant.md
│   ├── minimal.md
│   └── custom/          ← User-created templates
├── themes/              ← Color themes (CSS)
│   ├── ocean-blue.css
│   ├── ember-orange.css
│   ├── forest-green.css
│   ├── slate-dark.css
│   ├── royal-purple.css
│   ├── trust-navy.css
│   └── custom/          ← User-created themes
├── generated/           ← Output proposals
│   ├── YYYY-MM-DD_client-name.md    ← Draft
│   └── YYYY-MM-DD_client-name.html  ← Final
└── SERVICES.md          ← User's pricing/packages
```

## Trigger Phrases

| Phrase | Action |
|--------|--------|
| `"create proposal for [client]"` | Generate proposal, pull from recent meeting notes |
| `"proposal from [file]"` | Generate from specific meeting notes file |
| `"proposal wizard"` | Launch Design Wizard to create/customize template |
| `"show proposal styles"` | Display all 5 styles with descriptions |
| `"show color themes"` | Display all color themes with previews |
| `"change style to [x]"` | Switch proposal style |
| `"change theme to [x]"` | Switch color theme |
| `"preview proposal"` | Show current draft |
| `"edit [section]"` | Modify specific section |
| `"finalize proposal"` | Generate final HTML |
| `"export pdf"` | Convert HTML to PDF |

## Proposal Styles

### 1. Corporate
**Tone:** Formal, structured, trust-building
**Best for:** Enterprise clients, B2B, government, large organizations
**Sections:** Cover Page, Executive Summary, Company Overview, Understanding Your Needs, Proposed Solution, Methodology, Project Team, Timeline, Investment, Terms, Appendix

### 2. Entrepreneur
**Tone:** Bold, direct, action-oriented
**Best for:** Startups, SMBs, fast-moving founders
**Sections:** The Problem, The Solution, What You Get, How It Works, Investment, Why Us, Let's Go

### 3. Creative
**Tone:** Visual, modern, portfolio-focused
**Best for:** Agencies, designers, marketing, creative services
**Sections:** The Vision, Your Challenges, Our Approach, The Work, Case Studies, Timeline, Investment, The Team, Next Steps

### 4. Consultant
**Tone:** Professional, advisory, expertise-led
**Best for:** Coaches, consultants, advisors, professional services
**Sections:** Situation Analysis, Key Challenges, Recommendations, Engagement Options, Expected Outcomes, Credentials, Investment, Next Steps

### 5. Minimal
**Tone:** Clean, simple, no-fluff
**Best for:** Freelancers, small projects, retainers, quick quotes
**Sections:** Project Overview, Scope, Timeline, Investment, Terms, Accept

## Color Themes

| Theme | Primary | Accent | Background | Vibe |
|-------|---------|--------|------------|------|
| **Ocean Blue** | `#0ea5e9` | `#0284c7` | Light | Professional, trustworthy |
| **Ember Orange** | `#ff6b35` | `#ff8c42` | Light/Dark | Bold, energetic |
| **Forest Green** | `#22c55e` | `#16a34a` | Light | Growth, natural |
| **Slate Dark** | `#1e293b` | `#475569` | Dark | Modern, sophisticated |
| **Royal Purple** | `#8b5cf6` | `#7c3aed` | Light | Creative, premium |
| **Trust Navy** | `#1e3a5f` | `#2563eb` | Light | Corporate, established |

## Design Wizard

Triggered by `"proposal wizard"` — 6-step guided template creation:

**Step 1 — Business Type:** Agency, Consulting, Tech, Freelance, Professional, Other
**Step 2 — Typical Clients:** Enterprise, SMB, Startups, Individuals, Mix
**Step 3 — Tone:** Formal, Friendly, Bold, Minimal
**Step 4 — Sections:** Multi-select from 12 options
**Step 5 — Style:** Recommend based on answers or let user choose
**Step 6 — Color Theme:** Select from 6 themes or custom

Output: Saves custom template to `proposals/templates/custom/[name].md`

### Wizard Output Format
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TEMPLATE CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Name: [template-name]
🎨 Style: [style] | Theme: [theme]
📝 Sections: [list]

📁 Saved: proposals/templates/custom/[name].md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Proposal Generation

### Step 1: Gather Context
1. Search `meeting-notes/` for client name
2. Check `MEMORY.md` for client history
3. Load `proposals/SERVICES.md` for pricing
4. Ask user to fill gaps

### Step 2: Generate Draft
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 PROPOSAL DRAFT — [Client Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Context: meeting-notes/[file]
✅ Template: [style] | Theme: [color]
✅ Pricing: [package]

📁 Draft: proposals/generated/[date]_[client].md

Commands: "show", "edit [section]", "preview html", "finalize"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Edit & Refine
- `"edit executive summary"` → Rewrite section
- `"make it more formal"` → Adjust tone
- `"add testimonials"` → Insert section
- `"change price to $5,000"` → Update pricing

### Step 4: Finalize
Generate HTML using base template + theme CSS:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PROPOSAL FINALIZED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 [Client] Proposal
📁 HTML: proposals/generated/[date]_[client].html

Ready to send, export PDF, or download.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## HTML Generation

### Base Template
Use `assets/proposal-template.html` as foundation:
- Inject markdown content converted to HTML
- Apply theme CSS variables
- Apply style-specific layout classes

### Style Classes
- `.proposal-corporate` — Serif headers, formal spacing, bordered sections
- `.proposal-entrepreneur` — Bold headers, high contrast, CTA-focused
- `.proposal-creative` — Asymmetric layout, visual emphasis, portfolio grid
- `.proposal-consultant` — Clean lines, advisory tone, option cards
- `.proposal-minimal` — Maximum whitespace, essential typography only

### Requirements
- Mobile-responsive
- Print-ready (clean page breaks)
- PDF-exportable

## SERVICES.md Template

```markdown
# Services & Pricing

## Packages

### Starter — $X,XXX/month
- [Deliverable]

### Growth — $X,XXX/month
- Everything in Starter
- [Additional]

### Scale — $X,XXX/month
- Everything in Growth
- [Additional]

## Terms
- Payment: [Net 15, 50% upfront, etc.]
```

## Integration

### From ai-meeting-notes
Extract: Client name, pain points, scope discussed, budget hints, timeline, decision makers

### To ai-daily-briefing
Pending proposals appear in briefing as action items

## Default Pairings

| Client Type | Style | Theme |
|-------------|-------|-------|
| Enterprise | Corporate | Trust Navy |
| Startup | Entrepreneur | Ember Orange |
| Agency | Creative | Royal Purple |
| SMB | Consultant | Ocean Blue |
| Quick project | Minimal | Slate Dark |

## Error Handling

**No meeting notes:** Offer to create from scratch or paste notes
**No SERVICES.md:** Help create or allow manual pricing
**No template:** Prompt wizard or suggest built-in style
