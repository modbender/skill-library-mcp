---
name: aioz-ui-colors
description: Color token mapping for AIOZ UI V3. Maps Figma MCP component token names (e.g. --text-neu-bold, --sf-neu-block, --onsf-suc-default) to Tailwind CSS utility classes from tw-inline.css. Use this whenever the Figma MCP returns a color/fill token and you need the correct Tailwind class to apply.
---

# AIOZ UI V3 – Color Token → Tailwind Class Reference

**How to use:** When Figma MCP returns a fill, stroke, or text color token name, find it in the table below and use the corresponding Tailwind class.

## Color Token Map

**Input:** Figma MCP slash-path token  
**Output:** CSS variable → Tailwind class to use in `className`

### Figma Token → CSS Variable → Tailwind Class

| Figma MCP Token (slash format) | CSS Variable                               | Tailwind Class                          |
| ------------------------------ | ------------------------------------------ | --------------------------------------- |
| `Background/Bg-Screen`         | `--color-sf-screen`                        | `bg-sf-screen`                          |
| `Background/Bg-Muted`          | `--color-sf-muted`                         | `bg-sf-muted`                           |
| `Background/Bg-Object`         | `--color-sf-object`                        | `bg-sf-object`                          |
| `Text/Neu-Bold`                | `--color-title-neutral`                    | `text-title-neutral`                    |
| `Text/Neu-Pri`                 | `--color-text-neutral`                     | `text-title-neutral`                    |
| `Text/Neu-Body`                | `--color-text-neutral-body`                | `text-text-neutral-body`                |
| `Text/Neu-Mute`                | `--color-main-caption`                     | `text-content-sec`                      |
| `Text/Neu-White`               | `--color-text-neutral`                     | `text-white`                            |
| `Text/Brand`                   | `--color-text-brand`                       | `text-text-brand`                       |
| `Text/Brand-On item`           | `--color-text-brand-on-item`               | `text-text-brand-on-item`               |
| `Text/Suc-Pri`                 | `--color-text-success`                     | `text-text-success`                     |
| `Text/Warn-Pri`                | `--color-text-warning`                     | `text-text-warning`                     |
| `Text/Error-Pri`               | `--color-text-error`                       | `text-text-error`                       |
| `Text/Info-Pri`                | `--color-text-info`                        | `text-text-info`                        |
| `Onsf/Bra/Default`             | `--color-onsf-text-pri`                    | `text-onsf-text-pri`                    |
| `Onsf/Bra/Hover`               | `--color-onsf-text-pri-hover`              | `text-onsf-text-pri-hover`              |
| `Onsf/Bra/Pressed`             | `--color-onsf-text-pri-pressed`            | `text-onsf-text-pri-pressed`            |
| `Onsf/Bra/Dark`                | `--color-onsf-text-pri-dark`               | `text-onsf-text-pri-dark`               |
| `Onsf/Neu/Default`             | `--color-onsf-text-neutral`                | `text-onsf-text-neutral`                |
| `Onsf/Neu/Hover`               | `--color-onsf-text-neutral-hover`          | `text-onsf-text-neutral-hover`          |
| `Onsf/Neu/Pressed`             | `--color-onsf-text-neutral-pressed`        | `text-onsf-text-neutral-pressed`        |
| `Onsf/Neu/Focus`               | `--color-onsf-text-neutral-focus`          | `text-onsf-text-neutral-focus`          |
| `Onsf/Neu/Grey`                | `--color-onsf-text-neutral-grey`           | `text-onsf-text-neutral-grey`           |
| `Onsf/Neu/Lightgrey`           | `--color-onsf-text-neutral-lightgrey`      | `text-onsf-text-neutral-lightgrey`      |
| `Onsf/Error/Default`           | `--color-onsf-text-error`                  | `text-onsf-text-error`                  |
| `Onsf/Error/Hover`             | `--color-onsf-text-error-hover`            | `text-onsf-text-error-hover`            |
| `Onsf/Error/Pressed`           | `--color-onsf-text-error-pressed`          | `text-onsf-text-error-pressed`          |
| `Onsf/Error/Focus`             | `--color-onsf-text-error-focus`            | `text-onsf-text-error-focus`            |
| `Onsf/Suc/Default`             | `--color-onsf-text-success`                | `text-onsf-text-success`                |
| `Onsf/Suc/Hover`               | `--color-onsf-text-success-hover`          | `text-onsf-text-success-hover`          |
| `Onsf/Suc/Pressed`             | `--color-onsf-text-success-pressed`        | `text-onsf-text-success-pressed`        |
| `Onsf/Suc/Focus`               | `--color-onsf-text-success-focus`          | `text-onsf-text-success-focus`          |
| `Onsf/Warn/Default`            | `--color-onsf-text-warning`                | `text-onsf-text-warning`                |
| `Onsf/Warn/Hover`              | `--color-onsf-text-warning-hover`          | `text-onsf-text-warning-hover`          |
| `Onsf/Warn/Pressed`            | `--color-onsf-text-warning-pressed`        | `text-onsf-text-warning-pressed`        |
| `Onsf/Warn/Focus`              | `--color-onsf-text-warning-focus`          | `text-onsf-text-warning-focus`          |
| `Onsf/Info/Default`            | `--color-onsf-text-info`                   | `text-onsf-text-info`                   |
| `Onsf/Info/Hover`              | `--color-onsf-text-info-hover`             | `text-onsf-text-info-hover`             |
| `Onsf/Info/Pressed`            | `--color-onsf-text-info-pressed`           | `text-onsf-text-info-pressed`           |
| `Onsf/Info/Focus`              | `--color-onsf-text-info-focus`             | `text-onsf-text-info-focus`             |
| `Onsf/Disable/Disable`         | `--color-onsf-text-disable`                | `text-onsf-text-disable`                |
| `Onsf/Fix color/Neu`           | `--color-onsf-text-neutral-fix-on-neutral` | `text-onsf-text-neutral-fix-on-neutral` |
| `Onsf/Fix color/White`         | `--color-text-neutral`                     | `text-white`                            |
| `Onsf/Fix color/Pri`           | `--color-onsf-text-brand-fix-on-sec`       | `text-onsf-text-brand-fix-on-sec`       |
| `Onsf/Warning`                 | `--color-onsf-warning`                     | `text-onsf-text-warning`                |
| `Sf/Neu/Block`                 | `--color-sf-neutral-block`                 | `bg-sf-neutral-block`                   |
| `Sf/Neu/Default`               | `--color-sf-neutral`                       | `bg-sf-neutral`                         |
| `Sf/Neu/Light-Hover`           | `--color-sf-neutral-light`                 | `bg-sf-neutral-light`                   |
| `Sf/Neu/Hover`                 | `--color-sf-neutral-hover`                 | `bg-sf-neutral-hover`                   |
| `Sf/Neu/Pressed`               | `--color-sf-neutral-pressed`               | `bg-sf-neutral-pressed`                 |
| `Sf/Neu/Focus`                 | `--color-sf-neutral-focus`                 | `bg-sf-neutral-focus`                   |
| `Sf/Pri/Pri`                   | `--color-sf-pri`                           | `bg-sf-pri`                             |
| `Sf/Pri/Pri-Hover`             | `--color-sf-pri-hover`                     | `bg-sf-pri-hover`                       |
| `Sf/Pri/Pri-Pressed`           | `--color-sf-pri-pressed`                   | `bg-sf-pri-pressed`                     |
| `Sf/Pri/Sec-Default`           | `--color-sf-sec`                           | `bg-sf-sec`                             |
| `Sf/Pri/Sec-Hover`             | `--color-sf-sec-hover`                     | `bg-sf-sec-hover`                       |
| `Sf/Pri/Sec-Focus`             | `--color-sf-sec-focus`                     | `bg-sf-sec-focus`                       |
| `Sf/Pri/Sec-Pressed`           | `--color-sf-sec-pressed`                   | `bg-sf-sec-pressed`                     |
| `Sf/Suc/Pri-Default`           | `--color-sf-success-pri`                   | `bg-sf-success-pri`                     |
| `Sf/Suc/Pri-Hover`             | `--color-sf-success-pri-hover`             | `bg-sf-success-pri-hover`               |
| `Sf/Suc/Sec-Default`           | `--color-sf-success-sec`                   | `bg-sf-success-sec`                     |
| `Sf/Error/Pri-Default`         | `--color-sf-error-pri`                     | `bg-sf-error-pri`                       |
| `Sf/Error/Sec-Default`         | `--color-sf-error-sec`                     | `bg-sf-error-sec`                       |
| `Sf/Error/Sec-Hover`           | `--color-sf-error-sec-hover`               | `bg-sf-error-sec-hover`                 |
| `Sf/Error/Sec-Pressed`         | `--color-sf-error-sec-pressed`             | `bg-sf-error-sec-pressed`               |
| `Sf/Error/Sec-Focus`           | `--color-sf-error-sec-focus`               | `bg-sf-error-sec-focus`                 |
| `Sf/Warn/Pri-Default`          | `--color-sf-warning-pri`                   | `bg-sf-warning-pri`                     |
| `Sf/Warn/Sec-Default`          | `--color-sf-warning-sec`                   | `bg-sf-warning-sec`                     |
| `Sf/Info/Pri-Default`          | `--color-sf-info-pri`                      | `bg-sf-info-pri`                        |
| `Sf/Info/Sec-Default`          | `--color-sf-info-sec`                      | `bg-sf-info-sec`                        |
| `Sf/Disable/Sf-Disable`        | `--color-sf-disable`                       | `bg-sf-disable`                         |
| `Border/Neu/Default`           | `--color-border-neutral`                   | `border-border-neutral`                 |
| `Border/Neu/Black`             | `--color-border-neutral`                   | `border-border-neutral`                 |
| `Border/Neu/Grey`              | `--color-border-neutral-grey`              | `border-border-neutral-grey`            |
| `Border/Neu/Light grey`        | `--color-border-neutral-light-grey`        | `border-border-neutral-light-grey`      |
| `Border/Neu/Hover`             | `--color-border-neutral-hover`             | `border-border-neutral-hover`           |
| `Border/Neu/Pressed`           | `--color-border-neutral-pressed`           | `border-border-neutral-pressed`         |
| `Border/Neu/Neu-Focus`         | `--color-border-neutral-focus`             | `border-border-neutral-focus`           |
| `Border/Pri/Default`           | `--color-border-pri`                       | `border-border-pri`                     |
| `Border/Pri/Hover`             | `--color-border-pri-hover`                 | `border-border-pri-hover`               |
| `Border/Pri/Pressed`           | `--color-border-pri-pressed`               | `border-border-pri-pressed`             |
| `Border/Pri/Pri-Focus`         | `--color-border-pri-focus`                 | `border-border-pri-focus`               |
| `Border/Suc/Default`           | `--color-border-success`                   | `border-border-success`                 |
| `Border/Suc/Hover`             | `--color-border-success-hover`             | `border-border-success-hover`           |
| `Border/Error/Default`         | `--color-border-error`                     | `border-border-error`                   |
| `Border/Error/Hover`           | `--color-border-error-hover`               | `border-border-error-hover`             |
| `Border/Warn/Default`          | `--color-border-warning`                   | `border-border-warning`                 |
| `Border/Info/Default`          | `--color-border-info`                      | `border-border-info`                    |
| `Border/Disable/Disable`       | `--color-border-disable`                   | `border-border-disable`                 |

**Tailwind class prefix rule:**

- Token starts with `Text/` or `Onsf/` → prefix with `text-`
- Token starts with `Sf/` or `Background/` → prefix with `bg-`
- Token starts with `Border/` → prefix with `border-`

---

## Common Component Patterns

```tsx
// Page shell
<div className="min-h-screen bg-sf-screen">

// Card
<div className="bg-sf-object border border-border-neutral rounded-2xl p-6">

// Sidebar nav block
<nav className="bg-sf-neutral-block border-r border-border-neutral">

// Icon
<SomeIcon size={16} className="text-icon-neutral" />
```
