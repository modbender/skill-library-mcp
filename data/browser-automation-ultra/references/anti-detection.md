# Anti-Detection Rules for Browser Automation Scripts

## Why This Matters

Platforms like Xiaohongshu, DeviantArt, Pinterest, Behance use behavioral analysis to detect automation. Violations result in shadow bans, captcha loops, or account suspension.

## Rules

### 1. No Fixed Delays

```javascript
// ❌ NEVER
await page.waitForTimeout(3000);

// ✅ ALWAYS
await humanDelay(2000, 4000);
await humanThink(1000, 3000); // before form fills
```

### 2. No Instant Text Injection

```javascript
// ❌ NEVER — no keydown/keyup events, detected by frontend monitoring
await input.fill(text);
await page.evaluate(() => { input.value = text; });
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, text);

// ✅ ALWAYS — real keystroke events with variable timing
await humanType(page, 'input[name="title"]', text);
await humanFillContentEditable(page, '[contenteditable="true"]', text);
```

### 3. No Teleport Clicks

```javascript
// ❌ NEVER — coordinates jump instantly, no mousemove events
await element.click();
await page.click('button.submit');

// ✅ ALWAYS — bezier curve mouse path → random hover → press/release jitter
await humanClick(page, 'button.submit');
await humanClick(page, elementHandle); // also accepts element handles
```

### 4. Page Browsing Simulation Required

```javascript
// ❌ NEVER — open page then immediately operate
await page.goto(url);
await page.fill('input', text); // too fast

// ✅ ALWAYS — simulate human reading the page first
await page.goto(url, { waitUntil: 'networkidle' });
await humanDelay(2000, 4000);  // page load settling
await humanBrowse(page);       // scroll + mouse wander
await humanThink(800, 2000);   // pause before action
await humanType(page, 'input', text);
```

### 5. Cron Time Jitter

```javascript
// ❌ NEVER — publish at exact same time every day
// cron: 0 10 * * *

// ✅ ALWAYS — add random offset at script start
const { jitterWait } = require('./utils/human-like');
await jitterWait(1, 15); // random 1-15 minute delay
```

### 6. page.evaluate() Usage

```javascript
// ✅ OK — reading DOM state
const count = await page.evaluate(() => document.querySelectorAll('.item').length);

// ✅ OK — clicking from a dynamic list (no other way)
await page.evaluate((idx) => document.querySelectorAll('.tag')[idx].click(), index);

// ❌ NEVER — injecting text or triggering form submission
await page.evaluate((t) => { document.querySelector('input').value = t; }, text);
```

### 7. setInputFiles Exception

File upload has no human-like alternative. Direct call allowed:

```javascript
await fileInput.setInputFiles(path);
```

But always add random delays around it:

```javascript
await humanThink(500, 1500);
await fileInput.setInputFiles(imagePath);
await humanDelay(3000, 6000); // wait for upload processing
```

## human-like.js Function Reference

### humanDelay(minMs, maxMs) → Promise<number>
Random delay using uniform distribution. Returns actual ms waited.

### humanThink(minMs, maxMs) → Promise<number>
Alias for longer delays (default 1500-4000ms). Use before form interactions.

### humanClick(page, selectorOrElement, opts?) → Promise<void>
1. Resolves element bounding box
2. Picks random point within element (not always center)
3. Generates bezier curve mouse path from random viewport position
4. Moves mouse along path with 3-12ms steps
5. Hovers 80-250ms
6. mousedown → 40-120ms → mouseup
7. Post-click pause 100-400ms

Options: `{ timeout: 10000, button: 'left' }`

### humanType(page, selector, text, opts?) → Promise<void>
1. If selector provided, humanClick on it first
2. Types each character with gaussian-distributed delay
3. 3% chance of typo (adjacent QWERTY key) → auto-backspace → correct key
4. Extra pause after punctuation/spaces (30% chance)

Options: `{ minDelay: 50, maxDelay: 180, typoRate: 0.03 }`

### humanFillContentEditable(page, selector, text, opts?) → Promise<void>
humanClick on element, then type line-by-line with Enter between lines.

### humanBrowse(page, opts?) → Promise<void>
Simulates 2-5s of page browsing: random scrolls + mouse movements + pauses.

### humanScroll(page, opts?) → Promise<void>
2-5 scroll events with random direction (80% down, 20% up). 500-2000ms between scrolls.

### jitterWait(minMinutes, maxMinutes) → Promise<number>
Waits random minutes. Logs the wait time. Returns ms waited.

### jitterSchedule(baseMinutes, range) → number
Returns baseMinutes ± range (for schedule calculation, not waiting).
