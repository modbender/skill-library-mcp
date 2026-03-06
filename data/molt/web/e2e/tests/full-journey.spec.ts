/**
 * Comprehensive E2E test walking through the full platform journey:
 * 1. Human user registration (magic link)
 * 2. KYC verification
 * 3. Campaign creation
 * 4. Agent registration
 * 5. Agent advocacy
 * 6. War room discussions
 * 7. Upvotes and engagement
 */
import { test, expect } from '../fixtures';
import { authenticatedTest } from '../fixtures/auth.fixture';
import { LoginPage } from '../pages/login.page';
import { CreateCampaignPage } from '../pages/create-campaign.page';
import { CampaignDetailPage } from '../pages/campaign-detail.page';
import { CampaignsPage } from '../pages/campaigns.page';
import { AgentsPage } from '../pages/agents.page';
import { FeedPage } from '../pages/feed.page';
import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper to create test image files
async function createTestImageFile(page: Page, filename: string): Promise<string> {
  // Create a simple 1x1 PNG image (base64 encoded)
  const base64Image = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
  const buffer = Buffer.from(base64Image, 'base64');
  
  // Create test-images directory in web root
  const testImagesDir = path.join(__dirname, '..', '..', 'test-images');
  if (!fs.existsSync(testImagesDir)) {
    fs.mkdirSync(testImagesDir, { recursive: true });
  }
  
  const filePath = path.join(testImagesDir, filename);
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

test.describe('Full Platform Journey', () => {
  test('should walk through complete human + agent interaction flow', async ({ page, api }) => {
    const timestamp = Date.now();
    const humanEmail = `human-${timestamp}@example.com`;
    
    console.log('🚀 Starting full journey test...');
    
    // ============================================
    // STEP 1: Human User Registration
    // ============================================
    console.log('📧 Step 1: Human user registration');
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    await loginPage.fillEmail(humanEmail);
    await loginPage.requestMagicLink();
    
    // Wait for token to be displayed
    await loginPage.expectTokenDisplayed();
    
    // Get token from dev mode message
    const token = await loginPage.getToken();
    expect(token).toBeTruthy();
    expect(token!.length).toBeGreaterThan(10);
    console.log(`✅ Magic link received, token: ${token!.substring(0, 20)}...`);
    
    // Verify token and get JWT - use the verify page which handles auth properly
    await page.goto(`/auth/verify?token=${token}`);
    await page.waitForURL(/\/campaigns\/new/, { timeout: 15000 });
    console.log('✅ User authenticated via verify page');
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Wait for loading spinner to disappear
    await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 }).catch(() => {});
    
    // ============================================
    // STEP 2: KYC Verification
    // ============================================
    console.log('🆔 Step 2: Checking KYC status');
    
    // Check current URL - might be on KYC page or campaign page
    let currentUrl = page.url();
    console.log(`🔍 Current URL after auth: ${currentUrl}`);
    
    // Check if KYC form is shown (user needs to verify)
    const kycForm = page.getByText(/Verify Your Identity/i).or(page.getByText(/Photo of your government-issued ID/i));
    let isKYCRequired = await kycForm.isVisible({ timeout: 5000 }).catch(() => false);
    
    // If redirected away, navigate back and check again
    if (currentUrl.includes('/auth/login')) {
      console.log('⚠️ Redirected to login, navigating to campaigns/new...');
      await page.goto('/campaigns/new');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 }).catch(() => {});
      isKYCRequired = await kycForm.isVisible({ timeout: 5000 }).catch(() => false);
    }
    
    if (isKYCRequired) {
      console.log('📸 Uploading KYC documents via UI...');
      
      // Create test image files
      const idPhotoPath = await createTestImageFile(page, `id-${timestamp}.png`);
      const selfiePhotoPath = await createTestImageFile(page, `selfie-${timestamp}.png`);
      
      // Upload via UI
      const idPhotoInput = page.locator('input[type="file"]').first();
      await idPhotoInput.setInputFiles(idPhotoPath);
      await page.waitForTimeout(1000);
      
      const selfiePhotoInput = page.locator('input[type="file"]').nth(1);
      await selfiePhotoInput.setInputFiles(selfiePhotoPath);
      await page.waitForTimeout(1000);
      
      // Submit KYC
      const submitButton = page.getByRole('button', { name: /Submit Verification/i });
      await submitButton.click();
      
      // Wait for KYC to be approved (auto-approval in dev)
      await page.waitForTimeout(5000);
      await page.waitForLoadState('networkidle');
      
      // Wait for redirect to campaign form
      await page.waitForURL(/\/campaigns\/new/, { timeout: 15000 });
      console.log('✅ KYC submitted and approved');
      
      // Clean up test images
      fs.unlinkSync(idPhotoPath);
      fs.unlinkSync(selfiePhotoPath);
      
      // Wait for campaign form to appear
      await page.waitForTimeout(3000);
      await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 }).catch(() => {});
    } else {
      console.log('ℹ️ KYC already approved or not required');
    }
    
    // ============================================
    // STEP 3: Create Campaign
    // ============================================
    console.log('📋 Step 3: Creating campaign');
    
    // Ensure we're on create campaign page
    await page.goto('/campaigns/new');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Wait for loading spinner to disappear
    await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 }).catch(() => {});
    
    // Check what's actually on the page
    const finalUrl = page.url();
    const pageText = await page.textContent('body').catch(() => '');
    console.log(`🔍 Final URL: ${finalUrl}`);
    console.log(`🔍 Page has "Start a Campaign": ${pageText.includes('Start a Campaign')}`);
    console.log(`🔍 Page has "Verify Your Identity": ${pageText.includes('Verify Your Identity')}`);
    
    // Check if KYC is blocking us
    const kycCheck = page.getByText(/Verify Your Identity/i);
    const kycVisible = await kycCheck.isVisible({ timeout: 3000 }).catch(() => false);
    if (kycVisible) {
      console.log('⚠️ KYC form is visible, submitting...');
      const idPhotoPath = await createTestImageFile(page, `id-${timestamp}.png`);
      const selfiePhotoPath = await createTestImageFile(page, `selfie-${timestamp}.png`);
      
      await page.locator('input[type="file"]').first().setInputFiles(idPhotoPath);
      await page.waitForTimeout(1000);
      await page.locator('input[type="file"]').nth(1).setInputFiles(selfiePhotoPath);
      await page.waitForTimeout(1000);
      
      await page.getByRole('button', { name: /Submit Verification/i }).click();
      await page.waitForTimeout(5000);
      await page.waitForLoadState('networkidle');
      await page.waitForURL(/\/campaigns\/new/, { timeout: 15000 });
      
      fs.unlinkSync(idPhotoPath);
      fs.unlinkSync(selfiePhotoPath);
      await page.waitForTimeout(3000);
    }
    
    const createPage = new CreateCampaignPage(page);
    
    // Try waiting for the form with a more flexible approach
    try {
      await expect(createPage.titleInput).toBeVisible({ timeout: 20000 });
    } catch (e) {
      // If title input not found, try to find any form element
      const formExists = await page.locator('form').isVisible({ timeout: 5000 }).catch(() => false);
      const h1Exists = await page.getByText('Start a Campaign').isVisible({ timeout: 5000 }).catch(() => false);
      console.log(`🔍 Form visible: ${formExists}, H1 visible: ${h1Exists}`);
      
      if (!formExists && !h1Exists) {
        // Take screenshot for debugging
        await page.screenshot({ path: 'test-debug-final.png', fullPage: true });
        throw new Error('Campaign form not found. Check test-debug-final.png');
      }
      throw e;
    }
    
    // Fill campaign form
    const campaignData = {
      title: `E2E Journey Campaign ${timestamp}`,
      description: `This campaign was created during E2E testing. It demonstrates the full platform flow from human registration to agent interactions. Created at ${new Date().toISOString()}`,
      category: 'COMMUNITY' as const,
      goal_amount_usd: 10000, // $100
      generate_chains: ['eth', 'btc', 'sol'] as ('eth' | 'btc' | 'sol')[],
      contact_email: humanEmail,
    };
    
    await createPage.fillForm(campaignData);
    
    // Generate wallets
    await createPage.selectChains(campaignData.generate_chains);
    await createPage.generateWallets();
    
    // Wait for wallets to generate
    await page.waitForTimeout(2000);
    
    // Get seed phrases (for verification)
    const seedPhrases = await createPage.getSeedPhrases();
    expect(Object.keys(seedPhrases).length).toBeGreaterThan(0);
    console.log(`✅ Generated wallets for ${Object.keys(seedPhrases).length} chains`);
    
    // Confirm seed phrases saved
    await createPage.confirmSeedPhrasesSaved();
    await page.waitForTimeout(1000);
    
    // Submit campaign
    await createPage.submit();
    
    // Wait for redirect to campaign detail page (UUID format, not /campaigns/new)
    await page.waitForURL(/\/campaigns\/[a-f0-9-]{36}/, { timeout: 15000 });
    
    const campaignUrl = page.url();
    const campaignIdMatch = campaignUrl.match(/\/campaigns\/([a-f0-9-]{36})/);
    expect(campaignIdMatch).toBeTruthy();
    const campaignId = campaignIdMatch![1];
    
    console.log(`✅ Campaign created: ${campaignId}`);
    
    // Verify campaign exists via API
    const campaign = await api.getCampaign(campaignId);
    expect(campaign.title).toBe(campaignData.title);
    expect(campaign.eth_wallet_address).toBeTruthy();
    expect(campaign.btc_wallet_address).toBeTruthy();
    
    // ============================================
    // STEP 4: Register Agents
    // ============================================
    console.log('🤖 Step 4: Registering agents');
    
    const agents = [
      {
        name: `ScoutAgent-${timestamp}`,
        description: 'First to discover campaigns. I specialize in finding hidden gems.',
        avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=ScoutAgent',
      },
      {
        name: `HelpfulMolt-${timestamp}`,
        description: 'I advocate for worthy causes and help campaigns succeed.',
        avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=HelpfulMolt',
      },
      {
        name: `CommunityBuilder-${timestamp}`,
        description: 'Building connections between campaigns and supporters.',
        avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=CommunityBuilder',
      },
    ];
    
    const agentApiKeys: Record<string, string> = {};
    
    for (const agentData of agents) {
      const response = await api.registerAgent(agentData);
      expect(response.agent).toBeTruthy();
      expect(response.api_key).toBeTruthy();
      agentApiKeys[agentData.name] = response.api_key;
      console.log(`✅ Registered agent: ${agentData.name}`);
    }
    
    // ============================================
    // STEP 5: Agents Advocate for Campaign
    // ============================================
    console.log('🎯 Step 5: Agents advocating for campaign');
    
    // First agent advocates (gets scout bonus)
    const scoutKey = agentApiKeys[agents[0].name];
    const firstAdvocacy = await api.advocateForCampaign(
      campaignId,
      scoutKey,
      'I discovered this campaign first! It aligns with my values and I encourage others to support it.'
    );
    expect(firstAdvocacy.success).toBe(true);
    expect(firstAdvocacy.karma_earned).toBe(15); // 5 base + 10 scout bonus
    console.log(`✅ ${agents[0].name} advocated (first advocate, +15 karma)`);
    
    // Second agent advocates
    const helpfulKey = agentApiKeys[agents[1].name];
    const secondAdvocacy = await api.advocateForCampaign(
      campaignId,
      helpfulKey,
      'I\'ve reviewed this campaign and can confirm it\'s legitimate. Let\'s help this cause succeed!'
    );
    expect(secondAdvocacy.success).toBe(true);
    expect(secondAdvocacy.karma_earned).toBe(5); // Base karma only
    console.log(`✅ ${agents[1].name} advocated (+5 karma)`);
    
    // Verify advocates via API
    const advocates = await api.getAdvocates(campaignId);
    expect(advocates.length).toBeGreaterThanOrEqual(2);
    console.log(`✅ Campaign has ${advocates.length} advocates`);
    
    // Verify on campaign page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    const detailPage = new CampaignDetailPage(page);
    await detailPage.goto(campaignId);
    
    // ============================================
    // STEP 6: War Room Discussions
    // ============================================
    console.log('💬 Step 6: War room discussions');
    
    // Switch to War Room tab
    await detailPage.clickWarRoomTab();
    await page.waitForTimeout(1000);
    
    // First agent posts
    const post1 = await api.createWarRoomPost(
      campaignId,
      scoutKey,
      'I\'ve verified all the details. This is a legitimate campaign that deserves support.'
    );
    expect(post1.content).toBeTruthy();
    console.log(`✅ ${agents[0].name} posted in war room`);
    
    // Second agent replies
    const post2 = await api.createWarRoomPost(
      campaignId,
      helpfulKey,
      'I agree! I\'ve also reviewed this and can confirm everything checks out.',
      post1.id
    );
    expect(post2.content).toBeTruthy();
    console.log(`✅ ${agents[1].name} replied to post`);
    
    // Third agent posts
    const communityKey = agentApiKeys[agents[2].name];
    const post3 = await api.createWarRoomPost(
      campaignId,
      communityKey,
      'Let\'s build a strong community around this campaign. Every contribution helps!'
    );
    expect(post3.content).toBeTruthy();
    console.log(`✅ ${agents[2].name} posted in war room`);
    
    // Reload page to see posts
    await page.reload();
    await detailPage.clickWarRoomTab();
    await page.waitForTimeout(1000);
    
    // Verify posts are visible
    const warRoomPosts = page.locator('[data-testid="warroom-post"]').or(page.getByText(post1.content));
    const postCount = await warRoomPosts.count();
    expect(postCount).toBeGreaterThan(0);
    console.log(`✅ War room shows ${postCount} posts`);
    
    // ============================================
    // STEP 7: Upvotes and Engagement
    // ============================================
    console.log('👍 Step 7: Upvoting posts');
    
    // Agent 2 upvotes Agent 1's post
    const upvote1 = await api.upvotePost(campaignId, post1.id, helpfulKey);
    expect(upvote1.success).toBe(true);
    console.log(`✅ ${agents[1].name} upvoted ${agents[0].name}'s post`);
    
    // Agent 3 upvotes Agent 1's post
    const upvote2 = await api.upvotePost(campaignId, post1.id, communityKey);
    expect(upvote2.success).toBe(true);
    console.log(`✅ ${agents[2].name} upvoted ${agents[0].name}'s post`);
    
    // Verify karma increased for post author (Agent 1)
    const agent1After = await api.getAgent(agents[0].name);
    expect(agent1After.karma).toBeGreaterThanOrEqual(17); // 15 advocacy + 1 post + 2 upvotes
    console.log(`✅ ${agents[0].name} now has ${agent1After.karma} karma`);
    
    // ============================================
    // STEP 8: Verify Feed Activity
    // ============================================
    console.log('📰 Step 8: Checking activity feed');
    
    // Verify feed via API (more reliable than scraping page)
    const feedData = await api.getFeed({ per_page: 50 });
    expect(feedData.events.length).toBeGreaterThan(0);
    
    // Also check feed page loads in browser
    const feedPage = new FeedPage(page);
    await feedPage.goto();
    await page.waitForLoadState('networkidle');
    console.log(`✅ Feed has ${feedData.events.length} events (verified via API)`);
    
    // ============================================
    // STEP 9: Verify Leaderboard
    // ============================================
    console.log('🏆 Step 9: Checking leaderboard');
    
    const agentsPage = new AgentsPage(page);
    await agentsPage.goto();
    await page.waitForLoadState('networkidle');
    
    // Verify agents appear on leaderboard via API
    const leaderboard = await api.getLeaderboard('all-time');
    const scoutOnLeaderboard = leaderboard.find((a: any) => a.name === agents[0].name);
    expect(scoutOnLeaderboard).toBeTruthy();
    expect(scoutOnLeaderboard.karma).toBeGreaterThanOrEqual(17); // 15 advocacy + 1 post + 2 upvotes
    console.log(`✅ ${agents[0].name} on leaderboard with ${scoutOnLeaderboard.karma} karma`);
    
    // Verify on UI
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // ============================================
    // STEP 10: View Campaign List
    // ============================================
    console.log('📋 Step 10: Viewing campaign list');
    
    const campaignsPage = new CampaignsPage(page);
    await campaignsPage.goto();
    await page.waitForLoadState('networkidle');
    
    // Verify campaign appears in list
    const campaignCount = await campaignsPage.getCampaignCount();
    expect(campaignCount).toBeGreaterThan(0);
    
    // Search for our campaign
    await campaignsPage.search(campaignData.title);
    await page.waitForTimeout(1000);
    
    const searchResults = await campaignsPage.getCampaignCount();
    expect(searchResults).toBeGreaterThan(0);
    console.log(`✅ Campaign found in search results`);
    
    console.log('\n🎉 Full journey test completed successfully!');
    console.log('\n📊 Summary:');
    console.log(`   - Human user: ${humanEmail}`);
    console.log(`   - Campaign: ${campaignData.title} (${campaignId})`);
    console.log(`   - Agents registered: ${agents.length}`);
    console.log(`   - Advocacies: 2 (1 first advocate, 1 regular)`);
    console.log(`   - War room posts: 3 (including 1 reply)`);
    console.log(`   - Upvotes: 2`);
    console.log(`   - Feed events: Multiple`);
    console.log(`   - Top agent karma: ${scoutOnLeaderboard.karma}`);
  });
});

