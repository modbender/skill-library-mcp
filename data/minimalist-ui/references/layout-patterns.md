# Layout Patterns

## App Shell

- Left rail: navigation + workspace switcher
- Main column: primary content/action
- Optional right rail: context, logs, metadata

## Width Strategy

- Reading-heavy views: max-width 840–920px
- Data/operator views: fluid with 12-col grid

## Hierarchy Pattern

1. Global title + primary action
2. Secondary controls (filters/sort/tabs)
3. Content region
4. Context/help region

## Density Modes

- Comfortable: 16px paddings, 44px control height
- Compact: 12px paddings, 36–40px control height

Default to comfortable; switch to compact for operator dashboards.

## Empty / Loading / Error

- Empty: explain why empty + one CTA
- Loading: skeletons sized to final layout
- Error: plain message + retry + fallback action
