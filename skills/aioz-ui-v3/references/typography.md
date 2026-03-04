---
name: aioz-ui-typography
description: Typography utility reference for AIOZ UI V3 with Tailwind CSS v4.
---

# AIOZ UI V3 – Typography Reference

Each utility bakes in font-size + line-height + font-weight + font-family. **Never** add manual font-size overrides on top.

---

## Font Families

| Token                | Value                            |
| -------------------- | -------------------------------- |
| `font-neue`          | PP Neue Montreal (default)       |
| `font-formula`       | PP Formula (display titles only) |
| `font-fraktion-mono` | PP Fraktion Mono (code/mono)     |

## Figma MCP → Tailwind Mapping

**Input:** Figma MCP typography style name  
**Output:** Tailwind class

| Figma MCP Style  | Tailwind Class        |
| ---------------- | --------------------- |
| `Title/01`       | `text-title-01`       |
| `Title/02`       | `text-title-02`       |
| `Title/03`       | `text-title-03`       |
| `Title/04`       | `text-title-04`       |
| `Subheadline/01` | `text-subheadline-01` |
| `Subheadline/02` | `text-subheadline-02` |
| `Subheadline/03` | `text-subheadline-03` |
| `Body/00`        | `text-body-00`        |
| `Body/01`        | `text-body-01`        |
| `Body/02`        | `text-body-02`        |
| `Body/03`        | `text-body-03`        |
| `Body/00 Link`   | `text-body-00-link`   |
| `Body/01 Link`   | `text-body-01-link`   |
| `Body/02 Link`   | `text-body-02-link`   |
| `Body/03 Link`   | `text-body-03-link`   |
| `Caption`        | `text-caption`        |
| `Caption Link`   | `text-caption-link`   |
| `Button/00`      | `text-button-00`      |
| `Bold Button/00` | `text-bold-button-00` |
| `Button/01`      | `text-button-01`      |
| `Bold Button/01` | `text-bold-button-01` |
| `Button/02`      | `text-button-02`      |
| `Bold Button/02` | `text-bold-button-02` |
| `Mono/01`        | `text-mono-01`        |
| `Mono/02`        | `text-mono-02`        |

> Typography utilities already include font-size, line-height, weight, and font-family. **Never** add `text-sm`, `font-medium`, or `leading-*` on top.

## Size Heuristic (when Figma gives px without name)

| px   | Regular         | Medium/Bold           |
| ---- | --------------- | --------------------- |
| 32px | `text-title-01` | `text-title-01`       |
| 24px | `text-title-02` | `text-title-02`       |
| 20px | `text-body-00`  | `text-title-03`       |
| 18px | —               | `text-title-04`       |
| 16px | `text-body-01`  | `text-subheadline-01` |
| 14px | `text-body-02`  | `text-subheadline-02` |
| 12px | `text-body-03`  | `text-subheadline-03` |
| 10px | `text-caption`  | `text-caption-link`   |

## Typography × Color Pairings (common usage)

```tsx
<h1 className="text-title-03 text-title-neutral">Page Title</h1>
// Section subheading
<h2 className="text-subheadline-01 text-title-neutral">Section</h2>

```

## Anti-Patterns

```tsx
// ❌ Never reconstruct typography with raw utilities
<p className="text-sm font-medium leading-5 font-sans">Text</p>
<h1 className="text-4xl font-bold tracking-tight">Title</h1>
<span className="text-xs text-gray-500">Caption</span>

// ✅ Always use the design system typography class
<p className="text-body-02 text-text-neutral-body">Text</p>
<h1 className="text-title-03 text-title-neutral">Title</h1>
<span className="text-main-caption text-content-sec">Caption</span>
```
