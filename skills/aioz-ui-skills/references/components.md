---
name: aioz-ui-components
description: Complete API reference for AIOZ UI V3 component library. Use when writing, editing, or reviewing JSX/TSX code that uses Button, Input, Textarea, Checkbox, Switch, Badge, Avatar, Card, Dialog, Tabs, Tooltip, Accordion, Progress, Separator, DropdownMenu, Table, Sidebar, or Pagination from @aioz-ui/core-v3/components. Contains all props, variants, sizes, shapes, and ready-to-use code examples. For colors see colors.md, for typography see typography.md, for icons see icons.md.
---

# AIOZ UI V3 – Complete Component Reference

## Related Skills

- **colors.md** — All color tokens (text, bg, border, surface) and Figma MCP mappings
- **typography.md** — All text utility classes (`text-title-03`, `text-body-02`, etc.) and Figma mappings
- **icons.md** — Icon import guide, full icon list, Figma icon layer → import name rules

## 1. Button

```ts
// Skill definition
{
  "name": "createButton",
  "description": "Generates JSX for a Button component.",
  "parameters": {
    "variant": { "type": "string", "enum": ["primary","secondary","neutral","danger","ghost","text","ghost-danger"] },
    "size":    { "type": "string", "enum": ["sm","md","lg","icon"] },
    "shape":   { "type": "string", "enum": ["default","square","circle"] },
    "loading":     { "type": "boolean" },
    "disabled":    { "type": "boolean" },
    "loadingText": { "type": "string" },
    "leftIcon":    { "type": "ReactNode", "description": "Icon element, e.g. <Search01Icon size={16} />" },
    "rightIcon":   { "type": "ReactNode" }
  }
}
```

**Import**

```tsx
import { Button } from '@aioz-ui/core-v3/components'
import {
  Search01Icon,
  Plus01Icon,
  DownloadIcon,
  HeartIcon,
} from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Default primary button
<Button variant="primary" size="md" shape="default">Submit</Button>

// With left icon
<Button variant="primary" size="md" leftIcon={<Search01Icon size={16} />}>Search</Button>

// With both icons
<Button variant="neutral" size="md" leftIcon={<DownloadIcon size={16} />} rightIcon={<HeartIcon size={16} />}>Download</Button>

// Loading state with custom text
<Button variant="secondary" size="md" loading loadingText="Saving...">Save</Button>

// Disabled
<Button variant="primary" size="md" disabled>Disabled Primary</Button>

// Icon-only button (size="icon")
<Button variant="primary" size="icon" shape="circle">
  <Search01Icon size={16} />
</Button>

// Danger confirmation
<Button variant="danger" size="md">Delete</Button>
```

**All variants:** `primary` | `secondary` | `neutral` | `danger` | `ghost` | `text` | `ghost-danger`
**All sizes:** `sm` | `md` | `lg` | `icon`
**All shapes:** `default` | `square` | `circle`

---

## 2. Input

```ts
{
  "name": "createInput",
  "description": "Generates JSX for an Input component.",
  "parameters": {
    "size":        { "type": "string", "enum": ["sm","md","lg"] },
    "type":        { "type": "string", "enum": ["text","email","password","number","search","tel","url"] },
    "placeholder": { "type": "string" },
    "disabled":    { "type": "boolean" },
    "required":    { "type": "boolean" },
    "startIcon":   { "type": "ReactNode" },
    "endIcon":     { "type": "ReactNode" },
    "showCount":   { "type": "boolean" },
    "maxLength":   { "type": "number" },
    "aria-invalid":{ "type": "boolean", "description": "true = error state, false = valid state" }
  }
}
```

**Import**

```tsx
import { Input } from '@aioz-ui/core-v3/components'
import { Search01Icon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Basic
<Input size="md" type="text" placeholder="Enter text..." />

// With start icon
<Input placeholder="Search..." startIcon={<Search01Icon size={16} />} />

// With end icon
<Input placeholder="Enter text..." endIcon={<Search01Icon size={16} />} />

// With character count
<Input placeholder="Type something..." showCount maxLength={50} />

// Error state
<Input placeholder="Invalid input" aria-invalid={true} defaultValue="bad value" />

// Valid state
<Input placeholder="Valid input" aria-invalid={false} defaultValue="good value" />

// Disabled
<Input placeholder="Disabled" disabled />

// All three sizes
<Input size="sm" placeholder="Small" />
<Input size="md" placeholder="Medium" />
<Input size="lg" placeholder="Large" />
```

---

## 3. Textarea

```ts
{
  "name": "createTextarea",
  "description": "Generates JSX for a Textarea component.",
  "parameters": {
    "resize":             { "type": "string", "enum": ["none","vertical","horizontal","both"] },
    "disabled":           { "type": "boolean" },
    "showCharacterCount": { "type": "boolean" },
    "maxLength":          { "type": "number" },
    "placeholder":        { "type": "string" },
    "rows":               { "type": "number" },
    "aria-invalid":       { "type": "boolean" }
  }
}
```

**Import**

```tsx
import { Textarea } from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Default
<Textarea placeholder="Enter your message..." />

// With character count + limit
<Textarea placeholder="Type something..." showCharacterCount maxLength={500} />

// Fixed height, no resize
<Textarea placeholder="Cannot resize" resize="none" rows={4} />

// Error state
<Textarea placeholder="Error" aria-invalid={true} defaultValue="Invalid content" />

// Controlled with validation
const [val, setVal] = useState('')
<Textarea
  value={val}
  onChange={(e) => setVal(e.target.value)}
  showCharacterCount
  maxLength={500}
  rows={4}
/>
```

**resize options:** `none` | `vertical` (default) | `horizontal` | `both`

---

## 4. Checkbox

```ts
{
  "name": "createCheckbox",
  "description": "Generates JSX for a Checkbox component.",
  "parameters": {
    "shape":         { "type": "string", "enum": ["square","round"] },
    "checked":       { "type": "boolean" },
    "indeterminate": { "type": "boolean" },
    "disabled":      { "type": "boolean" },
    "onCheckedChange": { "type": "function", "signature": "(checked: boolean | 'indeterminate') => void" }
  }
}
```

Figma Checkbox Base -> using Checkbox

**Import**

```tsx
import { Checkbox } from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Basic with label
<div className="flex items-center space-x-2">
  <Checkbox id="terms" shape="square" />
  <label htmlFor="terms" className="text-sm">Accept terms</label>
</div>

// Controlled
const [checked, setChecked] = useState(false)
<Checkbox checked={checked} onCheckedChange={(v) => setChecked(!!v)} />

// Indeterminate (select-all pattern)
<Checkbox checked indeterminate onCheckedChange={(v) => {...}} />

// Rounded shape
<Checkbox shape="round" checked />

// Disabled states
<Checkbox disabled />
<Checkbox checked disabled />
<Checkbox indeterminate disabled />
```

**shapes:** `square` (default) | `round`

---

## 5. Switch

```ts
{
  "name": "createSwitch",
  "description": "Generates JSX for a Switch toggle component.",
  "parameters": {
    "size":            { "type": "string", "enum": ["sm","md"] },
    "checked":         { "type": "boolean" },
    "disabled":        { "type": "boolean" },
    "onCheckedChange": { "type": "function", "signature": "(checked: boolean | 'indeterminate') => void" }
  }
}
```

**Import**

```tsx
import { Switch } from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Basic
<div className="flex items-center space-x-2">
  <Switch id="wifi" />
  <label htmlFor="wifi" className="text-sm">Wi-Fi</label>
</div>

// Controlled
const [on, setOn] = useState(false)
<Switch checked={on} onCheckedChange={(v) => setOn(!!v)} />

// Settings row pattern
<div className="flex items-center justify-between">
  <label htmlFor="notifications" className="text-sm font-medium">Notifications</label>
  <Switch id="notifications" checked={on} onCheckedChange={(v) => setOn(!!v)} />
</div>

// Small size
<Switch size="sm" checked />

// Disabled
<Switch disabled />
<Switch checked disabled />
```

**sizes:** `sm` | `md` (default)

---

## 6. Badge

```ts
{
  "name": "createBadge",
  "description": "Generates JSX for a Badge component.",
  "parameters": {
    "variant":  { "type": "string", "enum": ["default","secondary","outlined","text"] },
    "color":    { "type": "string", "enum": ["default","success","warning","error","info"] },
    "shape":    { "type": "string", "enum": ["round","circle"] },
    "showIcon": { "type": "boolean" },
    "icon":     { "type": "ReactNode", "description": "Custom icon, e.g. <CircleCheckIcon size={16} />" },
    "children": { "type": "string" }
  }
}
```

**Import**

```tsx
import { Badge } from '@aioz-ui/core-v3/components'
import { CircleCheckIcon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Default badge
<Badge variant="secondary" color="default" shape="round">Badge Label</Badge>

// Status badges
<Badge variant="secondary" color="success" shape="round" showIcon>Active</Badge>
<Badge variant="secondary" color="warning" shape="round" showIcon>Pending</Badge>
<Badge variant="secondary" color="error"   shape="round" showIcon>Failed</Badge>
<Badge variant="secondary" color="info"    shape="round" showIcon>Info</Badge>

// With custom icon
<Badge variant="secondary" color="info" shape="round" showIcon icon={<CircleCheckIcon size={16} />}>
  Verified
</Badge>

// Outlined
<Badge variant="outlined" color="default" shape="round">Outlined</Badge>

// Text only
<Badge variant="text" color="success">Text Badge</Badge>
```

**variants:** `default` | `secondary` | `outlined` | `text`
**colors:** `default` | `success` | `warning` | `error` | `info`
**shapes:** `round` | `circle`

---

## 7. Avatar

```ts
{
  "name": "createAvatar",
  "description": "Generates JSX for an Avatar component with optional status and icon overlays.",
  "parameters": {
    "size":         { "type": "string", "enum": ["xxs","xs","sm","md","lg","xl","2xl","3xl","4xl","5xl","6xl"] },
    "shape":        { "type": "string", "enum": ["circle","square"] },
    "src":          { "type": "string", "description": "Image URL" },
    "fallbackText": { "type": "string", "description": "Initials shown when image fails, e.g. 'CN'" },
    "showStatus":   { "type": "boolean" },
    "statusVariant":{ "type": "string", "enum": ["default","online"] },
    "showIcon":     { "type": "boolean", "description": "Overlay action icon (e.g. edit)" }
  }
}
```

**Import**

```tsx
import {
  Avatar,
  AvatarFallback,
  AvatarIcon,
  AvatarImage,
  AvatarStatus,
} from '@aioz-ui/core-v3/components'
import { Pencil01Icon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Basic avatar with image
<Avatar size="lg" shape="circle">
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback size="lg">CN</AvatarFallback>
</Avatar>

// Fallback only (no image)
<Avatar size="md" shape="circle">
  <AvatarFallback size="md">AB</AvatarFallback>
</Avatar>

// With online status indicator
<div className="relative inline-block">
  <Avatar size="lg" shape="circle">
    <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
    <AvatarFallback size="lg">CN</AvatarFallback>
  </Avatar>
  <AvatarStatus size="lg" variant="online" avatarShape="circle" />
</div>

// With edit icon overlay
<div className="relative inline-block">
  <Avatar size="lg" shape="circle">
    <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
    <AvatarFallback size="lg">CN</AvatarFallback>
  </Avatar>
  <AvatarIcon size="lg" avatarShape="circle">
    <Pencil01Icon size={14} />
  </AvatarIcon>
</div>
```

**Icon size guide by avatar size:** `xxs`→2, `xs`→6, `sm`→8, `md`→12, `lg`→14, `xl`→16, `2xl`→16, `3xl`→16, `4xl`→24, `5xl`→32, `6xl`→48
**sizes:** `xxs` | `xs` | `sm` | `md` | `lg` | `xl` | `2xl` | `3xl` | `4xl` | `5xl` | `6xl`
**shapes:** `circle` | `square`

---

## 8. Card

```ts
{
  "name": "createCard",
  "description": "Generates JSX for a Card container component.",
  "parameters": {
    "title":       { "type": "string" },
    "description": { "type": "string" },
    "children":    { "type": "ReactNode", "description": "Main body content" },
    "className":   { "type": "string", "description": "Tailwind width, e.g. w-[350px]" }
  }
}
```

**Import**

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Full card
<Card className="w-[350px]">
  <CardContent>
    <CardHeader>
      <CardTitle>Card Title</CardTitle>
      <CardDescription>Supporting description text</CardDescription>
    </CardHeader>
    <p className="text-sm">Main card content goes here.</p>
  </CardContent>
</Card>

// Content only (no header)
<Card className="w-[350px]">
  <CardContent>
    <p className="text-sm">Simple content card.</p>
  </CardContent>
</Card>

// Grid of cards
<div className="flex gap-4 flex-wrap max-w-[800px]">
  {items.map((item) => (
    <Card key={item.id} className="flex-1 min-w-[250px]">
      <CardContent>
        <CardHeader>
          <CardTitle>{item.title}</CardTitle>
          <CardDescription>{item.description}</CardDescription>
        </CardHeader>
        <p className="text-sm">{item.body}</p>
      </CardContent>
    </Card>
  ))}
</div>
```

---

## 9. Dialog

```ts
{
  "name": "createDialog",
  "description": "Generates JSX for a Dialog (modal) component.",
  "parameters": {
    "overlayType": { "type": "string", "enum": ["default","transparent"], "description": "Overlay background style" },
    "title":       { "type": "string" },
    "description": { "type": "string" },
    "trigger":     { "type": "ReactNode", "description": "Element that opens the dialog" },
    "footer":      { "type": "ReactNode", "description": "Action buttons in the footer" }
  }
}
```

**Import**

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
  DialogClose,
  Button,
} from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Standard dialog
const [open, setOpen] = useState(false)
<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button variant="primary" size="md">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent overlayType="default">
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>Supporting description text.</DialogDescription>
    </DialogHeader>
    <div className="py-4">
      <p className="text-sm text-content-sec">Dialog body content here.</p>
    </div>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="neutral" size="md">Cancel</Button>
      </DialogClose>
      <Button variant="primary" size="md">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

// Confirmation / danger dialog
<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button variant="danger" size="md">Delete Item</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you sure?</DialogTitle>
      <DialogDescription>This action cannot be undone.</DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="neutral" size="md">Cancel</Button>
      </DialogClose>
      <Button variant="danger" size="md">Delete</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

// Transparent overlay
<DialogContent overlayType="transparent">...</DialogContent>
```

**overlayType:** `default` | `transparent`

---

## 10. Tabs

```ts
{
  "name": "createTabs",
  "description": "Generates JSX for a Tabs component.",
  "parameters": {
    "size":          { "type": "string", "enum": ["sm","md","lg"] },
    "withAnimation": { "type": "boolean", "description": "Animated spring border indicator on TabsList" },
    "defaultValue":  { "type": "string", "description": "Default active tab value" },
    "tabs": {
      "type": "array",
      "items": {
        "value":   { "type": "string" },
        "label":   { "type": "string" },
        "content": { "type": "ReactNode" },
        "disabled":{ "type": "boolean" }
      }
    }
  }
}
```

**Import**

```tsx
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@aioz-ui/core-v3/components'
import { Home01Icon, SettingsIcon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Basic tabs
<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1" size="md">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2" size="md">Tab 2</TabsTrigger>
    <TabsTrigger value="tab3" size="md">Tab 3</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">
    <div className="p-4 border rounded-lg">Content for Tab 1</div>
  </TabsContent>
  <TabsContent value="tab2">
    <div className="p-4 border rounded-lg">Content for Tab 2</div>
  </TabsContent>
  <TabsContent value="tab3">
    <div className="p-4 border rounded-lg">Content for Tab 3</div>
  </TabsContent>
</Tabs>

// Animated indicator
<Tabs defaultValue="home">
  <TabsList withAnimation={true}>
    <TabsTrigger value="home">Home</TabsTrigger>
    <TabsTrigger value="about">About</TabsTrigger>
  </TabsList>
  <TabsContent value="home">Home content</TabsContent>
  <TabsContent value="about">About content</TabsContent>
</Tabs>

// With icons in trigger
<TabsTrigger value="home" className="flex items-center gap-2">
  <Home01Icon />
  Home
</TabsTrigger>

// Disabled tab
<TabsTrigger value="locked" disabled>Locked</TabsTrigger>
```

**sizes:** `sm` | `md` (default) | `lg`

---

## 11. Tooltip

```ts
{
  "name": "createTooltip",
  "description": "Generates JSX for a Tooltip component.",
  "parameters": {
    "variant":       { "type": "string", "enum": ["default","error","success","warning","info"] },
    "side":          { "type": "string", "enum": ["top","right","bottom","left"] },
    "showArrow":     { "type": "boolean" },
    "showCloseIcon": { "type": "boolean" },
    "leftIcon":      { "type": "ReactNode" },
    "onClose":       { "type": "function" },
    "trigger":       { "type": "ReactNode" },
    "content":       { "type": "ReactNode" }
  }
}
```

**Import**

```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
  Button,
} from '@aioz-ui/core-v3/components'
import { CircleIcon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Always wrap tooltips in TooltipProvider
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="primary" size="md">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent variant="default" showArrow>
      <p>This is a tooltip</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>

// Positioned tooltip
<TooltipContent side="bottom" variant="info">
  <p>Info on bottom</p>
</TooltipContent>

// With left icon and close button
<TooltipContent
  variant="error"
  leftIcon={<CircleIcon size={20} />}
  showCloseIcon
  onClose={() => console.log('closed')}
>
  <p>Error with actions</p>
</TooltipContent>
```

**variants:** `default` | `error` | `success` | `warning` | `info`
**side:** `top` | `right` | `bottom` | `left`

---

## 12. Accordion

```ts
{
  "name": "createAccordion",
  "description": "Generates JSX for an Accordion component.",
  "parameters": {
    "type":        { "type": "string", "enum": ["single","multiple"] },
    "collapsible": { "type": "boolean" },
    "items": {
      "type": "array",
      "items": {
        "value":   { "type": "string" },
        "trigger": { "type": "string" },
        "content": { "type": "string" }
      }
    }
  }
}
```

**Import**

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Single collapsible
<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. It adheres to the WAI-ARIA design pattern.</AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>Yes. It comes with default styles that match the design system.</AccordionContent>
  </AccordionItem>
</Accordion>

// Multiple items open simultaneously
<Accordion type="multiple">
  <AccordionItem value="faq-1">
    <AccordionTrigger>FAQ Question 1</AccordionTrigger>
    <AccordionContent>Answer to question 1.</AccordionContent>
  </AccordionItem>
</Accordion>
```

---

## 13. Progress

```ts
{
  "name": "createProgress",
  "description": "Generates JSX for a Progress bar component.",
  "parameters": {
    "value":     { "type": "number", "description": "0–100" },
    "showValue": { "type": "boolean", "description": "Show percentage text label" }
  }
}
```

**Import**

```tsx
import { Progress } from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Static
<div className="w-[400px]">
  <Progress value={65} showValue={true} />
</div>

// Without label
<Progress value={40} showValue={false} />

// Animated (controlled)
const [progress, setProgress] = useState(0)
useEffect(() => {
  const timer = setInterval(() => {
    setProgress((p) => (p >= 100 ? 0 : p + 1))
  }, 50)
  return () => clearInterval(timer)
}, [])
<Progress value={progress} />

// Multiple bars
<div className="space-y-4">
  <Progress value={85} showValue={false} />
  <Progress value={60} showValue={false} />
  <Progress value={35} showValue={false} />
</div>
```

---

## 14. Separator

```ts
{
  "name": "createSeparator",
  "description": "Generates JSX for a Separator (divider) component.",
  "parameters": {
    "orientation": { "type": "string", "enum": ["horizontal","vertical"] },
    "decorative":  { "type": "boolean" },
    "className":   { "type": "string", "description": "Use h-px for horizontal, w-px h-full for vertical" }
  }
}
```

**Import**

```tsx
import { Separator } from '@aioz-ui/core-v3/components'
```

**Examples**

```tsx
// Horizontal
<Separator orientation="horizontal" decorative className="h-px" />

// Vertical (needs flex container with height)
<div className="flex h-20 items-center space-x-4">
  <span>Item 1</span>
  <Separator orientation="vertical" className="w-px h-full" />
  <span>Item 2</span>
</div>

// In a list (breadcrumb-style)
<div className="flex h-5 items-center space-x-4 text-sm">
  <div>Blog</div>
  <Separator orientation="vertical" className="h-full w-px" />
  <div>Docs</div>
  <Separator orientation="vertical" className="h-full w-px" />
  <div>Source</div>
</div>
```

---

## 15. DropdownMenu

```ts
{
  "name": "createDropdownMenu",
  "description": "Generates JSX for a DropdownMenu component.",
  "parameters": {
    "size":     { "type": "string", "enum": ["sm","md","lg"] },
    "trigger":  { "type": "ReactNode" },
    "items": {
      "type": "array",
      "items": {
        "label":    { "type": "string" },
        "value":    { "type": "string" },
        "selected": { "type": "boolean" },
        "onSelect": { "type": "function" }
      }
    }
  }
}
```

**Import**

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Button,
} from '@aioz-ui/core-v3/components'
import { ChevronDownIcon } from '@aioz-ui/icon-react'
```

**Examples**

```tsx
// Basic dropdown
const [selected, setSelected] = useState('')
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="primary" size="md">
      Options
      <ChevronDownIcon size={16} className="ml-2" />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem size="lg" selected={selected === 'opt1'} onSelect={() => setSelected('opt1')}>
      Option 1
    </DropdownMenuItem>
    <DropdownMenuItem size="lg" selected={selected === 'opt2'} onSelect={() => setSelected('opt2')}>
      Option 2
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem size="lg" onSelect={() => setSelected('danger')}>
      Danger Action
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

**item sizes:** `sm` | `md` | `lg` (default)

---

---

## 16. Table

**Import**

```tsx
import {
  Table,
  Header,
  Body,
  Footer,
  Row,
  Cell,
  HeadCell,
} from '@aioz-ui/core-v3/components'
```

**Props**

- `Table`: `containerClassName?`, `topComponent?`, `bottomComponent?` — slots rendered above/below the `<table>`
- `Row`: `hoverable?` (hover bg), `striped?` (even-row bg)
- `Cell`: wraps `<td>` — default class `px-4 py-5 text-body-01`
- `HeadCell`: wraps `<th>` — default class `p-4 py-2 text-body-01`

**Examples**

```tsx
// Basic data table
<Table>
  <Header>
    <tr>
      <HeadCell className="text-left text-subheadline-02 text-subtitle-neutral w-2/5">Site URL</HeadCell>
      <HeadCell className="text-left text-subheadline-02 text-subtitle-neutral">
        <div className="flex items-center gap-1">
          Status <FilterIcon size={14} />
        </div>
      </HeadCell>
      <HeadCell className="text-left text-subheadline-02 text-subtitle-neutral">
        <div className="flex items-center gap-1">
          Date Added <ArrowDownIcon size={14} />
        </div>
      </HeadCell>
      <HeadCell className="text-left text-subheadline-02 text-subtitle-neutral">Quick Action</HeadCell>
    </tr>
  </Header>
  <Body>
    {rows.map((row) => (
      <Row key={row.id} hoverable>
        <Cell className="text-title-neutral font-medium">{row.url}</Cell>
        <Cell><StatusBadge status={row.status} /></Cell>
        <Cell className="text-subtitle-neutral">{row.date}</Cell>
        <Cell>
          <div className="flex items-center gap-2">
            <button className="w-8 h-8 rounded-lg border border-border-neutral flex items-center justify-center text-icon-neutral hover:bg-sf-neutral transition-colors">
              <EyeOpenIcon size={16} />
            </button>
            <button className="w-8 h-8 rounded-lg border border-border-error flex items-center justify-center text-onsf-text-error hover:bg-sf-error-sec transition-colors">
              <Trash01Icon size={16} />
            </button>
          </div>
        </Cell>
      </Row>
    ))}
  </Body>
</Table>

// Table with top/bottom slots (search + pagination)
<Table
  bottomComponent={
    <div className="flex items-center justify-between px-4 py-3 border-t border-border-neutral">
      <span className="text-body-02 text-subtitle-neutral">Total {rows.length} items</span>
      <PaginationGroup
        currentPage={currentPage}
        totalPages={totalPages}
        handlePageChange={setCurrentPage}
        showFirstLast
      />
    </div>
  }
>
  {/* ... Header + Body ... */}
</Table>
```

---

## 17. Pagination

**Import**

```tsx
import { PaginationGroup } from '@aioz-ui/core-v3/components'
// Or individual pieces:
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  PaginationFirst,
  PaginationLast,
  PaginationEllipsis,
} from '@aioz-ui/core-v3/components'
```

**PaginationGroup props**
| Prop | Type | Default | Description |
|---|---|---|---|
| `currentPage` | `number` | — | Active page (1-based) |
| `totalPages` | `number` | — | Total page count |
| `handlePageChange` | `(page: number) => void` | — | Called on page click |
| `showFirstLast` | `boolean` | `true` | Show first/last arrow buttons |
| `iconSize` | `"sm" \| "md" \| "lg"` | `"lg"` | Arrow icon size |
| `paginationClass` | `string` | `""` | Extra class on the nav element |

**Examples**

```tsx
// Recommended: use PaginationGroup (all-in-one)
const [currentPage, setCurrentPage] = useState(1)
const totalPages = 10

<PaginationGroup
  currentPage={currentPage}
  totalPages={totalPages}
  handlePageChange={setCurrentPage}
  showFirstLast
/>

// Typically placed inside a Table bottomComponent
<Table
  bottomComponent={
    <div className="flex items-center justify-between px-4 py-3 border-t border-border-neutral">
      <span className="text-body-02 text-subtitle-neutral">Total 3 items</span>
      <PaginationGroup
        currentPage={currentPage}
        totalPages={totalPages}
        handlePageChange={setCurrentPage}
        showFirstLast
      />
    </div>
  }
>
```

---

## 18. Sidebar

**Import**

```tsx
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  useSidebar,
} from '@aioz-ui/core-v3/components'
```

**SidebarProvider props**
| Prop | Type | Default |
|---|---|---|
| `defaultOpen` | `boolean` | `true` |
| `width` | `string` | `"12rem"` |
| `widthIcon` | `string` | `"5.75rem"` |

**Sidebar props**
| Prop | Type | Options | Default |
|---|---|---|---|
| `collapsible` | `string` | `"offcanvas" \| "icon" \| "none"` | `"offcanvas"` |
| `variant` | `string` | `"sidebar" \| "floating" \| "inset"` | `"sidebar"` |
| `side` | `string` | `"left" \| "right"` | `"left"` |

**SidebarMenuButton props**
| Prop | Type | Description |
|---|---|---|
| `isActive` | `boolean` | Highlights the button as the active nav item |
| `asChild` | `boolean` | Render as child element |

**Full page layout example**

```tsx
'use client'
import { useState } from 'react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from '@aioz-ui/core-v3/components'
import {
  BarChart01Icon,
  ComputerIcon,
  Wallet01Icon,
  Book01Icon,
  ChevronDownIcon,
} from '@aioz-ui/icon-react'

const navItems = [
  { label: 'Dashboard', icon: <BarChart01Icon size={16} />, active: false },
  { label: 'Site Management', icon: <ComputerIcon size={16} />, active: true },
  { label: 'Wallet', icon: <Wallet01Icon size={16} />, active: false },
  { label: 'Policies', icon: <Book01Icon size={16} />, active: false },
]

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider defaultOpen width="180px">
      <div className="bg-sf-screen flex min-h-screen w-full">
        {/* Sidebar */}
        <Sidebar
          collapsible="none"
          className="border-border-neutral w-[180px] border-r"
        >
          <SidebarHeader className="px-4 pt-5 pb-4">
            <div className="flex items-center gap-2">
              <div className="bg-sf-pri flex h-6 w-6 items-center justify-center rounded">
                <span className="text-body-03 font-bold text-white">A</span>
              </div>
              <span className="text-subheadline-02 text-title-neutral">
                AIOZ Ads
              </span>
            </div>
          </SidebarHeader>

          <SidebarContent>
            <SidebarGroup className="px-3 pb-0">
              <SidebarMenu>
                {navItems.map((item) => (
                  <SidebarMenuItem key={item.label}>
                    <SidebarMenuButton
                      isActive={item.active}
                      className={
                        item.active
                          ? 'bg-sf-neutral text-title-neutral'
                          : 'text-subtitle-neutral hover:bg-sf-neutral hover:text-title-neutral'
                      }
                    >
                      <span className="shrink-0 text-current">{item.icon}</span>
                      <span className="text-body-02 truncate">
                        {item.label}
                      </span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter className="px-3 pb-4">
            <button className="hover:bg-sf-neutral flex w-full items-center gap-2 rounded-lg px-2 py-2 transition-colors">
              <div className="bg-sf-sec flex h-7 w-7 shrink-0 items-center justify-center rounded-full">
                <span className="text-subheadline-03 text-sf-pri">JD</span>
              </div>
              <span className="text-body-02 text-title-neutral flex-1 truncate text-left">
                Jane Doe
              </span>
              <ChevronDownIcon
                size={14}
                className="text-icon-neutral shrink-0"
              />
            </button>
          </SidebarFooter>
        </Sidebar>

        {/* Main content area */}
        <SidebarInset className="bg-sf-screen flex min-w-0 flex-1 flex-col">
          <header className="bg-sf-object border-border-neutral flex items-center border-b px-6 py-3">
            <h1 className="text-subheadline-01 text-title-neutral">
              Page Title
            </h1>
          </header>
          <div className="flex-1 p-6">{children}</div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}
```

---

## Global Rules

1. **V2 only**: Always import from `@aioz-ui/core-v3/components`.
2. **Icons**: Import from `@aioz-ui/icon-react`. Pass size via the `size` prop: `<Search01Icon size={16} />`. Color via `className="text-icon-neutral"`.
3. **Colors**: Use tokens from **colors.md** — never raw Tailwind colors (`text-gray-500`, `bg-white`). Common: `text-title-neutral`, `text-subtitle-neutral`, `bg-sf-screen`, `bg-sf-object`, `border-border-neutral`.
4. **Typography**: Use utilities from **typography.md** — never `text-sm`/`text-base`/`font-medium` in isolation. Common: `text-title-03`, `text-subheadline-01`, `text-body-02`.
5. **State**: Interactive components (Switch, Checkbox, Dialog) need `useState`. Use the controlled pattern shown above.
6. **Defaults**: `size="md"` + `variant="primary"` for Button; `size="md"` for Input/Tabs; `shape="square"` for Checkbox; `shape="circle"` for Avatar.
7. **Tooltip**: Always wrap in `<TooltipProvider>`.
8. **Dialog**: Use `DialogClose asChild` for cancel buttons so they close on click.
9. **Table typography**: HeadCells use `text-subheadline-02 text-subtitle-neutral`; body Cells default to `text-body-01` from component, override color with `text-title-neutral` (primary) or `text-subtitle-neutral` (secondary).
10. **Sidebar active item**: `bg-sf-neutral text-title-neutral`; inactive: `text-subtitle-neutral hover:bg-sf-neutral hover:text-title-neutral`.
11. **Storybook title map**: `UI/Button V2`, `UI/Input V2`, `UI/Badge V2`, `UI/Checkbox V2`, `UI/Switch V2`, `UI/Textarea V2`, `UI/Dialog V2`, `UI/Tabs V2`, `UI/Tooltip V2`, `UI/Avatar V2`, `UI/Card V2`, `UI/Accordion V2`, `UI/Progress V2`, `UI/Separator V2`, `UI/DropdownMenu V2`.

```

```
