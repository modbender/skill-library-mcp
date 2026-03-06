# Selectors Reference

Complete guide to element selection in Playwright.

## Selector Types

### CSS Selectors

Most common and versatile. Use standard CSS syntax.

```javascript
// ID
await page.click('#submit-button');

// Class
await page.click('.btn-primary');

// Attribute
await page.fill('input[name="email"]', 'test@example.com');
await page.click('[data-testid="login-btn"]');

// Descendant
await page.click('nav a[href="/about"]');

// nth-child (1-based index)
await page.click('.item:nth-child(3)');

// Complex combinations
await page.click('div.card > h2.title + button');
```

### Text Selectors

Find elements by their visible text content.

```javascript
// Exact match (case-insensitive)
await page.click('text=Submit');

// Contains substring
await page.click('text="Add to cart"');

// Regular expression
await page.click('text=/submit/i');           // case-insensitive
await page.click('text=/^Start.*$/');         // starts with "Start"

// Escape special characters
await page.click('text="Price: $10.00"');
```

### XPath Selectors

Use for complex traversal or when CSS isn't enough.

```javascript
// Basic XPath
await page.click('xpath=//button[@type="submit"]');

// Contains text
await page.click('xpath=//button[contains(text(), "Submit")]');

// Parent/child relationships
await page.click('xpath=//div[@class="card"]//button');

// Following sibling
await page.click('xpath=//label[text()="Email"]/following-sibling::input');

// Position-based
await page.click('xpath=(//button)[3]');       // 3rd button on page
```

### ARIA Role Selectors

Select by accessibility role (best for resilient tests).

```javascript
// Basic role
await page.click('role=button');

// Role with accessible name
await page.click('role=button[name="Submit"]');
await page.click('role=link[name="Learn more"]');

// Common roles
await page.fill('role=textbox[name="Email"]', 'test@example.com');
await page.check('role=checkbox[name="I agree"]');
await page.click('role=tab[name="Settings"]');
```

### Test ID Selectors

Most stable - not affected by layout or styling changes.

```javascript
// data-testid (convention)
await page.click('[data-testid="submit-button"]');
await page.fill('[data-testid="email-input"]', 'test@example.com');

// Custom data attribute
await page.click('[data-qa="login-btn"]');
await page.click('[data-automation-id="menu"]');
```

## Chaining Selectors

Combine multiple selector engines for precision.

```javascript
// CSS + text (within scope)
await page.click('.menu >> text=Settings');

// Within specific element
await page.click('nav >> css=a.active');

// Multiple levels
await page.click('section.products >> div.card:has-text("Laptop") >> button');
```

## Best Practices

### 1. Prefer Stable Selectors

```javascript
// ✅ Good - test ID (won't change with redesign)
await page.click('[data-testid="submit-btn"]');

// ⚠️ Okay - semantic role + name
await page.click('role=button[name="Submit order"]');

// ❌ Avoid - positional (fragile)
await page.click('div > div:nth-child(3) > button');

// ❌ Avoid - class names that may change
await page.click('.css-1a2b3c4');
```

### 2. Use Has-Text for Dynamic Content

```javascript
// Find row containing specific text, then click its button
await page.click('tr:has-text("Product A") >> button.edit');
```

### 3. Handling Multiple Matches

```javascript
// Get first match (default)
await page.click('.item');

// Get specific index
await page.click('.item >> nth=2');    // 3rd item (0-based)

// Count matches
const count = await page.locator('.item').count();

// Iterate all matches
const items = await page.locator('.item').all();
for (const item of items) {
  const text = await item.textContent();
  console.log(text);
}
```

### 4. Waiting for Selectors

```javascript
// Wait for element to appear
await page.waitForSelector('.results', { timeout: 10000 });

// Wait for element to be visible
await page.waitForSelector('.modal:visible');

// Wait for element to be hidden/removed
await page.waitForSelector('.loading', { state: 'hidden' });

// Wait for specific count
await page.waitForFunction(() => 
  document.querySelectorAll('.item').length >= 5
);
```

## Locator vs ElementHandle

Use `locator()` for modern, retryable selectors:

```javascript
// ✅ Modern - auto-retries, resilient
const submitBtn = page.locator('[data-testid="submit"]');
await submitBtn.click();

// Legacy - static snapshot
const submitBtn = await page.$('[data-testid="submit"]');
await submitBtn.click();
```

## Debugging Selectors

```javascript
// Highlight matching elements
await page.locator('.item').highlight();

// Count matches
const count = await page.locator('.item').count();
console.log(`Found ${count} items`);

// Check visibility
const isVisible = await page.locator('.modal').isVisible();

// Get element text for debugging
const text = await page.locator('h1').textContent();
console.log('Heading:', text);

// Use codegen to discover selectors
// npx playwright codegen https://example.com
```
