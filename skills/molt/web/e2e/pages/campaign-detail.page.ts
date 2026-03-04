import { Page, Locator } from '@playwright/test';

export class CampaignDetailPage {
  readonly page: Page;
  readonly campaignTitle: Locator;
  readonly campaignDescription: Locator;
  readonly progressBar: Locator;
  readonly detailsTab: Locator;
  readonly warRoomTab: Locator;
  readonly copyEthButton: Locator;
  readonly copyBtcButton: Locator;
  readonly copyDogeButton: Locator;
  readonly copySolButton: Locator;
  readonly advocatesList: Locator;
  readonly shareButtons: Locator;
  readonly donationList: Locator;
  readonly donationItems: Locator;

  constructor(page: Page) {
    this.page = page;
    this.campaignTitle = page.locator('h1').first();
    this.campaignDescription = page.locator('[data-testid="campaign-description"]');
    this.progressBar = page.locator('[data-testid="progress-bar"], .progress-bar');
    this.detailsTab = page.getByRole('tab', { name: /Details/i }).or(
      page.getByRole('button', { name: /Details/i })
    );
    this.warRoomTab = page.getByRole('tab', { name: /War Room/i }).or(
      page.getByRole('button', { name: /War Room/i })
    );
    this.copyEthButton = page.getByRole('button', { name: /Copy.*ETH/i }).or(page.locator('button').filter({ hasText: /ETH/i }).first());
    this.copyBtcButton = page.getByRole('button', { name: /Copy.*BTC/i }).or(page.locator('button').filter({ hasText: /BTC/i }).first());
    this.copyDogeButton = page.getByRole('button', { name: /Copy.*DOGE/i }).or(page.locator('button').filter({ hasText: /DOGE/i }).first());
    this.copySolButton = page.getByRole('button', { name: /Copy.*SOL/i }).or(page.locator('button').filter({ hasText: /SOL/i }).first());
    this.advocatesList = page.locator('[data-testid="advocates-list"]');
    this.shareButtons = page.locator('[data-testid="share-button"]');
    this.donationList = page.getByTestId('donation-list');
    this.donationItems = page.getByTestId('donation-item');
  }

  async goto(campaignId: string) {
    await this.page.goto(`/campaigns/${campaignId}`);
  }

  async getTitle(): Promise<string | null> {
    return await this.campaignTitle.textContent();
  }

  async clickDetailsTab() {
    await this.detailsTab.click();
  }

  async clickWarRoomTab() {
    await this.warRoomTab.click();
  }

  async copyEthAddress() {
    await this.copyEthButton.click();
  }

  async copyBtcAddress() {
    await this.copyBtcButton.click();
  }

  async copyDogeAddress() {
    if (await this.copyDogeButton.isVisible()) {
      await this.copyDogeButton.click();
    }
  }

  async copySolAddress() {
    if (await this.copySolButton.isVisible()) {
      await this.copySolButton.click();
    }
  }

  async expectTabActive(tabName: 'Details' | 'War Room') {
    const tab = tabName === 'Details' ? this.detailsTab : this.warRoomTab;
    await tab.waitFor({ state: 'visible' });
  }

  async expectDonationsVisible() {
    await expect(this.donationList.or(this.donationItems.first())).toBeVisible({ timeout: 5000 });
  }

  async getDonationCount(): Promise<number> {
    return await this.donationItems.count();
  }

  async getAdvocateCount(): Promise<number> {
    // Look for advocate count in various possible locations
    const advocateText = this.page.getByText(/advocate/i).or(this.page.locator('[data-testid="advocate-count"]'));
    const countText = await advocateText.first().textContent().catch(() => null);
    if (countText) {
      const match = countText.match(/(\d+)/);
      if (match) {
        return parseInt(match[1], 10);
      }
    }
    // Fallback: count advocate items
    const advocateItems = this.page.locator('[data-testid="advocate-item"], .advocate-item');
    return await advocateItems.count();
  }
}
