# Debugging Reference

Techniques for debugging Playwright scripts.

## Headless vs Headed Mode

### Headless (Default)

Faster, no UI - use for production runs.

```javascript
const browser = await chromium.launch({ headless: true });
```

### Headed (Visual)

See the browser window - essential for debugging.

```javascript
const browser = await chromium.launch({ headless: false });
```

### Slow Motion

Add delays between actions to observe behavior.

```javascript
const browser = await chromium.launch({
  headless: false,
  slowMo: 100  // 100ms delay between actions
});
```

## Visual Debugging

### Screenshots on Error

```javascript
try {
  await page.click('.submit-button');
} catch (error) {
  await page.screenshot({ path: 'tmp/error-screenshot.png' });
  throw error;
}
```

### Full Page Screenshots

```javascript
await page.screenshot({ path: 'tmp/page.png', fullPage: true });
```

### Element Screenshots

```javascript
await page.locator('.chart').screenshot({ path: 'tmp/chart.png' });
```

### Before/After Screenshots

```javascript
await page.screenshot({ path: 'tmp/before.png' });
await page.click('.expand-btn');
await page.waitForTimeout(500);
await page.screenshot({ path: 'tmp/after.png' });
```

## Console Logging

### Browser Console Messages

```javascript
page.on('console', msg => {
  console.log(`[${msg.type()}] ${msg.text()}`);
});

page.on('pageerror', error => {
  console.error('Page error:', error.message);
});
```

### Network Request Logging

```javascript
page.on('request', request => {
  console.log(`>> ${request.method()} ${request.url()}`);
});

page.on('response', response => {
  console.log(`<< ${response.status()} ${response.url()}`);
});
```

### Add Your Own Logs

```javascript
console.log('Navigating to page...');
await page.goto('https://example.com');
console.log('Page loaded, URL:', page.url());

const title = await page.title();
console.log('Page title:', title);
```

## Common Error Patterns

### Timeout Errors

```
Error: Timeout 30000ms exceeded
```

**Causes & Fixes:**
- Selector doesn't match any element → Verify selector with codegen
- Element exists but not visible → Use `state: 'attached'` or wait for visibility
- Page still loading → Add explicit wait

```javascript
// Wait for element to be attached to DOM
await page.waitForSelector('.result', { state: 'attached' });

// Wait for element to be visible
await page.waitForSelector('.result', { state: 'visible' });

// Increase timeout for slow operations
await page.waitForSelector('.result', { timeout: 60000 });
```

### Selector Not Found

```
Error: locator.click: Error: strict mode violation
```

**Fix:** Selector matches multiple elements. Be more specific:

```javascript
// ❌ Matches multiple buttons
await page.click('button');

// ✅ More specific
await page.click('button[type="submit"]');
await page.click('text=Submit order');
await page.click('button:has-text("Add")');
```

### Navigation Timeout

```
Error: page.goto: net::ERR_CONNECTION_REFUSED
```

**Check:**
- URL is correct
- Site is accessible
- No VPN/firewall blocking

### Frame/Iframe Issues

```javascript
// Access iframe content
const frame = page.frameLocator('iframe[name="content"]');
await frame.locator('.inside-iframe').click();
```

## Using Codegen for Debugging

Launch codegen to explore selectors interactively:

```bash
npx playwright codegen https://example.com
```

This opens:
1. Browser window you can interact with
2. Inspector showing generated code
3. Selector picker tool (🔍 icon)

## Trace Viewer (Advanced)

Record detailed traces for post-mortem debugging:

```javascript
const context = await browser.newContext();
await context.tracing.start({ screenshots: true, snapshots: true });

// ... your code ...

await context.tracing.stop({ path: 'tmp/trace.zip' });
```

View trace:
```bash
npx playwright show-trace tmp/trace.zip
```

## Element State Debugging

```javascript
// Check if element exists
const exists = await page.locator('.item').count() > 0;

// Check visibility
const isVisible = await page.locator('.modal').isVisible().catch(() => false);

// Check if enabled
const isEnabled = await page.locator('button').isEnabled();

// Get element count
const count = await page.locator('.item').count();
console.log(`Found ${count} items`);
```

## Network Debugging

```javascript
// Wait for specific request
await page.waitForRequest('**/api/data');

// Wait for response
const response = await page.waitForResponse('**/api/users');
console.log(await response.json());

// Mock slow network
const context = await browser.newContext({
  slowMo: 500  // Slow all operations
});
```

## Best Practices

1. **Start headed** - Always develop in headed mode (`headless: false`)
2. **Add screenshots** - Capture on errors and key milestones
3. **Log liberally** - Add console.log at each step
4. **Use slowMo** - Slow down to observe timing issues
5. **Verify selectors** - Use codegen to find correct selectors
6. **Check waits** - Ensure proper wait conditions for dynamic content
