# Selectors — Puppeteer

## Selector Priority (Best to Worst)

| Priority | Type | Example | Stability |
|----------|------|---------|-----------|
| 1 | Test ID | `[data-testid="submit"]` | Highest |
| 2 | ID | `#login-button` | High |
| 3 | Name | `[name="email"]` | High |
| 4 | Role + Text | `button:has-text("Submit")` | Medium |
| 5 | Semantic | `form button[type="submit"]` | Medium |
| 6 | Class | `.btn-primary` | Low |
| 7 | XPath | `//div[@class="x"]/button` | Lowest |

## Common Patterns

### Forms
```javascript
// Input by label relationship
await page.type('input[name="email"]', 'user@example.com');
await page.type('input[name="password"]', 'secret');

// Submit button
await page.click('form button[type="submit"]');
// or
await page.click('input[type="submit"]');
```

### Navigation
```javascript
// Links
await page.click('a[href="/dashboard"]');
await page.click('nav a:has-text("Settings")');

// Menu items
await page.click('[role="menuitem"]:has-text("Logout")');
```

### Tables
```javascript
// Specific cell
await page.$$eval('table tr td:nth-child(2)', cells => 
  cells.map(c => c.textContent)
);

// Row by content
await page.click('tr:has-text("John Doe") button.edit');
```

### Dynamic Content
```javascript
// Wait for element to appear
await page.waitForSelector('.results-loaded');

// Wait for text to appear
await page.waitForFunction(() => 
  document.body.innerText.includes('Success')
);
```

## Handling Difficult Elements

### Shadow DOM
```javascript
// Pierce shadow root
const handle = await page.evaluateHandle(() => {
  const host = document.querySelector('my-component');
  return host.shadowRoot.querySelector('button');
});
await handle.click();
```

### Iframes
```javascript
const frame = page.frames().find(f => f.name() === 'payment');
await frame.click('#card-number');
// or
const frameHandle = await page.$('iframe#payment');
const frame = await frameHandle.contentFrame();
```

### Canvas Elements
```javascript
// Click at coordinates
const canvas = await page.$('canvas');
const box = await canvas.boundingBox();
await page.mouse.click(box.x + 100, box.y + 50);
```

## Anti-Detection Selectors

Some sites detect automation. Avoid:
- `puppeteer` anywhere in code that runs in browser
- Sequential, robotic selector patterns
- Same delays between actions

Prefer:
- Human-like selection (visible text, semantic roles)
- Random delays
- Realistic mouse movements
