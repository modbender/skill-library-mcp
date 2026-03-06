#!/usr/bin/env node
/**
 * validate-kg.mjs — Post-extraction validator
 *
 * Compares article text against current KG to find gaps.
 * Designed to be called INSIDE the extraction bash script as a checkpoint.
 *
 * Usage:
 *   node scripts/validate-kg.mjs --file /tmp/article.txt [--root <id>] [--fix] [--json]
 *
 * Exit codes:
 *   0 = PASS (all quality gates met)
 *   1 = FAIL (gaps found)
 */

import { readFileSync } from 'fs';
import { createInterface } from 'readline';
import { load, getChildren, getEdges } from '../lib/graph.mjs';
import { loadConfig } from '../lib/config.mjs';

// ─── NER: Named Entity Recognition (regex-based) ──────────────────────────

// Common words that look like proper nouns but aren't entities
const STOP_WORDS = new Set([
  // Pronouns & determiners
  'The','This','That','These','Those','What','When','Where','Which','While',
  'How','Why','Who','Whom','Whose','But','And','For','Not','With','From',
  'Here','There','Then','Now','Today','Every','Each','Other','Another',
  'Most','Many','Some','All','Any','Several','Their','They','Its','Our',
  'His','Her','Your','You','Our','Your','My','Its',
  // Prepositions & conjunctions
  'Over','Under','After','Before','Between','Through','During','Without',
  'Against','Within','Along','About','Into','Upon','Onto','Among',
  // Common sentence starters
  'However','Meanwhile','Furthermore','Moreover','Nevertheless','Although',
  'Perhaps','Instead','Indeed','Certainly','Obviously','Clearly',
  // Time words
  'January','February','March','April','May','June','July','August',
  'September','October','November','December','Monday','Tuesday',
  'Wednesday','Thursday','Friday','Saturday','Sunday',
  'Jan','Feb','Mar','Apr','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
  // Common verbs/adjectives that appear capitalized at sentence start
  'See','Just','Still','Even','Only','Also','Like','Make','Take','Get',
  'Think','Know','Want','Need','Say','Tell','Give','Come','Go','Let',
  'Keep','Call','Turn','Put','Run','Set','Try','Ask','Sit','Cut',
  // Common descriptors
  'New','Old','Big','Small','High','Low','Large','Long','Short','Real',
  'White','Black','Blue','Red','Green','Full','Empty','Total','Final',
  // Business/econ terms that appear capitalized
  'CapEx','OpEx','EBITDA','GDP','IPO','YoY','QoQ','ACV','ARR','MBS',
  'FICO','JOLTS','NBER','CBO','FOMC','HELOC','SVO','RBC',
  'Permanent','Structural','Cyclical','Fiscal','Monetary','Federal',
  // Other false positives
  'Meanwhile','Despite','Rather','Whether','Neither','Either',
  'Spread','Premium','Revenue','Growth','Rate','Share','Market',
  'Insurance','Finance','Consulting','Productivity',
]);

// Words that are ALL CAPS and likely not org names (acronyms/abbreviations excluded)
const ALL_CAPS_STOPWORDS = /^[A-Z\s]{2,}$/;  // "CONSULTING AS", "PRODUCTIVITY INITIATIVES"

/**
 * Extract likely organization names from text.
 * Uses multiple heuristic signals, each adding confidence.
 */
function extractOrgs(text) {
  const candidates = new Map(); // name → { score, sources }

  // 1. Ticker pattern: "Company (TICK US)" — very high confidence
  let m;
  const tickerRe = /\b([A-Z][a-zA-Z&\s]{2,30}?)\s*\([A-Z]{1,5}\s+US\)/g;
  while ((m = tickerRe.exec(text)) !== null) {
    addCandidate(candidates, m[1].trim(), 3, 'ticker');
  }

  // 2. Corp suffix: "Foo Inc", "Bar Capital", etc. — high confidence
  //    Capture the FULL name including suffix
  const suffixWords = 'Inc|Corp|LLC|Ltd|Group|Capital|Partners|Management|Holdings|Fund|Financial|Investors|Service|Services|Lab|Labs';
  const corpRe = new RegExp(`\\b([A-Z][a-zA-Z&'.]+(?:\\s+[A-Z][a-zA-Z&'.]+)*\\s+(?:${suffixWords}))\\b`, 'g');
  while ((m = corpRe.exec(text)) !== null) {
    const fullName = m[1].trim();
    const parts = fullName.split(/\s+/);
    // Only count if there's at least one real word before the suffix
    const suffixSet = new Set(suffixWords.split('|'));
    const realWords = parts.filter(p => !suffixSet.has(p));
    if (realWords.length === 0) continue;  // skip pure suffix matches like "Investors Service"
    addCandidate(candidates, fullName, 3, 'corp-suffix');
  }

  // 3. Known financial patterns — high confidence
  const knownPatterns = [
    /\b(Moody's|S&P|Fannie Mae|Freddie Mac|Goldman Sachs|Morgan Stanley|JPMorgan)\b/g,
    /\b([A-Z][a-z]+\s+&\s+[A-Z][a-z]+)\b/g,  // "Hellman & Friedman"
  ];
  for (const p of knownPatterns) {
    while ((m = p.exec(text)) !== null) {
      addCandidate(candidates, m[1] || m[0], 3, 'known-pattern');
    }
  }

  // 4. Possessive with org-like context — medium confidence
  //    "ServiceNow's Q3 report" → ServiceNow
  const possRe = /\b([A-Z][a-zA-Z]{2,}(?:\.[a-z]+)?(?:\s+[A-Z][a-zA-Z]+)*)'s\b/g;
  while ((m = possRe.exec(text)) !== null) {
    const name = m[1].trim();
    if (!isStopWord(name)) {
      addCandidate(candidates, name, 2, 'possessive');
    }
  }

  // 5. Names appearing near financial verbs — medium confidence
  //    "X dropped 9%", "Y fell 18%", "Z reported", "W announced"
  const finVerbRe = /\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\s+(?:dropped|fell|rose|surged|declined|reported|announced|posted|printed|missed|flagged|downgraded|acquired|bought|sold|launched|cut|slashed)\b/g;
  while ((m = finVerbRe.exec(text)) !== null) {
    const name = m[1].trim();
    if (!isStopWord(name) && !ALL_CAPS_STOPWORDS.test(name)) {
      addCandidate(candidates, name, 2, 'fin-verb');
    }
  }

  // Filter: remove stop words, too-short names, ALL-CAPS noise
  const result = new Map();
  for (const [name, info] of candidates) {
    if (isStopWord(name)) continue;
    if (name.length <= 2) continue;
    if (ALL_CAPS_STOPWORDS.test(name) && info.score < 3) continue;
    if (/^\d/.test(name)) continue;  // starts with number
    result.set(name, info);
  }

  return result;
}

/** Extract person names from text */
function extractPeople(text) {
  const people = new Map();

  // Pattern: "FirstName LastName" near person-role words
  const nameRe = /\b([A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}(?:\s+[A-Z][a-z]{1,15})?)\b/g;
  const roleRe = /\b(CEO|CTO|CFO|Chair|Director|Manager|Professor|Author|Founder|analyst|researcher|engineer|proofreader|co-author|friend|colleague|wrote|authored|posed|said|told|called|named)\b/i;

  let m;
  while ((m = nameRe.exec(text)) !== null) {
    const name = m[1];
    // Verify: must be near a role word (within 150 chars)
    const ctx = text.substring(Math.max(0, m.index - 100), m.index + name.length + 150);
    if (roleRe.test(ctx) && !isStopWord(name.split(' ')[0]) && !isOrgLikeName(name)) {
      people.set(name, { source: 'role-context' });
    }
  }

  return people;
}

/** Extract dated events (headlines, quarter/month references) */
function extractEvents(text) {
  const events = [];
  let m;

  // Bloomberg/Reuters-style headlines
  const headlineRe = /([A-Z][A-Z\s:;,'\-]{10,}(?:\|[^|]+)*\|\s*(?:Bloomberg|Reuters|Financial Times|Moody's|Department|Indeed|Zillow|Fannie)[^.]*)/g;
  while ((m = headlineRe.exec(text)) !== null) {
    events.push({ type: 'headline', snippet: m[1].trim().substring(0, 250) });
  }

  // Quarter + Year
  const quarterRe = /\bQ[1-4]\s+20\d{2}\b/gi;
  while ((m = quarterRe.exec(text)) !== null) {
    events.push({ type: 'quarter', snippet: m[0] });
  }

  // Month Year
  const monthRe = /\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b/gi;
  while ((m = monthRe.exec(text)) !== null) {
    events.push({ type: 'month', snippet: m[0] });
  }

  // "early/mid/late YYYY"
  const fuzzyRe = /\b(?:early|mid|late|end of)\s+20\d{2}\b/gi;
  while ((m = fuzzyRe.exec(text)) !== null) {
    events.push({ type: 'fuzzy', snippet: m[0] });
  }

  return events;
}

/** Extract statistics (percentages, dollar amounts) */
function extractStats(text) {
  const stats = [];
  let m;

  const pctRe = /\d+\.?\d*\s*%/g;
  while ((m = pctRe.exec(text)) !== null) stats.push({ type: 'pct', val: m[0] });

  const dollarRe = /\$\d[\d,.]*\s*(?:billion|million|trillion|B|M|T)?/gi;
  while ((m = dollarRe.exec(text)) !== null) stats.push({ type: '$', val: m[0] });

  return stats;
}

// ─── Helpers ───────────────────────────────────────────────────────────────

function addCandidate(map, name, score, source) {
  const existing = map.get(name);
  if (existing) {
    existing.score += score;
    existing.sources.push(source);
  } else {
    map.set(name, { score, sources: [source] });
  }
}

function isStopWord(word) {
  if (STOP_WORDS.has(word)) return true;
  // Single common word (< 4 chars all caps is likely acronym, keep it)
  if (word.length <= 3 && /^[a-z]/i.test(word)) return true;
  return false;
}

function isOrgLikeName(name) {
  const orgIndicators = /\b(Capital|Global|American|International|National|United|Royal|General|First|Standard)\b/;
  return orgIndicators.test(name);
}

// ─── KG Comparison ─────────────────────────────────────────────────────────

function getAllRelatedNodes(store, rootId) {
  const nodeIds = new Set();
  nodeIds.add(rootId);

  // Descendants (recursive)
  function addDescendants(id) {
    for (const n of Object.values(store.nodes)) {
      if (n.parent === id && !nodeIds.has(n.id)) {
        nodeIds.add(n.id);
        addDescendants(n.id);
      }
    }
  }
  addDescendants(rootId);

  // 1-hop relations
  for (const e of (Array.isArray(store.edges) ? store.edges : Object.values(store.edges || {}))) {
    if (nodeIds.has(e.from)) nodeIds.add(e.to);
    if (nodeIds.has(e.to)) nodeIds.add(e.from);
  }

  // Descendants of newly added nodes
  for (const id of [...nodeIds]) addDescendants(id);

  return nodeIds;
}

function calcMaxDepth(store, rootId) {
  let maxDepth = 0;
  function walk(id, d) {
    if (d > maxDepth) maxDepth = d;
    for (const n of Object.values(store.nodes)) {
      if (n.parent === id) walk(n.id, d + 1);
    }
  }
  if (rootId) {
    walk(rootId, 0);
  } else {
    for (const n of Object.values(store.nodes)) {
      if (!n.parent) walk(n.id, 0);
    }
  }
  return maxDepth;
}

function compareWithKG(store, articleEntities, rootId, articleText) {
  // Get relevant nodes
  let nodeIds;
  if (rootId) {
    nodeIds = getAllRelatedNodes(store, rootId);
  } else {
    nodeIds = new Set(Object.keys(store.nodes));
  }

  const nodes = [...nodeIds].map(id => store.nodes[id]).filter(Boolean);
  const edges = (Array.isArray(store.edges) ? store.edges : Object.values(store.edges || {}))
    .filter(e => nodeIds.has(e.from) || nodeIds.has(e.to));

  // Build label index for fuzzy matching
  const kgIndex = new Set();
  for (const n of nodes) {
    kgIndex.add(n.label.toLowerCase());
    kgIndex.add(n.id.toLowerCase().replace(/[_-]/g, ' '));
    if (n.alias) kgIndex.add(n.alias.toLowerCase());
    if (n.tags) for (const t of n.tags) kgIndex.add(t.toLowerCase());
    // Also index words from label for partial matching
    for (const word of n.label.toLowerCase().split(/\s+/)) {
      if (word.length > 3) kgIndex.add(word);
    }
  }

  function isInKG(name) {
    const lower = name.toLowerCase();
    // Exact match
    if (kgIndex.has(lower)) return true;
    // Substring match (either direction)
    for (const l of kgIndex) {
      if (l.length > 3 && (l.includes(lower) || lower.includes(l))) return true;
    }
    // Check if this candidate is a suffix/part of an entity already in KG
    // "Investors Service" from "Moody's Investors Service" → if "moody" is in KG, skip
    // Strategy: check if the article text contains "KG_LABEL + candidate" pattern
    for (const n of nodes) {
      const nl = n.label.toLowerCase();
      // Check if article has "KGLabel ... candidateName" within 5 words
      const pattern = new RegExp(
        nl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "[\\s']{1,5}" + lower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
        'i'
      );
      if (pattern.test(articleText || '')) return true;
    }
    return false;
  }

  // Find missing entities (only high-confidence ones)
  const missingOrgs = [];
  for (const [name, info] of articleEntities.orgs) {
    if (!isInKG(name) && info.score >= 2) missingOrgs.push(name);
  }

  const missingPeople = [];
  for (const [name] of articleEntities.people) {
    if (!isInKG(name)) missingPeople.push(name);
  }

  // KG quality stats
  const typeCount = {};
  for (const n of nodes) typeCount[n.type] = (typeCount[n.type] || 0) + 1;

  const emptyOrgs = nodes.filter(n =>
    n.type === 'org' && (!n.attrs || Object.keys(n.attrs).length === 0)
  );

  const eventsInKG = nodes.filter(n => n.type === 'event');
  const noAttrsEvents = eventsInKG.filter(e =>
    !e.attrs || Object.keys(e.attrs).length === 0
  );

  const maxDepth = calcMaxDepth(store, rootId);

  return {
    totalEntities: nodes.length,
    totalRelations: edges.length,
    maxDepth,
    typeCount,
    emptyOrgs: emptyOrgs.map(n => ({ label: n.label, id: n.id })),
    noAttrsEvents: noAttrsEvents.map(n => ({ label: n.label, id: n.id })),
    eventsInKG: eventsInKG.length,
    detectedEvents: articleEntities.events.length,
    detectedStats: articleEntities.stats.length,
    missing: { orgs: missingOrgs, people: missingPeople },
  };
}

// ─── Output ────────────────────────────────────────────────────────────────

function printReport(comparison, jsonMode, fixMode) {
  const c = comparison;
  const cfg = loadConfig();
  const vc = cfg.validation; // validation config

  if (jsonMode) {
    console.log(JSON.stringify(c, null, 2));
    return c.totalEntities >= vc.minEntities;
  }

  console.log('');
  console.log('╔══════════════════════════════════════════════════════╗');
  console.log('║          KG Extraction Validator                     ║');
  console.log('╚══════════════════════════════════════════════════════╝');
  console.log('');
  console.log('  ── Current KG ──');
  console.log(`  Entities: ${c.totalEntities}  |  Relations: ${c.totalRelations}  |  Max depth: ${c.maxDepth}`);
  console.log(`  Types: ${JSON.stringify(c.typeCount)}`);
  console.log('');

  let failures = 0;
  console.log('  ── Quality Gates ──');

  // 1. Entity count
  if (c.totalEntities < vc.minEntities) {
    console.log(`  ❌ Entities: ${c.totalEntities} (need ≥${vc.minEntities})`);
    failures++;
  } else {
    console.log(`  ✅ Entities: ${c.totalEntities}`);
  }

  // 2. Relations — configurable ratio, min 10
  const relTarget = Math.max(10, Math.round(c.totalEntities * vc.minRelationRatio));
  if (c.totalRelations < relTarget) {
    console.log(`  ❌ Relations: ${c.totalRelations} (need ≥${relTarget} — add more cross-links!)`);
    failures++;
  } else {
    console.log(`  ✅ Relations: ${c.totalRelations}`);
  }

  // 3. Hierarchy depth
  if (c.maxDepth < vc.minDepth) {
    console.log(`  ❌ Depth: ${c.maxDepth} (need ≥${vc.minDepth} — put mechanisms UNDER domains, entities UNDER mechanisms)`);
    failures++;
  } else {
    console.log(`  ✅ Depth: ${c.maxDepth}`);
  }

  // 4. Events
  if (c.eventsInKG < vc.minEvents) {
    console.log(`  ❌ Events: ${c.eventsInKG} (need ≥${vc.minEvents})`);
    failures++;
  } else {
    console.log(`  ✅ Events: ${c.eventsInKG}`);
  }

  // 5. No empty orgs
  if (c.emptyOrgs.length > 0) {
    console.log(`  ❌ Empty orgs (no attrs): ${c.emptyOrgs.map(o => o.label).join(', ')}`);
    failures++;
  } else {
    console.log(`  ✅ All orgs have attrs`);
  }

  // Advisory: events without dates
  if (c.noAttrsEvents.length > 0) {
    console.log(`  ⚠️  Events missing date attrs: ${c.noAttrsEvents.map(e => e.label).join(', ')}`);
  }
  console.log('');

  // Missing entities
  if (c.missing.orgs.length > 0 || c.missing.people.length > 0) {
    console.log('  ── Possibly Missing ──');
    if (c.missing.orgs.length > 0) {
      console.log(`  🏢 Orgs (${c.missing.orgs.length}): ${c.missing.orgs.join(', ')}`);
      failures++;
    }
    if (c.missing.people.length > 0) {
      console.log(`  👤 People (${c.missing.people.length}): ${c.missing.people.join(', ')}`);
      failures++;
    }
    console.log('');
  }

  // Verdict
  console.log('  ══════════════════════════════════════════════════════');
  if (failures === 0) {
    console.log('  ✅ PASS — All quality gates met!');
  } else {
    console.log(`  ❌ FAIL — ${failures} issue(s) found.`);
    console.log('  Write another script to fix the issues above, then validate again.');
  }
  console.log('  ══════════════════════════════════════════════════════');
  console.log('');

  // Fix suggestions
  if (fixMode && failures > 0) {
    console.log('  ── Suggested fixes ──');
    for (const org of c.missing.orgs) {
      const id = 'org_' + org.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      console.log(`  node scripts/add.mjs entity --id "${id}" --type "org" --label "${org}" --parent "PARENT_DOMAIN" --attrs '{"role":"TODO"}'`);
    }
    for (const person of c.missing.people) {
      const id = 'human_' + person.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      console.log(`  node scripts/add.mjs entity --id "${id}" --type "human" --label "${person}" --attrs '{"role":"TODO"}'`);
    }
    for (const org of c.emptyOrgs) {
      console.log(`  # Fix empty org "${org.label}": add --attrs with role/stats`);
    }
    if (c.maxDepth < 3) {
      console.log(`  # Fix depth: move leaf entities to be children of mechanism/concept nodes, not domains directly`);
    }
    if (c.totalRelations < relTarget) {
      console.log(`  # Fix relations: add ${relTarget - c.totalRelations} more cross-links between entities`);
    }
    console.log('');
  }

  return failures === 0;
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const fixMode = args.includes('--fix');
  const rootIdx = args.indexOf('--root');
  const rootId = rootIdx !== -1 ? args[rootIdx + 1] : null;
  const fileIdx = args.indexOf('--file');

  let text = '';
  if (fileIdx !== -1 && args[fileIdx + 1]) {
    text = readFileSync(args[fileIdx + 1], 'utf8');
  } else if (!process.stdin.isTTY) {
    const rl = createInterface({ input: process.stdin });
    const lines = [];
    for await (const line of rl) lines.push(line);
    text = lines.join('\n');
  } else {
    console.error('Usage: node validate-kg.mjs --file article.txt [--root <id>] [--fix] [--json]');
    process.exit(1);
  }

  if (!text.trim()) { console.error('Error: empty input'); process.exit(1); }

  const articleEntities = {
    orgs: extractOrgs(text),
    people: extractPeople(text),
    events: extractEvents(text),
    stats: extractStats(text),
  };

  const store = load();
  const comparison = compareWithKG(store, articleEntities, rootId, text);
  const passed = printReport(comparison, jsonMode, fixMode);
  process.exit(passed ? 0 : 1);
}

main().catch(e => { console.error(e.message); process.exit(1); });
