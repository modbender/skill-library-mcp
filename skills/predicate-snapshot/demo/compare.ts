/**
 * Token Usage Comparison Demo
 *
 * Compares token usage between:
 * 1. Accessibility Tree (raw CDP dump)
 * 2. Predicate Snapshot (ML-ranked via PredicateBrowser)
 *
 * Run: PREDICATE_API_KEY=sk-... npm run demo
 */

import { PredicateBrowser, SentienceBrowser, Snapshot } from '@predicatesystems/runtime';
import { encode } from 'gpt-tokenizer';

// Use any to avoid Playwright version type conflicts between SDK and local
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Page = any;
type Browser = InstanceType<typeof SentienceBrowser>;

interface ComparisonResult {
  url: string;
  a11yTokens: number;
  predicateTokens: number;
  savings: number;
  a11yElements: number;
  predicateElements: number;
  isRealPredicate: boolean;
}

interface A11yNode {
  role?: string;
  name?: string;
  children?: A11yNode[];
  [key: string]: unknown;
}

/**
 * Count nodes in accessibility tree
 */
function countA11yNodes(tree: A11yNode | null): number {
  if (!tree) return 0;

  let count = 1;

  if (Array.isArray(tree.children)) {
    for (const child of tree.children) {
      count += countA11yNodes(child);
    }
  }

  return count;
}

/**
 * Get accessibility snapshot using CDP
 */
async function getAccessibilityTree(
  page: Page
): Promise<A11yNode | null> {
  const client = await page.context().newCDPSession(page);

  try {
    const { nodes } = await client.send('Accessibility.getFullAXTree');

    // Convert flat node list to tree structure
    const nodeMap = new Map<string, A11yNode>();
    let root: A11yNode | null = null;

    for (const node of nodes) {
      const a11yNode: A11yNode = {
        role: node.role?.value,
        name: node.name?.value,
        children: [],
      };
      nodeMap.set(node.nodeId, a11yNode);

      if (!node.parentId) {
        root = a11yNode;
      }
    }

    // Build tree relationships
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

/**
 * Format Predicate snapshot to pipe-delimited string for token counting
 */
function formatPredicateSnapshot(snap: Snapshot): string {
  const lines: string[] = ['ID|role|text|imp|is_primary|docYq|ord|DG|href'];

  for (const el of snap.elements.slice(0, 50)) {
    const id = el.id ?? 0;
    const role = el.role ?? '';
    const text = String(el.text ?? '').slice(0, 30).replace(/\|/g, ' ').replace(/\n/g, ' ');
    const imp = el.importance?.toFixed(2) ?? '0';
    const isPrimary = el.visual_cues?.is_primary ? '1' : '0';
    const docYq = el.doc_y ? Math.round(el.doc_y / 200) : 0;
    const ord = el.group_index ?? '-';
    const dg = el.in_dominant_group ? '1' : '0';
    const href = el.href ? String(el.href).slice(0, 20) : '';

    lines.push(`${id}|${role}|${text}|${imp}|${isPrimary}|${docYq}|${ord}|${dg}|${href}`);
  }

  return lines.join('\n');
}

/**
 * Compare token usage for a single URL
 */
async function compareTokenUsage(
  browser: Browser,
  url: string,
  useRealPredicate: boolean
): Promise<ComparisonResult> {
  console.log(`\nAnalyzing: ${url}`);

  await browser.goto(url);
  const page = browser.getPage()!;

  // Wait for dynamic content
  await page.waitForTimeout(2000);

  // 1. Capture accessibility tree (raw approach)
  console.log('  Capturing accessibility tree...');
  const a11yTree = await getAccessibilityTree(page);
  const a11yJson = JSON.stringify(a11yTree, null, 2);
  const a11yTokens = encode(a11yJson).length;
  const a11yElements = countA11yNodes(a11yTree);

  // 2. Capture Predicate snapshot
  let predicateTokens = 0;
  let predicateElements = 0;
  let isRealPredicate = false;

  // Try to use real extension snapshot (works with or without API key)
  const mode = useRealPredicate ? 'REAL - ML-ranked via API' : 'extension (local ranking)';
  console.log(`  Capturing Predicate snapshot (${mode})...`);
  try {
    const snap = await browser.snapshot({ limit: 50 });
    const formatted = formatPredicateSnapshot(snap);
    predicateTokens = encode(formatted).length;
    predicateElements = Math.min(snap.elements.length, 50);
    isRealPredicate = true;
  } catch (error) {
    console.log(`  Warning: Extension snapshot failed, falling back to simulation: ${error}`);
    const simulated = await simulatePredicateSnapshot(page, 50);
    predicateTokens = encode(simulated.output).length;
    predicateElements = simulated.elementCount;
  }

  return {
    url,
    a11yTokens,
    predicateTokens,
    savings: Math.round((1 - predicateTokens / a11yTokens) * 100),
    a11yElements,
    predicateElements,
    isRealPredicate,
  };
}

/**
 * Simulate Predicate snapshot (fallback when no API key)
 */
async function simulatePredicateSnapshot(
  page: Page,
  limit: number
): Promise<{ output: string; elementCount: number }> {
  const a11y = await getAccessibilityTree(page);

  const lines: string[] = ['ID|role|text|imp|is_primary|docYq|ord|DG|href'];

  const interactiveRoles = new Set([
    'button', 'link', 'textbox', 'checkbox', 'radio',
    'combobox', 'searchbox', 'menuitem', 'tab', 'switch',
  ]);

  let id = 1;
  const elements: Array<{ id: number; role: string; name: string; importance: number }> = [];

  function extractElements(node: A11yNode | null): void {
    if (!node) return;

    const role = (node.role || '').toLowerCase();
    const name = node.name || '';

    if (interactiveRoles.has(role) && name) {
      elements.push({
        id: id++,
        role,
        name: name.slice(0, 30),
        importance: Math.random() * 0.5 + 0.5,
      });
    }

    if (Array.isArray(node.children)) {
      for (const child of node.children) {
        extractElements(child);
      }
    }
  }

  extractElements(a11y);
  elements.sort((a, b) => b.importance - a.importance);

  for (const el of elements.slice(0, limit)) {
    const imp = el.importance.toFixed(2);
    const text = el.name.replace(/\|/g, ' ').replace(/\n/g, ' ');
    lines.push(`${el.id}|${el.role}|${text}|${imp}|0|0|-|0|`);
  }

  return { output: lines.join('\n'), elementCount: Math.min(elements.length, limit) };
}

/**
 * Main demo runner
 */
async function runDemo(): Promise<void> {
  const apiKey = process.env.PREDICATE_API_KEY;

  // Test sites: mix of simple, complex, and ad-heavy pages
  const testUrls = [
    'https://news.ycombinator.com',
    'https://example.com',
    'https://httpbin.org/html',
    'https://slickdeals.net',  // Ad-heavy site to show real-world benefits
  ];

  console.log('='.repeat(70));
  console.log(' TOKEN USAGE COMPARISON: Accessibility Tree vs. Predicate Snapshot');
  console.log('='.repeat(70));

  // Try to use PredicateBrowser with extension
  let browser: Browser | null = null;
  let useRealPredicate = false;

  try {
    browser = new PredicateBrowser(
      apiKey,
      undefined, // apiUrl
      true       // headless
    );
    await browser.start();
    useRealPredicate = !!apiKey;
    console.log(' Mode: PredicateBrowser with extension loaded');
    if (useRealPredicate) {
      console.log(' Snapshots: REAL (API key detected)');
    } else {
      console.log(' Snapshots: Extension-based (no API key, local ranking)');
    }
  } catch (error) {
    // Extension not available - fall back to plain Playwright
    console.log(' Mode: Fallback (extension not available)');
    console.log(' Snapshots: SIMULATED');
    console.log(` Note: ${error instanceof Error ? error.message.split('\n')[0] : error}`);

    // Use plain Playwright instead
    const { chromium } = await import('playwright');
    const playwrightBrowser = await chromium.launch({ headless: true });
    const context = await playwrightBrowser.newContext();
    const page = await context.newPage();

    // Create a minimal browser-like object
    browser = {
      goto: async (url: string) => { await page.goto(url, { waitUntil: 'networkidle' }); },
      getPage: () => page,
      snapshot: async () => { throw new Error('Extension not available'); },
      close: async () => { await playwrightBrowser.close(); },
    } as unknown as Browser;
  }

  console.log('='.repeat(70));

  try {
    console.log('\nBrowser started');

    const results: ComparisonResult[] = [];

    for (const url of testUrls) {
      try {
        const result = await compareTokenUsage(browser, url, useRealPredicate);
        results.push(result);
      } catch (error) {
        console.log(`  Error: ${error instanceof Error ? error.message : error}`);
      }
    }

    // Print results
    console.log('\n' + '='.repeat(70));
    console.log(' RESULTS');
    console.log('='.repeat(70));

    let totalA11y = 0;
    let totalPredicate = 0;

    for (const result of results) {
      totalA11y += result.a11yTokens;
      totalPredicate += result.predicateTokens;

      const hostname = new URL(result.url).hostname;
      const mode = result.isRealPredicate ? '(REAL)' : '(simulated)';
      console.log(`\n${hostname} ${mode}`);
      console.log('  +' + '-'.repeat(55) + '+');
      console.log(
        `  | Accessibility Tree: ${result.a11yTokens.toLocaleString().padStart(8)} tokens (${result.a11yElements} elements) |`
      );
      console.log(
        `  | Predicate Snapshot: ${result.predicateTokens.toLocaleString().padStart(8)} tokens (${result.predicateElements} elements) |`
      );
      console.log(`  | Savings:            ${result.savings.toString().padStart(8)}%                      |`);
      console.log('  +' + '-'.repeat(55) + '+');
    }

    // Summary
    const overallSavings = Math.round((1 - totalPredicate / totalA11y) * 100);

    console.log('\n' + '='.repeat(70));
    console.log(
      ` TOTAL: ${totalA11y.toLocaleString()} -> ${totalPredicate.toLocaleString()} tokens (${overallSavings}% reduction)`
    );
    console.log('='.repeat(70));

    // Cost projection
    const tasksPerMonth = 5000;
    const snapshotsPerTask = 5;
    const monthlySnapshots = tasksPerMonth * snapshotsPerTask;
    const avgA11y = totalA11y / results.length;
    const avgPredicate = totalPredicate / results.length;
    const a11yCost = avgA11y * monthlySnapshots * (3 / 1_000_000);
    const predicateCost = avgPredicate * monthlySnapshots * (3 / 1_000_000);

    console.log('\n MONTHLY COST PROJECTION (5,000 tasks, Claude Sonnet)');
    console.log(`   Accessibility Tree: $${a11yCost.toFixed(2)}`);
    console.log(`   Predicate Snapshot: $${predicateCost.toFixed(2)}`);
    console.log(`   Monthly Savings:    $${(a11yCost - predicateCost).toFixed(2)}`);
    console.log('');

  } finally {
    await browser.close();
  }
}

// Run demo
runDemo().catch(console.error);
