# Waiting Patterns — Puppeteer

## The Golden Rule

**Never assume an element exists. Always wait.**

90% of Puppeteer failures are timing issues. The page looks ready to you, but JavaScript hasn't finished rendering.

## Wait Methods

### waitForSelector (Most Common)
```javascript
// Wait for element to exist in DOM
await page.waitForSelector('#results');

// Wait for element to be visible
await page.waitForSelector('#modal', { visible: true });

// Wait for element to disappear
await page.waitForSelector('.loading', { hidden: true });

// With timeout
await page.waitForSelector('#slow-element', { timeout: 10000 });
```

### waitForNavigation
```javascript
// After clicking a link that navigates
await Promise.all([
  page.waitForNavigation(),
  page.click('a.next-page')
]);

// Wait for specific navigation type
await page.waitForNavigation({ waitUntil: 'networkidle0' });
```

### waitUntil Options
| Option | Meaning | Use When |
|--------|---------|----------|
| `load` | Window load event | Basic pages |
| `domcontentloaded` | DOM ready | Fast check |
| `networkidle0` | No requests for 500ms | SPAs, AJAX |
| `networkidle2` | Max 2 requests for 500ms | Most reliable |

### waitForFunction (Custom Conditions)
```javascript
// Wait for text to appear
await page.waitForFunction(() => 
  document.body.innerText.includes('Results loaded')
);

// Wait for array to have items
await page.waitForFunction(() => 
  window.searchResults && window.searchResults.length > 0
);

// Wait with arguments
await page.waitForFunction(
  (minCount) => document.querySelectorAll('.item').length >= minCount,
  {},
  5  // argument passed to function
);
```

### waitForResponse (API Calls)
```javascript
// Wait for specific API response
const response = await page.waitForResponse(
  res => res.url().includes('/api/data')
);
const data = await response.json();
```

### waitForRequest
```javascript
// Wait for request to be sent
await page.waitForRequest(req => 
  req.url().includes('/api/submit') && req.method() === 'POST'
);
```

## Common Patterns

### Click Then Wait
```javascript
// Pattern: click + wait for result
await page.click('#search-button');
await page.waitForSelector('.search-results');
```

### Form Submit
```javascript
// Submit and wait for navigation
await Promise.all([
  page.waitForNavigation(),
  page.click('button[type="submit"]')
]);
```

### Infinite Scroll
```javascript
// Load more content
let previousHeight;
while (true) {
  previousHeight = await page.evaluate('document.body.scrollHeight');
  await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
  await page.waitForFunction(
    `document.body.scrollHeight > ${previousHeight}`,
    { timeout: 3000 }
  ).catch(() => null);
  
  const newHeight = await page.evaluate('document.body.scrollHeight');
  if (newHeight === previousHeight) break;
}
```

### Loading Spinner
```javascript
// Wait for spinner to appear then disappear
await page.waitForSelector('.spinner', { visible: true });
await page.waitForSelector('.spinner', { hidden: true });
```

## Timeout Strategies

```javascript
// Global default (affects all waits)
page.setDefaultTimeout(30000);

// Per-operation timeout
await page.waitForSelector('#slow', { timeout: 60000 });

// Catch timeout gracefully
try {
  await page.waitForSelector('#maybe-exists', { timeout: 5000 });
} catch (e) {
  if (e.name === 'TimeoutError') {
    console.log('Element not found, continuing...');
  } else {
    throw e;
  }
}
```

## Avoid These

```javascript
// BAD: Fixed delay (unreliable, slow)
await page.waitForTimeout(3000);

// BAD: Assuming element exists
await page.click('#button'); // May fail

// BAD: Not waiting after navigation
await page.goto(url);
await page.click('#element'); // Page might not be ready
```

## Race Conditions

```javascript
// Wait for either success or error
const result = await Promise.race([
  page.waitForSelector('.success'),
  page.waitForSelector('.error')
]);

const isSuccess = await result.evaluate(el => 
  el.classList.contains('success')
);
```
