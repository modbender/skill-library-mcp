import { chromium } from 'playwright';

/**
 * Form Interaction Example
 * Demonstrates filling and submitting a form.
 * 
 * Usage: node examples/form-interaction.mjs
 * Note: This example uses httpbin.org for demonstration.
 */

const url = 'https://httpbin.org/forms/post';

const browser = await chromium.launch({ headless: false }); // Show browser
const page = await browser.newPage();

console.log('Opening form page...');
await page.goto(url, { waitUntil: 'networkidle' });

// Fill form fields
console.log('Filling form...');
await page.fill('input[name="custname"]', 'John Doe');
await page.fill('input[name="custtel"]', '555-0123');
await page.fill('input[name="custemail"]', 'john@example.com');

// Select dropdown
await page.selectOption('select[name="size"]', 'large');

// Check radio button
await page.check('input[value="bacon"]');

// Check multiple checkboxes
await page.check('input[name="topping"][value="cheese"]');
await page.check('input[name="topping"][value="mushroom"]');

// Add delivery instructions
await page.fill('textarea[name="comments"]', 'Please deliver to side door');

console.log('Form filled. Submitting...');

// Submit form and wait for navigation
await Promise.all([
  page.waitForNavigation(),
  page.click('button[type="submit"]')
]);

console.log(`Form submitted! Current URL: ${page.url()}`);
console.log('Taking screenshot of result...');
await page.screenshot({ path: 'tmp/form-result.png' });

// Keep browser open briefly to see result
await page.waitForTimeout(3000);
await browser.close();
console.log('Done!');
