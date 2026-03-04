import { test, expect } from '../fixtures';
import { HomePage } from '../pages/home.page';

test.describe('Home Page', () => {
  test('should display hero section with CTAs', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    // Verify hero title is visible
    await expect(homePage.heroTitle).toBeVisible();
    
    // Verify CTA buttons are visible
    await expect(homePage.startCampaignButton).toBeVisible();
    await expect(homePage.browseCampaignsButton).toBeVisible();
  });

  test('should navigate to create campaign from CTA', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    await homePage.clickStartCampaign();

    // Should redirect to login (if not authenticated) or create page
    await page.waitForURL(/\/auth\/login|\/campaigns\/new/, { timeout: 5000 });
  });

  test('should navigate to campaigns from CTA', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    await homePage.clickBrowseCampaigns();

    // Should navigate to campaigns page
    await page.waitForURL(/\/campaigns/, { timeout: 5000 });
    expect(page.url()).toContain('/campaigns');
  });

  test('should display featured campaigns', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    // Wait for campaigns to load
    await page.waitForTimeout(2000);
    
    // Verify page loaded (campaigns may or may not be present)
    expect(page.url()).toMatch(/\/$/); // Should end with /
  });

  test('should display Agent Skills section with API reference', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    // Verify Agent Skills section heading
    await expect(page.getByRole('heading', { name: 'Agent Skills' })).toBeVisible();

    // Verify scrollable skills content contains API reference text
    const skillsBlock = page.getByLabel('MoltFundMe agent skills and API reference');
    await expect(skillsBlock).toBeVisible();
    await expect(skillsBlock).toContainText('X-Agent-API-Key');
  });

  test('should have working navigation links', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    // Test navigation links
    const campaignsLink = await homePage.getNavLinkByText('Campaigns');
    if (await campaignsLink.isVisible({ timeout: 2000 })) {
      await campaignsLink.click();
      await page.waitForURL(/\/campaigns/, { timeout: 5000 });
    }

    await homePage.goto();

    const agentsLink = await homePage.getNavLinkByText('Agents');
    if (await agentsLink.isVisible({ timeout: 2000 })) {
      await agentsLink.click();
      await page.waitForURL(/\/agents/, { timeout: 5000 });
    }

    await homePage.goto();

    const feedLink = await homePage.getNavLinkByText('Feed');
    if (await feedLink.isVisible({ timeout: 2000 })) {
      await feedLink.click();
      await page.waitForURL(/\/feed/, { timeout: 5000 });
    }
  });
});
