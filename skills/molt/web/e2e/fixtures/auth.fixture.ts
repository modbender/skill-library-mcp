import { test as base, Page } from '@playwright/test';
import { test as apiTest } from './api.fixture';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

export interface AuthFixture {
  authenticatedPage: Page;
  authenticatedEmail: string;
  authenticatedToken: string;
}

export const test = apiTest.extend<AuthFixture>({
  authenticatedPage: async ({ browser, authenticatedEmail, authenticatedToken, api }, use) => {
    // Create a new context
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Go through the actual login flow
    await page.goto(`${BASE_URL}/auth/login`);
    
    // Request magic link
    const magicLinkResponse = await api.requestMagicLink(authenticatedEmail);
    const tokenMatch = magicLinkResponse.message?.match(/Token: ([^\s]+)/);
    if (!tokenMatch) {
      throw new Error('Failed to get magic link token (token not exposed - may be production mode)');
    }
    const magicToken = tokenMatch[1];
    
    // Fill email and submit (if form is shown)
    const emailInput = page.getByLabel(/Email/i).or(page.locator('input[type="email"]'));
    if (await emailInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await emailInput.fill(authenticatedEmail);
      await page.getByRole('button', { name: /Request Magic Link/i }).click();
      await page.waitForTimeout(1000);
    }
    
    // Navigate to verify page with token
    await page.goto(`${BASE_URL}/auth/verify?token=${magicToken}`);
    
    // Wait for redirect to campaigns/new (successful auth)
    await page.waitForURL(/\/campaigns\/new/, { timeout: 15000 });
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Wait for loading spinner to disappear (AuthContext loading)
    await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 }).catch(() => {});
    
    // Verify we're authenticated
    const tokenInStorage = await page.evaluate(() => window.localStorage.getItem('moltfundme_token'));
    if (!tokenInStorage) {
      throw new Error('Authentication failed - token not in localStorage');
    }
    
    // In production, KYC verification may be required before accessing the campaign form.
    // Handle KYC if it appears (upload test images and submit).
    // Check multiple times as KYC form may appear after initial page load
    let isKYCRequired = false;
    for (let attempt = 0; attempt < 3; attempt++) {
      await page.waitForTimeout(2000);
      const kycForm = page.getByText(/Verify Your Identity/i);
      isKYCRequired = await kycForm.isVisible({ timeout: 3000 }).catch(() => false);
      if (isKYCRequired) break;
    }
    
    if (isKYCRequired) {
      // Create minimal test image files for KYC upload
      const fs = await import('fs');
      const path = await import('path');
      const base64Image = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      const buffer = Buffer.from(base64Image, 'base64');
      const tmpDir = path.join(process.cwd(), 'test-images');
      if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });
      
      const idPath = path.join(tmpDir, `kyc-id-${Date.now()}.png`);
      const selfiePath = path.join(tmpDir, `kyc-selfie-${Date.now()}.png`);
      fs.writeFileSync(idPath, buffer);
      fs.writeFileSync(selfiePath, buffer);
      
      // Upload ID photo and selfie
      const fileInputs = page.locator('input[type="file"]');
      const fileInputCount = await fileInputs.count();
      if (fileInputCount >= 2) {
        await fileInputs.first().setInputFiles(idPath);
        await page.waitForTimeout(1000);
        await fileInputs.nth(1).setInputFiles(selfiePath);
        await page.waitForTimeout(1000);
        
        // Submit KYC
        await page.getByRole('button', { name: /Submit Verification/i }).click();
        await page.waitForTimeout(5000);
        await page.waitForLoadState('networkidle');
        
        // Wait for success message or redirect
        await Promise.race([
          page.getByText(/KYC verification submitted successfully/i).waitFor({ timeout: 10000 }).catch(() => {}),
          page.waitForURL(/\/campaigns\/new/, { timeout: 10000 }).catch(() => {}),
          page.waitForTimeout(10000),
        ]);
        
        // Wait for loading to complete
        await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 15000 }).catch(() => {});
        await page.waitForLoadState('networkidle');
      }
      
      // Clean up temp files
      try {
        fs.unlinkSync(idPath);
        fs.unlinkSync(selfiePath);
      } catch (e) {
        // Ignore cleanup errors
      }
    }
    
    // Ensure we're on the campaign form page and it's loaded
    await page.waitForTimeout(2000);
    await page.waitForLoadState('networkidle');
    
    // Verify campaign form is accessible (either visible or KYC was completed)
    const campaignFormVisible = await page.getByLabel('Campaign Title').isVisible({ timeout: 5000 }).catch(() => false);
    const stillKycForm = await page.getByText(/Verify Your Identity/i).isVisible({ timeout: 2000 }).catch(() => false);
    
    if (!campaignFormVisible && stillKycForm) {
      throw new Error('KYC form still blocking campaign creation after submission attempt');
    }
    
    await use(page);
    await context.close();
  },

  authenticatedEmail: async ({ api }, use) => {
    const email = `test-${Date.now()}@example.com`;
    await use(email);
  },

  authenticatedToken: async ({ api, authenticatedEmail }, use) => {
    // Request magic link
    const magicLinkResponse = await api.requestMagicLink(authenticatedEmail);
    
    // Extract token from message (dev mode format: "Token: <token>")
    const tokenMatch = magicLinkResponse.message.match(/Token: ([^\s]+)/);
    if (!tokenMatch) {
      throw new Error('Failed to extract token from magic link response');
    }
    const token = tokenMatch[1];

    // Verify token to get JWT
    const verifyResponse = await api.verifyToken(token);
    if (!verifyResponse.success || !verifyResponse.access_token) {
      throw new Error('Failed to verify token and get access token');
    }

    await use(verifyResponse.access_token);
  },
});
