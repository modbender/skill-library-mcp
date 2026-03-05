---
name: aioz-ui-v3
description: Build UI components and pages using AIOZ UI V3 design system. Use this skill whenever the user wants to create, edit, or style React components using AIOZ UI tokens, Tailwind classes, color tokens, typography utilities, icons from @aioz-ui/icon-react, or chart components (LineChart, AreaChart, BarChart, DonutChart). Trigger on any task involving AIOZ UI components, design tokens like --sf-neu-block or --text-neu-bold, brand colors, typography classes (text-title-01, text-body-02), icon imports, data visualization, or translating Figma MCP output into production-ready code.
---

# AIOZ UI V3 — Figma MCP → Code Mapping Skill

This skill defines exactly how to translate **Figma MCP output** into production React code using the AIOZ UI V3 design system.

> **Rule #1:** Never guess token names or class names. Always follow the mapping tables below.

---

## How Figma MCP Returns Data

When the Figma MCP agent inspects a node, it returns values in these formats:

| Data Type      | Figma MCP Example                                   | Action                                  |
| -------------- | --------------------------------------------------- | --------------------------------------- |
| Color / fill   | `Onsf/Error/Default`, `Sf/Pri/Pri`                  | → Look up in `references/colors.md`     |
| Typography     | `Button/01`, `Body/02`, `Subheadline/01`            | → Look up in `references/typography.md` |
| Icon layer     | `icon/24px/outline/wallet-01`                       | → Look up in `references/icons.md`      |
| Component name | `Button/Primary`, `Badge/Success`, `Fields/Default` | → See **Component Map** below           |
| Variant string | `Type=Primary, Size=Medium, Shape=Square`           | → See **Variant → Prop Map** below      |
| Variable value | `"Onsf/Bra/Default": "#121212"`                     | Slash-path format, never CSS `--var`    |
| Setup / config | Project configuration questions                     | → Look up in `references/setup.md`      |

> ⚠️ Figma MCP always returns token names with **slash separators** like `Onsf/Error/Default`.
> It does **NOT** return CSS custom property format like `--onsf-error-default`.

---

## ⚠️ Two Import Paths — Never Mix Them

```tsx
// Charts — @aioz-ui/core/components
import {
  LineChart,
  AreaChart,
  BarChart,
  DonutChart,
  CustomLegend,
  Separator,
  useSeriesVisibility,
} from '@aioz-ui/core/components'

// All other UI components — @aioz-ui/core-v3/components
import {
  Button,
  Input,
  Badge,
  Table,
  Header,
  Body,
  Row,
  HeadCell,
  Cell,
} from '@aioz-ui/core-v3/components'

// Icons — @aioz-ui/icon-react (always PascalCase + "Icon" suffix)
import { Search01Icon, Plus01Icon, Wallet01Icon } from '@aioz-ui/icon-react'
```

---

## Component Map

**Input:** Figma MCP `name` field on a symbol/instance node
**Output:** React component to use

| Figma Node Name Pattern | React Component   | Import                                                                                                                      |
| ----------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `Button/*`              | `Button`          | `import { Button } from '@aioz-ui/core-v3/components'`                                                                      |
| `Fields/*`              | `Input`           | `import { Input } from '@aioz-ui/core-v3/components'`                                                                       |
| `Badge/*`               | `Badge`           | `import { Badge } from '@aioz-ui/core-v3/components'`                                                                       |
| `Tag/*`                 | `Tag`             | `import { Tag } from '@aioz-ui/core-v3/components'`                                                                         |
| `Card/*`                | `Card`            | `import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@aioz-ui/core-v3/components'`                   |
| `Toggle/*`              | `Switch`          | `import { Switch } from '@aioz-ui/core-v3/components'`                                                                      |
| `Checkbox/*`            | `Checkbox`        | `import { Checkbox } from '@aioz-ui/core-v3/components'`                                                                    |
| `Tooltips/*`            | `Tooltip`         | `import { Tooltip, TooltipProvider, TooltipTrigger, TooltipContent } from '@aioz-ui/core-v3/components'`                    |
| `Tabs/*`                | `Tabs`            | `import { Tabs, TabsList, TabsTrigger, TabsContent } from '@aioz-ui/core-v3/components'`                                    |
| `Table/*`               | `Table`           | `import { Table, Header, Body, Row, HeadCell, Cell } from '@aioz-ui/core-v3/components'`                                    |
| `Separator/*`           | `Separator`       | `import { Separator } from '@aioz-ui/core-v3/components'`                                                                   |
| `Pagination item/*`     | `PaginationGroup` | `import { PaginationGroup } from '@aioz-ui/core-v3/components'`                                                             |
| `Progress bar/*`        | `Progress`        | `import { Progress } from '@aioz-ui/core-v3/components'`                                                                    |
| `Slider/*`              | `Slider`          | `import { Slider } from '@aioz-ui/core-v3/components'`                                                                      |
| `Upload file/*`         | `UploadFile`      | `import { UploadFile } from '@aioz-ui/core-v3/components'`                                                                  |
| `Menu item/*`           | `MenuItem`        | `import { MenuItem } from '@aioz-ui/core-v3/components'`                                                                    |
| `Dropdown item/*`       | `DropdownMenu`    | `import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@aioz-ui/core-v3/components'`    |
| `Modal/*`               | `Dialog`          | `import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from '@aioz-ui/core-v3/components'` |
| `Block/*`               | `Block`           | `import { Block } from '@aioz-ui/core-v3/components'`                                                                       |
| `IconBadge/*`           | `IconBadge`       | `import { IconBadge } from '@aioz-ui/core-v3/components'`                                                                   |
| `Message/*`             | `Message`         | `import { Message } from '@aioz-ui/core-v3/components'`                                                                     |
| `Breadcrumb/*`          | `Breadcrumb`      | `import { Breadcrumb } from '@aioz-ui/core-v3/components'`                                                                  |
| `Date picker/*`         | `DatePicker`      | `import { DatePicker } from '@aioz-ui/core-v3/components'`                                                                  |

---

## Variant → Prop Map

Figma MCP encodes variants as comma-separated `Key=Value` pairs in the node name:

```
"Type=Primary, Size=Medium, Icon Only=False, Shape=Square, Danger=False, State=Hover"
```

| Figma Variant                 | React Prop            | Notes                |
| ----------------------------- | --------------------- | -------------------- |
| `Type=Primary`                | `variant="primary"`   |                      |
| `Type=Secondary`              | `variant="secondary"` |                      |
| `Type=Neutral`                | `variant="neutral"`   |                      |
| `Type=Text`                   | `variant="text"`      |                      |
| `Type=Danger` / `Danger=True` | `variant="danger"`    |                      |
| `Size=Large`                  | `size="lg"`           |                      |
| `Size=Medium`                 | `size="md"`           |                      |
| `Size=Small`                  | `size="sm"`           |                      |
| `Shape=Circle`                | `shape="circle"`      |                      |
| `Shape=Square`                | `shape="square"`      |                      |
| `Shape=Default`               | `shape="default"`     |                      |
| `State=Default`               | _(no prop)_           | Default render state |
| `State=Hover`                 | _(no prop)_           | CSS handles it       |
| `State=Focused`               | _(no prop)_           | CSS handles it       |
| `State=Pressed`               | _(no prop)_           | CSS handles it       |
| `State=Disabled`              | `disabled`            |                      |
| `State=Loading`               | `loading`             |                      |
| `Icon Only=True`              | `size="icon"`         | Button only          |

---

## Full Translation Example

Given this Figma MCP output:

```json
{
  "name": "Type=Primary, Size=Medium, Icon Only=False, Shape=Square, Danger=False, State=Default",
  "fills": [{ "token": "Sf/Pri/Pri" }],
  "textColor": "Onsf/Bra/Default",
  "typography": "Button/01"
}
```

Translate to:

```tsx
import { Button } from '@aioz-ui/core-v3/components'
;<Button variant="primary" size="md" shape="square">
  Label
</Button>
```

> Colors and typography are handled by `Button` internally. Apply color/typography classes manually only when building **custom layouts** outside of component primitives.

---

## Core Rules

1. **Token-first** — Never use raw Tailwind colors or sizing.

   ```
   ❌  text-gray-500   bg-white   border-gray-200   text-sm font-medium
   ✅  text-content-sec   bg-sf-screen   border-border-neutral   text-body-02
   ```

2. **Component-first** — Use design system primitives over custom divs. See Component Map above.

3. **Typography is atomic** — Each `text-*` class already encodes font-size, line-height, weight, and font-family. Never stack additional font utilities on top.

4. **Icons only from `@aioz-ui/icon-react`** — Never SVG literals, emoji, or other libraries.

   ```tsx
   import { Search01Icon } from '@aioz-ui/icon-react'
   ;<Search01Icon size={16} className="text-icon-neutral" />
   ```

5. **On-surface text** — Text on a `bg-sf-*` surface must use the matching `text-onsf-*` class:

   ```
   bg-sf-pri        →  text-onsf-text-pri
   bg-sf-error-sec  →  text-onsf-text-error
   bg-sf-neutral    →  text-onsf-text-neutral
   ```

6. **Charts** — Always import from `@aioz-ui/core/components` (not `-v3`). Always wrap in the card shell. Always provide both `categories` and `overwriteCategories`. Read `references/charts.md` before writing any chart code.

---

## Reference Files

Open the relevant file for deep-dive API docs, full token lists, and component examples:

| File                       | Open When                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------- |
| `references/colors.md`     | Full token → Tailwind class tables for text, background, and border tokens         |
| `references/typography.md` | Full `text-*` class list with font-size, weight, and line-height specs             |
| `references/icons.md`      | Icon name transformation rule, size guide, and common icon import list             |
| `references/components.md` | Full props, all variants, and ready-to-use code examples for every component       |
| `references/charts.md`     | LineChart, AreaChart, BarChart, DonutChart — APIs, variants, legend, hidden-series |
