---
description: "Implementation rules for color contrast and accessible color usage"
---
# Color & Contrast

CONTRAST RATIO REQUIREMENTS (WCAG 2.1 / Apple HIG):
- Normal text (<20pt): minimum 4.5:1 contrast ratio.
- Large text (20pt+ regular or 14pt+ bold): minimum 3:1 contrast ratio.
- Preferred: 7:1 for maximum readability.
- UI components (icons, borders, controls): minimum 3:1 against background.

SEMANTIC COLOR USAGE:
- Red (.red / destructive): delete, remove, error, critical alert.
- Green (.green): success, complete, enabled, positive.
- Orange (.orange): warning, caution, attention needed.
- Blue (.blue): informational, links, primary actions.
- NEVER use red for positive actions or green for destructive actions.

NEVER RELY ON COLOR ALONE:
- Status indicators: color + icon + text label (e.g. green circle + checkmark + "Complete").
- Error fields: red border + error icon + error message text.
- Charts/graphs: use patterns, shapes, or labels alongside color coding.
- Colorblindness: avoid red/green as the sole differentiator — use red/blue or add shapes.

SYSTEM ADAPTIVE COLORS:
- .primary: adapts to light/dark automatically — use for main text.
- .secondary: lighter text for subtitles, metadata.
- Color(.systemBackground): adapts to system appearance.
- These work well for structural elements; use AppTheme for brand colors.

DARK MODE COLOR PAIRING:
- Every custom color must have both light and dark variants.
- Light mode: dark text on light backgrounds.
- Dark mode: light text on dark backgrounds.
- Both variants must independently meet contrast requirements.
- Test both modes — a color that works in light may fail in dark.

APPTHEME COLOR PATTERNS:
- Use Color(light:dark:) extension when app has appearance switching.
- Use plain Color(hex:) when no dark mode support.
- Define semantic tokens: AppTheme.Colors.primary, .surface, .error, .success.
- NEVER use raw hex strings in views — always reference AppTheme tokens.

TEXT ON IMAGES/GRADIENTS:
- Add a dark overlay (.black.opacity(0.4)) before placing white text on images.
- Or use .shadow(color: .black.opacity(0.3), radius: 2) on text.
- Never place light text on light images without contrast treatment.

OPACITY GUIDELINES:
- Avoid text below .opacity(0.6) — fails contrast requirements.
- Disabled state: use .disabled() modifier (auto-handles opacity correctly).
- Placeholder text: use .foregroundStyle(.secondary) instead of manual opacity.
