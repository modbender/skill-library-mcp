---
description: "Implementation rules for iOS typography and type hierarchy"
---
# Typography

IOS TYPE SCALE (use system text styles — NEVER .system(size:)):

| Style          | Size | Weight   | SwiftUI                   | Use Case                        |
|----------------|------|----------|---------------------------|---------------------------------|
| Large Title    | 34pt | Regular  | .largeTitle               | Screen titles (NavigationStack) |
| Title          | 28pt | Regular  | .title                    | Section headers                 |
| Title 2        | 22pt | Regular  | .title2                   | Sub-section headers             |
| Title 3        | 20pt | Regular  | .title3                   | Card titles                     |
| Headline       | 17pt | Semibold | .headline                 | Row titles, emphasized labels   |
| Body           | 17pt | Regular  | .body                     | Primary content text            |
| Callout        | 16pt | Regular  | .callout                  | Secondary descriptions          |
| Subheadline    | 15pt | Regular  | .subheadline              | Supporting text, timestamps     |
| Footnote       | 13pt | Regular  | .footnote                 | Tertiary info, disclaimers      |
| Caption        | 12pt | Regular  | .caption                  | Metadata, labels                |
| Caption 2      | 11pt | Regular  | .caption2                 | Smallest readable text          |

HIERARCHY RULES:
- ONE .largeTitle per screen (via .navigationTitle with .large display mode).
- .headline for list row titles and card headings.
- .body for primary content paragraphs and descriptions.
- .subheadline or .caption for metadata (dates, counts, secondary info).
- Visual hierarchy: at least 2 levels of contrast per screen (e.g. .headline + .caption).

FONT WEIGHT GUIDANCE:
- .regular: body text, descriptions.
- .medium: subtle emphasis, tab labels.
- .semibold: section headers, row titles, buttons.
- .bold: primary action labels, important callouts.
- AVOID .ultraLight, .thin, .light — poor readability, especially on small screens.

FONT DESIGN:
- .fontDesign(.rounded): friendly, playful apps (fitness, kids, social).
- .fontDesign(.serif): editorial, premium (news, reading, luxury).
- .fontDesign(.monospaced): technical, developer tools, code display.
- .fontDesign(.default): neutral, professional (productivity, finance).
- Apply on outermost container — it cascades to all children.

DYNAMIC TYPE:
- System text styles automatically scale with user's accessibility settings.
- NEVER use .font(.system(size: N)) — it opts out of Dynamic Type.
- If a layout breaks at larger type sizes, use .minimumScaleFactor(0.8) as last resort.
- Test with largest accessibility size: Xcode → Environment Overrides → Dynamic Type.

LINE SPACING & READABILITY:
- System styles include appropriate leading — don't override unless necessary.
- For long-form text, .lineSpacing(4) improves readability.
- Maximum comfortable line length: ~70 characters. Use .frame(maxWidth: 600) for wide screens.

NUMBER & DATA DISPLAY:
- Use .monospacedDigit() for numbers that change (timers, counters, prices).
- This prevents layout jitter as digits change width.
- Example: Text(price).font(.title2).monospacedDigit()
