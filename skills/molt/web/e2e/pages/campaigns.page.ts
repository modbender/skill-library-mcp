import { Page, Locator } from '@playwright/test';

export class CampaignsPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly categorySelect: Locator;
  readonly sortSelect: Locator;
  readonly campaignCards: Locator;
  readonly pagination: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.getByPlaceholder('Search campaigns...');
    this.categorySelect = page.locator('select').first();
    this.sortSelect = page.locator('select').nth(1);
    // Match campaign cards but exclude navigation links (like /campaigns/new)
    this.campaignCards = page.locator('[data-testid="campaign-card"]').or(
      page.locator('a[href*="/campaigns/"]').filter({ hasNot: page.locator('[href="/campaigns/new"]') })
        .filter({ has: page.locator('h2, h3, [class*="title"], [class*="card"]') })
    );
    this.pagination = page.locator('[data-testid="pagination"]');
  }

  async goto() {
    await this.page.goto('/campaigns');
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Wait for debounce
  }

  async selectCategory(category: string) {
    await this.categorySelect.selectOption(category);
  }

  async selectSort(sort: string) {
    await this.sortSelect.selectOption(sort);
  }

  async clickCampaign(index: number = 0) {
    await this.campaignCards.nth(index).click();
  }

  async getCampaignCount(): Promise<number> {
    return await this.campaignCards.count();
  }

  async expectCampaignsVisible(count?: number) {
    if (count !== undefined) {
      await this.page.waitForFunction(
        (expectedCount) => {
          const cards = document.querySelectorAll('[data-testid="campaign-card"], a[href*="/campaigns/"]');
          return cards.length === expectedCount;
        },
        count
      );
    } else {
      await this.campaignCards.first().waitFor({ state: 'visible' });
    }
  }
}
