import { Page, Locator } from '@playwright/test';

export class AgentsPage {
  readonly page: Page;
  readonly leaderboard: Locator;
  readonly topAgents: Locator;
  readonly timeframeFilter: Locator;
  readonly agentLinks: Locator;

  constructor(page: Page) {
    this.page = page;
    this.leaderboard = page.locator('[data-testid="leaderboard"]');
    this.topAgents = page.locator('[data-testid="top-agent"], .podium');
    this.timeframeFilter = page.locator('select, [data-testid="timeframe-filter"]');
    this.agentLinks = page.locator('a[href*="/agents/"]');
  }

  async goto() {
    await this.page.goto('/agents');
  }

  async selectTimeframe(timeframe: 'all-time' | 'month' | 'week') {
    if (await this.timeframeFilter.isVisible()) {
      await this.timeframeFilter.selectOption(timeframe);
    }
  }

  async clickAgent(index: number = 0) {
    await this.agentLinks.nth(index).click();
  }

  async expectTopAgentsVisible(count: number = 3) {
    await this.topAgents.first().waitFor({ state: 'visible' });
    const actualCount = await this.topAgents.count();
    if (actualCount < count) {
      throw new Error(`Expected at least ${count} top agents, found ${actualCount}`);
    }
  }

  async getLeaderboardAgents(): Promise<Array<{ name: string; karma: number }>> {
    await this.page.waitForLoadState('networkidle');
    // Get agents from the page - look for agent cards or list items
    const agentCards = this.page.locator('[data-testid="agent-card"], .agent-card, a[href*="/agents/"]');
    const count = await agentCards.count();
    const agents: Array<{ name: string; karma: number }> = [];
    
    for (let i = 0; i < count; i++) {
      const card = agentCards.nth(i);
      const name = await card.textContent().catch(() => '');
      // Try to extract karma from text
      const karmaText = await card.locator('text=/\\d+.*karma/i').textContent().catch(() => '0');
      const karmaMatch = karmaText.match(/(\d+)/);
      const karma = karmaMatch ? parseInt(karmaMatch[1], 10) : 0;
      
      if (name) {
        agents.push({ name: name.trim(), karma });
      }
    }
    
    return agents;
  }
}
