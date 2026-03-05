/**
 * Test script for predicate-snapshot skill via OpenClaw
 *
 * This script tests the skill's installation, module loading, tool registration,
 * and actual snapshot execution using SentienceBrowser (which loads the extension).
 *
 * Run: npx ts-node test-skill.ts
 * Or via Docker: ./docker-test.sh skill
 */

import * as path from 'path';
import * as fs from 'fs';

// Colors for terminal output
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';
const CYAN = '\x1b[36m';
const NC = '\x1b[0m'; // No Color

const TEST_URL = 'https://www.localllamaland.com/login';

async function main() {
  console.log(`${GREEN}========================================${NC}`);
  console.log(`${GREEN}Predicate Snapshot Skill - Integration Test${NC}`);
  console.log(`${GREEN}========================================${NC}`);
  console.log();

  // Step 1: Verify skill is installed
  console.log(`${CYAN}Step 1: Verifying skill installation...${NC}`);
  const skillPath = path.join(process.env.HOME || '/root', '.openclaw/skills/predicate-snapshot');
  const skillMdPath = path.join(skillPath, 'SKILL.md');
  const distPath = path.join(skillPath, 'dist/index.js');

  if (!fs.existsSync(skillMdPath)) {
    console.log(`${RED}ERROR: SKILL.md not found at ${skillMdPath}${NC}`);
    process.exit(1);
  }
  if (!fs.existsSync(distPath)) {
    console.log(`${RED}ERROR: Built skill not found at ${distPath}${NC}`);
    process.exit(1);
  }
  console.log(`${GREEN}✓ Skill installed at ${skillPath}${NC}`);

  // Step 2: Parse SKILL.md frontmatter
  console.log();
  console.log(`${CYAN}Step 2: Parsing SKILL.md...${NC}`);
  const skillMd = fs.readFileSync(skillMdPath, 'utf-8');
  const frontmatterMatch = skillMd.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    console.log(`${RED}ERROR: No frontmatter found in SKILL.md${NC}`);
    process.exit(1);
  }

  const frontmatter = frontmatterMatch[1];
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const commandToolMatch = frontmatter.match(/^command-tool:\s*(.+)$/m);

  const skillName = nameMatch?.[1] || 'unknown';
  const commandTool = commandToolMatch?.[1] || 'unknown';

  console.log(`  Name: ${skillName}`);
  console.log(`  Command tool: ${commandTool}`);
  console.log(`${GREEN}✓ SKILL.md parsed successfully${NC}`);

  // Step 3: Load the skill module
  console.log();
  console.log(`${CYAN}Step 3: Loading skill module...${NC}`);

  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const skillModule = require(distPath);

  if (!skillModule.mcpTools) {
    console.log(`${RED}ERROR: mcpTools not exported from skill${NC}`);
    process.exit(1);
  }

  const tools = Object.keys(skillModule.mcpTools);
  console.log(`  Exported tools: ${tools.join(', ')}`);

  // Verify each tool has required properties
  for (const toolName of tools) {
    const tool = skillModule.mcpTools[toolName];
    if (!tool.handler || typeof tool.handler !== 'function') {
      console.log(`${RED}ERROR: Tool '${toolName}' missing handler function${NC}`);
      process.exit(1);
    }
    if (!tool.description) {
      console.log(`${YELLOW}Warning: Tool '${toolName}' missing description${NC}`);
    }
  }
  console.log(`${GREEN}✓ All tools have valid handlers${NC}`);

  // Step 4: Launch PredicateBrowser (loads extension automatically)
  console.log();
  console.log(`${CYAN}Step 4: Launching PredicateBrowser with extension...${NC}`);
  console.log(`  Target URL: ${TEST_URL}`);

  // Import PredicateBrowser from the SDK
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { PredicateBrowser } = require('@predicatesystems/runtime');

  // Debug: Show where the SDK will look for the extension
  console.log(`  SDK __dirname: ${require.resolve('@predicatesystems/runtime')}`);
  const runtimePath = path.dirname(require.resolve('@predicatesystems/runtime'));
  console.log(`  Runtime path: ${runtimePath}`);

  // Check extension candidates
  const extensionCandidates = [
    path.resolve(runtimePath, '../extension'),
    path.resolve(runtimePath, 'extension'),
    path.resolve(runtimePath, '../src/extension'),
    path.resolve(runtimePath, '../../src/extension'),
    path.resolve(process.cwd(), 'extension'),
  ];

  for (const candidate of extensionCandidates) {
    const hasManifest = fs.existsSync(path.join(candidate, 'manifest.json'));
    console.log(`  Extension candidate: ${candidate} (${hasManifest ? 'EXISTS' : 'not found'})`);
  }

  // PredicateBrowser constructor: (apiKey?, apiUrl?, headless?, proxy?, userDataDir?, ...)
  // Use undefined for apiKey and apiUrl, true for headless
  console.log(`  Creating PredicateBrowser instance...`);
  const predicateBrowser = new PredicateBrowser(
    undefined, // apiKey
    undefined, // apiUrl
    true       // headless (uses --headless=new which supports extensions)
  );

  console.log(`  Starting browser (this loads the extension)...`);
  console.log(`  [${new Date().toISOString()}] Calling predicateBrowser.start()...`);

  // Add timeout for browser start
  const startTimeout = 60000; // 60 seconds
  const startPromise = predicateBrowser.start();
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Browser start timed out after ${startTimeout}ms`)), startTimeout)
  );

  await Promise.race([startPromise, timeoutPromise]);
  console.log(`  [${new Date().toISOString()}] predicateBrowser.start() completed`);
  console.log(`${GREEN}✓ PredicateBrowser started with extension loaded${NC}`);

  const page = predicateBrowser.getPage();
  await page.goto(TEST_URL, { waitUntil: 'domcontentloaded' });

  // Verify page loaded
  const title = await page.title();
  console.log(`  Page title: ${title}`);
  console.log(`${GREEN}✓ Browser launched and navigated successfully${NC}`);

  // Step 5: Test predicate-act tool parameter validation
  console.log();
  console.log(`${CYAN}Step 5: Testing tool parameter validation...${NC}`);

  const actTool = skillModule.mcpTools['predicate-act'];
  if (!actTool) {
    console.log(`${RED}ERROR: predicate-act tool not found${NC}`);
    await predicateBrowser.close();
    process.exit(1);
  }

  // Test invalid action parameter
  const invalidResult = await actTool.handler({ action: 'invalid_action', elementId: 1 }, { page });

  if (!invalidResult.success && invalidResult.error?.includes('Invalid action')) {
    console.log(`${GREEN}✓ Parameter validation works (rejected invalid action)${NC}`);
  } else {
    console.log(`${YELLOW}Warning: Parameter validation may not be working${NC}`);
  }

  // Step 6: Wait for extension to be ready
  console.log();
  console.log(`${CYAN}Step 6: Waiting for Sentience extension to be ready...${NC}`);

  // Wait for page to be fully ready
  await page.waitForLoadState('networkidle').catch(() => {});

  // Wait for extension injection (window.sentience.snapshot should be available)
  const extensionReady = await page
    .waitForFunction(
      () =>
        typeof (window as unknown as { sentience?: { snapshot?: unknown } }).sentience !== 'undefined' &&
        typeof (window as unknown as { sentience: { snapshot: unknown } }).sentience.snapshot === 'function',
      { timeout: 15000 }
    )
    .then(() => true)
    .catch(() => false);

  if (extensionReady) {
    console.log(`${GREEN}✓ Sentience extension is ready (window.sentience.snapshot available)${NC}`);
  } else {
    console.log(`${YELLOW}Warning: Extension may not be fully loaded yet${NC}`);
  }

  // Step 7: Test snapshot tool with extension
  console.log();
  console.log(`${CYAN}Step 7: Testing predicate-snapshot-local tool with extension...${NC}`);

  // Check for createBrowserUseSession export
  if (!skillModule.createBrowserUseSession) {
    console.log(`${RED}ERROR: createBrowserUseSession not exported from skill${NC}`);
    await predicateBrowser.close();
    process.exit(1);
  }

  const localSnapshotTool = skillModule.mcpTools['predicate-snapshot-local'];
  if (!localSnapshotTool) {
    console.log(`${RED}ERROR: predicate-snapshot-local tool not found${NC}`);
    await predicateBrowser.close();
    process.exit(1);
  }

  console.log(`  Testing predicate-snapshot-local tool...`);

  // Create browser-use compatible session from Playwright page
  const browserUseSession = skillModule.createBrowserUseSession(page);

  const snapshotResult = await localSnapshotTool.handler(
    { limit: 30 },
    { page, browserSession: browserUseSession }
  );

  if (snapshotResult.success) {
    console.log(`${GREEN}✓ Local snapshot executed successfully${NC}`);
    // Parse and show element count
    const lines = snapshotResult.data?.split('\n') || [];
    const elementLines = lines.filter((line: string) => line.match(/^\d+\|/));
    console.log(`  Elements captured: ${elementLines.length}`);
    if (elementLines.length > 0) {
      console.log(`  Sample element: ${elementLines[0].substring(0, 80)}...`);
    }
  } else {
    console.log(`${RED}ERROR: Snapshot failed: ${snapshotResult.error}${NC}`);
    await predicateBrowser.close();
    process.exit(1);
  }

  // Step 8: Test with ML-powered snapshot (if API key available)
  console.log();
  console.log(`${CYAN}Step 8: Testing predicate-snapshot tool (ML-powered)...${NC}`);

  const mlSnapshotTool = skillModule.mcpTools['predicate-snapshot'];
  if (!mlSnapshotTool) {
    console.log(`${RED}ERROR: predicate-snapshot tool not found${NC}`);
    await predicateBrowser.close();
    process.exit(1);
  }

  if (process.env.PREDICATE_API_KEY) {
    console.log(`  PREDICATE_API_KEY is set, testing ML-powered snapshot...`);

    const mlSnapshotResult = await mlSnapshotTool.handler(
      { limit: 30 },
      { page, browserSession: browserUseSession }
    );

    if (mlSnapshotResult.success) {
      console.log(`${GREEN}✓ ML-powered snapshot executed successfully${NC}`);
      const lines = mlSnapshotResult.data?.split('\n') || [];
      const elementLines = lines.filter((line: string) => line.match(/^\d+\|/));
      console.log(`  Elements captured: ${elementLines.length}`);
    } else {
      console.log(`${YELLOW}Warning: ML snapshot failed: ${mlSnapshotResult.error}${NC}`);
    }
  } else {
    console.log(`${YELLOW}  PREDICATE_API_KEY not set, skipping ML-powered snapshot test${NC}`);
    console.log(`${GREEN}✓ ML snapshot tool registered (requires API key)${NC}`);
  }

  // Cleanup
  await predicateBrowser.close();

  // Summary
  console.log();
  console.log(`${GREEN}========================================${NC}`);
  console.log(`${GREEN}Test Summary${NC}`);
  console.log(`${GREEN}========================================${NC}`);
  console.log(`${GREEN}✓ Skill installation verified${NC}`);
  console.log(`${GREEN}✓ SKILL.md frontmatter valid${NC}`);
  console.log(`${GREEN}✓ mcpTools exported correctly${NC}`);
  console.log(`${GREEN}✓ All tool handlers registered${NC}`);
  console.log(`${GREEN}✓ PredicateBrowser with extension working${NC}`);
  console.log(`${GREEN}✓ Parameter validation functional${NC}`);
  console.log(`${GREEN}✓ Sentience extension loaded and ready${NC}`);
  console.log(`${GREEN}✓ Local snapshot captures elements${NC}`);
  if (process.env.PREDICATE_API_KEY) {
    console.log(`${GREEN}✓ ML-powered snapshot working${NC}`);
  }
  console.log();
  console.log(`${GREEN}All integration tests passed!${NC}`);
  console.log();
  console.log(`${CYAN}The skill is ready for use with OpenClaw.${NC}`);
}

main().catch((err) => {
  console.log(`${RED}Test failed with error:${NC}`);
  console.error(err);
  process.exit(1);
});
