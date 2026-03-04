#!/usr/bin/env node

import { exec } from 'child_process';
import { promisify } from 'util';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SKILL_DIR = join(__dirname, '..');
const DATA_DIR = join(SKILL_DIR, 'data');
const SAVED_TIPS_FILE = join(DATA_DIR, 'saved-tips.json');
const SKIPPED_FILE = join(DATA_DIR, 'skipped-topics.json');
const PREFERENCES_FILE = join(DATA_DIR, 'preferences.json');

// Ensure data directory exists
if (!existsSync(DATA_DIR)) {
  mkdirSync(DATA_DIR, { recursive: true });
}

// Default data
const DEFAULT_SAVED_TIPS = [];
const DEFAULT_SKIPPED = [];
const DEFAULT_PREFERENCES = {
  categories: ['cost', 'speed', 'memory', 'skills', 'automation'],
  preferredCategory: null,
  impactFilter: 'all' // all, low, medium, high
};

// Sources configuration
const SOURCES = {
  reddit: {
    openclaw: { focus: 'Official tips', keywords: ['openclaw', 'cron', 'skill', 'memory'] },
    LocalLLaMA: { focus: 'LLM optimization', keywords: ['ollama', 'model', 'cost', 'local'] },
    ClaudeAI: { focus: 'AI agent strategies', keywords: ['claude', 'agent', 'automation'] },
    AgentsOfAI: { focus: 'AI implementations', keywords: ['agent', 'automation'] },
    selfhosted: { focus: 'Infrastructure', keywords: ['selfhosted', 'server', 'docker'] }
  },
  github: {
    openclaw: 'openclaw/openclaw'
  }
};

// Tips database (curated from best practices)
const TIPS_DATABASE = [
  {
    id: 'tiered-model-routing',
    title: 'Use tiered model routing',
    category: 'cost',
    impact: 'high',
    effort: 'low',
    content: `Route 80% tasks to cheap model (local model), 20% to premium (premium model). Save ~$50/month.`,
    implementation: `1. Add model routing in cron jobs\n2. Use cheap model for routine tasks\n3. Reserve premium for complex reasoning`,
    docs: 'docs.openclaw.ai/models'
  },
  {
    id: 'cron-script-first',
    title: 'Cron jobs should be script-first',
    category: 'automation',
    impact: 'high',
    effort: 'medium',
    content: `Keep cron prompts short. Convert long instructions to scripts. Reduces tokens and costs.`,
    implementation: `1. Create scripts/ folder\n2. Move complex logic to .mjs files\n3. Cron just runs: node scripts/job.mjs`,
    docs: 'docs.openclaw.ai/cron'
  },
  {
    id: 'alert-only-delivery',
    title: 'Use alert-only delivery for crons',
    category: 'automation',
    impact: 'high',
    effort: 'low',
    content: `Cron jobs should return NO_REPLY when nothing changed. Only alert on anomalies.`,
    implementation: `Add to cron payload:\n- Return NO_REPLY on success\n- Send alert only on error/changes`,
    docs: 'docs.openclaw.ai/cron'
  },
  {
    id: 'semantic-memory',
    title: 'Enable semantic memory search',
    category: 'memory',
    impact: 'high',
    effort: 'medium',
    content: `Use embedding model for semantic search. Better context recall, less token waste.`,
    implementation: `1. Add to config: memorySearch.enabled: true\n2. Use ollama with embedding model\n3. Configure under agents.defaults`,
    docs: 'docs.openclaw.ai/memory'
  },
  {
    id: 'batch-cron-jobs',
    title: 'Batch similar cron jobs together',
    category: 'speed',
    impact: 'medium',
    effort: 'low',
    content: `Combine similar checks into single cron to reduce API calls and overhead.`,
    implementation: `1. Review cron jobs\n2. Group by category\n3. Single cron: email + calendar + weather`,
    docs: 'docs.openclaw.ai/cron'
  },
  {
    id: 'isolated-subagents',
    title: 'Use isolated sub-agents for heavy work',
    category: 'automation',
    impact: 'high',
    effort: 'medium',
    content: `Heavy tasks should run in isolated sessions to avoid main context bloat.`,
    implementation: `Use sessionTarget: "isolated" for:\n- Long-running tasks\n- Background monitoring\n- Heavy computations`,
    docs: 'docs.openclaw.ai/agents'
  },
  {
    id: 'context-discipline',
    title: 'Practice context discipline',
    category: 'memory',
    impact: 'high',
    effort: 'medium',
    content: `Keep context lean. Move static data to references/scripts. Use progressive disclosure.`,
    implementation: `1. Move large data to references/\n2. Keep SKILL.md short\n3. Use memory files for state`,
    docs: 'docs.openclaw.ai/memory'
  },
  {
    id: 'idempotent-crons',
    title: 'Make cron jobs idempotent',
    category: 'automation',
    impact: 'medium',
    effort: 'medium',
    content: `Safe to re-run. Use state files to track progress and avoid duplicate work.`,
    implementation: `1. Add cursor/state file\n2. Check last run before executing\n3. Store outputs in memory/`,
    docs: 'docs.openclaw.ai/cron'
  },
  {
    id: 'heartbeat-optimization',
    title: 'Optimize heartbeat usage',
    category: 'speed',
    impact: 'medium',
    effort: 'low',
    content: `Native heartbeat loads context. Use isolated cron for background checks instead.`,
    implementation: `1. Disable native heartbeat\n2. Use cron: "0 * * * *" for checks\n3. Return NO_REPLY on success`,
    docs: 'docs.openclaw.ai/heartbeat'
  },
  {
    id: 'skills-modular',
    title: 'Keep skills modular and lean',
    category: 'skills',
    impact: 'medium',
    effort: 'medium',
    content: `Short SKILL.md + references/ folder. Heavy skills slow down loading.`,
    implementation: `1. SKILL.md < 100 lines\n2. Move docs to references/\n3. Use metadata for requirements`,
    docs: 'docs.openclaw.ai/skills'
  }
];

// Reddit fetcher
const REDDIT_SKILL = '/home/adelpro/.openclaw/workspace/skills/reddit-readonly/scripts/reddit-readonly.mjs';

async function fetchReddit(subreddit, limit = 10) {
  try {
    const { stdout } = await execAsync(`node ${REDDIT_SKILL} posts ${subreddit} --limit ${limit} --sort hot`);
    return JSON.parse(stdout);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

// Data management functions
function loadData(file, defaults) {
  try {
    if (existsSync(file)) {
      return JSON.parse(readFileSync(file, 'utf-8'));
    }
  } catch (e) {
    // Return defaults on error
  }
  return defaults;
}

function saveData(file, data) {
  try {
    writeFileSync(file, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('Error saving data:', e.message);
  }
}

function getSavedTips() {
  return loadData(SAVED_TIPS_FILE, DEFAULT_SAVED_TIPS);
}

function getSkipped() {
  return loadData(SKIPPED_FILE, DEFAULT_SKIPPED);
}

function getPreferences() {
  return loadData(PREFERENCES_FILE, DEFAULT_PREFERENCES);
}

function saveTip(tipId) {
  const saved = getSavedTips();
  if (!saved.includes(tipId)) {
    saved.push(tipId);
    saveData(SAVED_TIPS_FILE, saved);
    console.log('✓ Tip saved!');
  }
}

function skipTopic(topic) {
  const skipped = getSkipped();
  if (!skipped.includes(topic)) {
    skipped.push(topic);
    saveData(SKIPPED_FILE, skipped);
    console.log('✓ Topic skipped!');
  }
}

// Filter tips based on preferences and history
function getDailyTip() {
  const prefs = getPreferences();
  const skipped = getSkipped();
  const saved = getSavedTips();
  
  // Filter available tips
  let available = TIPS_DATABASE.filter(tip => {
    // Exclude skipped categories
    if (skipped.includes(tip.category)) return false;
    // Exclude specific tips
    if (skipped.includes(tip.id)) return false;
    return true;
  });
  
  // Filter by impact if set
  if (prefs.impactFilter !== 'all') {
    available = available.filter(tip => tip.impact === prefs.impactFilter);
  }
  
  // Prefer unsaved tips first, then rotate through all
  const unsaved = available.filter(tip => !saved.includes(tip.id));
  
  if (unsaved.length > 0) {
    return unsaved[Math.floor(Math.random() * unsaved.length)];
  }
  
  return available[Math.floor(Math.random() * available.length)];
}

// Format tip as message
function formatTip(tip) {
  const impactEmoji = tip.impact === 'high' ? '🟢' : tip.impact === 'medium' ? '🟡' : '🔴';
  const effortText = tip.effort === 'low' ? 'Low Effort' : tip.effort === 'medium' ? 'Medium Effort' : 'High Effort';
  
  return `💡 TIP OF THE DAY
${tip.title}

${impactEmoji} ${effortText} | 📈 ${tip.impact.charAt(0).toUpperCase() + tip.impact.slice(1)} Impact

${tip.content}

🔧 How to:
${tip.implementation}

🔗 ${tip.docs}

━━━━━━━━━━━━━━
👍 Save this | 👎 Skip | ➕ More tips`;
}

// Search tips
function searchTips(query) {
  const q = query.toLowerCase();
  return TIPS_DATABASE.filter(tip => 
    tip.title.toLowerCase().includes(q) ||
    tip.content.toLowerCase().includes(q) ||
    tip.category.includes(q)
  );
}

// Weekly report
function weeklyReport() {
  const saved = getSavedTips();
  const savedTips = TIPS_DATABASE.filter(tip => saved.includes(tip.id));
  
  let report = `📈 OPENCLAW-DAILY-TIPS - Weekly Report

══════════════════════════════════════

📊 This Week:
- Tips shown: ${TIPS_DATABASE.length}
- Tips saved: ${saved.length}

`;
  
  if (savedTips.length > 0) {
    report += `💾 Saved Tips:\n`;
    savedTips.forEach((tip, i) => {
      report += `${i + 1}. ${tip.title} (${tip.category})\n`;
    });
    report += '\n';
  }
  
  report += `📈 Recommended Focus:\n`;
  
  // Count by category
  const categories = {};
  TIPS_DATABASE.forEach(tip => {
    categories[tip.category] = (categories[tip.category] || 0) + 1;
  });
  
  Object.entries(categories).sort((a, b) => b[1] - a[1]).forEach(([cat, count]) => {
    report += `- ${cat}: ${count} tips\n`;
  });
  
  report += '\n⚡ Next Week Goal: Try 3 saved tips';
  
  return report;
}

// CLI
const args = process.argv.slice(2);
const command = args[0] || 'tips';

if (command === 'tips') {
  const tip = getDailyTip();
  console.log('\n' + formatTip(tip));
  console.log('\n(Save this tip: edit data/saved-tips.json)');
  
} else if (command === 'save' && args[1]) {
  saveTip(args[1]);
  
} else if (command === 'skip' && args[1]) {
  skipTopic(args[1]);
  
} else if (command === 'search' && args[1]) {
  const results = searchTips(args[1]);
  console.log(`\n🔍 Results for "${args[1]}":\n`);
  results.forEach((tip, i) => {
    console.log(`${i + 1}. [${tip.category}] ${tip.title}`);
    console.log(`   ${tip.content.substring(0, 100)}...\n`);
  });
  
} else if (command === 'weekly') {
  console.log(weeklyReport());
  
} else if (command === 'all') {
  console.log('\n📚 All Available Tips:\n');
  TIPS_DATABASE.forEach((tip, i) => {
    const saved = getSavedTips();
    const savedMark = saved.includes(tip.id) ? '✓' : ' ';
    console.log(`${savedMark} ${i + 1}. [${tip.category}] ${tip.title}`);
  });
  
} else {
  console.log('Usage:');
  console.log('  node openclaw-daily-tips.mjs tips      # Daily tip');
  console.log('  node openclaw-daily-tips.mjs save <id>  # Save a tip');
  console.log('  node openclaw-daily-tips.mjs skip <topic> # Skip topic');
  console.log('  node openclaw-daily-tips.mjs search <query> # Search');
  console.log('  node openclaw-daily-tips.mjs weekly     # Weekly report');
  console.log('  node openclaw-daily-tips.mjs all        # List all tips');
}
