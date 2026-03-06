import { Page, Locator, expect } from '@playwright/test';

export interface CampaignFormData {
  title: string;
  description: string;
  category: 'MEDICAL' | 'DISASTER_RELIEF' | 'EDUCATION' | 'COMMUNITY' | 'EMERGENCY' | 'OTHER';
  goal_amount_usd: number;
  // Wallet addresses now optional - generated client-side
  eth_wallet_address?: string;
  btc_wallet_address?: string;
  doge_wallet_address?: string;
  sol_wallet_address?: string;
  // New: chain selection for generation
  generate_chains?: ('btc' | 'eth' | 'doge' | 'sol')[];
  cover_image_url?: string;
  end_date?: string;
}

export class CreateCampaignPage {
  readonly page: Page;
  readonly titleInput: Locator;
  readonly descriptionInput: Locator;
  readonly categorySelect: Locator;
  readonly goalInput: Locator;
  readonly coverImageInput: Locator;
  readonly endDateInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly backLink: Locator;
  
  // New wallet generation elements
  readonly chainSelector: Locator;
  readonly generateWalletsButton: Locator;
  readonly walletModal: Locator;
  readonly seedPhraseDisplay: Locator;
  readonly confirmCheckbox: Locator;
  readonly confirmButton: Locator;

  constructor(page: Page) {
    this.page = page;
    // Use more flexible selectors
    this.titleInput = page.getByLabel('Campaign Title').or(page.locator('input[placeholder*="Help Maria"], input[placeholder*="campaign"]').first());
    this.descriptionInput = page.getByLabel('Campaign Description').or(page.locator('textarea').first());
    this.categorySelect = page.getByLabel('Category').or(page.locator('select').first());
    this.goalInput = page.getByLabel('Goal Amount (USD)').or(page.getByLabel('Goal Amount')).or(page.locator('input[type="number"]').first());
    this.coverImageInput = page.getByLabel(/Cover Image/i).or(page.locator('input[type="url"]').first());
    this.endDateInput = page.getByLabel(/Campaign End Date/i).or(page.locator('input[type="date"]').first());
    this.submitButton = page.getByRole('button', { name: /Create Campaign/i });
    this.cancelButton = page.getByRole('button', { name: /Cancel/i });
    this.backLink = page.getByRole('link', { name: /Back to Campaigns/i });
    
    // Wallet generation selectors
    this.chainSelector = page.getByTestId('chain-selector');
    this.generateWalletsButton = page.getByRole('button', { name: /Generate Wallets/i });
    this.walletModal = page.getByRole('dialog', { name: /Generate Wallets/i }).or(
      page.locator('[role="dialog"][aria-modal="true"]')
    );
    this.seedPhraseDisplay = page.locator('[data-testid^="seed-phrase-display"]').or(page.locator('[data-chain]'));
    this.confirmCheckbox = page.getByLabel(/I have saved my recovery phrases/i).or(page.getByLabel(/saved.*recovery/i));
    this.confirmButton = page.getByRole('button', { name: /Confirm.*Create/i }).or(page.getByRole('button', { name: /Confirm/i }));
  }

  async goto() {
    await this.page.goto('/campaigns/new');
    await this.page.waitForLoadState('networkidle');
    
    // Wait for form to load
    await this.titleInput.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
  }

  async selectChains(chains: ('btc' | 'eth' | 'doge' | 'sol')[]) {
    for (const chain of chains) {
      const chainLabel = chain === 'btc' ? 'Bitcoin' : 
                        chain === 'eth' ? 'Ethereum' : 
                        chain === 'doge' ? 'Dogecoin' : 'Solana';
      await this.page.getByLabel(new RegExp(chainLabel, 'i')).check();
    }
  }

  async generateWallets() {
    await this.generateWalletsButton.click();
    await this.walletModal.waitFor({ state: 'visible', timeout: 10000 });
  }

  async confirmSeedPhrasesSaved() {
    await this.confirmCheckbox.check();
    await this.confirmButton.click();
    // Wait for modal to close
    await this.walletModal.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
  }

  async getSeedPhrases(): Promise<Record<string, string>> {
    const phrases: Record<string, string> = {};
    // Look for seed phrase displays by data-chain attribute
    const phraseElements = await this.page.locator('[data-chain]').all();
    for (const el of phraseElements) {
      const chain = await el.getAttribute('data-chain');
      // Get the text content from the code/pre element inside
      const phraseText = await el.locator('code, pre, .font-mono').first().textContent().catch(() => 
        el.textContent()
      );
      if (chain && phraseText) {
        // Extract just the seed phrase (12 words)
        const words = phraseText.trim().split(/\s+/);
        if (words.length >= 12) {
          phrases[chain] = words.slice(0, 12).join(' ');
        }
      }
    }
    return phrases;
  }

  async fillForm(data: CampaignFormData) {
    // Wait for form to be ready - check for title input
    await this.titleInput.waitFor({ state: 'visible', timeout: 10000 });
    
    await this.titleInput.fill(data.title);
    
    // Wait for description input
    await this.descriptionInput.waitFor({ state: 'visible', timeout: 10000 });
    await this.descriptionInput.fill(data.description);
    
    // Wait for category select
    await this.categorySelect.waitFor({ state: 'visible', timeout: 10000 });
    await this.categorySelect.selectOption(data.category);
    
    // Wait for goal input
    await this.goalInput.waitFor({ state: 'visible', timeout: 10000 });
    await this.goalInput.fill(data.goal_amount_usd.toString());

    // Handle wallet generation if chains are specified
    if (data.generate_chains && data.generate_chains.length > 0) {
      await this.selectChains(data.generate_chains);
      await this.generateWallets();
      
      // Wait for wallets to be generated
      await this.page.waitForTimeout(1000);
      
      // Verify seed phrases are displayed
      const phrases = await this.getSeedPhrases();
      expect(Object.keys(phrases).length).toBeGreaterThan(0);
      
      // Confirm and close modal
      await this.confirmSeedPhrasesSaved();
    }

    // Legacy support: if wallet addresses are provided directly, they won't be used
    // (the new flow requires wallet generation)

    if (data.cover_image_url) {
      await this.coverImageInput.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
      if (await this.coverImageInput.isVisible()) {
        await this.coverImageInput.fill(data.cover_image_url);
      }
    }

    if (data.end_date) {
      await this.endDateInput.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
      if (await this.endDateInput.isVisible()) {
        await this.endDateInput.fill(data.end_date);
      }
    }
  }

  async submit() {
    await this.submitButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }

  async expectValidationError(field: string, message?: string) {
    // Look for error messages - they can be in various places
    const errorText = message || field;
    const errorLocator = this.page.getByText(new RegExp(errorText, 'i')).first();
    await errorLocator.waitFor({ state: 'visible', timeout: 5000 });
  }

  async expectLoadingState() {
    await this.page.getByText(/Creating Campaign/i).waitFor({ state: 'visible' });
  }
}
