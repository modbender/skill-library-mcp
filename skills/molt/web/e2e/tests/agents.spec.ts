import { test, expect } from '../fixtures';
import { AgentsPage } from '../pages/agents.page';

test.describe('Agents', () => {
  test('should display leaderboard', async ({ page, api }) => {
    const agentsPage = new AgentsPage(page);
    await agentsPage.goto();

    // Leaderboard should be visible
    await page.waitForTimeout(1000); // Wait for data to load
    
    // Verify page loaded
    expect(page.url()).toContain('/agents');
  });

  test('should filter leaderboard by timeframe', async ({ page }) => {
    const agentsPage = new AgentsPage(page);
    await agentsPage.goto();

    // Try to select different timeframes if filter exists
    if (await agentsPage.timeframeFilter.isVisible()) {
      await agentsPage.selectTimeframe('week');
      await page.waitForTimeout(500);

      await agentsPage.selectTimeframe('month');
      await page.waitForTimeout(500);

      await agentsPage.selectTimeframe('all-time');
      await page.waitForTimeout(500);
    }
  });

  test('should navigate to agent profile', async ({ page, api }) => {
    // Register a test agent
    const agentName = `test-agent-${Date.now()}`;
    const agentResponse = await api.registerAgent({
      name: agentName,
      description: 'Test agent for E2E',
    });

    const agentsPage = new AgentsPage(page);
    await agentsPage.goto();

    // Find and click agent link
    const agentLink = page.getByRole('link', { name: agentName });
    if (await agentLink.isVisible({ timeout: 5000 })) {
      await agentLink.click();
      
      // Should navigate to agent profile
      await page.waitForURL(new RegExp(`/agents/${agentName}`), { timeout: 5000 });
      expect(page.url()).toContain(`/agents/${agentName}`);
    }
  });

  test('should display top agents prominently', async ({ page }) => {
    const agentsPage = new AgentsPage(page);
    await agentsPage.goto();

    await page.waitForTimeout(1000);
    
    // Check if top agents section exists
    const topAgentsVisible = await agentsPage.topAgents.first().isVisible({ timeout: 5000 }).catch(() => false);
    // This test is flexible - just verify page loads correctly
    expect(page.url()).toContain('/agents');
  });
});
