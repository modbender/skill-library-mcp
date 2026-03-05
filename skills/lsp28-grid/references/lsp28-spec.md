# LSP28 The Grid Specification

## Overview

LSP28 The Grid is a standard for organizing and displaying content on Universal Profiles. It allows UP owners to create a grid layout of mini-apps, iframes, and external links.

## Data Key

```
0x31cf14955c5b0052c1491ec06644438ec7c14454be5eb6cb9ce4e4edef647423
```

This is the keccak256 hash of 'LSP28Grid'.

## Data Format

The grid data is stored as a VerifiableURI, which is a base64-encoded JSON object:

```
data:application/json;base64,<base64-encoded-json>
```

## JSON Schema

```typescript
interface GridData {
  isEditable: boolean;  // Whether the grid can be edited
  items: GridItem[];    // Array of grid items
}

interface GridItem {
  type: 'miniapp' | 'iframe' | 'external';
  id: string;           // Unique identifier
  title: string;        // Display title
}

interface MiniAppItem extends GridItem {
  type: 'miniapp';
  text: string;         // Button/label text
  backgroundColor: string;  // Hex color (e.g., '#fe005b')
  textColor: string;    // Hex color for text (e.g., '#ffffff')
  size?: 'small' | 'medium' | 'large';
}

interface IframeItem extends GridItem {
  type: 'iframe';
  src: string;          // iframe source URL
}

interface ExternalItem extends GridItem {
  type: 'external';
  url: string;          // External link URL
}
```

## Item Types

### Mini-App (type: 'miniapp')

Interactive button that can trigger actions within the grid context.

**Properties:**
- `type`: 'miniapp' (required)
- `id`: Unique string identifier (required)
- `title`: Display title (required)
- `text`: Button text label (required)
- `backgroundColor`: Background color in hex format (required)
- `textColor`: Text color in hex format (required)
- `size`: Optional size variant ('small', 'medium', 'large')

**Example:**
```json
{
  "type": "miniapp",
  "id": "staking",
  "title": "Stakingverse",
  "text": "Stake LYX",
  "backgroundColor": "#1a1a2e",
  "textColor": "#ffffff"
}
```

### IFrame (type: 'iframe')

Embeds external content directly in the grid.

**Properties:**
- `type`: 'iframe' (required)
- `id`: Unique string identifier (required)
- `title`: Display title (required)
- `src`: iframe source URL (required)

**Example:**
```json
{
  "type": "iframe",
  "id": "chart",
  "title": "Price Chart",
  "src": "https://dexscreener.com/lukso/CHART_URL"
}
```

### External Link (type: 'external')

Links to external websites that open in a new tab.

**Properties:**
- `type`: 'external' (required)
- `id`: Unique string identifier (required)
- `title`: Display title (required)
- `url`: External URL (required)

**Example:**
```json
{
  "type": "external",
  "id": "docs",
  "title": "Documentation",
  "url": "https://docs.lukso.tech"
}
```

## Best Practices

### Color Contrast

Always ensure sufficient contrast between background and text colors:

| Background | Text Color | Contrast Ratio |
|------------|-----------|----------------|
| #1a1a2e (dark) | #ffffff (white) | 15.8:1 ✓ |
| #ffffff (white) | #000000 (black) | 21:1 ✓ |
| #fe005b (pink) | #ffffff (white) | 4.5:1 ✓ |
| #000000 (black) | #fe005b (pink) | 4.5:1 ✓ |

### ID Uniqueness

Each grid item must have a unique `id` within the grid. Using descriptive IDs helps with debugging:
- Good: 'stakingverse', 'twitter-link', 'price-chart'
- Bad: '1', '2', 'item1'

### URL Safety

For iframe and external items, ensure URLs:
- Use HTTPS when possible
- Allow iframe embedding (for iframe type)
- Are from trusted sources

## Common Errors

### Wrong Property Names

❌ Wrong:
```json
{
  "type": "miniapp",
  "color": "#fe005b",
  "content": "Click me"
}
```

✅ Correct:
```json
{
  "type": "miniapp",
  "backgroundColor": "#fe005b",
  "text": "Click me"
}
```

### Missing Required Fields

All items must have: `type`, `id`, `title`
Mini-apps additionally require: `text`, `backgroundColor`, `textColor`

### Invalid JSON

Always validate JSON before encoding:
```javascript
JSON.parse(jsonString); // Should not throw
```

## Resources

- LSP28 Specification: https://github.com/lukso-network/LIPs/blob/main/LSPs/LSP-28-TheGrid.md
- LUKSO Docs: https://docs.lukso.tech
