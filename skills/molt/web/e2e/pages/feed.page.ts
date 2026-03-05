import { Page, Locator } from '@playwright/test';

export class FeedPage {
  readonly page: Page;
  readonly feedEvents: Locator;
  readonly filterChips: Locator;
  readonly campaignLinks: Locator;
  readonly pagination: Locator;

  constructor(page: Page) {
    this.page = page;
    this.feedEvents = page.locator('[data-testid="feed-event"], .feed-event');
    this.filterChips = page.locator('[data-testid="filter-chip"], button[data-filter]');
    this.campaignLinks = page.locator('a[href*="/campaigns/"]');
    this.pagination = page.locator('[data-testid="pagination"]');
  }

  async goto() {
    await this.page.goto('/feed');
  }

  async selectFilter(filter: 'all' | 'campaigns' | 'advocacy' | 'discussions') {
    const filterButton = this.page.getByRole('button', { name: new RegExp(filter, 'i') });
    if (await filterButton.isVisible()) {
      await filterButton.click();
    }
  }

  async clickCampaignLink(index: number = 0) {
    await this.campaignLinks.nth(index).click();
  }

  async getEventCount(): Promise<number> {
    return await this.feedEvents.count();
  }

  async expectEventsVisible(count?: number) {
    if (count !== undefined) {
      await this.page.waitForFunction(
        (expectedCount) => {
          const events = document.querySelectorAll('[data-testid="feed-event"], .feed-event');
          return events.length >= expectedCount;
        },
        count
      );
    } else {
      await this.feedEvents.first().waitFor({ state: 'visible' });
    }
  }

  async getFeedEvents(): Promise<Array<{ text: string }>> {
    await this.page.waitForLoadState('networkidle');
    const events: Array<{ text: string }> = [];
    const count = await this.feedEvents.count();
    
    for (let i = 0; i < count; i++) {
      const event = this.feedEvents.nth(i);
      const text = await event.textContent().catch(() => '');
      if (text) {
        events.push({ text });
      }
    }
    
    return events;
  }
}
