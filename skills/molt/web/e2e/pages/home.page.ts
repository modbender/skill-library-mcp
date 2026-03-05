import { Page, Locator } from '@playwright/test';

export class HomePage {
  readonly page: Page;
  readonly startCampaignButton: Locator;
  readonly browseCampaignsButton: Locator;
  readonly heroTitle: Locator;
  readonly featuredCampaigns: Locator;
  readonly navLinks: Locator;

  constructor(page: Page) {
    this.page = page;
    // CTA buttons - match both old ("Start a Campaign") and new ("Start a MoltFundMe") text
    this.startCampaignButton = page.getByRole('link', { name: /Start a (Campaign|MoltFundMe)/i }).first();
    this.browseCampaignsButton = page.getByRole('link', { name: /Browse Campaigns|View all/i }).first();
    this.heroTitle = page.getByRole('heading', { name: /Where.*(Molts|AI agents) help/i });
    this.featuredCampaigns = page.locator('[data-testid="featured-campaigns"]');
    this.navLinks = page.locator('nav a');
  }

  async goto() {
    await this.page.goto('/');
  }

  async clickStartCampaign() {
    await this.startCampaignButton.click();
  }

  async clickBrowseCampaigns() {
    await this.browseCampaignsButton.click();
  }

  async getNavLinkByText(text: string) {
    return this.navLinks.filter({ hasText: text });
  }
}
