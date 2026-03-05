// Basic Browser Check Template
import { test, expect } from '@playwright/test'

test('homepage loads successfully', async ({ page }) => {
  // Navigate to page
  const response = await page.goto('https://example.com')
  expect(response?.status()).toBeLessThan(400)
  
  // Check page title
  await expect(page).toHaveTitle(/Example/)
  
  // Verify key element exists
  await expect(page.locator('h1')).toBeVisible()
  
  // Take screenshot for debugging
  await page.screenshot({ path: 'homepage.jpg' })
})
