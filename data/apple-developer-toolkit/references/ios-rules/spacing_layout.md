---
description: "Implementation rules for spacing, layout grid, and tap targets"
---
# Spacing & Layout

8-POINT GRID SYSTEM:
All spacing values must be multiples of 4pt. Standard scale:

| Token             | Value | Use Case                                    |
|-------------------|-------|---------------------------------------------|
| Spacing.xxSmall   | 4pt   | Icon-to-label gap, tight inline spacing     |
| Spacing.xSmall    | 8pt   | Between related items (label + value)        |
| Spacing.small     | 12pt  | List row internal padding                    |
| Spacing.medium    | 16pt  | Standard padding, outer margins              |
| Spacing.large     | 24pt  | Section spacing, card-to-card gap            |
| Spacing.xLarge    | 32pt  | Major section breaks                         |
| Spacing.xxLarge   | 48pt  | Screen-level top/bottom breathing room       |

NEVER use arbitrary values (5, 7, 10, 13, 15, 18, 25, etc.). Snap to the grid.

STANDARD MARGINS:
- Outer screen margins: 16pt (.padding(.horizontal, AppTheme.Spacing.medium)).
- Card internal padding: 16pt (.padding(AppTheme.Spacing.medium)).
- Section spacing (between groups): 24pt.
- List row vertical padding: 12pt.
- Toolbar/header spacing: 16pt horizontal, 8pt vertical.

TAP TARGET SIZES:
- Minimum: 44x44pt for ALL interactive elements (Apple HIG requirement).
- If visual element is smaller (e.g. 24x24 icon), expand hit area:
  .frame(minWidth: 44, minHeight: 44)
  .contentShape(Rectangle())
- Inline buttons in text: ensure surrounding padding creates 44pt height.
- Icon buttons: use .frame(width: 44, height: 44) even if icon is 20-24pt.

VERTICAL RHYTHM:
- Consistent spacing within a section (all rows use same gap).
- Larger gap between sections than within sections.
- Example: 8pt between rows within a section, 24pt between sections.
- Headers get extra top spacing: 32pt above, 8pt below.

DENSITY GUIDELINES (from plan's design.density):
- "spacious": Use .large/.xLarge gaps. Generous padding (20-24pt). Best for meditation, health, reading apps.
- "standard": Use .medium gaps. 16pt padding. Default for most apps.
- "compact": Use .small/.xSmall gaps. 12pt padding. Best for data-heavy apps (finance, productivity).

CARD LAYOUT PATTERN:
```swift
VStack(alignment: .leading, spacing: AppTheme.Spacing.xSmall) {
    // Card content
}
.padding(AppTheme.Spacing.medium)
.background(AppTheme.Colors.surface)
.clipShape(RoundedRectangle(cornerRadius: AppTheme.Style.cornerRadius))
.shadow(color: .black.opacity(0.06), radius: 8, y: 4)
```

HORIZONTAL LAYOUTS:
- Space between icon and label: 8pt.
- Space between label and trailing value: use Spacer().
- Button bar with 2-3 buttons: HStack with spacing: 12pt.
- 4+ buttons: wrap in ScrollView(.horizontal).

SAFE AREA:
- Content respects safe areas by default — don't add redundant padding.
- Full-screen backgrounds use .ignoresSafeArea() to extend edge-to-edge.
- Overlays use .safeAreaInset(edge:) — never manual padding for safe areas.
