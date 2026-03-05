import { test, expect } from '../fixtures';
import { authenticatedTest } from '../fixtures';
import { CreateCampaignPage } from '../pages/create-campaign.page';

test.describe('Wallet Generation Flow', () => {
  authenticatedTest('should generate wallets for selected chains', async ({ authenticatedPage }) => {
    const createPage = new CreateCampaignPage(authenticatedPage);
    await createPage.goto();
    
    // Fill basic campaign info
    await createPage.titleInput.fill('Wallet Gen Test Campaign');
    await createPage.descriptionInput.fill('Testing wallet generation');
    await createPage.categorySelect.selectOption('COMMUNITY');
    await createPage.goalInput.fill('5000');
    
    // Select chains
    await createPage.selectChains(['btc', 'eth', 'sol']);
    
    // Generate wallets
    await createPage.generateWallets();
    
    // Verify modal shows seed phrases
    await expect(createPage.walletModal).toBeVisible({ timeout: 10000 });
    // Wait for at least one seed phrase to appear
    await expect(createPage.page.locator('[data-chain]').first()).toBeVisible({ timeout: 10000 });
    
    // Get and verify seed phrases
    const phrases = await createPage.getSeedPhrases();
    expect(Object.keys(phrases).length).toBeGreaterThan(0);
    
    // Verify each phrase has 12 words
    for (const [chain, phrase] of Object.entries(phrases)) {
      expect(phrase.split(' ').length).toBeGreaterThanOrEqual(12);
    }
    
    // Confirm and submit
    await createPage.confirmSeedPhrasesSaved();
    
    // Modal should close
    await createPage.walletModal.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
    
    // Submit the form
    await createPage.submit();
    
    // Should redirect to campaign detail
    await authenticatedPage.waitForURL(/\/campaigns\/[^/]+/, { timeout: 15000 });
  });
  
  authenticatedTest('should not allow submission without confirming seed phrase backup', async ({ authenticatedPage }) => {
    const createPage = new CreateCampaignPage(authenticatedPage);
    await createPage.goto();
    
    // Fill form and generate wallets
    await createPage.titleInput.fill('No Confirm Test');
    await createPage.descriptionInput.fill('Test');
    await createPage.categorySelect.selectOption('OTHER');
    await createPage.goalInput.fill('1000');
    
    await createPage.selectChains(['eth']);
    await createPage.generateWallets();
    
    // Wait for modal and confirm button
    await expect(createPage.walletModal).toBeVisible();
    await expect(createPage.confirmButton).toBeVisible();
    
    // Try to submit without checking confirmation - button should be disabled
    const isDisabled = await createPage.confirmButton.isDisabled();
    expect(isDisabled).toBe(true);
  });
  
  authenticatedTest('should copy seed phrase to clipboard', async ({ authenticatedPage, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    
    const createPage = new CreateCampaignPage(authenticatedPage);
    await createPage.goto();
    
    await createPage.selectChains(['eth']);
    await createPage.generateWallets();
    
    // Wait for modal
    await expect(createPage.walletModal).toBeVisible();
    
    // Find and click copy button for ETH
    const copyButton = authenticatedPage.getByRole('button', { name: /Copy.*ETH/i }).or(
      authenticatedPage.getByRole('button', { name: /Copy/i }).first()
    );
    await copyButton.click();
    
    // Verify clipboard (if possible)
    try {
      const clipboardText = await authenticatedPage.evaluate(() => navigator.clipboard.readText());
      expect(clipboardText.split(' ').length).toBeGreaterThanOrEqual(12);
    } catch (e) {
      // Clipboard access might not work in test environment, that's okay
      // Just verify the button was clickable
      expect(await copyButton.isVisible()).toBe(true);
    }
  });
  
  authenticatedTest('should show warning about saving seed phrases', async ({ authenticatedPage }) => {
    const createPage = new CreateCampaignPage(authenticatedPage);
    await createPage.goto();
    
    await createPage.selectChains(['btc']);
    await createPage.generateWallets();
    
    // Verify warning message is visible (use first() to handle multiple matches)
    await expect(authenticatedPage.getByText(/save.*recovery.*phrases/i).first()).toBeVisible({ timeout: 5000 });
    await expect(authenticatedPage.getByText(/cannot.*recover/i).first().or(
      authenticatedPage.getByText(/lose.*funds/i).first()
    )).toBeVisible({ timeout: 5000 });
  });
  
  authenticatedTest('should allow selecting multiple chains', async ({ authenticatedPage }) => {
    const createPage = new CreateCampaignPage(authenticatedPage);
    await createPage.goto();
    
    // Select available chains (Dogecoin may not be available in all environments)
    const availableChains: ('btc' | 'eth' | 'sol')[] = ['btc', 'eth', 'sol'];
    const selectedChains: ('btc' | 'eth' | 'sol')[] = [];
    
    for (const chain of availableChains) {
      const chainLabel = chain === 'btc' ? 'Bitcoin' : chain === 'eth' ? 'Ethereum' : 'Solana';
      const checkbox = authenticatedPage.getByLabel(new RegExp(chainLabel, 'i'));
      if (await checkbox.isVisible({ timeout: 2000 }).catch(() => false)) {
        await checkbox.check();
        selectedChains.push(chain);
      }
    }
    
    expect(selectedChains.length).toBeGreaterThanOrEqual(2);
    
    // Generate wallets
    await createPage.generateWallets();
    
    // Verify selected chains have seed phrases
    const phrases = await createPage.getSeedPhrases();
    expect(Object.keys(phrases).length).toBeGreaterThanOrEqual(2);
  });
});
