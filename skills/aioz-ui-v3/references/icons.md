---
name: aioz-ui-icons
description: Icon usage guide for AIOZ UI V3. Covers how to convert Figma MCP icon layer names into @aioz-ui/icon-react import names, how to size and color icons, and a reference list of common icons. Read this whenever the Figma MCP returns an icon layer name, or whenever you need to add an icon to a component.
---

# AIOZ UI V3 — Icons Reference

## Source

All icons come from **`@aioz-ui/icon-react`**. Never use SVG literals, emoji, Lucide directly, or any other icon library.

```tsx
import { Search01Icon, Plus01Icon, Wallet01Icon } from '@aioz-ui/icon-react'
```

---

## Figma MCP Layer Name → Import Name

### Transformation Rule (4 steps)

Given a Figma MCP icon layer name like `icon/24px/outline/wallet-01`:

1. **Strip the prefix** — drop everything up to and including the last `/`  
   `icon/24px/outline/wallet-01` → `wallet-01`

2. **Split on hyphens** → `["wallet", "01"]`

3. **PascalCase each segment** → `["Wallet", "01"]`

4. **Join + append `Icon`** → `Wallet01Icon`

### Examples

| Figma MCP Layer Name              | Import Name        |
| --------------------------------- | ------------------ |
| `icon/24px/outline/wallet-01`     | `Wallet01Icon`     |
| `icon/24px/outline/search-01`     | `Search01Icon`     |
| `icon/24px/outline/plus-01`       | `Plus01Icon`       |
| `icon/24px/outline/bar-chart-01`  | `BarChart01Icon`   |
| `icon/24px/outline/chevron-down`  | `ChevronDownIcon`  |
| `icon/24px/outline/chevron-up`    | `ChevronUpIcon`    |
| `icon/24px/outline/chevron-left`  | `ChevronLeftIcon`  |
| `icon/24px/outline/chevron-right` | `ChevronRightIcon` |
| `icon/24px/outline/trash-01`      | `Trash01Icon`      |
| `icon/24px/outline/eye-open`      | `EyeOpenIcon`      |
| `icon/24px/outline/eye-closed`    | `EyeClosedIcon`    |
| `icon/24px/outline/pencil-01`     | `Pencil01Icon`     |
| `icon/24px/outline/settings`      | `SettingsIcon`     |
| `icon/24px/outline/computer`      | `ComputerIcon`     |
| `icon/24px/outline/book-01`       | `Book01Icon`       |
| `icon/24px/outline/home-01`       | `Home01Icon`       |
| `icon/24px/outline/filter`        | `FilterIcon`       |
| `icon/24px/outline/arrow-down`    | `ArrowDownIcon`    |
| `icon/24px/outline/arrow-up`      | `ArrowUpIcon`      |
| `icon/24px/outline/arrow-left`    | `ArrowLeftIcon`    |
| `icon/24px/outline/arrow-right`   | `ArrowRightIcon`   |
| `icon/24px/outline/circle-check`  | `CircleCheckIcon`  |
| `icon/24px/outline/circle`        | `CircleIcon`       |
| `icon/24px/outline/download`      | `DownloadIcon`     |
| `icon/24px/outline/heart`         | `HeartIcon`        |
| `icon/24px/fill/search-01`        | `Search01Icon`     |

> The `outline` / `fill` / `16px` / `24px` prefix segments are all stripped — only the final segment matters.

---

## Usage

### Standard Usage

```tsx
import { Search01Icon } from '@aioz-ui/icon-react'
;<Search01Icon size={16} className="text-icon-neutral" />
```

### Props

| Prop        | Type     | Default | Description                         |
| ----------- | -------- | ------- | ----------------------------------- |
| `size`      | `number` | `24`    | Width and height in px              |
| `className` | `string` | —       | Tailwind class — use for color only |

### Coloring Icons

Icons inherit color via `currentColor`. Always use a design token class:

```tsx
// Standard icon color
<Search01Icon size={16} className="text-icon-neutral" />

// Icon on a colored surface
<TrashIcon size={16} className="text-onsf-text-error" />

// Icon inside a success badge
<CircleCheckIcon size={16} className="text-onsf-text-success" />

// Brand icon
<Wallet01Icon size={16} className="text-onsf-text-pri" />

// Muted icon
<FilterIcon size={14} className="text-content-sec" />
```

### Icon Sizes by Context

| Context                  | Size  |
| ------------------------ | ----- |
| Button (sm)              | 14    |
| Button (md)              | 16    |
| Button (lg)              | 16–18 |
| Table header sort/filter | 14    |
| Sidebar nav item         | 16    |
| Inline body text         | 14–16 |
| Badge                    | 14–16 |
| Avatar overlay (lg)      | 14    |
| Avatar overlay (xl+)     | 16    |
| Tooltip left icon        | 20    |

---

## Common Icon Reference List

```tsx
// Navigation
import {
  Home01Icon,
  BarChart01Icon,
  ComputerIcon,
  Wallet01Icon,
  Book01Icon,
  SettingsIcon,
} from '@aioz-ui/icon-react'

// Actions
import {
  Plus01Icon,
  Pencil01Icon,
  Trash01Icon,
  DownloadIcon,
  Search01Icon,
  FilterIcon,
} from '@aioz-ui/icon-react'

// Arrows & Chevrons
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
} from '@aioz-ui/icon-react'
import {
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@aioz-ui/icon-react'

// Status
import { CircleCheckIcon, CircleIcon, HeartIcon } from '@aioz-ui/icon-react'

// Visibility
import { EyeOpenIcon, EyeClosedIcon } from '@aioz-ui/icon-react'
```

---

## What NOT to Do

```tsx
// ❌ SVG literal
<svg viewBox="0 0 24 24"><path d="..." /></svg>

// ❌ Emoji
<span>🔍</span>

// ❌ Lucide directly
import { Search } from 'lucide-react'

// ❌ Wrong naming — no "Icon" suffix
import { Search01 } from '@aioz-ui/icon-react'

// ❌ Raw color on icon
<Search01Icon size={16} className="text-gray-400" />

// ✅ Correct
import { Search01Icon } from '@aioz-ui/icon-react'
<Search01Icon size={16} className="text-icon-neutral" />
```
