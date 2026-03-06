import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly requestMagicLinkButton: Locator;
  readonly tokenDisplay: Locator;
  readonly verifyLink: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel(/Email/i).or(page.locator('input[type="email"]'));
    this.requestMagicLinkButton = page.getByRole('button', { name: /Request Magic Link/i });
    this.tokenDisplay = page.locator('code');
    this.verifyLink = page.getByRole('link', { name: /Verify Token/i });
    this.errorMessage = page.locator('.text-error, [role="alert"]');
  }

  async goto() {
    await this.page.goto('/auth/login');
  }

  async fillEmail(email: string) {
    await this.emailInput.fill(email);
  }

  async requestMagicLink() {
    await this.requestMagicLinkButton.click();
  }

  async getToken(): Promise<string | null> {
    const tokenElement = this.tokenDisplay.first();
    if (await tokenElement.isVisible()) {
      return await tokenElement.textContent();
    }
    return null;
  }

  async clickVerifyLink() {
    await this.verifyLink.click();
  }

  async expectTokenDisplayed() {
    await this.tokenDisplay.first().waitFor({ state: 'visible' });
  }

  async expectError(message?: string) {
    if (message) {
      await this.page.getByText(message).waitFor({ state: 'visible' });
    } else {
      await this.errorMessage.first().waitFor({ state: 'visible' });
    }
  }
}
