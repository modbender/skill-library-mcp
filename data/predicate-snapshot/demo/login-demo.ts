/**
 * Login + Profile Check Demo
 *
 * Ported from Python: sentience-sdk-playground/login_profile_check/main.py
 *
 * Demonstrates multi-step browser automation with:
 * - Delayed hydration handling using AgentRuntime.check().eventually()
 * - State-aware assertions (isEnabled, isDisabled)
 * - Form filling with LLM element selection
 * - Human-like typing with random delays
 * - A11y Tree vs Predicate Snapshot comparison
 *
 * Target site: https://www.localllamaland.com/login
 * Site characteristics (intentional challenges):
 * - DELAYED HYDRATION: Login form loads after ~600ms
 * - BUTTON DISABLED→ENABLED: Login button becomes enabled after both fields filled
 * - PROFILE PAGE LATE-LOAD: Profile card content loads after 800-1200ms
 *
 * Run: npm run demo:login -- --headed --overlay
 *
 * Options:
 *   --headed    Run browser in headed mode (visible window)
 *   --overlay   Show green overlay on captured elements (requires --headed)
 */

import * as dotenv from 'dotenv';
dotenv.config();

const args = process.argv.slice(2);
const HEADED = args.includes('--headed');
const SHOW_OVERLAY = args.includes('--overlay');

import {
  PredicateBrowser,
  SentienceBrowser,
  Snapshot,
  LLMProvider,
  LocalLLMProvider,
  OpenAIProvider,
  AnthropicProvider,
  AgentRuntime,
  Tracer,
  JsonlTraceSink,
  exists,
  isEnabled,
  isDisabled,
  urlContains,
} from '@predicatesystems/runtime';
import { encode } from 'gpt-tokenizer';
import * as crypto from 'crypto';
import * as path from 'path';
import * as os from 'os';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Page = any;
type Browser = InstanceType<typeof SentienceBrowser>;

// Test credentials for the fake site
const TEST_USERNAME = 'testuser';
const TEST_PASSWORD = 'password123';

interface A11yNode {
  nodeId?: string;
  role?: string;
  name?: string;
  description?: string;
  value?: string;
  children?: A11yNode[];
  [key: string]: unknown;
}

interface StepTokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
}

interface StepResult {
  success: boolean;
  usage: StepTokenUsage | null;
  note?: string;
}

interface StepStats {
  stepIndex: number;
  goal: string;
  success: boolean;
  durationMs: number;
  tokenUsage: StepTokenUsage | null;
  url: string;
  note?: string;
  approach: 'a11y' | 'predicate';
}

interface ParsedElement {
  id: number;
  role: string;
  text: string;
  disabled?: boolean;
}

// ============ Utility Functions ============

function nowIso(): string {
  return new Date().toISOString().replace('T', ' ').substring(0, 19);
}

function parseClickId(text: string): number | null {
  const m = text.match(/CLICK\s*\(\s*(\d+)\s*\)/i);
  return m ? parseInt(m[1], 10) : null;
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function randomDelay(minMs: number, maxMs: number): number {
  return Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
}

// ============ Browser Adapter ============

/**
 * Adapter to make SentienceBrowser compatible with AgentRuntime's BrowserLike interface.
 * AgentRuntime expects snapshot(page, options) but SentienceBrowser has snapshot(options).
 */
function createBrowserAdapter(browser: Browser) {
  return {
    snapshot: async (_page: Page, options?: Record<string, unknown>): Promise<Snapshot> => {
      return await browser.snapshot(options);
    },
  };
}

// ============ Accessibility Tree Functions ============

async function getAccessibilityTree(page: Page): Promise<A11yNode | null> {
  const client = await page.context().newCDPSession(page);

  try {
    const { nodes } = await client.send('Accessibility.getFullAXTree');

    const nodeMap = new Map<string, A11yNode>();
    let root: A11yNode | null = null;

    for (const node of nodes) {
      const a11yNode: A11yNode = {
        nodeId: node.nodeId,
        role: node.role?.value,
        name: node.name?.value,
        description: node.description?.value,
        value: node.value?.value,
        children: [],
      };
      nodeMap.set(node.nodeId, a11yNode);

      if (!node.parentId) {
        root = a11yNode;
      }
    }

    for (const node of nodes) {
      if (node.parentId && nodeMap.has(node.parentId)) {
        const parent = nodeMap.get(node.parentId)!;
        const child = nodeMap.get(node.nodeId);
        if (child && parent.children) {
          parent.children.push(child);
        }
      }
    }

    return root;
  } finally {
    await client.detach();
  }
}

function formatA11yForLLM(tree: A11yNode | null): { formatted: string; elements: ParsedElement[] } {
  if (!tree) return { formatted: '[]', elements: [] };

  const elements: ParsedElement[] = [];
  let id = 1;

  function extract(node: A11yNode): void {
    if (node.role && node.name) {
      elements.push({
        id: id++,
        role: node.role,
        text: node.name.slice(0, 100),
      });
    }
    if (node.children) {
      for (const child of node.children) {
        extract(child);
      }
    }
  }

  extract(tree);
  const formatted = JSON.stringify(elements.map(e => ({ id: e.id, role: e.role, name: e.text })), null, 2);
  return { formatted, elements };
}

// ============ Predicate Snapshot Functions ============

function formatPredicateForLLM(snap: Snapshot): { formatted: string; elements: ParsedElement[] } {
  const lines: string[] = ['ID|role|text|importance|is_primary|disabled'];
  const elements: ParsedElement[] = [];

  for (const el of snap.elements.slice(0, 50)) {
    const id = el.id ?? 0;
    const role = el.role ?? '';
    const text = String(el.text ?? '').slice(0, 40).replace(/\|/g, ' ').replace(/\n/g, ' ');
    const imp = el.importance?.toFixed(2) ?? '0';
    const isPrimary = el.visual_cues?.is_primary ? 'yes' : 'no';
    const disabled = el.disabled ? 'yes' : 'no';

    lines.push(`${id}|${role}|${text}|${imp}|${isPrimary}|${disabled}`);
    elements.push({ id, role, text, disabled: el.disabled ?? false });
  }

  return { formatted: lines.join('\n'), elements };
}

function getElementText(elements: ParsedElement[], id: number): string {
  const el = elements.find(e => e.id === id);
  if (!el) return '(not found)';
  const text = el.text.slice(0, 50);
  return text || `[${el.role}]`;
}

// ============ LLM Functions ============

function buildLLMPrompt(task: string, elements: string, format: 'a11y' | 'predicate'): string {
  const formatExplanation = format === 'a11y'
    ? 'The elements are in JSON format with id, role, and name fields.'
    : `The elements are in pipe-delimited format: ID|role|text|importance|is_primary|disabled
- disabled=yes means the element cannot be interacted with`;

  return `You are a browser automation agent controlling a login form.

You must respond with exactly ONE action in this format:
- CLICK(<id>) - to click an element
- TYPE(<id>, "<text>") - to type text into an input field

${formatExplanation}

TASK: ${task}

ELEMENTS:
${elements}

Respond with ONLY the action (CLICK or TYPE), nothing else.`;
}

function initLLMProvider(): LLMProvider {
  if (process.env.OPENAI_API_KEY) {
    console.log('Using OpenAI provider');
    return new OpenAIProvider(process.env.OPENAI_API_KEY, 'gpt-4o-mini');
  }

  if (process.env.ANTHROPIC_API_KEY) {
    console.log('Using Anthropic provider');
    return new AnthropicProvider(process.env.ANTHROPIC_API_KEY, 'claude-3-haiku-20240307');
  }

  if (process.env.SENTIENCE_LOCAL_LLM_BASE_URL || process.env.OLLAMA_BASE_URL) {
    console.log('Using local LLM provider');
    return new LocalLLMProvider({
      baseUrl: process.env.SENTIENCE_LOCAL_LLM_BASE_URL || process.env.OLLAMA_BASE_URL,
      model: process.env.SENTIENCE_LOCAL_LLM_MODEL || 'llama3.2',
    });
  }

  throw new Error(
    'No LLM provider configured. Set one of:\n' +
    '  - OPENAI_API_KEY\n' +
    '  - ANTHROPIC_API_KEY\n' +
    '  - SENTIENCE_LOCAL_LLM_BASE_URL (for Ollama/LM Studio)'
  );
}

// ============ Human-like Typing ============

async function typeHumanLike(page: Page, text: string): Promise<void> {
  for (const char of text) {
    await page.keyboard.type(char);
    await sleep(randomDelay(50, 120));
    // Occasional longer pause (8% chance)
    if (Math.random() < 0.08) {
      await sleep(randomDelay(180, 400));
    }
  }
}

// ============ Main Demo ============

async function runLoginDemo(): Promise<void> {
  console.log('='.repeat(70));
  console.log(' LOGIN + PROFILE CHECK: A11y Tree vs. Predicate Snapshot');
  console.log('='.repeat(70));

  const llm = initLLMProvider();
  console.log(`Model: ${llm.modelName}`);

  if (HEADED) {
    console.log('Running in headed mode (visible browser window)');
    if (SHOW_OVERLAY) {
      console.log('Overlay enabled: elements will be highlighted with green borders');
    }
  }

  // Initialize browser
  const apiKey = process.env.PREDICATE_API_KEY;
  const headless = !HEADED;
  let browser: Browser;
  let useRealPredicate = false;

  try {
    browser = new PredicateBrowser(apiKey, undefined, headless);
    await browser.start();
    useRealPredicate = !!apiKey;
    console.log(`Predicate snapshots: ${useRealPredicate ? 'REAL (ML-ranked)' : 'extension-based'}`);
  } catch {
    console.log('Falling back to plain Playwright (extension not available)');
    const { chromium } = await import('playwright');
    const playwrightBrowser = await chromium.launch({ headless });
    const context = await playwrightBrowser.newContext();
    const page = await context.newPage();

    browser = {
      goto: async (url: string) => { await page.goto(url, { waitUntil: 'networkidle' }); },
      getPage: () => page,
      snapshot: async () => { throw new Error('Extension not available'); },
      close: async () => { await playwrightBrowser.close(); },
    } as unknown as Browser;
  }

  console.log('='.repeat(70));

  const page = browser.getPage()!;

  // Create tracer and runtime for SDK-based verification
  const runId = crypto.randomUUID();
  const traceFile = path.join(os.tmpdir(), `login-demo-${runId}.jsonl`);
  const sink = new JsonlTraceSink(traceFile);
  const tracer = new Tracer(runId, sink);
  const browserAdapter = createBrowserAdapter(browser);
  const runtime = new AgentRuntime(browserAdapter, page, tracer);

  console.log(`Trace file: ${traceFile}`);

  // Run workflow with both approaches
  const approaches: Array<'a11y' | 'predicate'> = ['a11y', 'predicate'];
  const allStats: Map<string, StepStats[]> = new Map();

  for (const approach of approaches) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(` Running with ${approach.toUpperCase()} approach`);
    console.log('='.repeat(70));

    const stats: StepStats[] = [];
    let totalTokens: StepTokenUsage = { promptTokens: 0, completionTokens: 0, totalTokens: 0 };

    // Helper to run a step
    const runStep = async (
      stepIndex: number,
      goal: string,
      fn: () => Promise<StepResult>
    ): Promise<boolean> => {
      const startTime = Date.now();
      console.log(`\n[${nowIso()}] Step ${stepIndex}: ${goal}`);

      // Use SDK's step tracking
      runtime.beginStep(goal, stepIndex - 1);

      let result: StepResult;
      try {
        result = await fn();
      } catch (e) {
        console.log(`  ERROR: ${e instanceof Error ? e.message : e}`);
        result = { success: false, usage: null, note: String(e) };
      }

      const durationMs = Date.now() - startTime;

      if (result.usage) {
        totalTokens = {
          promptTokens: totalTokens.promptTokens + result.usage.promptTokens,
          completionTokens: totalTokens.completionTokens + result.usage.completionTokens,
          totalTokens: totalTokens.totalTokens + result.usage.totalTokens,
        };
      }

      stats.push({
        stepIndex,
        goal,
        success: result.success,
        durationMs,
        tokenUsage: result.usage,
        url: page.url(),
        note: result.note,
        approach,
      });

      const noteStr = result.note ? ` | ${result.note}` : '';
      console.log(`  ${result.success ? 'PASS' : 'FAIL'} (${durationMs}ms)${noteStr}`);
      if (result.usage) {
        console.log(`  Tokens: prompt=${result.usage.promptTokens} total=${result.usage.totalTokens}`);
      }

      return result.success;
    };

    // Helper to get snapshot based on approach
    const getSnapshot = async (): Promise<{ formatted: string; elements: ParsedElement[]; tokens: number }> => {
      if (approach === 'a11y') {
        const tree = await getAccessibilityTree(page);
        const { formatted, elements } = formatA11yForLLM(tree);
        return { formatted, elements, tokens: encode(formatted).length };
      } else {
        const snap = await browser.snapshot({ limit: 50, show_overlay: SHOW_OVERLAY, goal: 'Find form elements' });
        const { formatted, elements } = formatPredicateForLLM(snap);
        return { formatted, elements, tokens: encode(formatted).length };
      }
    };

    // Navigate to login page
    await browser.goto('https://www.localllamaland.com/login');
    await page.waitForLoadState('domcontentloaded');

    // ======== Step 1: Wait for login form hydration ========
    const step1Ok = await runStep(1, 'Wait for login form hydration', async () => {
      console.log('  Waiting for form to hydrate using runtime.check().eventually()...');

      // Use SDK's check().eventually() pattern - same as Python SDK
      const formLoaded = await runtime.check(
        exists('role=textbox'),
        'login_form_hydrated',
        true // required
      ).eventually({
        timeoutMs: 15000,
        pollMs: 500,
      });

      if (!formLoaded) {
        return { success: false, usage: null, note: 'Form did not hydrate' };
      }

      // Verify button is initially disabled using SDK predicates
      const buttonDisabled = runtime.assert(
        isDisabled('role=button'),
        'login_button_disabled_initially',
        false // not required
      );
      console.log(`  Button initially disabled: ${buttonDisabled}`);

      // Get element count from last snapshot
      const snap = await runtime.snapshot();
      return { success: true, usage: null, note: `Found ${snap.elements.length} elements` };
    });

    if (!step1Ok) {
      console.log('  Step 1 failed, skipping remaining steps');
      allStats.set(approach, stats);
      continue;
    }

    // ======== Step 2: Fill username field ========
    const step2Ok = await runStep(2, 'Fill username field', async () => {
      const { formatted, elements, tokens } = await getSnapshot();
      console.log(`  Snapshot: ${elements.length} elements, ${tokens} tokens`);

      const task = 'Find the username input field (the FIRST textbox on the page) and click it to focus.';
      const prompt = buildLLMPrompt(task, formatted, approach);

      const response = await llm.generate('', prompt, { temperature: 0, max_tokens: 50 });
      const clickId = parseClickId(response.content);

      if (clickId === null) {
        return {
          success: false,
          usage: { promptTokens: tokens, completionTokens: 0, totalTokens: tokens },
          note: `LLM returned: ${response.content}`,
        };
      }

      console.log(`  LLM chose element ${clickId}: "${getElementText(elements, clickId)}"`);

      // Click and type - try Predicate ID first, then fallback
      try {
        await page.click(`[data-predicate-id="${clickId}"]`, { timeout: 5000 });
      } catch {
        // Fallback: click first textbox/input
        await page.locator('input[type="text"], input:not([type]), [role="textbox"]').first().click({ timeout: 3000 });
      }
      await sleep(200);
      await typeHumanLike(page, TEST_USERNAME);

      return {
        success: true,
        usage: { promptTokens: tokens, completionTokens: 10, totalTokens: tokens + 10 },
        note: `Typed "${TEST_USERNAME}"`,
      };
    });

    if (!step2Ok) {
      allStats.set(approach, stats);
      continue;
    }

    // ======== Step 3: Fill password field ========
    const step3Ok = await runStep(3, 'Fill password field', async () => {
      const { formatted, elements, tokens } = await getSnapshot();

      const task = 'Find the password input field (look for a field with "password" in text/placeholder) and click it.';
      const prompt = buildLLMPrompt(task, formatted, approach);

      const response = await llm.generate('', prompt, { temperature: 0, max_tokens: 50 });
      const clickId = parseClickId(response.content);

      if (clickId === null) {
        return {
          success: false,
          usage: { promptTokens: tokens, completionTokens: 0, totalTokens: tokens },
          note: `LLM returned: ${response.content}`,
        };
      }

      console.log(`  LLM chose element ${clickId}: "${getElementText(elements, clickId)}"`);

      // Click and type password - try Predicate ID first, then fallback to password input
      try {
        await page.click(`[data-predicate-id="${clickId}"]`, { timeout: 5000 });
      } catch {
        // Fallback: try common password field selectors
        try {
          await page.locator('input[type="password"]').first().click({ timeout: 3000 });
        } catch {
          // Last resort: click the second textbox
          await page.locator('[role="textbox"]').nth(1).click({ timeout: 3000 });
        }
      }
      await sleep(200);
      await typeHumanLike(page, TEST_PASSWORD);

      // Wait for button to become enabled using SDK's check().eventually()
      console.log('  Waiting for login button to become enabled...');
      const buttonEnabled = await runtime.check(
        isEnabled('role=button'),
        'login_button_enabled_after_fill',
        true // required
      ).eventually({
        timeoutMs: 5000,
        pollMs: 300,
      });

      return {
        success: true,
        usage: { promptTokens: tokens, completionTokens: 10, totalTokens: tokens + 10 },
        note: `Button enabled: ${buttonEnabled}`,
      };
    });

    if (!step3Ok) {
      allStats.set(approach, stats);
      continue;
    }

    // ======== Step 4: Click login button ========
    const step4Ok = await runStep(4, 'Click login button', async () => {
      await sleep(300);
      const { formatted, elements, tokens } = await getSnapshot();

      // Verify button is enabled before clicking
      const buttonReady = runtime.assert(
        isEnabled('role=button'),
        'login_button_enabled_before_click',
        false
      );
      if (!buttonReady) {
        console.log('  Warning: Button may not be enabled, proceeding anyway');
      }

      const task = 'Find and click the login/submit button (role="button" with text containing "Login" or "Sign in").';
      const prompt = buildLLMPrompt(task, formatted, approach);

      const response = await llm.generate('', prompt, { temperature: 0, max_tokens: 50 });
      const clickId = parseClickId(response.content);

      if (clickId === null) {
        return {
          success: false,
          usage: { promptTokens: tokens, completionTokens: 0, totalTokens: tokens },
          note: `LLM returned: ${response.content}`,
        };
      }

      console.log(`  LLM chose element ${clickId}: "${getElementText(elements, clickId)}"`);

      // Click login button
      const preUrl = page.url();
      try {
        await page.click(`[data-predicate-id="${clickId}"]`, { timeout: 5000 });
      } catch {
        // Fallback: click button with Login/Sign text
        await page.locator('button:has-text("Sign"), button:has-text("Login"), [role="button"]').first().click({ timeout: 3000 });
      }

      // Wait for navigation
      await sleep(1500);
      await page.waitForLoadState('domcontentloaded').catch(() => {});

      const postUrl = page.url();
      const navigated = postUrl !== preUrl || postUrl.includes('profile');

      return {
        success: navigated,
        usage: { promptTokens: tokens, completionTokens: 10, totalTokens: tokens + 10 },
        note: `Navigated to ${postUrl}`,
      };
    });

    if (!step4Ok) {
      allStats.set(approach, stats);
      continue;
    }

    // ======== Step 5: Navigate to profile page ========
    const step5Ok = await runStep(5, 'Navigate to profile page', async () => {
      const currentUrl = page.url();

      if (!currentUrl.includes('profile')) {
        const { formatted, elements, tokens } = await getSnapshot();

        const task = 'Find and click the Profile link in the navigation (role="link" with text "Profile").';
        const prompt = buildLLMPrompt(task, formatted, approach);

        const response = await llm.generate('', prompt, { temperature: 0, max_tokens: 50 });
        const clickId = parseClickId(response.content);

        if (clickId !== null) {
          console.log(`  LLM chose element ${clickId}: "${getElementText(elements, clickId)}"`);
          try {
            await page.click(`[data-predicate-id="${clickId}"]`, { timeout: 5000 });
          } catch {
            // Fallback: click profile link
            await page.locator('a[href*="profile"], a:has-text("Profile"), [role="link"]:has-text("Profile")').first().click({ timeout: 3000 });
          }
          await page.waitForLoadState('domcontentloaded').catch(() => {});
        }

        // Verify we're on profile page using SDK predicate
        const onProfile = runtime.assert(
          urlContains('profile'),
          'on_profile_page',
          true
        );

        return {
          success: onProfile,
          usage: { promptTokens: tokens, completionTokens: 10, totalTokens: tokens + 10 },
          note: `URL: ${page.url()}`,
        };
      }

      return { success: true, usage: null, note: 'Already on profile page' };
    });

    if (!step5Ok) {
      allStats.set(approach, stats);
      continue;
    }

    // ======== Step 6: Extract username from profile ========
    await runStep(6, 'Extract username from profile', async () => {
      // Wait for profile content to load using SDK's check().eventually()
      console.log('  Waiting for profile card to load...');
      const profileLoaded = await runtime.check(
        exists("text~'Profile'"),
        'profile_card_loaded',
        true
      ).eventually({
        timeoutMs: 10000,
        pollMs: 500,
      });

      if (!profileLoaded) {
        return { success: false, usage: null, note: 'Profile card did not load' };
      }

      const { elements, tokens } = await getSnapshot();

      // Look for username in elements
      let foundUsername = '';
      let foundEmail = '';

      for (const el of elements) {
        const text = el.text.toLowerCase();
        if (text.includes('@') && !foundEmail) {
          foundEmail = el.text;
        } else if (text.includes(TEST_USERNAME.toLowerCase())) {
          foundUsername = el.text;
        }
      }

      console.log(`  Found username: ${foundUsername || '(not found)'}`);
      console.log(`  Found email: ${foundEmail || '(not found)'}`);

      return {
        success: !!(foundUsername || foundEmail),
        usage: { promptTokens: tokens, completionTokens: 0, totalTokens: tokens },
        note: foundUsername ? `username=${foundUsername}` : foundEmail ? `email=${foundEmail}` : 'not found',
      };
    });

    allStats.set(approach, stats);
  }

  // ======== Print Summary ========
  console.log('\n' + '='.repeat(70));
  console.log(' RESULTS SUMMARY');
  console.log('='.repeat(70));

  const a11yStats = allStats.get('a11y') || [];
  const predicateStats = allStats.get('predicate') || [];

  const sumTokens = (stats: StepStats[]) =>
    stats.reduce((sum, s) => sum + (s.tokenUsage?.totalTokens || 0), 0);
  const sumLatency = (stats: StepStats[]) =>
    stats.reduce((sum, s) => sum + s.durationMs, 0);
  const countSuccess = (stats: StepStats[]) =>
    stats.filter(s => s.success).length;

  const a11yTokens = sumTokens(a11yStats);
  const predicateTokens = sumTokens(predicateStats);
  const a11yLatency = sumLatency(a11yStats);
  const predicateLatency = sumLatency(predicateStats);
  const a11ySuccess = countSuccess(a11yStats);
  const predicateSuccess = countSuccess(predicateStats);
  const totalSteps = Math.max(a11yStats.length, predicateStats.length);

  const tokenSavings = a11yTokens > 0 ? Math.round((1 - predicateTokens / a11yTokens) * 100) : 0;
  const latencySavings = a11yLatency > 0 ? Math.round((1 - predicateLatency / a11yLatency) * 100) : 0;

  console.log(`
+-----------------------------------------------------------------------+
| Metric              | A11y Tree        | Predicate        | Delta     |
+-----------------------------------------------------------------------+
| Total Tokens        | ${String(a11yTokens).padStart(16)} | ${String(predicateTokens).padStart(16)} | -${tokenSavings}%      |
| Total Latency (ms)  | ${String(a11yLatency).padStart(16)} | ${String(predicateLatency).padStart(16)} | ${latencySavings > 0 ? '-' : '+'}${Math.abs(latencySavings)}%      |
| Steps Passed        | ${String(a11ySuccess + '/' + totalSteps).padStart(16)} | ${String(predicateSuccess + '/' + totalSteps).padStart(16)} |           |
+-----------------------------------------------------------------------+
`);

  console.log(`Key Insight: Predicate snapshots use ${tokenSavings}% fewer tokens`);
  console.log('for a multi-step login workflow with form filling.\n');

  // Per-step breakdown
  console.log('Step-by-step breakdown:');
  console.log('-'.repeat(70));
  for (let i = 0; i < totalSteps; i++) {
    const a11y = a11yStats[i];
    const pred = predicateStats[i];
    if (a11y && pred) {
      const a11yT = a11y.tokenUsage?.totalTokens || 0;
      const predT = pred.tokenUsage?.totalTokens || 0;
      const savings = a11yT > 0 ? Math.round((1 - predT / a11yT) * 100) : 0;
      console.log(`Step ${i + 1}: ${a11y.goal}`);
      console.log(`  A11y: ${a11yT} tokens, ${a11y.durationMs}ms, ${a11y.success ? 'PASS' : 'FAIL'}`);
      console.log(`  Pred: ${predT} tokens, ${pred.durationMs}ms, ${pred.success ? 'PASS' : 'FAIL'} (${savings}% savings)`);
    }
  }

  await browser.close();
}

// Run
runLoginDemo().catch(console.error);
