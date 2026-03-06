// Login Flow Browser Check Template
import { test, expect } from '@playwright/test'

test('user can login successfully', async ({ page }) => {
  // Navigate to login page
  await page.goto('https://app.example.com/login')
  
  // Fill in credentials
  await page.fill('input[name="email"]', process.env.TEST_EMAIL!)
  await page.fill('input[name="password"]', process.env.TEST_PASSWORD!)
  
  // Submit login form
  await page.click('button[type="submit"]')
  
  // Verify successful login (redirected to dashboard)
  await expect(page).toHaveURL(/\/dashboard/)
  
  // Verify user element is visible
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
})
